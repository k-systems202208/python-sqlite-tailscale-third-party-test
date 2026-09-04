# Notes Web App

`python-sqlite-tailscale-webapp-template` から作成した第三者利用テスト用のWebアプリです。

共通基盤の Flask / SQLite / Tailscale / Auth / CSRF / Security / Migration / Backup / Doctor / CI は維持し、テンプレートの `items` サンプルを削除して独自の `notes` featureへ置き換えています。

## 構成

```text
app/features/notes/
├─ __init__.py
├─ routes.py
├─ service.py
├─ templates/notes/index.html
└─ migrations/003_notes.sql
```

共通基盤は `app/core/`、`app/auth.py`、`app/db.py`、`app/csrf.py`、`app/security.py` 等をそのまま利用します。

## URL

- `/` - 共通core
- `/notes` - Notes画面
- `/api/notes` - ログイン利用者本人のNotes API
- `/healthz` - Webプロセス生存確認
- `/readyz` - SQLite readiness
- `/api/me` - 現在利用者

旧サンプルの `/items` / `/api/items` は削除済みです。

## 開発開始

Windows PowerShell:

```powershell
python -m scripts.doctor
.\scripts\bootstrap.ps1
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m scripts.doctor
.\scripts\check.ps1
.\scripts\start.ps1
```

macOS / Linux:

```bash
python3 -m scripts.doctor
./scripts/bootstrap.sh
cp .env.example .env
.venv/bin/python -m scripts.doctor
./scripts/check.sh
./scripts/start.sh
```

## Notesのデータ設計

`notes` は利用者ごとの個人データです。SELECT / UPDATE / DELETEは `owner_user_id` をSQL条件に含め、他利用者のデータを操作できないようにしています。

Migrationは `003_notes.sql` を使用します。テンプレートのsample migration version 2を過去に適用した環境でもversion番号を再利用しないためです。新規DBではversion 1 → 3の順で適用されます。

## 品質確認

```powershell
.\scripts\check.ps1
```

CIではPython 3.11 / 3.12 / 3.13 / 3.14とWindows PowerShell 5.1を確認します。

## GitHub運用

このRepositoryでは次を使用します。

```text
日本語Issue
  ↓
Issue番号入りBranch
  ↓
Commit / Push
  ↓
Pull Request
  ↓
GitHub Actions CI
  ↓
Squash Merge
```

Git / GitHubの操作説明は [BEGINNER-GUIDE.md](BEGINNER-GUIDE.md) を参照してください。

## 共通ドキュメント

テンプレート由来の共通基盤を安全に維持するため、独自アプリ化後も次の資料を残します。

- [docs/CUSTOMIZING.md](docs/CUSTOMIZING.md) - テンプレートから独自アプリへ作り替える手順
- [docs/EXTENDING.md](docs/EXTENDING.md) - feature追加時の共通契約
- [docs/OPERATIONS.md](docs/OPERATIONS.md) - 運用・障害切り分け・Backup / Restore
- [docs/TEMPLATE-SMOKE-TEST.md](docs/TEMPLATE-SMOKE-TEST.md) - 第三者利用の受入確認
- [docs/GITHUB-SETUP.md](docs/GITHUB-SETUP.md) - GitHub Ruleset / Required Check設定

## 実地テスト記録

このRepositoryを作成してからの検証内容は [THIRD-PARTY-TEST.md](THIRD-PARTY-TEST.md) に記録しています。
