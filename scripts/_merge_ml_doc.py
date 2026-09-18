from pathlib import Path
import shutil

import pymupdf

root = Path(".")
orig = root / "scripts" / "_ML_Dokumentacija_orig.pdf"
p84 = root / "scripts" / "_insert_8_4.pdf"
p9 = root / "scripts" / "_insert_9_intro.pdf"
p153 = root / "scripts" / "_insert_15_3.pdf"
tmp = root / "scripts" / "_ML_Dokumentacija_merged.pdf"

base = pymupdf.open(orig)
out = pymupdf.open()

# Original pages 1-11 (indices 0-10)
out.insert_pdf(base, from_page=0, to_page=10)
# Rebuilt 8.3 + new 8.4, then rebuilt start of chapter 9
out.insert_pdf(pymupdf.open(p84))
out.insert_pdf(pymupdf.open(p9))
# Original pages 13-21 (indices 12-20) — skip original page 12
out.insert_pdf(base, from_page=12, to_page=20)
# New 15.3 before DISKUSIJA
out.insert_pdf(pymupdf.open(p153))
# Original pages 22-27 (indices 21-26)
out.insert_pdf(base, from_page=21, to_page=26)

out.save(tmp)
print("merged pages", out.page_count)
out.close()
base.close()
shutil.copyfile(tmp, root / "ML_Dokumentacija.pdf")
print("copied to ML_Dokumentacija.pdf")
