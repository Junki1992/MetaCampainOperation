# Meta広告キャンペーン自動管理ツール

Meta Marketing APIを使用して広告キャンペーンの自動停止・起動を管理するWebアプリケーションです。

## 機能

- **キャンペーン管理**: 複数アカウントのキャンペーン一覧表示・操作
- **自動スケジューリング**: 時間指定・条件付きでの自動停止・起動
- **認証管理**: Meta API トークンの安全な管理
- **Web UI**: 直感的なダッシュボード

## 技術スタック

- **Backend**: Django 4.2 + Django REST Framework
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL
- **API**: Meta Marketing API (facebook-business)
- **Frontend**: HTML/CSS/JavaScript (Bootstrap)

## セットアップ

### 1. 環境準備

```bash
# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下を設定：

```env
# Django設定
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/campaign_db

# Meta API設定
META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
META_ACCESS_TOKEN=your-access-token

# Redis設定
REDIS_URL=redis://localhost:6379/0

# セキュリティ
ENCRYPTION_KEY=your-encryption-key
```

### 3. データベース設定

```bash
# マイグレーション実行
python manage.py makemigrations
python manage.py migrate

# スーパーユーザー作成
python manage.py createsuperuser
```

### 4. Celery設定

```bash
# Redis起動（別ターミナル）
redis-server

# Celeryワーカー起動（別ターミナル）
celery -A campaign_operation worker -l info

# Celeryビート起動（別ターミナル）
celery -A campaign_operation beat -l info
```

### 5. 開発サーバー起動

```bash
python manage.py runserver
```

## 使用方法

1. **Metaアカウント認証**: `/auth/meta/` でMetaアカウントにログイン
2. **キャンペーン確認**: `/campaigns/` でキャンペーン一覧を表示
3. **スケジュール設定**: `/schedules/` で自動操作を設定
4. **手動操作**: キャンペーン一覧から個別に停止・起動

## プロジェクト構造

```
campaign_operation/
├── manage.py
├── requirements.txt
├── campaign_operation/          # プロジェクト設定
├── campaigns/                   # キャンペーン管理
├── accounts/                    # 認証管理
├── scheduler/                   # スケジューリング
└── templates/                   # HTMLテンプレート
```

## ライセンス

MIT License 