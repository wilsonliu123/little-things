#!/usr/bin/env python3
"""Render a manual from Markdown to HTML/PDF with image support and safer CJK output."""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
from pathlib import Path

IMAGE_ONLY_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")
IMAGE_INLINE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_INLINE_RE = re.compile(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)")
CODE_INLINE_RE = re.compile(r"`([^`\n]+)`")
CJK_CODE_SPAN_RE = re.compile(r"`([^`\n]*[\u4e00-\u9fff][^`\n]*)`")
EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]"
)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff\u3400-\u4dbf\-]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-").lower()
    return text


def resolve_src(raw_path: str, base_dir: Path) -> str:
    raw_path = raw_path.strip().strip('"').strip("'")
    if re.match(r"^(https?|data|file):", raw_path):
        return raw_path
    return (base_dir / raw_path).resolve().as_uri()


def build_figure(alt_text: str, raw_path: str, base_dir: Path) -> str:
    src = resolve_src(raw_path, base_dir)
    safe_alt = html.escape(alt_text)
    figure = [f'<figure class="manual-figure"><img src="{src}" alt="{safe_alt}">']
    if alt_text:
        figure.append(f"<figcaption>{safe_alt}</figcaption>")
    figure.append("</figure>")
    return "".join(figure)


def render_inline(text: str, base_dir: Path) -> str:
    placeholders: dict[str, str] = {}

    def stash(rendered: str) -> str:
        key = f"__INLINE_TOKEN_{len(placeholders)}__"
        placeholders[key] = rendered
        return key

    text = IMAGE_INLINE_RE.sub(
        lambda m: stash(
            f'<img class="inline-image" src="{resolve_src(m.group(2), base_dir)}" '
            f'alt="{html.escape(m.group(1))}">'
        ),
        text,
    )
    text = LINK_INLINE_RE.sub(
        lambda m: stash(
            f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'
        ),
        text,
    )
    text = CODE_INLINE_RE.sub(
        lambda m: stash(
            (
                f'<span class="inline-ui">{html.escape(m.group(1))}</span>'
                if re.search(r"[\u4e00-\u9fff]", m.group(1))
                else f'<code class="inline-code">{html.escape(m.group(1))}</code>'
            )
        ),
        text,
    )

    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*(.+?)\*", r"<em>\1</em>", escaped)

    for key, value in placeholders.items():
        escaped = escaped.replace(key, value)
    return escaped


def markdown_to_html(md_content: str, title: str, source_dir: Path) -> str:
    lines = md_content.splitlines()
    html_parts: list[str] = []
    nav_items: list[tuple[int, str, str]] = []
    in_code_block = False
    code_lang = ""
    code_lines: list[str] = []
    in_table = False
    table_rows: list[str] = []
    in_list = False
    list_items: list[str] = []
    list_type = "ul"

    def flush_code() -> None:
        nonlocal in_code_block, code_lang, code_lines
        if not code_lines:
            in_code_block = False
            code_lang = ""
            return
        code_text = html.escape("\n".join(code_lines))
        if code_lang == "mermaid":
            html_parts.append(f'<div class="mermaid">\n{html.unescape(code_text)}\n</div>')
        else:
            html_parts.append(f'<pre><code>{code_text}</code></pre>')
        in_code_block = False
        code_lang = ""
        code_lines = []

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        result = ["<table>", "<tbody>"]
        header_done = False
        for i, row in enumerate(table_rows):
            cells = [c.strip() for c in row.split("|")]
            if len(cells) >= 2 and cells[0] == "":
                cells = cells[1:]
            if len(cells) >= 1 and cells[-1] == "":
                cells = cells[:-1]
            if not cells:
                continue
            if i == 1 and all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            tag = "th" if not header_done else "td"
            if not header_done:
                result[-1] = "<thead>"
                result.append("<tr>")
            else:
                result.append("<tr>")
            for cell in cells:
                result.append(f"<{tag}>{render_inline(cell, source_dir)}</{tag}>")
            result.append("</tr>")
            if not header_done:
                result.append("</thead>")
                result.append("<tbody>")
                header_done = True
        result.append("</tbody>")
        result.append("</table>")
        html_parts.append("\n".join(result))
        table_rows = []
        in_table = False

    def flush_list() -> None:
        nonlocal in_list, list_items, list_type
        if not list_items:
            in_list = False
            list_type = "ul"
            return
        result = [f"<{list_type}>"]
        for item in list_items:
            result.append(f"  <li>{render_inline(item, source_dir)}</li>")
        result.append(f"</{list_type}>")
        html_parts.append("\n".join(result))
        list_items = []
        in_list = False
        list_type = "ul"

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                if in_list:
                    flush_list()
                in_code_block = True
                code_lang = stripped.replace("```", "").strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped == "---":
            if in_table:
                flush_table()
            if in_list:
                flush_list()
            html_parts.append("<hr>")
            continue

        image_only = IMAGE_ONLY_RE.match(stripped)
        if image_only:
            if in_table:
                flush_table()
            if in_list:
                flush_list()
            html_parts.append(build_figure(image_only.group(1), image_only.group(2), source_dir))
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            if in_table:
                flush_table()
            if in_list:
                flush_list()
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            slug = slugify(text)
            html_parts.append(f"<h{level} id=\"{slug}\">{render_inline(text, source_dir)}</h{level}>")
            if level in (2, 3):
                nav_items.append((level, text, slug))
            continue

        if stripped.startswith("|"):
            if in_list:
                flush_list()
            in_table = True
            table_rows.append(stripped)
            continue
        elif in_table:
            flush_table()

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        number_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if bullet_match or number_match:
            if in_table:
                flush_table()
            next_type = "ul" if bullet_match else "ol"
            item_text = bullet_match.group(1) if bullet_match else number_match.group(1)
            if in_list and list_type != next_type:
                flush_list()
            in_list = True
            list_type = next_type
            list_items.append(item_text)
            continue
        elif in_list and stripped == "":
            flush_list()
            continue
        elif in_list and not (bullet_match or number_match):
            flush_list()

        if stripped.startswith(">"):
            text = stripped.lstrip(">").strip()
            html_parts.append(f"<blockquote><p>{render_inline(text, source_dir)}</p></blockquote>")
            continue

        if stripped == "":
            continue

        html_parts.append(f"<p>{render_inline(stripped, source_dir)}</p>")

    if in_code_block:
        flush_code()
    if in_table:
        flush_table()
    if in_list:
        flush_list()

    nav_parts: list[str] = []
    for level, text, slug in nav_items:
        class_name = "nav-sub" if level == 3 else "nav-main"
        nav_parts.append(f'<a class="{class_name}" href="#{slug}">{html.escape(text)}</a>')

    content_html = "\n".join(html_parts)
    nav_html = "\n".join(nav_parts)

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --line: #d8e0ea;
      --text: #1f2937;
      --muted: #5f6b7a;
      --primary: #2563eb;
      --primary-soft: #eaf1ff;
      --sidebar-width: 280px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      display: flex;
      color: var(--text);
      background: var(--bg);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC",
        "Noto Sans SC", "Microsoft JhengHei", "PingFang TC", "PingFang SC", sans-serif;
      line-height: 1.75;
    }}
    .sidebar {{
      position: fixed;
      top: 0;
      left: 0;
      width: var(--sidebar-width);
      height: 100vh;
      overflow-y: auto;
      background: #0f172a;
      color: #dbe6ff;
      padding: 24px 18px 32px;
    }}
    .sidebar h2 {{
      margin-top: 0;
      margin-bottom: 18px;
      font-size: 18px;
      color: #f8fbff;
    }}
    .sidebar a {{
      display: block;
      text-decoration: none;
      color: #bfd0ff;
      padding: 6px 10px;
      border-radius: 8px;
      margin-bottom: 4px;
      font-size: 14px;
    }}
    .sidebar a:hover {{
      background: rgba(255,255,255,0.08);
    }}
    .sidebar .nav-sub {{
      padding-left: 22px;
      font-size: 13px;
    }}
    .main {{
      margin-left: var(--sidebar-width);
      width: 100%;
      max-width: 980px;
      padding: 40px 56px 80px;
    }}
    h1 {{
      margin-top: 0;
      margin-bottom: 12px;
      font-size: 34px;
    }}
    h2 {{
      margin-top: 44px;
      margin-bottom: 14px;
      padding-bottom: 8px;
      border-bottom: 2px solid var(--primary);
      font-size: 26px;
    }}
    h3 {{
      margin-top: 28px;
      margin-bottom: 10px;
      font-size: 20px;
    }}
    p, li, td, th {{
      font-size: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0;
      background: var(--panel);
      border: 1px solid var(--line);
    }}
    th {{
      text-align: left;
      background: #eef3fa;
      border-bottom: 1px solid var(--line);
      padding: 10px 14px;
    }}
    td {{
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    pre {{
      background: #0f172a;
      color: #e5edf8;
      padding: 18px;
      border-radius: 12px;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "Noto Sans Mono CJK TC", "Noto Sans Mono CJK SC", "SF Mono",
        "Fira Code", "Menlo", monospace;
    }}
    .inline-code {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 8px;
      background: var(--primary-soft);
      color: var(--primary);
      font-size: 0.95em;
      font-family: "Noto Sans TC", "Noto Sans SC", "Microsoft JhengHei",
        "PingFang TC", "PingFang SC", "SF Mono", "Fira Code", monospace;
    }}
    .inline-ui {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 8px;
      background: var(--primary-soft);
      color: var(--primary);
      font-size: 0.95em;
      font-weight: 600;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC",
        "Noto Sans SC", "Microsoft JhengHei", "PingFang TC", "PingFang SC", sans-serif;
    }}
    blockquote {{
      margin: 18px 0;
      padding: 14px 18px;
      border-left: 4px solid var(--primary);
      background: #eef4ff;
    }}
    .manual-figure {{
      margin: 24px 0;
      page-break-inside: avoid;
    }}
    .manual-figure img {{
      display: block;
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #fff;
    }}
    .manual-figure figcaption {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }}
    .inline-image {{
      max-width: 100%;
      vertical-align: middle;
    }}
    hr {{
      border: none;
      border-top: 1px solid var(--line);
      margin: 32px 0;
    }}
    @media print {{
      .sidebar {{ display: none; }}
      .main {{ margin-left: 0; max-width: 100%; padding: 0; }}
    }}
  </style>
</head>
<body>
  <nav class="sidebar">
    <h2>{html.escape(title)}</h2>
    {nav_html}
  </nav>
  <main class="main">
    <h1>{html.escape(title)}</h1>
    {content_html}
  </main>
</body>
</html>
"""


def check_markdown(md_content: str, source_dir: Path) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []

    emoji_count = len(EMOJI_RE.findall(md_content))
    if emoji_count:
        warnings.append(
            f"Found {emoji_count} emoji/symbol glyphs. Replace them with plain text before final PDF export."
        )

    cjk_code_spans = [m.group(1) for m in CJK_CODE_SPAN_RE.finditer(md_content)]
    if cjk_code_spans:
        preview = ", ".join(cjk_code_spans[:5])
        warnings.append(
            "Found inline code spans containing Chinese text. They will be rendered as UI labels using text fonts, "
            "but prefer bold text in the source for clearer semantics. "
            f"Examples: {preview}"
        )

    for alt_text, raw_path in IMAGE_INLINE_RE.findall(md_content):
        raw_path = raw_path.strip().strip('"').strip("'")
        if re.match(r"^(https?|data|file):", raw_path):
            continue
        candidate = (source_dir / raw_path).resolve()
        if not candidate.exists():
            errors.append(f"Missing image asset for '{alt_text}': {candidate}")

    return warnings, errors


def write_html(md_path: Path, html_path: Path) -> tuple[list[str], list[str]]:
    md_content = md_path.read_text(encoding="utf-8")
    warnings, errors = check_markdown(md_content, md_path.parent)
    if errors:
        raise FileNotFoundError("\n".join(errors))

    title_match = re.search(r"^#\s+(.+)$", md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem
    html_output = markdown_to_html(md_content, title, md_path.parent)
    html_path.write_text(html_output, encoding="utf-8")
    return warnings, errors


def write_pdf(html_path: Path, pdf_path: Path) -> None:
    try:
        from weasyprint import CSS, HTML
        from weasyprint.text.fonts import FontConfiguration
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "weasyprint is required for PDF export. Install it before running this script."
        ) from exc

    font_config = FontConfiguration()
    pdf_css = """
    @page { size: A4; margin: 1.8cm; }
    .sidebar { display: none !important; }
    .main { margin-left: 0 !important; max-width: 100% !important; padding: 0 !important; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC",
        "Noto Sans SC", "Microsoft JhengHei", "PingFang TC", "PingFang SC", sans-serif;
    }
    .inline-code {
      font-family: "Noto Sans TC", "Noto Sans SC", "Microsoft JhengHei",
        "PingFang TC", "PingFang SC", "SF Mono", "Fira Code", monospace !important;
    }
    .inline-ui {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC",
        "Noto Sans SC", "Microsoft JhengHei", "PingFang TC", "PingFang SC", sans-serif !important;
    }
    pre, pre code {
      font-family: "Noto Sans Mono CJK TC", "Noto Sans Mono CJK SC", "SF Mono",
        "Fira Code", "Menlo", monospace !important;
    }
    .manual-figure, table, blockquote { page-break-inside: avoid; }
    img { max-width: 100%; }
    """
    HTML(filename=str(html_path)).write_pdf(
        str(pdf_path),
        stylesheets=[CSS(string=pdf_css, font_config=font_config)],
        font_config=font_config,
        presentational_hints=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a manual from Markdown to HTML and optionally PDF."
    )
    parser.add_argument("input_markdown", help="Source markdown file")
    parser.add_argument("--html", dest="html_path", help="Output HTML path")
    parser.add_argument("--pdf", dest="pdf_path", help="Output PDF path")
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Treat emoji/CJK inline-code warnings as fatal",
    )
    args = parser.parse_args()

    md_path = Path(args.input_markdown).expanduser().resolve()
    html_path = (
        Path(args.html_path).expanduser().resolve()
        if args.html_path
        else md_path.with_suffix(".html")
    )
    pdf_path = Path(args.pdf_path).expanduser().resolve() if args.pdf_path else None

    warnings, _ = write_html(md_path, html_path)
    print(f"HTML generated: {html_path}")

    if warnings:
        print("Warnings:")
        for item in warnings:
            print(f"- {item}")
        if args.fail_on_warning:
            return 2

    if pdf_path:
        write_pdf(html_path, pdf_path)
        print(f"PDF generated: {pdf_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
