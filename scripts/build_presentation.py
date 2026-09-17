"""Build a 16:9 presentation PDF for the professor meeting."""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Prezentacija - korelacije i podjele.pdf"
PLOTS = ROOT / "results" / "plots"
FONTS = Path(r"C:\Windows\Fonts")

# 16:9 widescreen
W, H = 13.333 * inch, 7.5 * inch

NAVY = HexColor("#1B365D")
NAVY_DEEP = HexColor("#12243F")
TEAL = HexColor("#1F7A6E")
GOLD = HexColor("#C9A227")
CORAL = HexColor("#C44B32")
LIGHT = HexColor("#F4F7FA")
ROW = HexColor("#E8F1EE")
MUTED = HexColor("#5B6773")
INK = HexColor("#1E2A32")
LINE = HexColor("#D5DDE5")

pdfmetrics.registerFont(TTFont("Calibri", str(FONTS / "calibri.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Bold", str(FONTS / "calibrib.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Italic", str(FONTS / "calibrii.ttf")))

SLIDES: list = []


def p(text: str, size: float = 18, color=INK, align=TA_LEFT, leading: float | None = None, bold: bool = False) -> Paragraph:
    return Paragraph(
        text,
        ParagraphStyle(
            "x",
            fontName="Calibri-Bold" if bold else "Calibri",
            fontSize=size,
            textColor=color,
            alignment=align,
            leading=leading or size * 1.28,
        ),
    )


def header(c: Canvas, title: str, kicker: str = "") -> None:
    c.setFillColor(NAVY)
    c.rect(0, H - 0.92 * inch, W, 0.92 * inch, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - 0.98 * inch, W, 0.06 * inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Calibri", 10)
    c.drawString(0.55 * inch, H - 0.32 * inch, kicker or "MONEY VS HAPPINESS  ·  WHR 2023")
    c.setFillColor(white)
    c.setFont("Calibri-Bold", 22)
    c.drawString(0.55 * inch, H - 0.72 * inch, title)
    c.setFillColor(LINE)
    c.rect(0, 0, W, 0.38 * inch, fill=1, stroke=0)
    c.setFillColor(MUTED)
    c.setFont("Calibri", 9)
    c.drawString(0.55 * inch, 0.14 * inch, "Korelacije među faktorima i train/test podjele")


def footer_num(c: Canvas, n: int, total: int) -> None:
    c.setFillColor(MUTED)
    c.setFont("Calibri", 9)
    c.drawRightString(W - 0.5 * inch, 0.14 * inch, f"{n} / {total}")


def draw_para(c: Canvas, para: Paragraph, x: float, y: float, width: float) -> float:
    w, h = para.wrap(width, 500)
    para.drawOn(c, x, y - h)
    return h


def draw_table(c: Canvas, headers: list[str], rows: list[list], col_widths: list[float], x: float, y: float, font=11) -> float:
    th = ParagraphStyle("th", fontName="Calibri-Bold", fontSize=font, textColor=white, alignment=TA_CENTER, leading=font * 1.25)
    td = ParagraphStyle("td", fontName="Calibri", fontSize=font, textColor=INK, alignment=TA_CENTER, leading=font * 1.25)
    td_l = ParagraphStyle("tdl", fontName="Calibri", fontSize=font, textColor=INK, alignment=TA_LEFT, leading=font * 1.25)
    td_b = ParagraphStyle("tdb", fontName="Calibri-Bold", fontSize=font, textColor=NAVY, alignment=TA_CENTER, leading=font * 1.25)
    data = [[Paragraph(h, th) for h in headers]]
    for r in rows:
        cells = []
        for i, v in enumerate(r):
            bold = False
            if isinstance(v, tuple):
                v, bold = v
            style = td_b if bold else (td_l if i == 0 else td)
            cells.append(Paragraph(str(v), style))
        data.append(cells)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    for i in range(1, len(data)):
        cmds.append(("BACKGROUND", (0, i), (-1, i), ROW if i % 2 == 0 else white))
    t.setStyle(TableStyle(cmds))
    tw, thgt = t.wrap(sum(col_widths), 600)
    t.drawOn(c, x, y - thgt)
    return thgt


def fit_image(c: Canvas, path: Path, x: float, y: float, max_w: float, max_h: float) -> None:
    with PILImage.open(path) as im:
        wpx, hpx = im.size
    aspect = hpx / float(wpx)
    w, h = max_w, max_w * aspect
    if h > max_h:
        h = max_h
        w = h / aspect
    c.drawImage(str(path), x + (max_w - w) / 2, y, width=w, height=h, mask="auto", preserveAspectRatio=True, anchor="sw")


def callout(c: Canvas, text: str, x: float, y: float, w: float, fill=TEAL) -> float:
    para = p(text, 14, INK, leading=19)
    pw, ph = para.wrap(w - 24, 400)
    box_h = ph + 22
    c.setFillColor(fill)
    c.roundRect(x, y - box_h, w, box_h, 8, fill=1, stroke=0)
    c.setFillColor(HexColor("#F7FBFA"))
    c.roundRect(x + 6, y - box_h + 6, w - 12, box_h - 12, 6, fill=1, stroke=0)
    para.drawOn(c, x + 18, y - box_h + 14)
    return box_h


def new_slide(c: Canvas) -> None:
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def slide_title(c: Canvas) -> None:
    c.setFillColor(NAVY_DEEP)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, H - 0.22 * inch, W, 0.22 * inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 0.55 * inch, W, 0.10 * inch, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Calibri", 13)
    c.drawCentredString(W / 2, H - 1.7 * inch, "PREZENTACIJA ZA SASTANAK")
    c.setFillColor(white)
    c.setFont("Calibri-Bold", 36)
    c.drawCentredString(W / 2, H - 2.55 * inch, "Korelacije među podacima")
    c.drawCentredString(W / 2, H - 3.15 * inch, "i train/test podjele")
    c.setFillColor(HexColor("#C5D4E4"))
    c.setFont("Calibri", 16)
    c.drawCentredString(W / 2, H - 3.85 * inch, "Jesu li neki faktori suvišni?  Mijenja li se model ako podijelimo podatke drugačije?")
    c.setFillColor(HexColor("#9FB4C7"))
    c.setFont("Calibri", 13)
    c.drawCentredString(W / 2, 1.15 * inch, "Money vs Happiness  ·  World Happiness Report 2023  ·  137 zemalja")
    c.drawCentredString(W / 2, 0.82 * inch, "Linear Regression  ·  Random Forest  ·  XGBoost")


def slide_agenda(c: Canvas) -> None:
    header(c, "Dva pitanja na ovom sastanku")
    cards = [
        ("1", "Korelacije među 6 faktora", "Da li su neki socio-ekonomski faktori\ntoliko slični da jednu kolonu treba izbaciti?"),
        ("2", "Više train/test podjela", "80/20 nije jedini način. Šta se desi na\n90/10, 70/30, 60/40 — poboljša li se model?"),
    ]
    x0 = 0.7 * inch
    for i, (num, title, body) in enumerate(cards):
        x = x0 + i * 6.15 * inch
        y = 1.35 * inch
        c.setFillColor(LIGHT)
        c.roundRect(x, y, 5.8 * inch, 4.35 * inch, 12, fill=1, stroke=0)
        c.setFillColor(TEAL if i == 0 else NAVY)
        c.circle(x + 0.55 * inch, y + 3.55 * inch, 0.32 * inch, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 18)
        c.drawCentredString(x + 0.55 * inch, y + 3.47 * inch, num)
        c.setFillColor(NAVY)
        c.setFont("Calibri-Bold", 20)
        c.drawString(x + 1.1 * inch, y + 3.45 * inch, title)
        c.setFillColor(INK)
        c.setFont("Calibri", 15)
        for j, line in enumerate(body.split("\n")):
            c.drawString(x + 0.4 * inch, y + 2.55 * inch - j * 0.38 * inch, line)
    c.setFillColor(MUTED)
    c.setFont("Calibri-Italic", 12)
    c.drawString(0.7 * inch, 0.95 * inch, "Glavni protokol ostaje 80/20 i svih 6 kolona. Ovo su provjere, ne lov na ljepši broj.")


def slide_with_target(c: Canvas) -> None:
    header(c, "Prvo: ko ide sa srećom?", "KORELACIJE  ·  CILJ")
    h = draw_table(
        c,
        ["Faktor", "Pearson r", "Poruka"],
        [
            [("Social support", True), ("0.835", True), "Najjači korelat sreće"],
            [("Logged GDP per capita", True), ("0.784", True), "Jaka pozitivna veza"],
            ["Healthy life expectancy", "0.746", "Jaka pozitivna veza"],
            ["Freedom to make life choices", "0.663", "Umjereno–jaka"],
            ["Perceptions of corruption", "−0.472", "Umjerena negativna"],
            ["Generosity", "0.044", "Praktično nula"],
        ],
        [4.6 * inch, 1.8 * inch, 4.6 * inch],
        0.9 * inch,
        H - 1.25 * inch,
        font=13,
    )
    callout(
        c,
        "Ovo nije pitanje o izbacivanju kolone. Korelacija ≠ kauzalnost. Profesorica je zatim tražila korelacije MEĐU faktorima.",
        0.9 * inch,
        H - 1.35 * inch - h - 0.25 * inch,
        11.5 * inch,
        TEAL,
    )


def slide_heatmap(c: Canvas) -> None:
    header(c, "Među 6 faktora: jesu li duplikati?", "KORELACIJE  ·  PREDIKTORI")
    fit_image(c, PLOTS / "predictor_correlation_heatmap.png", 0.35 * inch, 0.55 * inch, 8.3 * inch, 5.7 * inch)
    # right callouts
    x = 8.85 * inch
    boxes = [
        (TEAL, "Jedini par |r| ≥ 0.80", "GDP ↔ Healthy life\nexpectancy\n\nr = 0.84"),
        (NAVY, "Ostali parovi", "GDP ↔ Social support  0.74\nSocial ↔ Healthy life  0.73\nGenerosity ≈ 0 sa svima"),
        (CORAL, "Prag", "Sumnja na redundantnost\nako je |r| ≥ 0.80"),
    ]
    y = 5.85 * inch
    for fill, title, body in boxes:
        c.setFillColor(fill)
        c.roundRect(x, y - 1.55 * inch, 3.95 * inch, 1.48 * inch, 8, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 13)
        c.drawString(x + 0.18 * inch, y - 0.32 * inch, title)
        c.setFont("Calibri", 12)
        for i, line in enumerate(body.split("\n")):
            c.drawString(x + 0.18 * inch, y - 0.58 * inch - i * 0.22 * inch, line)
        y -= 1.68 * inch


def slide_vif(c: Canvas) -> None:
    header(c, "VIF: je li r = 0.84 razlog za brisanje?", "KORELACIJE  ·  MULTIKOLINEARNOST")
    draw_table(
        c,
        ["Faktor", "VIF", "Dijagnoza"],
        [
            ["Logged GDP per capita", "4.20", "Umjereno, ispod 5"],
            ["Healthy life expectancy", "3.73", "Nisko–umjereno"],
            ["Social support", "2.95", "Nisko"],
            ["Freedom to make life choices", "1.59", "Nisko"],
            ["Perceptions of corruption", "1.43", "Nisko"],
            ["Generosity", "1.19", "Skoro nezavisan"],
        ],
        [5.2 * inch, 1.6 * inch, 4.4 * inch],
        0.9 * inch,
        H - 1.25 * inch,
        font=14,
    )
    callout(
        c,
        "Prag za ozbiljan problem je VIF > 10. Najviši VIF ovdje je 4.20. Pearson r gleda parove; VIF gleda koliko se jedan faktor da objasniti ostalih pet odjednom.",
        0.9 * inch,
        1.55 * inch,
        11.5 * inch,
        NAVY,
    )


def slide_keep_columns(c: Canvas) -> None:
    header(c, "Odluka: nijedna kolona nije izbačena", "KORELACIJE  ·  ZAKLJUČAK")
    points = [
        ("1", "Statistika", "Samo jedan par iznad 0.80. Svi VIF < 5."),
        ("2", "Sadržaj", "GDP i Healthy life expectancy nisu duplikati — bogatstvo vs zdravlje."),
        ("3", "Modeli", "Stabla (RF, XGBoost) podnose korelirane prediktore. Brisanje bi više naškodilo interpretaciji."),
        ("4", "Trag u LR", "Healthy life expectancy: r = 0.75 sa srećom, ali koeficijent samo +0.02. GDP „pojede“ efekat — bilježi se, ne briše se kolona."),
    ]
    for i, (num, title, body) in enumerate(points):
        y = 5.55 * inch - i * 1.15 * inch
        c.setFillColor(TEAL if i % 2 == 0 else NAVY)
        c.circle(0.95 * inch, y + 0.28 * inch, 0.22 * inch, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 13)
        c.drawCentredString(0.95 * inch, y + 0.22 * inch, num)
        c.setFillColor(NAVY)
        c.setFont("Calibri-Bold", 18)
        c.drawString(1.4 * inch, y + 0.38 * inch, title)
        c.setFillColor(INK)
        c.setFont("Calibri", 15)
        c.drawString(1.4 * inch, y + 0.08 * inch, body)


def slide_why_splits(c: Canvas) -> None:
    header(c, "Zašto više podjela, ne samo 80/20?", "TRAIN / TEST")
    items = [
        ("Glavni protokol", "80/20  ·  109 train / 28 test  ·  seed 42"),
        ("Šta je dodato", "Omjeri 90/10, 70/30, 60/40  +  isti 80/20 sa seedovima 0, 7, 42, 123"),
        ("Zašto fiksni hiperparametri", "Da se porede splitovi, ne sreća GridSearch-a"),
        ("Kako čitati brojke", "„Bolji R²“ na jednom holdoutu ≠ bolji model. Na 137 zemalja test skup lako bude lakši ili teži."),
    ]
    for i, (t, b) in enumerate(items):
        y = 5.45 * inch - i * 1.15 * inch
        c.setFillColor(LIGHT)
        c.roundRect(0.65 * inch, y, 12.05 * inch, 1.02 * inch, 10, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0.65 * inch, y, 0.12 * inch, 1.02 * inch, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont("Calibri-Bold", 16)
        c.drawString(1.05 * inch, y + 0.58 * inch, t)
        c.setFillColor(INK)
        c.setFont("Calibri", 15)
        c.drawString(1.05 * inch, y + 0.22 * inch, b)


def slide_ratio_table(c: Canvas) -> None:
    header(c, "Test R² po omjeru  (seed = 42)", "TRAIN / TEST  ·  REZULTATI")
    draw_table(
        c,
        ["Split", "Train / test", "LR", "Random Forest", "XGBoost", "Naspram 80/20"],
        [
            ["90/10", "123 / 14", "0.623", "0.493", "0.581", "Svi padaju"],
            [("80/20", True), ("109 / 28", True), ("0.780", True), "0.729", "0.675", "Baza"],
            ["70/30", "95 / 42", "0.850", "0.770", "0.725", "Izgleda bolje"],
            ["60/40", "82 / 55", "0.823", "0.755", "0.731", "Izgleda bolje"],
        ],
        [1.5 * inch, 1.7 * inch, 1.5 * inch, 2.1 * inch, 1.7 * inch, 2.6 * inch],
        0.75 * inch,
        H - 1.2 * inch,
        font=14,
    )
    # three verdict chips
    chips = [
        (CORAL, "Najgore", "90/10 — test ima samo 14 zemalja"),
        (GOLD, "Najljepši broj", "70/30 · LR · R² = 0.850"),
        (TEAL, "Protokol", "80/20 ostaje — slaže se sa CV 0.779"),
    ]
    for i, (col, t, b) in enumerate(chips):
        x = 0.75 * inch + i * 4.1 * inch
        c.setFillColor(col)
        c.roundRect(x, 0.7 * inch, 3.9 * inch, 1.35 * inch, 10, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 14)
        c.drawString(x + 0.2 * inch, 1.62 * inch, t)
        c.setFont("Calibri", 13)
        c.drawString(x + 0.2 * inch, 1.18 * inch, b)


def slide_ratio_chart(c: Canvas) -> None:
    header(c, "Gdje se model pokvario, a gdje „poboljšao“?", "TRAIN / TEST  ·  GRAFIKON")
    fit_image(c, PLOTS / "split_ratio_comparison.png", 0.4 * inch, 1.55 * inch, 12.5 * inch, 4.55 * inch)
    c.setFillColor(INK)
    c.setFont("Calibri", 13)
    c.drawCentredString(W / 2, 1.15 * inch, "Lijevo: Test R² (više = bolje).  Desno: Test MAE (niže = bolje).  90% train = najgori ishod za sve modele.")


def slide_deltas(c: Canvas) -> None:
    header(c, "Promjena Test R² naspram 80/20", "TRAIN / TEST  ·  PLUS / MINUS")
    draw_table(
        c,
        ["Model", "90/10", "80/20 baza", "70/30", "60/40"],
        [
            ["Linear Regression", "0.623  (−0.16)", "0.780", "0.850  (+0.07)", "0.823  (+0.04)"],
            ["Random Forest", "0.493  (−0.24)", "0.729", "0.770  (+0.04)", "0.755  (+0.03)"],
            ["XGBoost", "0.581  (−0.09)", "0.675", "0.725  (+0.05)", "0.731  (+0.06)"],
        ],
        [2.6 * inch, 2.3 * inch, 2.2 * inch, 2.4 * inch, 2.4 * inch],
        0.7 * inch,
        H - 1.2 * inch,
        font=14,
    )
    bullets = [
        "90/10: nedvosmisleno pogoršanje. Mali test (14 zemalja) nije evaluacija.",
        "70/30 i 60/40 dižu R² na ovom seedu — to može biti lakši test skup, ne bolji model.",
        "Na 70/30 RF/XGB imaju viši R², ali MAE im je malo lošiji. „Bolje“ nije jednoznačno.",
        "LR je iznad stabala na svakom omjeru ovog seeda.",
    ]
    for i, t in enumerate(bullets):
        c.setFillColor(TEAL)
        c.circle(0.95 * inch, 3.05 * inch - i * 0.55 * inch, 0.09 * inch, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Calibri", 15)
        c.drawString(1.25 * inch, 2.97 * inch - i * 0.55 * inch, t)


def slide_seeds(c: Canvas) -> None:
    header(c, "Isti 80/20, drugi shuffle — je li seed 42 bio sretan?", "TRAIN / TEST  ·  ROBUSTNOST")
    fit_image(c, PLOTS / "split_seed_comparison.png", 0.35 * inch, 0.55 * inch, 8.0 * inch, 5.55 * inch)
    draw_table(
        c,
        ["Seed", "LR", "RF", "Prvi"],
        [
            ["0", "0.619", "0.635", "RF"],
            ["7", "0.741", "0.749", "RF"],
            [("42", True), ("0.780", True), "0.729", "LR"],
            ["123", "0.822", "0.839", "RF"],
        ],
        [1.15 * inch, 1.15 * inch, 1.15 * inch, 1.05 * inch],
        8.55 * inch,
        H - 1.25 * inch,
        font=13,
    )
    callout(
        c,
        "LR na istom 80/20 skače od 0.62 do 0.82. Seed 42 je u gornjoj polovini, nije ekstrem. Rang modela se vrti — zato rangiramo po 5-fold CV, ne po jednom holdoutu.",
        8.55 * inch,
        2.55 * inch,
        4.3 * inch,
        NAVY,
    )


def slide_best(c: Canvas) -> None:
    header(c, "Koja se ispostavila kao najbolja?", "TRAIN / TEST  ·  ODLUKA")
    rows = [
        ("Najviši Test R²", "70/30 · LR · 0.850", "Sreća tog test skupa. Nije protokol."),
        ("Najgora podjela", "90/10", "Svi modeli padaju. 14 test zemalja."),
        ("Najstabilnija ocjena", "5-fold CV · LR 0.779 ± 0.038", "Svaka zemlja jednom u testu."),
        ("Šta zadržavamo", "80/20 · seed 42", "Standard. Holdout ≈ CV. Reproducibilno."),
    ]
    for i, (k, v, why) in enumerate(rows):
        y = 5.45 * inch - i * 1.18 * inch
        c.setFillColor(LIGHT)
        c.roundRect(0.6 * inch, y, 12.15 * inch, 1.05 * inch, 10, fill=1, stroke=0)
        accent = TEAL if i == 3 else (CORAL if i == 1 else NAVY)
        c.setFillColor(accent)
        c.roundRect(0.6 * inch, y, 0.14 * inch, 1.05 * inch, 4, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont("Calibri", 12)
        c.drawString(1.0 * inch, y + 0.72 * inch, k.upper())
        c.setFillColor(NAVY)
        c.setFont("Calibri-Bold", 20)
        c.drawString(1.0 * inch, y + 0.38 * inch, v)
        c.setFillColor(INK)
        c.setFont("Calibri", 13)
        c.drawString(1.0 * inch, y + 0.12 * inch, why)


def slide_close(c: Canvas) -> None:
    header(c, "Šta ostaje u projektu", "ZATVARANJE")
    left = [
        ("Svih 6 kolona", "GDP i zdravlje dijele signal, ali nisu ista stvar."),
        ("80/20 + 5-fold CV", "70/30 izgleda ljepše, ali to bi bilo biranje splita nakon testa."),
        ("Linearna regresija", "Najbolja po CV (0.779 ± 0.038). Jednostavan model na malom uzorku."),
    ]
    for i, (t, b) in enumerate(left):
        y = 5.4 * inch - i * 1.45 * inch
        c.setFillColor(NAVY if i == 2 else TEAL)
        c.roundRect(0.65 * inch, y, 12.05 * inch, 1.28 * inch, 12, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 22)
        c.drawString(1.0 * inch, y + 0.72 * inch, t)
        c.setFont("Calibri", 15)
        c.drawString(1.0 * inch, y + 0.32 * inch, b)


def slide_say(c: Canvas) -> None:
    header(c, "Tri rečenice ako zapnem", "CHEAT-SHEET")
    texts = [
        ("Korelacije", "„Među 6 faktora jedini par iznad 0.8 je GDP i Healthy life expectancy, r = 0.84. VIF je ispod 5. Kolonu nisam izbacila jer mjere različite stvari.“"),
        ("Podjele", "„Na 90/10 se svi pokvare. Na 70/30 LR dođe do 0.85, ali to je sreća testa. Isti 80/20 s drugim seedom skače 0.62–0.82.“"),
        ("Odluka", "„Ostaje 80/20 i svih 6 kolona. Rang držim po 5-fold CV, gdje je linearna regresija i dalje prva.“"),
    ]
    for i, (t, b) in enumerate(texts):
        y = 4.92 * inch - i * 1.48 * inch
        c.setFillColor(TEAL if i < 2 else NAVY)
        c.roundRect(0.6 * inch, y, 12.15 * inch, 1.4 * inch, 10, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Calibri-Bold", 14)
        c.drawString(0.9 * inch, y + 1.02 * inch, t.upper())
        para = p(b, 15, white, leading=20)
        draw_para(c, para, 0.9 * inch, y + 0.95 * inch, 11.5 * inch)


BUILDERS = [
    slide_title,
    slide_agenda,
    slide_with_target,
    slide_heatmap,
    slide_vif,
    slide_keep_columns,
    slide_why_splits,
    slide_ratio_table,
    slide_ratio_chart,
    slide_deltas,
    slide_seeds,
    slide_best,
    slide_close,
    slide_say,
]


def build() -> None:
    c = Canvas(
        str(OUT),
        pagesize=(W, H),
        title="Prezentacija — korelacije i train/test podjele",
        author="Money vs Happiness",
    )
    total = len(BUILDERS)
    for i, fn in enumerate(BUILDERS, start=1):
        new_slide(c)
        fn(c)
        if fn is not slide_title:
            footer_num(c, i, total)
        c.showPage()
    c.save()
    print(f"Wrote {OUT} ({total} slides)")


if __name__ == "__main__":
    build()
