---
name: tech-writter
description: "Backend service technical documentation writer. Generate comprehensive API documentation with endpoint specs, input/output parameters (types, constraints, defaults), request/response samples, error code tables, auth/permission guides, version changelogs, internal logic explanations with Mermaid diagrams, SVG animated flow charts (HTML only), and database ER diagrams. Supports output in HTML (with sidebar navigation, animated SVG flows), Markdown, PDF (WeasyPrint with CJK fonts), and Word (python-docx with CJK fonts). Use when: (1) writing backend API documentation, (2) documenting internal service logic, (3) creating technical specs for backend services, (4) generating API reference docs from code, (5) user mentions 'tech doc', 'API doc', 'backend doc', 'service doc', 'technical documentation', or '技術文檔'."
---

# Tech Writter - 後端服務技術文檔撰寫

## Workflow

Generate backend technical documentation in these steps:

1. **Gather context** - Read source code, identify API endpoints, data models, business logic
2. **Choose output format** - Ask user: HTML (recommended, supports SVG animation) / MD / PDF / Word
3. **Choose language** - Ask user: 繁體中文 / English / both
4. **Generate document** - Follow the document structure below
5. **Convert format** - If PDF/Word needed, first generate HTML then convert via scripts

## Document Structure

Every backend service doc MUST include these sections in order:

### 1. Overview (概述)
- Service name, version, base URL
- Brief description of the service's purpose
- Tech stack summary
- Dependencies on other services

### 2. Authentication & Authorization (認證與授權)
- Auth method (Bearer Token / API Key / OAuth2)
- Token acquisition flow (use Mermaid sequence diagram)
- Token refresh mechanism
- Role/permission matrix table

### 3. API Reference (API 接口文檔)

For EACH endpoint, include:

**Endpoint header:**
- HTTP method + path + status badge (stable/beta/deprecated)
- One-line description

**Parameters table** (see [references/api_doc_spec.md](references/api_doc_spec.md) for full spec):

| Parameter | Type | Required | Constraints | Default | Description |
|-----------|------|----------|-------------|---------|-------------|

- Include path params, query params, headers, and request body
- For nested objects, use dot notation: `data.user.name`
- Always specify: type, required/optional, constraints (regex, range, enum, length), default value

**Request/Response samples:**
- Success request with full headers + body
- Success response (200/201)
- Error response (at least one common error)
- cURL example for each endpoint

### 4. Error Code Reference (錯誤碼對照表)
- Unified error response format
- Error code table grouped by HTTP status
- See [references/api_doc_spec.md](references/api_doc_spec.md) §4 for encoding rules

### 5. Internal Logic (內部邏輯說明)

Use diagrams to explain complex logic. See [references/diagram_guide.md](references/diagram_guide.md) for templates.

**Diagram selection:**
- API request flow → Mermaid Sequence Diagram
- Business logic branching → Mermaid Flowchart
- Resource state transitions → Mermaid State Diagram
- Data flow with animation → SVG animated arrows (HTML only)
- Database relationships → Mermaid ER Diagram
- Data model structure → Mermaid Class Diagram

For HTML format: prefer SVG animated flow diagrams for data flow visualization (arrows with `stroke-dasharray` animation).

For MD format: use Mermaid only (no SVG animation support).

### 6. Database Schema (數據庫結構)
- ER diagram (Mermaid erDiagram)
- Key table descriptions with column details
- Index strategy notes

### 7. Performance & Rate Limiting (性能與限流)
- Rate limit rules per endpoint or role
- Timeout settings
- Pagination strategy
- Caching strategy notes

### 8. Version Changelog (版本變更記錄)
- Follow format in [references/api_doc_spec.md](references/api_doc_spec.md) §6
- Categories: Added / Changed / Deprecated / Removed / Breaking Changes

## Output Format Guide

### HTML (Recommended)
- Use the template at [assets/template.html](assets/template.html)
- Features: sidebar navigation, Mermaid rendering, SVG animations, responsive, print-friendly
- Replace `{{DOC_TITLE}}`, `{{VERSION}}`, `{{DATE}}`, `{{AUTHOR}}`, `{{LANG}}` placeholders
- Build sidebar nav from h2/h3 headings
- Mermaid diagrams render automatically via CDN

### Markdown
- Standard GFM (GitHub Flavored Markdown)
- Use fenced code blocks with `mermaid` language tag for diagrams
- No SVG animation support - use static Mermaid diagrams instead

### PDF (from HTML)
- Run: `python scripts/html_to_pdf.py <input.html> [output.pdf]`
- Requires: `pip install weasyprint`
- CJK fonts handled automatically (Noto Sans TC/SC)

### Word / DOCX (from HTML)
- Run: `python scripts/html_to_docx.py <input.html> [output.docx]`
- Requires: `pip install python-docx`
- Uses Microsoft JhengHei font for CJK support
- Tables and code blocks preserved

## CJK Font Strategy

To prevent garbled Chinese characters across all formats:
- **HTML**: CSS font-family includes Noto Sans TC, Microsoft JhengHei, PingFang TC
- **PDF**: WeasyPrint with Google Fonts Noto Sans TC import
- **Word**: python-docx with Microsoft JhengHei as default font
- **Markdown**: No font control needed (renderer handles it)

## References

- **API documentation spec**: [references/api_doc_spec.md](references/api_doc_spec.md) - Parameter tables, error codes, auth patterns, changelog format
- **Diagram guide**: [references/diagram_guide.md](references/diagram_guide.md) - Mermaid templates, SVG animation patterns, ER diagrams
