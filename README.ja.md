# RW Master System

[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

[![CI](https://github.com/zethfion/rw-master-system/actions/workflows/ci.yml/badge.svg)](https://github.com/zethfion/rw-master-system/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/zethfion/rw-master-system)](https://github.com/zethfion/rw-master-system/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![対応プラットフォーム](https://img.shields.io/badge/対応-Codex%20%7C%20Claude%20Code%20%7C%20Grok-6f42c1)](https://github.com/zethfion/rw-master-system#install-the-v021-plugin)

RW Master System は、公開資料またはユーザーが利用権限を持つ資料から、非公開かつ出典に基づく AI 専門家ナレッジシステムを構築するためのオープンソース Agent Skill / plugin です。同じ正規 skill を Codex、Claude Code、Grok で利用でき、各プラットフォーム固有の部分は薄いネイティブ manifest に限定しています。

この skill は、情報源の棚卸し、証拠の保存、再利用可能なフレームワークの蒸留、誠実な専門家プロファイルの作成、完成したシステムの利用方法まで agent を導きます。このリポジトリに含まれるのは手法、テンプレート、オフライン検証ツールであり、個人の非公開コーパスではありません。

## このリポジトリに含まれるもの

- `skills/master-system-builder/SKILL.md`：再利用可能な agent ワークフロー。
- `skills/master-system-builder/references/`：情報源、証拠、安全性、運用に関する詳細ガイド。
- `skills/master-system-builder/scripts/`：決定論的なローカル初期化・検証ツール。
- `skills/master-system-builder/assets/`：新しい専門家パッケージへコピーする空のテンプレート。
- `.codex-plugin/`、`.claude-plugin/`、`plugin.json`：各プラットフォーム向けのネイティブ配布 metadata。
- `evals/` と `tests/`：トリガーケース、プライバシー回帰テスト、決定論的検証。

## このリポジトリに含まれないもの

- 非公開 email、有料講座の内容、書籍本文、実在する相談記録。
- token、cookie、認証情報、署名付き URL、アカウント識別子。
- 実在人物になりすますための構築済み模倣物。
- telemetry や隠されたネットワーク callback。

## v0.2.1 plugin のインストール

### Codex

```bash
codex plugin marketplace add zethfion/rw-master-system --ref v0.2.1
codex plugin add rw-master-system@rw-master-system
```

新しい Codex task を開始し、`$master-system-builder` を呼び出すか、構築したい専門家ナレッジシステムを自然言語で説明してください。

### Claude Code

```bash
claude plugin marketplace add zethfion/rw-master-system
claude plugin install rw-master-system@rw-master-system
```

新しい Claude Code session を開始してください。`/rw-master-system:master-system-builder` を呼び出すか、タスクを自然言語で説明できます。

### Grok

```bash
grok plugin install zethfion/rw-master-system@v0.2.1
```

新しい Grok session を開始してください。`/master-system-builder` を呼び出すか、タスクを自然言語で説明できます。

## standalone skill のみをインストールする

`LICENSE` を含む `skills/master-system-builder` ディレクトリ全体を、各プラットフォームが検出する次の場所へコピーしてください。

- Codex：`${CODEX_HOME:-$HOME/.codex}/skills/`
- Claude Code：`~/.claude/skills/`
- Grok：`~/.grok/skills/` または `~/.agents/skills/`

`SKILL.md` だけをコピーしないでください。このワークフローは同梱の scripts、references、assets、正規 `VERSION` ファイルにも依存しています。

## クイックスタート

プロンプト例：

```text
$master-system-builder を使って、<名前> の非公開な専門家ナレッジシステムを構築してください。まず Phase 0 の提案から始めてください。私は次の資料を利用する権限を持っています：<リンクまたはパス>。このシステムの具体的な目的は <目的> です。
```

skill は、小規模な提案と情報源の境界確認から始めます。ユーザーが明示的に許可しない限り、資料を一括取得したり、認証・課金・その他のアクセス制御を越えたりしません。

同梱 script はインストール後の skill ディレクトリを基準に解決されるため、呼び出し元の現在の作業ディレクトリには依存しません。

## 検証レベル

```bash
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level structure
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level mvp
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level release
```

- `structure`：schema、必須パス、バージョンの provenance、プライバシー既定値を検証します。
- `mvp`：受理済みのローカル証拠、追跡可能な claim、情報源付きの framework card 3 件、明示された未知事項、consultation 例も要求します。
- `release`：さらに `public_release_allowed: true` という明示的な承認を要求し、非公開 corpus、secret、個人 email、不可視制御文字、symlink を拒否します。

初期化直後の空のパッケージが通過できるのは `structure` だけで、完成済み MVP として扱われることはありません。

## プライバシーモデル

生成されるパッケージには、非公開を既定とする `.gitignore`、`PRIVACY.md`、無効化された network telemetry、`public_release_allowed: false` が含まれます。この値を `true` に変更することは、人間による明示的な公開承認であり、自動的には行われません。

## プロベナンス

同梱 script で初期化したパッケージには、透明な識別子 `rw-master-system/v1` と生成 skill バージョン `0.2.1` が記録されます。これは公開された由来の印であり、追跡機能ではありません。利用データがユーザーの端末外へ送信されることはありません。

## コミュニティと連絡先

- 質問、アイデア、協業の相談：[GitHub Discussions](https://github.com/zethfion/rw-master-system/discussions)
- 再現可能な bug と機能提案：[GitHub Issues](https://github.com/zethfion/rw-master-system/issues)
- 機密性の高いセキュリティ報告：[GitHub Private Vulnerability Reporting](https://github.com/zethfion/rw-master-system/security/advisories/new)

非公開の情報源、個人情報、有料コンテンツ、認証情報、脆弱性の証拠を公開 Issues や Discussions に投稿しないでください。Git commit metadata に保存される GitHub noreply アドレスは著者帰属のためのもので、連絡用 inbox ではありません。

## コントリビューション

ドキュメント修正、テスト、範囲を限定した改善を歓迎します。ワークフローや schema を大きく変更する場合は、証拠・プライバシー・互換性の境界を明確にするため、まず Discussion または Issue を作成してください。

独立した branch で作業し、`main` への pull request を作成して、次を実行してください。

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_distribution.py
python3 skills/master-system-builder/scripts/audit_public_release.py .
```

`skills/master-system-builder/` を唯一の正規 skill として維持してください。プラットフォーム manifest は薄い adapter にとどめ、`SKILL.md` を複製してはいけません。

## ライセンス

MIT License です。詳細は `LICENSE` を参照してください。
