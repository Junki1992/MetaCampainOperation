from django.contrib import admin
from .models import MetaAccount, Campaign, CampaignPerformance, CampaignOperation


@admin.register(MetaAccount)
class MetaAccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'account_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'account_id', 'is_active')
        }),
        ('認証情報', {
            'fields': ('access_token',),
            'classes': ('collapse',)
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'campaign_id', 'meta_account', 'status', 'objective',
        'daily_budget', 'impressions', 'clicks', 'spend', 'ctr', 'cpc', 'last_synced'
    ]
    list_filter = ['status', 'objective', 'meta_account', 'created_time']
    search_fields = ['name', 'campaign_id']
    readonly_fields = [
        'campaign_id', 'created_time', 'updated_time', 'last_synced', 'created_at',
        'impressions', 'clicks', 'spend', 'ctr', 'cpc'
    ]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('meta_account', 'campaign_id', 'name', 'status', 'objective')
        }),
        ('予算設定', {
            'fields': ('daily_budget', 'lifetime_budget')
        }),
        ('期間設定', {
            'fields': ('start_time', 'stop_time')
        }),
        ('パフォーマンス指標', {
            'fields': ('impressions', 'clicks', 'spend', 'ctr', 'cpc'),
            'classes': ('collapse',)
        }),
        ('システム情報', {
            'fields': ('created_time', 'updated_time', 'last_synced', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """手動でのキャンペーン追加を無効化"""
        return False


@admin.register(CampaignPerformance)
class CampaignPerformanceAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'date', 'impressions', 'clicks', 'spend', 'ctr', 'cpc']
    list_filter = ['date', 'campaign__meta_account']
    search_fields = ['campaign__name']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        """手動でのパフォーマンスデータ追加を無効化"""
        return False


@admin.register(CampaignOperation)
class CampaignOperationAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'operation', 'performed_by', 'success', 'performed_at']
    list_filter = ['operation', 'success', 'performed_at', 'campaign__meta_account']
    search_fields = ['campaign__name', 'performed_by__username']
    readonly_fields = ['performed_at']
    
    fieldsets = (
        ('操作情報', {
            'fields': ('campaign', 'operation', 'performed_by', 'success')
        }),
        ('エラー情報', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('日時情報', {
            'fields': ('performed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """手動での操作履歴追加を無効化"""
        return False
