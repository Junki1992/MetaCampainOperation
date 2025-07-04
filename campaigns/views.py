from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Campaign, MetaAccount, CampaignOperation
from .serializers import (
    CampaignSerializer, CampaignListSerializer, CampaignToggleSerializer,
    CampaignOperationSerializer, MetaAccountSerializer, CampaignSyncSerializer
)
from .services import MetaAPIService, CampaignSyncService
import json
import logging

logger = logging.getLogger(__name__)


# Create your views here.

# Web UI Views
@login_required
def dashboard(request):
    """ダッシュボード画面"""
    campaigns = Campaign.objects.select_related('meta_account').all()
    meta_accounts = MetaAccount.objects.filter(is_active=True)
    
    context = {
        'campaigns': campaigns,
        'meta_accounts': meta_accounts,
        'total_campaigns': campaigns.count(),
        'active_campaigns': campaigns.filter(status='ACTIVE').count(),
        'paused_campaigns': campaigns.filter(status='PAUSED').count(),
    }
    return render(request, 'campaigns/dashboard.html', context)


@login_required
def campaign_detail(request, campaign_id):
    """キャンペーン詳細画面"""
    campaign = get_object_or_404(Campaign, id=campaign_id)
    operations = CampaignOperation.objects.filter(campaign=campaign).order_by('-performed_at')[:10]
    
    context = {
        'campaign': campaign,
        'operations': operations,
    }
    return render(request, 'campaigns/campaign_detail.html', context)


@login_required
def sync_campaigns(request):
    """キャンペーン同期画面"""
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        if account_id:
            try:
                meta_account = MetaAccount.objects.get(account_id=account_id)
                sync_service = CampaignSyncService()
                synced_count = sync_service.sync_campaigns(meta_account)
                messages.success(request, f'{synced_count}件のキャンペーンを同期しました。')
            except Exception as e:
                messages.error(request, f'同期エラー: {str(e)}')
    
    meta_accounts = MetaAccount.objects.filter(is_active=True)
    return render(request, 'campaigns/sync_campaigns.html', {'meta_accounts': meta_accounts})


@login_required
def account_list(request):
    """Metaアカウント一覧画面"""
    accounts = MetaAccount.objects.all().order_by('-created_at')
    
    context = {
        'accounts': accounts,
        'total_accounts': accounts.count(),
        'active_accounts': accounts.filter(is_active=True).count(),
    }
    return render(request, 'campaigns/account_list.html', context)


@login_required
def account_add(request):
    """Metaアカウント追加画面"""
    if request.method == 'POST':
        account_id = request.POST.get('account_id')
        if account_id and not account_id.startswith('act_'):
            account_id = f'act_{account_id}'
        name = request.POST.get('name')
        access_token = request.POST.get('access_token')
        
        if account_id and name:
            try:
                # 既存アカウントかチェック
                existing = MetaAccount.objects.filter(account_id=account_id).first()
                if existing:
                    messages.error(request, 'このアカウントIDは既に登録されています。')
                else:
                    MetaAccount.objects.create(
                        account_id=account_id,
                        name=name,
                        access_token=access_token or '',
                        is_active=True
                    )
                    messages.success(request, 'アカウントを追加しました。')
                    return redirect('campaigns:account_list')
            except Exception as e:
                messages.error(request, f'アカウント追加エラー: {str(e)}')
    
    return render(request, 'campaigns/account_add.html')


@login_required
def account_edit(request, account_id):
    """Metaアカウント編集画面"""
    account = get_object_or_404(MetaAccount, id=account_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        is_active = request.POST.get('is_active') == 'on'
        access_token = request.POST.get('access_token')
        
        if name:
            try:
                account.name = name
                account.is_active = is_active
                if access_token:
                    account.access_token = access_token
                account.save()
                messages.success(request, 'アカウントを更新しました。')
                return redirect('campaigns:account_list')
            except Exception as e:
                messages.error(request, f'アカウント更新エラー: {str(e)}')
    
    context = {
        'account': account,
    }
    return render(request, 'campaigns/account_edit.html', context)


@login_required
def account_delete(request, account_id):
    """Metaアカウント削除"""
    account = get_object_or_404(MetaAccount, id=account_id)
    
    if request.method == 'POST':
        try:
            account.delete()
            messages.success(request, 'アカウントを削除しました。')
        except Exception as e:
            messages.error(request, f'アカウント削除エラー: {str(e)}')
    
    return redirect('campaigns:account_list')


@login_required
def account_detail(request, account_id):
    """Metaアカウント詳細画面"""
    account = get_object_or_404(MetaAccount, id=account_id)
    return render(request, 'campaigns/account_detail.html', {'account': account})


# API Views
class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """キャンペーン管理API"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Campaign.objects.select_related('meta_account').all()
        
        # フィルタリング
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        account_filter = self.request.query_params.get('account', None)
        if account_filter:
            queryset = queryset.filter(meta_account__account_id=account_filter)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """キャンペーンの停止・起動切り替え"""
        campaign = self.get_object()
        serializer = CampaignToggleSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            
            try:
                meta_service = MetaAPIService()
                
                if action == 'start':
                    new_status = 'ACTIVE'
                    operation_type = 'START'
                else:
                    new_status = 'PAUSED'
                    operation_type = 'PAUSE'
                
                # Meta APIでステータス更新
                meta_service.update_campaign_status(campaign.campaign_id, new_status)
                
                # ローカルDBも更新
                campaign.status = new_status
                campaign.save()
                
                # 操作履歴を記録
                CampaignOperation.objects.create(
                    campaign=campaign,
                    operation=operation_type,
                    performed_by=request.user,
                    success=True
                )
                
                return Response({
                    'success': True,
                    'message': f'キャンペーンを{action}しました。',
                    'new_status': new_status
                })
                
            except Exception as e:
                # 操作履歴を記録（エラー）
                CampaignOperation.objects.create(
                    campaign=campaign,
                    operation=operation_type,
                    performed_by=request.user,
                    success=False,
                    error_message=str(e)
                )
                
                return Response({
                    'success': False,
                    'message': f'操作に失敗しました: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """キャンペーン情報の同期"""
        campaign = self.get_object()
        
        try:
            sync_service = CampaignSyncService()
            sync_service.sync_campaigns(campaign.meta_account)
            
            # 更新されたキャンペーン情報を取得
            campaign.refresh_from_db()
            serializer = self.get_serializer(campaign)
            
            return Response({
                'success': True,
                'message': 'キャンペーン情報を同期しました。',
                'campaign': serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'同期に失敗しました: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class MetaAccountViewSet(viewsets.ReadOnlyModelViewSet):
    """Metaアカウント管理API"""
    queryset = MetaAccount.objects.filter(is_active=True)
    serializer_class = MetaAccountSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def sync_accounts(self, request):
        """Metaアカウント一覧の同期"""
        try:
            meta_service = MetaAPIService()
            accounts_data = meta_service.get_ad_accounts()
            
            synced_count = 0
            for account_data in accounts_data:
                account, created = MetaAccount.objects.update_or_create(
                    account_id=account_data['id'],
                    defaults={
                        'name': account_data['name'],
                        'is_active': True,
                    }
                )
                synced_count += 1
            
            return Response({
                'success': True,
                'message': f'{synced_count}件のアカウントを同期しました。',
                'accounts_count': synced_count
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'同期に失敗しました: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class CampaignOperationViewSet(viewsets.ReadOnlyModelViewSet):
    """キャンペーン操作履歴API"""
    queryset = CampaignOperation.objects.select_related('campaign', 'performed_by').all()
    serializer_class = CampaignOperationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # キャンペーンIDでフィルタリング
        campaign_id = self.request.query_params.get('campaign', None)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        return queryset.order_by('-performed_at')


# AJAX Views
@csrf_exempt
@require_http_methods(["POST"])
def ajax_toggle_campaign(request):
    """AJAX用キャンペーン切り替え"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '認証が必要です。'})
    
    try:
        data = json.loads(request.body)
        campaign_id = data.get('campaign_id')
        action = data.get('action')
        
        if not campaign_id or not action:
            return JsonResponse({'success': False, 'message': 'パラメータが不足しています。'})
        
        campaign = get_object_or_404(Campaign, id=campaign_id)
        
        if not campaign.can_toggle:
            return JsonResponse({'success': False, 'message': 'このキャンペーンは操作できません。'})
        
        meta_service = MetaAPIService()
        
        if action == 'start':
            new_status = 'ACTIVE'
            operation_type = 'START'
        elif action == 'pause':
            new_status = 'PAUSED'
            operation_type = 'PAUSE'
        else:
            return JsonResponse({'success': False, 'message': '無効なアクションです。'})
        
        # Meta APIでステータス更新
        meta_service.update_campaign_status(campaign.campaign_id, new_status)
        
        # ローカルDBも更新
        campaign.status = new_status
        campaign.save()
        
        # 操作履歴を記録
        CampaignOperation.objects.create(
            campaign=campaign,
            operation=operation_type,
            performed_by=request.user,
            success=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'キャンペーンを{action}しました。',
            'new_status': new_status,
            'campaign_id': campaign_id
        })
        
    except Exception as e:
        logger.error(f"AJAX toggle error: {e}")
        return JsonResponse({
            'success': False,
            'message': f'操作に失敗しました: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def ajax_sync_campaigns(request):
    """AJAX用キャンペーン同期"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '認証が必要です。'})
    
    try:
        data = json.loads(request.body)
        account_id = data.get('account_id')
        
        if not account_id:
            return JsonResponse({'success': False, 'message': 'アカウントIDが必要です。'})
        
        meta_account = get_object_or_404(MetaAccount, account_id=account_id)
        sync_service = CampaignSyncService()
        synced_count = sync_service.sync_campaigns(meta_account)
        
        return JsonResponse({
            'success': True,
            'message': f'{synced_count}件のキャンペーンを同期しました。',
            'synced_count': synced_count
        })
        
    except Exception as e:
        logger.error(f"AJAX sync error: {e}")
        return JsonResponse({
            'success': False,
            'message': f'同期に失敗しました: {str(e)}'
        })
