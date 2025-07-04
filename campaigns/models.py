from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class MetaAccount(models.Model):
    """Meta広告アカウント情報"""
    name = models.CharField(max_length=255, verbose_name="アカウント名")
    account_id = models.CharField(max_length=50, unique=True, verbose_name="アカウントID")
    access_token = models.TextField(verbose_name="アクセストークン")
    is_active = models.BooleanField(default=True, verbose_name="有効")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "Metaアカウント"
        verbose_name_plural = "Metaアカウント"

    def __str__(self):
        return f"{self.name} ({self.account_id})"


class Campaign(models.Model):
    """広告キャンペーン"""
    STATUS_CHOICES = [
        ('ACTIVE', 'アクティブ'),
        ('PAUSED', '一時停止'),
        ('DELETED', '削除済み'),
        ('ARCHIVED', 'アーカイブ'),
    ]

    meta_account = models.ForeignKey(MetaAccount, on_delete=models.CASCADE, verbose_name="Metaアカウント")
    campaign_id = models.CharField(max_length=50, unique=True, verbose_name="キャンペーンID")
    name = models.CharField(max_length=255, verbose_name="キャンペーン名")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="ステータス")
    objective = models.CharField(max_length=100, blank=True, verbose_name="目的")
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="日予算")
    lifetime_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="総予算")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="開始日時")
    stop_time = models.DateTimeField(null=True, blank=True, verbose_name="終了日時")
    created_time = models.DateTimeField(null=True, blank=True, verbose_name="作成日時")
    updated_time = models.DateTimeField(null=True, blank=True, verbose_name="更新日時")
    
    # パフォーマンス指標
    impressions = models.IntegerField(default=0, verbose_name="インプレッション数")
    clicks = models.IntegerField(default=0, verbose_name="クリック数")
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="費用")
    ctr = models.DecimalField(max_digits=5, decimal_places=4, default=0, verbose_name="CTR")
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="CPC")
    
    # 同期情報
    last_synced = models.DateTimeField(auto_now=True, verbose_name="最終同期日時")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "キャンペーン"
        verbose_name_plural = "キャンペーン"
        ordering = ['-created_time']

    def __str__(self):
        return f"{self.name} ({self.campaign_id})"

    @property
    def is_active(self):
        """キャンペーンがアクティブかどうか"""
        return self.status == 'ACTIVE'

    @property
    def can_toggle(self):
        """停止・起動の切り替えが可能かどうか"""
        return self.status in ['ACTIVE', 'PAUSED']


class CampaignPerformance(models.Model):
    """キャンペーンパフォーマンス履歴"""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name="キャンペーン")
    date = models.DateField(verbose_name="日付")
    impressions = models.IntegerField(default=0, verbose_name="インプレッション数")
    clicks = models.IntegerField(default=0, verbose_name="クリック数")
    spend = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="費用")
    ctr = models.DecimalField(max_digits=5, decimal_places=4, default=0, verbose_name="CTR")
    cpc = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="CPC")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "キャンペーンパフォーマンス"
        verbose_name_plural = "キャンペーンパフォーマンス"
        unique_together = ['campaign', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.campaign.name} - {self.date}"


class CampaignOperation(models.Model):
    """キャンペーン操作履歴"""
    OPERATION_CHOICES = [
        ('START', '開始'),
        ('PAUSE', '停止'),
        ('DELETE', '削除'),
        ('UPDATE', '更新'),
    ]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name="キャンペーン")
    operation = models.CharField(max_length=20, choices=OPERATION_CHOICES, verbose_name="操作")
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="実行者")
    success = models.BooleanField(default=True, verbose_name="成功")
    error_message = models.TextField(blank=True, verbose_name="エラーメッセージ")
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="実行日時")

    class Meta:
        verbose_name = "キャンペーン操作履歴"
        verbose_name_plural = "キャンペーン操作履歴"
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.campaign.name} - {self.get_operation_display()} ({self.performed_at})"
