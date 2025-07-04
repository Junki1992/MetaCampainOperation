from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'campaigns', views.CampaignViewSet, basename='campaign')
router.register(r'accounts', views.MetaAccountViewSet, basename='account')
router.register(r'operations', views.CampaignOperationViewSet, basename='operation')

app_name = 'campaigns'

urlpatterns = [
    # Web UI URLs
    path('', views.dashboard, name='dashboard'),
    path('campaign/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('sync/', views.sync_campaigns, name='sync_campaigns'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # AJAX URLs
    path('ajax/toggle/', views.ajax_toggle_campaign, name='ajax_toggle_campaign'),
    path('ajax/sync/', views.ajax_sync_campaigns, name='ajax_sync_campaigns'),

    # アカウント管理URLs
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.account_add, name='account_add'),
    path('accounts/<int:account_id>/edit/', views.account_edit, name='account_edit'),
    path('accounts/<int:account_id>/delete/', views.account_delete, name='account_delete'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
] 