# Third-party Template Test

このRepositoryは `python-sqlite-tailscale-webapp-template` の第三者利用実地テスト用です。

## 実施内容

- GitHubの **Use this template** から新規Repositoryを作成
- ChatGPT GitHub連携へ新Repositoryを追加
- 日本語Issueを作成
- Issue番号入りBranchを作成
- `app/features/items/` を削除
- 独自 `notes` featureを追加
- Migration / Service / Route / Template / Testをfeature単位で実装
- Pull Request / GitHub Actions CI / Squash Mergeまで確認

## 独自feature

```text
app/features/notes/
├─ __init__.py
├─ routes.py
├─ service.py
├─ templates/notes/index.html
└─ migrations/003_notes.sql
```

URL:

- `/notes`
- `/api/notes`

このRepository固有の検証記録であり、共通テンプレート本体へ業務仕様を追加するものではありません。
