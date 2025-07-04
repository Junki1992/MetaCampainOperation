#!/usr/bin/env python
"""
Meta API設定確認スクリプト
"""
import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User

# 環境変数を読み込み
load_dotenv()

def check_api_config():
    """API設定を確認"""
    print("=== Meta API設定確認 ===\n")
    
    # 環境変数の確認
    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    print("1. 環境変数の確認:")
    print(f"   APP_ID: {'✓ 設定済み' if app_id else '✗ 未設定'}")
    print(f"   APP_SECRET: {'✓ 設定済み' if app_secret else '✗ 未設定'}")
    print(f"   ACCESS_TOKEN: {'✓ 設定済み' if access_token else '✗ 未設定'}")
    
    if not all([app_id, app_secret, access_token]):
        print("\n❌ 環境変数が不足しています。.envファイルを確認してください。")
        return False
    
    print("\n2. API接続テスト:")
    try:
        # Facebook API初期化
        FacebookAdsApi.init(
            app_id=app_id,
            app_secret=app_secret,
            access_token=access_token,
            api_version='v18.0'
        )
        print("   ✓ API初期化成功")
        
        # ユーザー情報取得
        api = FacebookAdsApi.get_default_api()
        me = User('me').api_get()
        print(f"   ✓ ユーザーID: {me['id']}")
        print(f"   ✓ ユーザー名: {me.get('name', 'N/A')}")
        
        # 広告アカウント一覧取得
        accounts = me.get_ad_accounts()
        print(f"   ✓ 広告アカウント数: {len(accounts)}")
        
        if accounts:
            print("\n3. 広告アカウント一覧:")
            for i, account in enumerate(accounts[:5], 1):  # 最初の5件のみ表示
                print(f"   {i}. {account.get('name', 'N/A')} (ID: {account['id']})")
            
            # 最初のアカウントでキャンペーン一覧を取得
            first_account = accounts[0]
            print(f"\n4. キャンペーン一覧 ({first_account.get('name', 'N/A')}):")
            
            account = AdAccount(first_account['id'])
            campaigns = account.get_campaigns(
                fields=['id', 'name', 'status'],
                params={'limit': 5}
            )
            
            if campaigns:
                for i, campaign in enumerate(campaigns, 1):
                    print(f"   {i}. {campaign['name']} (ID: {campaign['id']}, ステータス: {campaign['status']})")
            else:
                print("   (キャンペーンが見つかりません)")
        
        print("\n✅ API設定が正常に動作しています！")
        return True
        
    except Exception as e:
        print(f"   ❌ API接続エラー: {str(e)}")
        print("\n🔧 トラブルシューティング:")
        print("   1. .envファイルの設定値を確認")
        print("   2. Meta for Developersでアプリの権限を確認")
        print("   3. アクセストークンの有効期限を確認")
        return False

if __name__ == "__main__":
    check_api_config() 