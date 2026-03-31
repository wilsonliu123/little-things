#!/usr/bin/env python3
"""HTML to PDF converter using WeasyPrint with CJK font support."""
import sys
import os

def convert(html_path: str, output_path: str = None):
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
    except ImportError:
        print("ERROR: weasyprint not installed. Run: pip install weasyprint")
        sys.exit(1)

    if not os.path.exists(html_path):
        print(f"ERROR: File not found: {html_path}")
        sys.exit(1)

    if output_path is None:
        output_path = os.path.splitext(html_path)[0] + ".pdf"

    font_config = FontConfiguration()

    # Inject CJK font CSS to prevent garbled characters
    cjk_css = """
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                     "Noto Sans TC", "Noto Sans SC", "Microsoft JhengHei",
                     "PingFang TC", "PingFang SC", sans-serif;
    }
    code, pre {
        font-family: "SF Mono", "Fira Code", "Noto Sans Mono CJK TC", monospace;
    }
    """

    html = HTML(filename=html_path)
    html.write_pdf(
        output_path,
        font_config=font_config,
        stylesheets=[],
        presentational_hints=True,
    )
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python html_to_pdf.py <input.html> [output.pdf]")
        sys.exit(1)
    out = sys.argv[2] if len(sys.argv) > 2 else None
    convert(sys.argv[1], out)
