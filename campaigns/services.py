import os
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError
import logging

logger = logging.getLogger(__name__)


class MetaAPIService:
    """Meta Marketing APIとの通信を行うサービス"""
    
    def __init__(self, access_token=None):
        self.access_token = access_token or settings.META_ACCESS_TOKEN
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        
        # Facebook API初期化
        FacebookAdsApi.init(
            app_id=self.app_id,
            app_secret=self.app_secret,
            access_token=self.access_token,
            api_version='v18.0'
        )
    
    def get_ad_accounts(self):
        """広告アカウント一覧を取得"""
        try:
            # ユーザーの広告アカウントを取得
            me = FacebookAdsApi.get_default_api().get_object('me')
            accounts = me.get_ad_accounts()
            
            account_list = []
            for account in accounts:
                account_data = {
                    'id': account['id'],
                    'name': account.get('name', ''),
                    'account_status': account.get('account_status'),
                    'currency': account.get('currency'),
                    'timezone_name': account.get('timezone_name'),
                }
                account_list.append(account_data)
            
            return account_list
            
        except FacebookRequestError as e:
            logger.error(f"Meta API error: {e}")
            raise Exception(f"Meta API error: {e}")
    
    def get_campaigns(self, account_id, limit=100):
        """指定アカウントのキャンペーン一覧を取得"""
        try:
            account = AdAccount(account_id)
            
            # キャンペーン情報を取得
            campaigns = account.get_campaigns(
                fields=[
                    'id',
                    'name',
                    'status',
                    'objective',
                    'daily_budget',
                    'lifetime_budget',
                    'start_time',
                    'stop_time',
                    'created_time',
                    'updated_time',
                    'insights{impressions,clicks,spend,ctr,cpc}'
                ],
                params={
                    'limit': limit,
                    'date_preset': 'last_30d'
                }
            )
            
            campaign_list = []
            for campaign in campaigns:
                # パフォーマンスデータを取得
                insights = campaign.get('insights', {}).get('data', [])
                performance = insights[0] if insights else {}
                
                campaign_data = {
                    'id': campaign['id'],
                    'name': campaign['name'],
                    'status': campaign['status'],
                    'objective': campaign.get('objective', ''),
                    'daily_budget': campaign.get('daily_budget', 0) / 100 if campaign.get('daily_budget') else None,
                    'lifetime_budget': campaign.get('lifetime_budget', 0) / 100 if campaign.get('lifetime_budget') else None,
                    'start_time': campaign.get('start_time'),
                    'stop_time': campaign.get('stop_time'),
                    'created_time': campaign.get('created_time'),
                    'updated_time': campaign.get('updated_time'),
                    'impressions': performance.get('impressions', 0),
                    'clicks': performance.get('clicks', 0),
                    'spend': float(performance.get('spend', 0)),
                    'ctr': float(performance.get('ctr', 0)) if performance.get('ctr') else 0,
                    'cpc': float(performance.get('cpc', 0)) if performance.get('cpc') else 0,
                }
                campaign_list.append(campaign_data)
            
            return campaign_list
            
        except FacebookRequestError as e:
            logger.error(f"Meta API error for account {account_id}: {e}")
            raise Exception(f"Meta API error: {e}")
    
    def update_campaign_status(self, campaign_id, status):
        """キャンペーンのステータスを更新"""
        try:
            campaign = Campaign(campaign_id)
            
            # ステータスを更新
            if status == 'ACTIVE':
                campaign.api_update(fields=[], params={'status': 'ACTIVE'})
            elif status == 'PAUSED':
                campaign.api_update(fields=[], params={'status': 'PAUSED'})
            else:
                raise ValueError(f"Invalid status: {status}")
            
            return True
            
        except FacebookRequestError as e:
            logger.error(f"Meta API error updating campaign {campaign_id}: {e}")
            raise Exception(f"Meta API error: {e}")
    
    def get_campaign_performance(self, campaign_id, date_preset='last_30d'):
        """キャンペーンのパフォーマンスデータを取得"""
        try:
            campaign = Campaign(campaign_id)
            
            insights = campaign.get_insights(
                fields=[
                    'impressions',
                    'clicks',
                    'spend',
                    'ctr',
                    'cpc',
                    'date_start',
                    'date_stop'
                ],
                params={
                    'date_preset': date_preset,
                    'time_increment': 1
                }
            )
            
            performance_data = []
            for insight in insights:
                data = {
                    'date': insight['date_start'],
                    'impressions': int(insight.get('impressions', 0)),
                    'clicks': int(insight.get('clicks', 0)),
                    'spend': float(insight.get('spend', 0)),
                    'ctr': float(insight.get('ctr', 0)) if insight.get('ctr') else 0,
                    'cpc': float(insight.get('cpc', 0)) if insight.get('cpc') else 0,
                }
                performance_data.append(data)
            
            return performance_data
            
        except FacebookRequestError as e:
            logger.error(f"Meta API error getting performance for campaign {campaign_id}: {e}")
            raise Exception(f"Meta API error: {e}")


class CampaignSyncService:
    """キャンペーン同期サービス"""
    
    def __init__(self):
        self.meta_service = MetaAPIService()
    
    def sync_campaigns(self, meta_account):
        """指定アカウントのキャンペーンを同期"""
        from .models import Campaign, CampaignPerformance
        
        try:
            # Meta APIからキャンペーン一覧を取得
            campaigns_data = self.meta_service.get_campaigns(meta_account.account_id)
            
            synced_count = 0
            for campaign_data in campaigns_data:
                # キャンペーンを更新または作成
                campaign, created = Campaign.objects.update_or_create(
                    campaign_id=campaign_data['id'],
                    defaults={
                        'meta_account': meta_account,
                        'name': campaign_data['name'],
                        'status': campaign_data['status'],
                        'objective': campaign_data['objective'],
                        'daily_budget': campaign_data['daily_budget'],
                        'lifetime_budget': campaign_data['lifetime_budget'],
                        'start_time': campaign_data['start_time'],
                        'stop_time': campaign_data['stop_time'],
                        'created_time': campaign_data['created_time'],
                        'updated_time': campaign_data['updated_time'],
                        'impressions': campaign_data['impressions'],
                        'clicks': campaign_data['clicks'],
                        'spend': campaign_data['spend'],
                        'ctr': campaign_data['ctr'],
                        'cpc': campaign_data['cpc'],
                    }
                )
                
                # パフォーマンスデータも同期
                self.sync_campaign_performance(campaign)
                synced_count += 1
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Campaign sync error: {e}")
            raise e
    
    def sync_campaign_performance(self, campaign):
        """キャンペーンのパフォーマンスデータを同期"""
        from .models import CampaignPerformance
        
        try:
            # 過去30日分のパフォーマンスデータを取得
            performance_data = self.meta_service.get_campaign_performance(
                campaign.campaign_id, 
                date_preset='last_30d'
            )
            
            for data in performance_data:
                CampaignPerformance.objects.update_or_create(
                    campaign=campaign,
                    date=data['date'],
                    defaults={
                        'impressions': data['impressions'],
                        'clicks': data['clicks'],
                        'spend': data['spend'],
                        'ctr': data['ctr'],
                        'cpc': data['cpc'],
                    }
                )
                
        except Exception as e:
            logger.error(f"Performance sync error for campaign {campaign.id}: {e}")
            # パフォーマンス同期エラーは致命的ではないので、ログのみ残す 