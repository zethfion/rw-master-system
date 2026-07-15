# RW Master System

[English](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

[![CI](https://github.com/zethfion/rw-master-system/actions/workflows/ci.yml/badge.svg)](https://github.com/zethfion/rw-master-system/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/zethfion/rw-master-system)](https://github.com/zethfion/rw-master-system/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![支援平台](https://img.shields.io/badge/支援平台-Codex%20%7C%20Claude%20Code%20%7C%20Grok-6f42c1)](#安裝-v021-plugin)

RW Master System 是一套開源的 Agent Skill 與 plugin，用來從公開資料或使用者已獲授權的材料，建立私密、來源有據的 AI 專家知識系統。同一份核心 skill 可同時用於 Codex、Claude Code 與 Grok；各平台只提供薄薄一層原生 manifest，不複製核心內容。

它會引導 agent 盤點來源、保存證據、蒸餾可重用的框架、建立誠實的專家輪廓，並教使用者如何操作成果。倉庫提供方法、模板與離線驗證工具，不包含任何人的私人語料庫。

## 使用者會得到什麼體驗

原本，有用的知識可能散落在書籍、影片、podcast、文章、email 與筆記裡。一般 AI 雖然能生成看似合理的答案，使用者卻很難確認答案根據哪份來源、是否真的符合該專家的方法，以及模型有哪些事情其實不知道。

RW Master System 會協助你把已獲授權的材料整理成一套私密的專家知識包，直接在 Codex、Claude Code 或 Grok 裡使用。完成小型 MVP 後，你可以：

- 直接提出工作上的真實問題，不必自己回頭翻遍所有資料。
- 得到適用的框架與可執行建議，同時看見證據來源、取捨及明確標示的未知事項。
- 把專家的方法運用在策略、寫作、審查或決策上，不必要求 AI 冒充本人，也不會覆蓋你自己的聲音。
- 比較多套專家知識包，保留真正的分歧，而不是強行混合成一個模糊答案。
- 持續加入新的授權材料，保留可追溯的變更，不必每次從頭重建。

一次典型的諮詢，可以只有這麼簡單：

```text
請用這套專家知識包檢視我的產品推出計畫。告訴我適用哪個框架、引用支持結論的來源、分開標示證據與推論，並指出目前仍不知道什麼。
```

agent 會挑選相關的框架卡，只取回回答這個問題所需的來源片段，提供一份可以檢查、而不是只能選擇相信的答案。資料範圍、隱私與最終判斷仍由你掌控。

## 這個倉庫包含什麼

- `skills/master-system-builder/SKILL.md`：可重用的 agent 工作流程。
- `skills/master-system-builder/references/`：來源、證據、安全與維運的詳細指引。
- `skills/master-system-builder/scripts/`：可重現的本機初始化與驗證工具。
- `skills/master-system-builder/assets/`：建立新專家包時使用的空白模板。
- `.codex-plugin/`、`.claude-plugin/` 與 `plugin.json`：各平台的原生發行 metadata。
- `evals/` 與 `tests/`：觸發案例、隱私回歸測試與確定性驗證。

## 這個倉庫絕不包含什麼

- 私人 email、付費課程內容、書籍全文或真實諮詢紀錄。
- token、cookie、憑證、signed URL 或帳號識別資訊。
- 預先製作、用來冒充真人的模仿品。
- telemetry 或隱藏的網路 callback。

## 安裝 v0.2.1 plugin

### Codex

```bash
codex plugin marketplace add zethfion/rw-master-system --ref v0.2.1
codex plugin add rw-master-system@rw-master-system
```

開啟新的 Codex task，然後呼叫 `$master-system-builder`，或直接用自然語言描述要建立的專家知識系統。

### Claude Code

```bash
claude plugin marketplace add zethfion/rw-master-system
claude plugin install rw-master-system@rw-master-system
```

開啟新的 Claude Code session。呼叫 `/rw-master-system:master-system-builder`，或直接用自然語言描述任務。

### Grok

```bash
grok plugin install zethfion/rw-master-system@v0.2.1
```

開啟新的 Grok session。呼叫 `/master-system-builder`，或直接用自然語言描述任務。

## 只安裝 standalone skill

請複製完整的 `skills/master-system-builder` 資料夾，包含其中的 `LICENSE`，放到平台支援的 skill 探索路徑：

- Codex：`${CODEX_HOME:-$HOME/.codex}/skills/`
- Claude Code：`~/.claude/skills/`
- Grok：`~/.grok/skills/` 或 `~/.agents/skills/`

請勿只複製 `SKILL.md`；這套工作流程也依賴同資料夾內的 scripts、references、assets 與 canonical `VERSION` 檔。

## 快速開始

範例指令：

```text
使用 $master-system-builder 幫我為 <名稱> 建立一套私密的專家知識系統。請先提出 Phase 0 方案。我有權使用這些材料：<連結或路徑>。這套系統要幫我完成：<具體目的>。
```

skill 會先提出小規模方案並確認資料來源邊界。除非使用者已明確授權，否則不會批次下載資料，也不會跨越登入、付款或其他存取控制。

內附 script 會從安裝後的 skill 目錄解析路徑，不依賴呼叫者目前所在的工作目錄。

## 驗證層級

```bash
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level structure
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level mvp
python3 /path/to/master-system-builder/scripts/validate_master.py /path/to/expert-package --level release
```

- `structure`：驗證 schema、必要路徑、版本來源與隱私預設值。
- `mvp`：另外要求至少一份已接受的本機證據、可追溯 claim、三張有來源的 framework card、明確的未知事項，以及一個 consultation 範例。
- `release`：再要求人工把 `public_release_allowed` 設為 `true`，並拒絕私人 corpus 目錄、secret、個人 email、隱藏控制字元與 symlink。

剛初始化的空骨架只會通過 `structure`，不會被誤判成已完成的 MVP。

## 隱私模型

新產生的 package 預設包含私密 `.gitignore`、`PRIVACY.md`、停用的 network telemetry，以及 `public_release_allowed: false`。把此值改成 `true` 是需要人類明確批准的發布步驟，不會自動發生。

## 來源標記

由內附 script 初始化的 package 會記錄透明識別碼 `rw-master-system/v1` 與生成 skill 版本 `0.2.1`。這是公開來源標記，不是追蹤機制；任何使用資料都不會離開使用者的電腦。

## 社群與聯絡方式

- 一般問題、想法與合作交流：[GitHub Discussions](https://github.com/zethfion/rw-master-system/discussions)
- 可重現的 bug 與功能建議：[GitHub Issues](https://github.com/zethfion/rw-master-system/issues)
- 敏感安全問題：[GitHub Private Vulnerability Reporting](https://github.com/zethfion/rw-master-system/security/advisories/new)

請勿在公開的 Issues 或 Discussions 張貼私人來源、個人資料、付費內容、憑證或漏洞證據。Git commit metadata 中的 GitHub noreply 地址只用於作者歸屬，不是有人查看的聯絡信箱。

## 參與貢獻

歡迎改善文件、補測試與提出範圍明確的修正。如果要大幅修改工作流程或 schema，請先開 Discussion 或 Issue，確認證據、隱私與平台相容邊界。

請在獨立 branch 工作，開 pull request 合併進 `main`，並執行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_distribution.py
python3 skills/master-system-builder/scripts/audit_public_release.py .
```

請維持 `skills/master-system-builder/` 為唯一核心 skill。各平台 manifest 只能是薄 adapter，不應複製 `SKILL.md`。

## 授權

採用 MIT License，詳見 `LICENSE`。
