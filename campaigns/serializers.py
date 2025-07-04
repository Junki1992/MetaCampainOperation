from rest_framework import serializers
from .models import Campaign, MetaAccount, CampaignPerformance, CampaignOperation


class MetaAccountSerializer(serializers.ModelSerializer):
    """Metaアカウントシリアライザー"""
    
    class Meta:
        model = MetaAccount
        fields = ['id', 'name', 'account_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CampaignPerformanceSerializer(serializers.ModelSerializer):
    """キャンペーンパフォーマンスシリアライザー"""
    
    class Meta:
        model = CampaignPerformance
        fields = ['id', 'date', 'impressions', 'clicks', 'spend', 'ctr', 'cpc', 'created_at']
        read_only_fields = ['created_at']


class CampaignSerializer(serializers.ModelSerializer):
    """キャンペーンシリアライザー"""
    meta_account = MetaAccountSerializer(read_only=True)
    performance_history = CampaignPerformanceSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'campaign_id', 'name', 'status', 'status_display', 'objective',
            'daily_budget', 'lifetime_budget', 'start_time', 'stop_time',
            'created_time', 'updated_time', 'impressions', 'clicks', 'spend',
            'ctr', 'cpc', 'last_synced', 'created_at', 'meta_account',
            'performance_history', 'is_active', 'can_toggle'
        ]
        read_only_fields = [
            'campaign_id', 'created_time', 'updated_time', 'last_synced',
            'created_at', 'is_active', 'can_toggle'
        ]


class CampaignToggleSerializer(serializers.Serializer):
    """キャンペーン停止・起動用シリアライザー"""
    action = serializers.ChoiceField(choices=['start', 'pause'], required=True)
    
    def validate_action(self, value):
        """アクションの妥当性を検証"""
        if value not in ['start', 'pause']:
            raise serializers.ValidationError("Invalid action. Must be 'start' or 'pause'.")
        return value


class CampaignOperationSerializer(serializers.ModelSerializer):
    """キャンペーン操作履歴シリアライザー"""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    operation_display = serializers.CharField(source='get_operation_display', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = CampaignOperation
        fields = [
            'id', 'campaign', 'campaign_name', 'operation', 'operation_display',
            'performed_by', 'performed_by_name', 'success', 'error_message',
            'performed_at'
        ]
        read_only_fields = ['performed_at']


class CampaignListSerializer(serializers.ModelSerializer):
    """キャンペーン一覧用シリアライザー（軽量版）"""
    meta_account_name = serializers.CharField(source='meta_account.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'campaign_id', 'name', 'status', 'status_display',
            'objective', 'daily_budget', 'impressions', 'clicks', 'spend',
            'ctr', 'cpc', 'last_synced', 'meta_account_name', 'is_active', 'can_toggle'
        ]
        read_only_fields = ['last_synced', 'is_active', 'can_toggle']


class CampaignSyncSerializer(serializers.Serializer):
    """キャンペーン同期用シリアライザー"""
    account_id = serializers.CharField(required=True)
    
    def validate_account_id(self, value):
        """アカウントIDの妥当性を検証"""
        try:
            MetaAccount.objects.get(account_id=value)
        except MetaAccount.DoesNotExist:
            raise serializers.ValidationError("Meta account not found.")
        return value 