---
name: tech-writter
description: "Backend service technical documentation writer. Generate comprehensive API documentation with endpoint specs, request and response field details, constraints, samples, auth and permission guides, internal logic explanations, diagrams, database notes, performance notes, and changelogs for backend services. When key delivery choices are missing, pause and run a short clarification flow one question at a time before writing. Use when: (1) writing backend API documentation, (2) documenting internal service logic, (3) creating technical specs for backend services, (4) generating API reference docs from code, (5) user mentions 'tech doc', 'API doc', 'backend doc', 'service doc', 'technical documentation', or '技術文檔'."
---

# Tech Writter - 後端服務技術文檔撰寫

## Core principles

1. 把技術文檔當成可交付成果，而不是簡短摘要。
2. 先讀程式碼、路由、資料模型、測試與配置，再開始寫文檔。
3. 不可虛構端點、欄位、流程、權限、錯誤碼或資料表。
4. 若關鍵交付選項缺失，必須先與使用者確認，再開始撰寫。
5. 只問真正影響結果的問題；若答案已由使用者明示或可從專案規則確認，就不要做形式化追問。
6. 當資訊不足時，寧可明確標註「待確認」或「未驗證」，也不要用空泛內容把段落湊滿。
7. 預設產出應足以支援交接、評審與後續維護，不要只寫成高層介紹。
8. 文檔範圍、文檔深度與輸出格式不得由 agent 自行默認補完；若使用者未明示且 repo 未硬性規定，必須先問。

## Workflow

Generate backend technical documentation in these steps:

1. **Gather context** - Read source code, routes, handlers, DTOs, services, tests, configs, SQL, and existing docs. Build an evidence list before writing.
2. **Lock delivery choices** - Extract what is already known from the user request and repository policy. If important choices are still missing, ask the user one question at a time using the clarification protocol below.
3. **Set depth and scope** - Decide whether the output is API-only, logic-focused, or a full service dossier. Then match the document depth to the user's need instead of defaulting to a thin outline.
4. **Generate document** - Follow the document structure below and cover every verified section that applies.
5. **Mark gaps explicitly** - If some details cannot be verified from code or context, add a short "Known gaps / assumptions" note instead of guessing.
6. **Convert format** - If PDF or Word is needed, first generate HTML, then convert via scripts.

## Required clarification step

Before drafting the document, extract whatever you can from the current
conversation and project files. Then check whether these items are known and
materially affect the result:

1. 文檔範圍
2. 文檔深度
3. 輸出格式
4. 語言
5. 圖表密度（僅在涉及內部邏輯、架構或資料流說明時需要）

Treat an item as "known" only when one of these is true:

1. 使用者已明確指定。
2. repo / 團隊規則已硬性規定，且沒有其他可選空間。
3. 代碼或既有交付流程能唯一鎖定答案，而不是只提供弱訊號。

Weak signals do **not** count as locked choices. Do not silently infer scope,
depth, or format from:

- 服務名稱，例如「pi-be 手冊」
- 任務類型，例如「技術手冊」「技術文檔」
- 輸出目錄或檔名
- skill 自己偏好的 recommended 選項
- agent 自己對「通常應該怎麼做」的判斷

If scope, depth, or output format are not explicitly locked under the rules
above, you must ask before drafting. Only skip clarification when every
required item is truly fixed, not merely guessable.

Examples:

- User says「寫 pi-be 手冊，輸出到某目錄」:
  scope = unknown, depth = unknown, format = unknown → must ask.
- User says「寫 pi-be 完整服務技術手冊，完整交接版，HTML」:
  scope = known, depth = known, format = known → can continue.
- Repo requires Traditional Chinese for docs:
  language = known from repo rule → do not ask language.

### Sequential clarification protocol

When any required item is missing, use this exact interaction style:

1. 每次只問一個尚未確認的問題。
2. 每題都要提供**剛好三個**互斥選項。
3. 其中一個選項必須直接標註 `Recommended`，並在同一行用簡短理由說明為何推薦。
4. 選項要根據當前情境改寫，不要每次機械重複同一組文案。
5. 問完一題後，必須等待使用者回答，不能在同一則訊息中追問下一題。
6. 不可在同一則訊息中重複同一題、同一組選項，或重貼已鎖定的摘要。
7. 若使用者已用自由文字清楚回答，即使沒有選編號，也應直接採納並進入下一個缺失項。
8. 每次收到回答後，只用一行短句確認剛鎖定的選擇，再決定是否需要下一題。
9. 在所有必要答案都已鎖定前，不得開始撰寫最終文檔。
10. 每一則澄清回覆最多只能包含：
    - 一行已鎖定項確認
    - 一個待回答問題標題
    - 一組三選一選項

## Clarification question catalog

Use the following question types only when the answer is still unknown. Adjust
the wording to fit the user's actual request.

### 1. 文檔範圍

Ask this when the user只說「寫技術文檔」「寫手冊」「寫 pi-be 手冊」這類籠統需求，
但沒有明確說清楚要覆蓋哪些內容。服務名、模組名或輸出路徑都不等於已鎖定範圍。

Recommended option pattern:

1. `完整服務文檔 (Recommended: 能同時覆蓋 API、內部邏輯、資料結構與運維重點，最不容易寫得過薄)`
2. `API 接口文檔`
3. `內部邏輯 / 架構說明`

### 2. 文檔深度

Ask this when the user沒有明確說明要簡版、標準版還是完整交接版。這一題優先級很高，
因為它直接決定文檔是否會過於簡單。像「寫一份手冊」「寫完整一點」這種表述若仍
有解釋空間，仍然要問，不可直接默認成完整交接版。

Recommended option pattern:

1. `完整交接版 (Recommended: 會補齊參數、範例、錯誤碼、流程圖與限制條件，適合交付和審查)`
2. `標準說明版`
3. `快速概覽版`

Depth expectations:

- **完整交接版**：盡量覆蓋所有適用章節；每個端點都要有完整參數表、至少一個成功回應與一個常見錯誤回應；非平凡邏輯需要圖表與文字解釋。
- **標準說明版**：保留完整章節骨架，但可合併次要補充；端點範例與錯誤場景可以精簡到代表性內容。
- **快速概覽版**：只適用於明確要求精簡時；仍需列出範圍、限制與未展開項，不可冒充完整技術文檔。

### 3. 輸出格式

Ask this when the deliverable format is not fixed by the user or repo workflow.
輸出目錄、檔名或你自己偏好的展示方式都不算格式已鎖定；只有使用者明確說
HTML / Markdown / PDF / Word，或 repo 明文規定某種格式時，才能跳過這一題。

Recommended option pattern:

1. `HTML (Recommended: 最適合長文、側邊導航、Mermaid 與 SVG 動態流程圖)`
2. `Markdown`
3. `PDF / Word 成品`

If the repo already enforces a specific format, do not ask this question.

### 4. 語言

Ask this only when language is unclear and there is no stronger repository or
team convention.

Recommended option pattern:

1. `依專案慣例語言 (Recommended: 可保持與現有文檔與團隊溝通一致)`
2. `繁體中文`
3. `English / bilingual`

If repository instructions already require a language, follow that rule and skip
this question.

### 5. 圖表密度

Ask this when the request包含內部邏輯、資料流、架構或 onboarding 交接需求，而圖表量會明顯影響交付結果。
若你已鎖定「完整服務文檔」或「內部邏輯 / 架構說明」，但使用者沒有明確表態圖表量，
這一題通常也要問，不能直接默認成「關鍵流程圖即可」。

Recommended option pattern:

1. `關鍵流程圖即可 (Recommended: 兼顧資訊量與可讀性，不會讓文檔太空也不會過度堆圖)`
2. `完整圖表版`
3. `純文字為主`

## Coverage standard

Unless the user explicitly asks for a lightweight output, the document should
meet this bar:

1. 端點清單不能漏掉主要公開接口。
2. 每個端點都應交代用途、認證、參數、限制、成功回應、常見錯誤與 cURL 範例。
3. 內部邏輯不可只貼圖，必須搭配文字說明輸入、判斷條件、輸出與副作用。
4. 若有資料表、儲存層或實體關係，應補上 ER 圖或結構說明。
5. 若有速率限制、快取、超時、分頁、非同步任務，應在性能與限制章節交代。
6. 若版本資訊不完整，應明示 changelog 依據來源，必要時標示「待補」。
7. 若任何章節不適用，也應簡短說明「不適用原因」，不要直接空白略過。

## Document structure

Every backend service doc should include these sections in order when evidence
exists. If a section is not applicable, say so briefly.

### 1. Overview (概述)

- Service name, version, base URL
- Brief description of the service's purpose
- Tech stack summary
- Dependencies on other services

### 2. Authentication & Authorization (認證與授權)

- Auth method (Bearer Token / API Key / OAuth2 / Session)
- Token acquisition flow (use Mermaid sequence diagram when applicable)
- Token refresh mechanism
- Role or permission matrix table

### 3. API Reference (API 接口文檔)

For each endpoint, include:

**Endpoint header**

- HTTP method + path + status badge (`stable` / `beta` / `deprecated`)
- One-line description
- Detailed behavior or side effects when they matter

**Parameters table** (see [references/api_doc_spec.md](references/api_doc_spec.md) for full spec):

| Parameter | Type | Required | Constraints | Default | Description |
|-----------|------|----------|-------------|---------|-------------|

- Include path params, query params, headers, and request body
- For nested objects, use dot notation, such as `data.user.name`
- Always specify type, required or optional, constraints, default value, and meaning

**Request and response samples**

- Success request with full headers and body
- Success response (`200` / `201`)
- Error response (at least one representative common error)
- cURL example for each endpoint

### 4. Error Code Reference (錯誤碼對照表)

- Unified error response format
- Error code table grouped by HTTP status
- See [references/api_doc_spec.md](references/api_doc_spec.md) §4 for encoding rules

### 5. Internal Logic (內部邏輯說明)

Use diagrams to explain complex logic. See
[references/diagram_guide.md](references/diagram_guide.md) for templates.

Diagram selection:

- API request flow → Mermaid Sequence Diagram
- Business logic branching → Mermaid Flowchart
- Resource state transitions → Mermaid State Diagram
- Data flow with animation → SVG animated arrows (HTML only)
- Database relationships → Mermaid ER Diagram
- Data model structure → Mermaid Class Diagram

For HTML format, prefer SVG animated flow diagrams for data flow visualization
when they genuinely add clarity.

For Markdown format, use Mermaid only.

### 6. Database Schema (數據庫結構)

- ER diagram (`mermaid erDiagram`)
- Key table descriptions with column details
- Index strategy notes

### 7. Performance & Rate Limiting (性能與限流)

- Rate limit rules per endpoint or role
- Timeout settings
- Pagination strategy
- Caching strategy notes
- Async job or queue behavior when applicable

### 8. Version Changelog (版本變更記錄)

- Follow format in [references/api_doc_spec.md](references/api_doc_spec.md) §6
- Categories: Added / Changed / Deprecated / Removed / Breaking Changes
- If the changelog basis is incomplete, explicitly state the comparison baseline

### 9. Known Gaps / Assumptions (已知缺口 / 假設)

- List any unverified details, unavailable examples, or repo areas that were not inspected
- Keep this section short, specific, and evidence-based

## Output format guide

### HTML (Recommended)

- Use the template at [assets/template.html](assets/template.html)
- Features: sidebar navigation, Mermaid rendering, SVG animations, responsive, print-friendly
- Replace `{{DOC_TITLE}}`, `{{VERSION}}`, `{{DATE}}`, `{{AUTHOR}}`, `{{LANG}}` placeholders
- Build sidebar nav from h2 and h3 headings
- Mermaid diagrams render automatically via CDN

### Markdown

- Standard GFM (GitHub Flavored Markdown)
- Use fenced code blocks with `mermaid` language tag for diagrams
- No SVG animation support; use static Mermaid diagrams instead

### PDF (from HTML)

- Run: `python scripts/html_to_pdf.py <input.html> [output.pdf]`
- Requires: `pip install weasyprint`
- CJK fonts handled automatically (Noto Sans TC/SC)

### Word / DOCX (from HTML)

- Run: `python scripts/html_to_docx.py <input.html> [output.docx]`
- Requires: `pip install python-docx`
- Uses Microsoft JhengHei font for CJK support
- Tables and code blocks preserved

## CJK font strategy

To prevent garbled Chinese characters across all formats:

- **HTML**: CSS font-family includes Noto Sans TC, Microsoft JhengHei, PingFang TC
- **PDF**: WeasyPrint with Google Fonts Noto Sans TC import
- **Word**: python-docx with Microsoft JhengHei as default font
- **Markdown**: No font control needed (renderer handles it)

## References

- **API documentation spec**: [references/api_doc_spec.md](references/api_doc_spec.md) - Parameter tables, error codes, auth patterns, changelog format
- **Diagram guide**: [references/diagram_guide.md](references/diagram_guide.md) - Mermaid templates, SVG animation patterns, ER diagrams
