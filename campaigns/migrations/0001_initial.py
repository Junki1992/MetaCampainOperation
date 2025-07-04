# Generated by Django 4.2.7 on 2025-07-04 03:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "campaign_id",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="キャンペーンID"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="キャンペーン名")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "アクティブ"),
                            ("PAUSED", "一時停止"),
                            ("DELETED", "削除済み"),
                            ("ARCHIVED", "アーカイブ"),
                        ],
                        max_length=20,
                        verbose_name="ステータス",
                    ),
                ),
                (
                    "objective",
                    models.CharField(blank=True, max_length=100, verbose_name="目的"),
                ),
                (
                    "daily_budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="日予算",
                    ),
                ),
                (
                    "lifetime_budget",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        max_digits=10,
                        null=True,
                        verbose_name="総予算",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="開始日時"),
                ),
                (
                    "stop_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="終了日時"),
                ),
                (
                    "created_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="作成日時"),
                ),
                (
                    "updated_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="更新日時"),
                ),
                (
                    "impressions",
                    models.IntegerField(default=0, verbose_name="インプレッション数"),
                ),
                ("clicks", models.IntegerField(default=0, verbose_name="クリック数")),
                (
                    "spend",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=10, verbose_name="費用"
                    ),
                ),
                (
                    "ctr",
                    models.DecimalField(
                        decimal_places=4, default=0, max_digits=5, verbose_name="CTR"
                    ),
                ),
                (
                    "cpc",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=10, verbose_name="CPC"
                    ),
                ),
                (
                    "last_synced",
                    models.DateTimeField(auto_now=True, verbose_name="最終同期日時"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="作成日時"),
                ),
            ],
            options={
                "verbose_name": "キャンペーン",
                "verbose_name_plural": "キャンペーン",
                "ordering": ["-created_time"],
            },
        ),
        migrations.CreateModel(
            name="MetaAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="アカウント名")),
                (
                    "account_id",
                    models.CharField(
                        max_length=50, unique=True, verbose_name="アカウントID"
                    ),
                ),
                ("access_token", models.TextField(verbose_name="アクセストークン")),
                ("is_active", models.BooleanField(default=True, verbose_name="有効")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="作成日時"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新日時"),
                ),
            ],
            options={
                "verbose_name": "Metaアカウント",
                "verbose_name_plural": "Metaアカウント",
            },
        ),
        migrations.CreateModel(
            name="CampaignOperation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "operation",
                    models.CharField(
                        choices=[
                            ("START", "開始"),
                            ("PAUSE", "停止"),
                            ("DELETE", "削除"),
                            ("UPDATE", "更新"),
                        ],
                        max_length=20,
                        verbose_name="操作",
                    ),
                ),
                ("success", models.BooleanField(default=True, verbose_name="成功")),
                (
                    "error_message",
                    models.TextField(blank=True, verbose_name="エラーメッセージ"),
                ),
                (
                    "performed_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="実行日時"),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="campaigns.campaign",
                        verbose_name="キャンペーン",
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="実行者",
                    ),
                ),
            ],
            options={
                "verbose_name": "キャンペーン操作履歴",
                "verbose_name_plural": "キャンペーン操作履歴",
                "ordering": ["-performed_at"],
            },
        ),
        migrations.AddField(
            model_name="campaign",
            name="meta_account",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="campaigns.metaaccount",
                verbose_name="Metaアカウント",
            ),
        ),
        migrations.CreateModel(
            name="CampaignPerformance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(verbose_name="日付")),
                (
                    "impressions",
                    models.IntegerField(default=0, verbose_name="インプレッション数"),
                ),
                ("clicks", models.IntegerField(default=0, verbose_name="クリック数")),
                (
                    "spend",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=10, verbose_name="費用"
                    ),
                ),
                (
                    "ctr",
                    models.DecimalField(
                        decimal_places=4, default=0, max_digits=5, verbose_name="CTR"
                    ),
                ),
                (
                    "cpc",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=10, verbose_name="CPC"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="作成日時"),
                ),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="campaigns.campaign",
                        verbose_name="キャンペーン",
                    ),
                ),
            ],
            options={
                "verbose_name": "キャンペーンパフォーマンス",
                "verbose_name_plural": "キャンペーンパフォーマンス",
                "ordering": ["-date"],
                "unique_together": {("campaign", "date")},
            },
        ),
    ]
