import subprocess
import sys

# Install pymupdf if needed
try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pymupdf', '-q'])
    import fitz

pdf_path = r"D:\LQP\Project\Rita\Workspaces\EES_2026_Analysis\Document\GHN_EES_2026_BaoCao_PhanTich_ChienLuoc_v3.pdf"

doc = fitz.open(pdf_path)
print(f"Pages: {len(doc)}")
print("=" * 80)

for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text()
    if text.strip():
        print(f"\n{'='*20} PAGE {page_num + 1} {'='*20}")
        print(text)
