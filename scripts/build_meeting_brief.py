"""Build a meeting-brief PDF about predictor correlations and train/test splits."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Priprema za sastanak - korelacije i podjele.pdf"
PLOTS = ROOT / "results" / "plots"
FONTS = Path(r"C:\Windows\Fonts")

NAVY = HexColor("#1B365D")
TEAL = HexColor("#1F7A6E")
CORAL = HexColor("#C44B32")
GOLD = HexColor("#C9A227")
LIGHT = HexColor("#F3F6F9")
ROW_ALT = HexColor("#EAF2F0")
LINE = HexColor("#D5DDE5")
MUTED = HexColor("#5B6773")

pdfmetrics.registerFont(TTFont("Calibri", str(FONTS / "calibri.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Bold", str(FONTS / "calibrib.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Italic", str(FONTS / "calibrii.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", str(FONTS / "calibriz.ttf")))


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    s: dict[str, ParagraphStyle] = {}
    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker", parent=base["Normal"], fontName="Calibri", fontSize=11,
        textColor=TEAL, alignment=TA_CENTER, spaceAfter=8, tracking=1,
    )
    s["cover_title"] = ParagraphStyle(
        "cover_title", parent=base["Normal"], fontName="Calibri-Bold", fontSize=22,
        textColor=NAVY, alignment=TA_CENTER, leading=28, spaceAfter=10,
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub", parent=base["Normal"], fontName="Calibri", fontSize=12,
        textColor=MUTED, alignment=TA_CENTER, leading=18, spaceAfter=6,
    )
    s["h1"] = ParagraphStyle(
        "h1", parent=base["Normal"], fontName="Calibri-Bold", fontSize=16,
        textColor=NAVY, spaceBefore=4, spaceAfter=10, leading=20,
    )
    s["h2"] = ParagraphStyle(
        "h2", parent=base["Normal"], fontName="Calibri-Bold", fontSize=12.5,
        textColor=TEAL, spaceBefore=12, spaceAfter=6, leading=16,
    )
    s["h3"] = ParagraphStyle(
        "h3", parent=base["Normal"], fontName="Calibri-Bold", fontSize=11,
        textColor=NAVY, spaceBefore=8, spaceAfter=4, leading=14,
    )
    s["body"] = ParagraphStyle(
        "body", parent=base["Normal"], fontName="Calibri", fontSize=10.5,
        textColor=HexColor("#243039"), alignment=TA_JUSTIFY, leading=15,
        spaceAfter=8,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"], fontName="Calibri", fontSize=10.5,
        textColor=HexColor("#243039"), leading=15, leftIndent=12,
        spaceAfter=4, bulletIndent=0,
    )
    s["caption"] = ParagraphStyle(
        "caption", parent=base["Normal"], fontName="Calibri-Italic", fontSize=9,
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=10, leading=12,
    )
    s["th"] = ParagraphStyle(
        "th", parent=base["Normal"], fontName="Calibri-Bold", fontSize=8.5,
        textColor=white, alignment=TA_CENTER, leading=11,
    )
    s["td"] = ParagraphStyle(
        "td", parent=base["Normal"], fontName="Calibri", fontSize=8.5,
        textColor=HexColor("#243039"), alignment=TA_CENTER, leading=11,
    )
    s["td_left"] = ParagraphStyle(
        "td_left", parent=base["Normal"], fontName="Calibri", fontSize=8.5,
        textColor=HexColor("#243039"), alignment=TA_LEFT, leading=11,
    )
    s["td_bold"] = ParagraphStyle(
        "td_bold", parent=base["Normal"], fontName="Calibri-Bold", fontSize=8.5,
        textColor=NAVY, alignment=TA_CENTER, leading=11,
    )
    s["say_title"] = ParagraphStyle(
        "say_title", parent=base["Normal"], fontName="Calibri-Bold", fontSize=10.5,
        textColor=white, leading=13,
    )
    s["say_body"] = ParagraphStyle(
        "say_body", parent=base["Normal"], fontName="Calibri", fontSize=10,
        textColor=HexColor("#1D2A32"), leading=14, alignment=TA_JUSTIFY,
    )
    s["footer"] = ParagraphStyle(
        "footer", parent=base["Normal"], fontName="Calibri", fontSize=8, textColor=MUTED,
    )
    s["toc"] = ParagraphStyle(
        "toc", parent=base["Normal"], fontName="Calibri", fontSize=11,
        textColor=NAVY, leading=18, leftIndent=8, spaceAfter=2,
    )
    return s


S = styles()


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 1.15 * cm, A4[0], 1.15 * cm, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1] - 1.28 * cm, A4[0], 0.13 * cm, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("Calibri", 8.5)
    canvas.drawString(1.8 * cm, A4[1] - 0.75 * cm, "Money vs Happiness  ·  Priprema za sastanak s profesoricom")
    canvas.drawRightString(A4[0] - 1.8 * cm, A4[1] - 0.75 * cm, "WHR 2023")
    canvas.setFillColor(LINE)
    canvas.rect(0, 0, A4[0], 1.05 * cm, fill=1, stroke=0)
    canvas.setFillColor(MUTED)
    canvas.setFont("Calibri", 8)
    canvas.drawString(1.8 * cm, 0.42 * cm, "Interni briefing — nije zamjena za PROJECT_REPORT.md")
    canvas.drawRightString(A4[0] - 1.8 * cm, 0.42 * cm, f"str. {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, A4[1] - 3.2 * cm, A4[0], 0.28 * cm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 2.4 * cm, A4[0], 0.18 * cm, fill=1, stroke=0)
    canvas.restoreState()


def p(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def bullets(items: list[str]) -> list:
    out = []
    for item in items:
        out.append(Paragraph(f"•  {item}", S["bullet"]))
    return out


def section_rule() -> Table:
    t = Table([[""]], colWidths=[17 * cm], rowHeights=[3])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL)]))
    return t


def make_table(headers: list[str], rows: list[list[str]], col_widths: list[float], left_cols: set[int] | None = None) -> Table:
    left_cols = left_cols or {0}
    head = [Paragraph(h, S["th"]) for h in headers]
    data = [head]
    for r in rows:
        cells = []
        for i, val in enumerate(r):
            st = S["td_left"] if i in left_cols else S["td"]
            if isinstance(val, tuple):
                val, bold = val
                st = S["td_bold"] if bold else st
            cells.append(Paragraph(str(val), st))
        data.append(cells)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Calibri-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.3, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        bg = ROW_ALT if i % 2 == 0 else white
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(style_cmds))
    return t


def callout(title: str, body: str, fill: HexColor = TEAL) -> Table:
    inner = Table(
        [
            [Paragraph(title, S["say_title"])],
            [Paragraph(body, S["say_body"])],
        ],
        colWidths=[16.2 * cm],
    )
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), fill),
                ("BACKGROUND", (0, 1), (-1, 1), LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (0, 0), 8),
                ("BOTTOMPADDING", (0, 0), (0, 0), 6),
                ("TOPPADDING", (0, 1), (0, 1), 8),
                ("BOTTOMPADDING", (0, 1), (0, 1), 10),
            ]
        )
    )
    wrap = Table([[inner]], colWidths=[16.6 * cm])
    wrap.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.2, fill),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return wrap


def fig(path: Path, width: float = 16.2 * cm, max_height: float = 9.4 * cm, caption: str | None = None) -> list:
    from PIL import Image as PILImage

    with PILImage.open(path) as im:
        wpx, hpx = im.size
    aspect = hpx / float(wpx)
    height = width * aspect
    if height > max_height:
        height = max_height
        width = height / aspect
    img = Image(str(path), width=width, height=height)
    img.hAlign = "CENTER"
    block: list = [img]
    if caption:
        block.append(p(caption, "caption"))
    return [KeepTogether(block)]


def build() -> None:
    story: list = []

    # --- Cover (drawn mostly by canvas; flowables sit on navy) ---
    cover_title = ParagraphStyle(
        "cover_on_navy", parent=S["cover_title"], textColor=white, fontSize=24, leading=30, spaceAfter=14,
    )
    cover_sub = ParagraphStyle(
        "cover_on_navy_sub", parent=S["cover_sub"], textColor=HexColor("#D7E3EE"), fontSize=12.5, leading=18,
    )
    cover_meta = ParagraphStyle(
        "cover_meta", parent=S["cover_sub"], textColor=HexColor("#9FB4C7"), fontSize=10.5, leading=16,
    )
    story.append(Spacer(1, 5.2 * cm))
    story.append(Paragraph("PRIPREMA ZA SASTANAK", ParagraphStyle("k", parent=S["cover_kicker"], textColor=GOLD, fontSize=12)))
    story.append(Paragraph("Korelacije među podacima<br/>i analiza train/test podjela", cover_title))
    story.append(Paragraph(
        "Kako predstaviti profesorici šta je urađeno, šta brojke znače,<br/>i zašto nijedna kolona nije izbačena niti je 70/30 „pobijedio“ 80/20.",
        cover_sub,
    ))
    story.append(Spacer(1, 1.6 * cm))
    story.append(Paragraph(
        "Projekat: <b>Money vs Happiness</b><br/>Podaci: World Happiness Report 2023 · 137 zemalja<br/>Sastanak: 18. septembar 2026.",
        cover_meta,
    ))
    story.append(PageBreak())

    # --- How to use ---
    story.append(p("Kako koristiti ovaj dokument", "h1"))
    story.append(section_rule())
    story.append(Spacer(1, 8))
    story.append(p(
        "Ovo nije cijeli akademski izvještaj. To je <b>briefing za usmeno izlaganje</b>: dva pitanja "
        "koja je profesorica eksplicitno tražila, sa tačnim brojkama iz pipeline-a, grafikona i CSV tabela. "
        "Ako zatraži detalj, uputi je na <b>PROJECT_REPORT.md</b> (sekcije 10.3.1 i 13.4) i fajlove u <b>results/</b>."
    ))
    story.append(p("Predloženi redoslijed na sastanku (oko 8–10 minuta):"))
    for item in [
        "<b>1 min</b> — podsjetnik: predviđamo Happiness score iz 6 socio-ekonomskih faktora.",
        "<b>3–4 min</b> — korelacije: prvo sa srećom, zatim <i>među</i> faktorima (da li izbaciti kolonu).",
        "<b>4–5 min</b> — train/test: 90/10, 80/20, 70/30, 60/40 + različiti seedovi; gdje se model „popravio“, a gdje pokvario.",
        "<b>Zatvaranje</b> — jedna rečenica: zadržavamo svih 6 kolona i 80/20 + 5-fold CV.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))
    story.append(Spacer(1, 8))
    story.append(p("Sadržaj", "h2"))
    for item in [
        "1. Korelacija među podacima — šta, kako, odluka o kolonama",
        "2. Train/test podjele — svaki omjer, dobitak/gubitak, koja je „najbolja“",
        "3. Cheat-sheet za sastanak — rečenice koje možeš doslovno reći",
    ]:
        story.append(Paragraph(f"•  {item}", S["toc"]))

    story.append(PageBreak())

    # ========== PART 1 ==========
    story.append(p("1. Korelacija među podacima", "h1"))
    story.append(section_rule())
    story.append(Spacer(1, 8))

    story.append(p("1.1 Šta je profesorica tražila", "h2"))
    story.append(p(
        "Prvo je tražila korelaciju između podataka. Zatim je precizirala: treba vidjeti "
        "<b>korelaciju među 6 socio-ekonomskih faktora</b>, da se utvrdi jesu li neki faktori "
        "toliko slični da jednu kolonu treba <b>izbaciti</b>. To nije isto što i korelacija sa srećom. "
        "Prvo pokazuje <i>ko je povezan s ciljem</i>. Drugo pokazuje <i>ko je suvišan među prediktorima</i> "
        "(multikolinearnost / redundantnost)."
    ))

    story.append(p("1.2 Dva različita pitanja — ne pomiješaj ih", "h2"))
    story.append(make_table(
        ["Pitanje", "Šta se računa", "Gdje je u projektu", "Zašto"],
        [
            [
                "Ko ide sa srećom?",
                "Pearson r faktora sa Happiness score",
                "heatmap cilj + 6 faktora",
                "EDA: koji signali su jaki",
            ],
            [
                "Jesu li faktori duplikati?",
                "Pearson r među 6 faktora + VIF",
                "heatmap samo prediktori",
                "Da li izbaciti kolonu",
            ],
        ],
        [3.6 * cm, 4.6 * cm, 4.6 * cm, 3.6 * cm],
    ))
    story.append(p(
        "Tabela 1. Dvije korelacione analize u projektu. Profesorica na ovom sastanku pita za donji red.",
        "caption",
    ))

    story.append(p("1.3 Metoda (reci ovo ako pita „kako ste to radili“)", "h2"))
    for item in [
        "<b>Pearsonova korelacija</b> mjeri <i>linearnu</i> povezanost. Raspon: −1 (jaka negativna) do +1 (jaka pozitivna). Blizu 0 = nema linearne veze.",
        "Prag za sumnju na redundantnost: <b>|r| ≥ 0.80</b>. To je uobičajeno pravilo palca, nije zakon.",
        "Dodatna provjera: <b>VIF</b> (Variance Inflation Factor). Za svaki faktor i računa se VIF<sub>i</sub> = 1 / (1 − R²<sub>i</sub>), gdje se taj faktor regresira na ostalih 5. Uobičajeni prag za ozbiljan problem: <b>VIF &gt; 10</b>. VIF &lt; 5 smatra se prihvatljivim.",
        "Kod: <b>src/eda.py</b> → <b>analyze_predictor_redundancy()</b>. Tabele: <b>results/predictor_correlations.csv</b>, <b>results/predictor_vif.csv</b>.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(p("1.4 Korelacije sa Happiness score (kontekst, 30 sekundi)", "h2"))
    story.append(p(
        "Ovo nije pitanje o izbacivanju kolone, ali profesorica često krene odavde. "
        "To su Pearson r vrijednosti prema cilju (WHR 2023):"
    ))
    story.append(make_table(
        ["Faktor", "Pearson r sa Happiness score", "Interpretacija"],
        [
            ["Social support", ("0.835", True), "Najjača pozitivna veza"],
            ["Logged GDP per capita", ("0.784", True), "Jaka pozitivna veza"],
            ["Healthy life expectancy", "0.746", "Jaka pozitivna veza"],
            ["Freedom to make life choices", "0.663", "Umjereno–jaka pozitivna"],
            ["Perceptions of corruption", "−0.472", "Umjerena negativna veza"],
            ["Generosity", "0.044", "Praktično nula — nema linearne veze"],
        ],
        [5.5 * cm, 5.5 * cm, 5.4 * cm],
    ))
    story.append(p(
        "Tabela 2. Koji faktori idu sa srećom. Socijalna podrška je statistički jača od GDP-a. "
        "Generosity gotovo da ne postoji kao linearni prediktor.",
        "caption",
    ))
    story.append(p(
        "Važna rečenica: <b>korelacija nije kauzalnost</b>. Ovo je presjek jedne godine (137 zemalja), "
        "ne dokaz da povećanje socijalne podrške <i>uzrokuje</i> sreću."
    ))

    story.append(PageBreak())
    story.append(p("1.5 Korelacije MEĐU 6 faktora — srž njenog pitanja", "h2"))
    story.append(p(
        "Ovdje cilj (Happiness score) nije u matrici. Gledamo samo prediktore: jesu li dva faktora "
        "statistički ista priča. Zelenije = jača pozitivna sličnost, narančasto = negativna veza."
    ))
    story.extend(fig(
        PLOTS / "predictor_correlation_heatmap.png",
        width=14.2 * cm,
        max_height=11.2 * cm,
        caption="Slika 1. Pearson matrica samo među prediktorima. Tamnozeleno polje GDP ↔ Healthy life expectancy (0.84) je jedini par iznad praga 0.80.",
    ))

    story.append(p("1.6 Svi parovi, sortirani po sličnosti", "h2"))
    story.append(make_table(
        ["Faktor 1", "Faktor 2", "r", "|r| ≥ 0.80?", "Šta to znači"],
        [
            ["Logged GDP per capita", "Healthy life expectancy", ("0.836", True), ("DA", True), "Jedini kandidat za izbacivanje"],
            ["Logged GDP per capita", "Social support", "0.738", "ne", "Slični, ali ispod praga"],
            ["Social support", "Healthy life expectancy", "0.725", "ne", "Slični, ali ispod praga"],
            ["Social support", "Freedom to make life choices", "0.542", "ne", "Umjereno"],
            ["Logged GDP per capita", "Freedom to make life choices", "0.451", "ne", "Umjereno"],
            ["Logged GDP per capita", "Perceptions of corruption", "−0.437", "ne", "Bogatije zemlje: niža percepcija korupcije"],
            ["Healthy life expectancy", "Freedom to make life choices", "0.414", "ne", "Slabo–umjereno"],
            ["Healthy life expectancy", "Perceptions of corruption", "−0.404", "ne", "Slabo–umjereno"],
            ["Freedom to make life choices", "Perceptions of corruption", "−0.384", "ne", "Slabo–umjereno"],
            ["Social support", "Perceptions of corruption", "−0.272", "ne", "Slabo"],
            ["Freedom to make life choices", "Generosity", "0.170", "ne", "Skoro nezavisno"],
            ["Logged GDP per capita", "Generosity", "−0.156", "ne", "Skoro nezavisno"],
            ["Healthy life expectancy", "Generosity", "−0.134", "ne", "Skoro nezavisno"],
            ["Generosity", "Perceptions of corruption", "−0.123", "ne", "Skoro nezavisno"],
            ["Social support", "Generosity", "0.037", "ne", "Potpuno drugi signal"],
        ],
        [4.0 * cm, 4.2 * cm, 1.6 * cm, 2.2 * cm, 4.4 * cm],
        left_cols={0, 1, 4},
    ))
    story.append(p("Tabela 3. Petnaest parova (C(6,2) = 15). Samo jedan prelazi prag.", "caption"))

    story.append(p("1.7 VIF — da li je r = 0.84 dovoljan razlog za brisanje?", "h2"))
    story.append(p(
        "Pearson r gleda parove. VIF gleda <b>koliko se jedan faktor da objasniti svim ostalima odjednom</b>. "
        "To je stroža, standardna dijagnostika za linearnu regresiju."
    ))
    story.append(make_table(
        ["Faktor", "VIF", "R² na ostalih 5", "Dijagnoza"],
        [
            ["Logged GDP per capita", "4.20", "0.76", "Umjereno, ispod 5"],
            ["Healthy life expectancy", "3.73", "0.73", "Nisko–umjereno"],
            ["Social support", "2.95", "0.66", "Nisko"],
            ["Freedom to make life choices", "1.59", "0.37", "Nisko"],
            ["Perceptions of corruption", "1.43", "0.30", "Nisko"],
            ["Generosity", "1.19", "0.16", "Nisko — skoro nezavisan"],
        ],
        [5.2 * cm, 2.4 * cm, 3.6 * cm, 5.2 * cm],
        left_cols={0, 3},
    ))
    story.append(p(
        "Tabela 4. Nijedan VIF nije ni blizu 10. Čak ni GDP (najviši) nije iznad 5.",
        "caption",
    ))

    story.append(p("1.8 Odluka: nijedna kolona nije izbačena", "h2"))
    story.append(p("Argumenti, redom, ako te prekine:"))
    for item in [
        "<b>Statistika:</b> jedini par iznad 0.80 je GDP ↔ Healthy life expectancy (r = 0.836). Svi VIF &lt; 5.",
        "<b>Sadržaj:</b> to nisu duplikati. Jedno mjeri materijalno bogatstvo, drugo zdravstveni ishod. Bogatije zemlje <i>imaju</i> duži zdrav život, ali to su različiti koncepti.",
        "<b>Modeli:</b> Random Forest i XGBoost podnose korelirane prediktore bolje od linearne regresije. Brisanje kolone bi više naškodilo interpretaciji nego što bi „očistilo“ stabla.",
        "<b>Trag u LR:</b> Healthy life expectancy ima r = 0.746 sa srećom, ali LR koeficijent samo <b>+0.020</b>. Dio efekta „pojede“ GDP. To je klasičan znak multikolinearnosti — <i>bilježi se, ne briše se automatski kolona</i>.",
        "<b>Generosity</b> nije kandidat za izbacivanje zbog sličnosti s drugima (r ≈ 0), nego je slab prediktor cilja. To je druga odluka, i u projektu je zadržana jer je WHR standardni faktor.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(Spacer(1, 8))
    story.append(callout(
        "Šta reći profesorici — korelacije (30 sekundi)",
        "„Uradila sam Pearsonovu matricu među svih 6 faktora. Jedini par iznad 0.8 je GDP i Healthy life expectancy, r = 0.84. "
        "VIF je svugdje ispod 5, najviši je GDP 4.20. Nisam izbacivala kolonu jer mjere različite stvari, a prag za VIF je 10. "
        "Generosity je nezavisna od ostalih. Socijalna podrška je i dalje najjači korelat sreće (r = 0.84), ispred GDP-a.“",
    ))

    story.append(PageBreak())

    # ========== PART 2 ==========
    story.append(p("2. Train/test podjele", "h1"))
    story.append(section_rule())
    story.append(Spacer(1, 8))

    story.append(p("2.1 Šta je profesorica tražila", "h2"))
    story.append(p(
        "Glavni protokol je bio <b>80/20</b> (109 zemalja za trening, 28 za test, <b>random_state=42</b>). "
        "Rekla je da podjelu uradim <b>na više različitih načina</b> da se vidi hoće li se model poboljšati ili pokvariti. "
        "To je pitanje o <b>robustnosti</b>, ne o traženju omjera koji da najljepši Test R²."
    ))

    story.append(p("2.2 Šta je tačno urađeno", "h2"))
    for item in [
        "Glavni izvještaj <b>ostaje 80/20, seed 42</b> — to se nije mijenjalo.",
        "<b>Četiri omjera</b>, isti seed 42: <b>90/10, 80/20, 70/30, 60/40</b>.",
        "<b>Četiri shuffle-a</b> istog 80/20 omjera: seedovi <b>0, 7, 42, 123</b> — da se vidi da li je baš taj 80/20 bio sretan.",
        "Tri modela: Linear Regression, Random Forest, XGBoost. Za ovu usporedbu su <b>fiksni hiperparametri</b> (bez GridSearch-a), da se porede splitovi, ne sreća tuninga.",
        "Kod: <b>src/model.py</b> → <b>run_split_sensitivity()</b>. CSV: <b>split_ratio_metrics.csv</b>, <b>split_seed_metrics.csv</b>.",
        "Linearna regresija na 80/20 seed 42 ima <b>isti</b> Test R² kao u glavnoj tabeli (<b>0.780</b>), jer LR nema tuning. RF/XGBoost u ovoj usporedbi su malo drugačiji od „tuned“ brojki u glavnom izvještaju — to reci ako uporedi tabele.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(p("2.3 Kako čitati „poboljšao se / pokvario se“", "h2"))
    story.append(p(
        "Bazna linija je <b>80/20, seed 42</b>. „Poboljšanje“ ovdje znači <b>viši Test R² / niži MAE na tom holdoutu</b>, "
        "ne da je model naučio bolju pravu vezu. Na 137 zemalja, koje zemlje upadnu u test skup može promijeniti R² za "
        "više od 0.20. Zato brojke niže <b>opisuju šta se desilo na tom splitu</b>, a zaključak na kraju kaže "
        "šta od toga smijemo tretirati kao bolji protokol."
    ))

    story.append(p("2.4 Svaka podjela — šta se radilo i šta se dobilo", "h2"))

    story.append(p("A) 90/10 — 123 train / 14 test", "h3"))
    story.append(p(
        "Najviše podataka za učenje, ali test ima samo <b>14 zemalja</b>. To je statistički premalo: jedan ili dva outliera "
        "pokvare cijeli R²."
    ))
    story.append(make_table(
        ["Model", "Test R²", "Test MAE", "Naspram 80/20", "Ocjena"],
        [
            ["Linear Regression", "0.623", "0.483", "R² −0.157 · MAE +0.077", "Jako pogoršanje"],
            ["Random Forest", "0.493", "0.511", "R² −0.236 · MAE +0.088", "Najveći pad"],
            ["XGBoost", "0.581", "0.513", "R² −0.094 · MAE +0.032", "Pogoršanje"],
        ],
        [3.6 * cm, 2.4 * cm, 2.4 * cm, 4.4 * cm, 3.6 * cm],
        left_cols={0, 3, 4},
    ))
    story.append(p(
        "Tabela 5. 90/10 je <b>najgora podjela</b> za sva tri modela. Više treninga ovdje nije pomoglo, "
        "jer test nije pouzdan. Ako pita „zašto ne 90/10 kad ima više train podataka?“: zato što ocjenjujemo "
        "model na 14 tačaka — to nije evaluacija, to je loterija.",
        "caption",
    ))

    story.append(p("B) 80/20 — 109 train / 28 test  (glavni protokol, seed 42)", "h3"))
    story.append(p(
        "Standardni akademski holdout. Dovoljno testa da R² ne stoji na 14 tačaka, dovoljno treninga za 6 faktora."
    ))
    story.append(make_table(
        ["Model", "Test R²", "Test MAE", "Uloga"],
        [
            ["Linear Regression", ("0.780", True), "0.406", "Najbolji na ovom splitu; isti broj kao glavni izvještaj"],
            ["Random Forest", "0.729", "0.423", "Drugi (untuned u ovoj tabeli)"],
            ["XGBoost", "0.675", "0.481", "Treći (untuned; tuned u glavnom izvještaju je 0.751)"],
        ],
        [4.0 * cm, 2.6 * cm, 2.6 * cm, 7.2 * cm],
        left_cols={0, 3},
    ))
    story.append(p(
        "Tabela 6. Referentna tačka. 5-fold CV za LR je 0.779 ± 0.038 — skoro identično ovom holdoutu, što je dobar znak da seed 42 nije lud.",
        "caption",
    ))

    story.append(p("C) 70/30 — 95 train / 42 test", "h3"))
    story.append(p(
        "Više testa, manje treninga. Na ovom seedu svi modeli imaju <b>viši Test R²</b> nego na 80/20. "
        "To izgleda kao pobjeda — i to treba odmah demistificirati."
    ))
    story.append(make_table(
        ["Model", "Test R²", "Test MAE", "Naspram 80/20", "Ocjena"],
        [
            ["Linear Regression", ("0.850", True), "0.386", "R² +0.070 · MAE −0.021", "Najviši R² od svih omjera"],
            ["Random Forest", "0.770", "0.432", "R² +0.041 · MAE +0.009", "R² gore, MAE malo gore"],
            ["XGBoost", "0.725", "0.489", "R² +0.050 · MAE +0.008", "R² gore, MAE malo gore"],
        ],
        [3.6 * cm, 2.4 * cm, 2.4 * cm, 4.4 * cm, 3.6 * cm],
        left_cols={0, 3, 4},
    ))
    story.append(p(
        "Tabela 7. 70/30 je holdout s <b>najljepšim Test R²</b> (LR 0.850). To NIJE dokaz da je 70/30 bolji protokol. "
        "Test skup od 42 zemlje na seedu 42 bio je „lakši“ (manje teških slučajeva). "
        "RF i XGB imaju viši R² ali MAE im je čak malo lošiji — već tu se vidi da „bolje“ nije jednoznačno.",
        "caption",
    ))

    story.append(p("D) 60/40 — 82 train / 55 test", "h3"))
    story.append(p(
        "Još veći test, još manji train (samo 82 zemlje za 6 faktora). LR i dalje izgleda bolje od 80/20 na ovom seedu, "
        "ali slabije od 70/30. Stabla ostaju iza LR."
    ))
    story.append(make_table(
        ["Model", "Test R²", "Test MAE", "Naspram 80/20", "Ocjena"],
        [
            ["Linear Regression", "0.823", "0.392", "R² +0.043 · MAE −0.014", "Izgleda bolje od 80/20, gore od 70/30"],
            ["Random Forest", "0.755", "0.401", "R² +0.026 · MAE −0.022", "Blago bolje"],
            ["XGBoost", "0.731", "0.431", "R² +0.056 · MAE −0.050", "R² i MAE bolji nego na 80/20"],
        ],
        [3.6 * cm, 2.4 * cm, 2.4 * cm, 4.4 * cm, 3.6 * cm],
        left_cols={0, 3, 4},
    ))
    story.append(p("Tabela 8. 60/40 nije katastrofa, ali gubi train podatke bez jasnog sistematskog dobitka.", "caption"))

    story.append(PageBreak())
    story.append(p("2.5 Pregled: gdje se pogoršalo, gdje „poboljšalo“", "h2"))
    story.append(p("Promjena Test R² u odnosu na 80/20 (seed 42). Minus = pogoršanje, plus = viši R² na tom holdoutu."))
    story.append(make_table(
        ["Model", "90/10", "80/20 (baza)", "70/30", "60/40"],
        [
            ["Linear Regression", ("0.623  (−0.16)", True), "0.780", "0.850  (+0.07)", "0.823  (+0.04)"],
            ["Random Forest", "0.493  (−0.24)", "0.729", "0.770  (+0.04)", "0.755  (+0.03)"],
            ["XGBoost", "0.581  (−0.09)", "0.675", "0.725  (+0.05)", "0.731  (+0.06)"],
        ],
        [3.4 * cm, 3.6 * cm, 3.4 * cm, 3.4 * cm, 3.6 * cm],
        left_cols={0},
    ))
    story.append(p("Tabela 9. 90/10 je pad za sve modele. 70/30 i 60/40 dižu R² na ovom seedu.", "caption"))

    story.extend(fig(
        PLOTS / "split_ratio_comparison.png",
        width=16.2 * cm,
        max_height=7.6 * cm,
        caption="Slika 2. Lijevo R² (više = bolje), desno MAE (niže = bolje). X-osa je udio treninga: 90 → 60. Svi modeli padaju na 90% train (mali test). LR je iznad ostalih na svakom omjeru ovog seeda.",
    ))

    story.append(p("Jedna rečenica po omjeru:", "h3"))
    for item in [
        "<b>90/10:</b> svi modeli se <b>pokvare</b>. Najgori ishod. Ne koristiti.",
        "<b>80/20:</b> stabilna baza. LR 0.780 slaže se sa CV 0.779.",
        "<b>70/30:</b> najviši R² (LR 0.850) — <b>izgleda kao poboljšanje, ali je sreća testa</b>.",
        "<b>60/40:</b> i dalje izgleda bolje od 80/20 na ovom seedu, ali slabije od 70/30; manje podataka za učenje.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(p("2.6 Isti 80/20, drugi shuffle — da nije 80/20 bio sretan?", "h2"))
    story.append(p(
        "Omjer ostaje 80/20, mijenja se samo koji slučajni 28 zemalja idu u test. Ako je model zaista stabilan, "
        "R² ne smije skakati kao loto."
    ))
    story.append(make_table(
        ["Seed", "LR R²", "RF R²", "XGB R²", "Ko je prvi?", "Naspram seed 42 (LR)"],
        [
            ["0", "0.619", "0.635", "0.607", "Random Forest", "LR −0.161  (pogoršanje)"],
            ["7", "0.741", "0.749", "0.737", "Random Forest", "LR −0.039"],
            [("42 (glavni)", True), ("0.780", True), "0.729", "0.675", "Linear Regression", "baza"],
            ["123", "0.822", "0.839", "0.798", "Random Forest", "LR +0.042  (izgleda bolje)"],
        ],
        [2.6 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 3.4 * cm, 4.8 * cm],
        left_cols={0, 4, 5},
    ))
    story.append(p(
        "Tabela 10. LR Test R² na istom 80/20 ide od <b>0.619 do 0.822</b>. Seed 42 (0.780) je u gornjoj polovini, "
        "nije ni najsretniji ni najnesretniji. Na 3 od 4 seeda Random Forest čak nadmašuje LR — zato se rang "
        "<b>ne smije</b> objavljivati s jednog holdouta.",
        "caption",
    ))
    story.extend(fig(
        PLOTS / "split_seed_comparison.png",
        width=15.2 * cm,
        max_height=7.2 * cm,
        caption="Slika 3. Isti omjer, četiri shuffle-a. Visina stubova skače — to je cijela poenta malog uzorka.",
    ))

    story.append(p(
        "Šta da zapamtiš sa ove slike: seed 0 je loš za sve; seed 123 je sretan (čak RF ispred LR); seed 42 je u sredini–gore. "
        "Zato 80/20 nije prevara, ali jedan holdout nije dovoljan za rang modela."
    ))

    story.append(p("2.7 Koja se ispostavila kao najbolja?", "h2"))
    story.append(p(
        "Ovjde moraš razdvojiti <b>najljepši jedan broj</b> od <b>najboljeg protokola</b>. "
        "Ako ih pomiješaš, profesorica će s pravom reći da juriš R²."
    ))
    story.append(make_table(
        ["Kriterij", "Pobjednik", "Zašto to NIJE / JESTE odgovor"],
        [
            [
                "Najviši Test R² (omjeri)",
                "70/30 · LR · 0.850",
                "Samo ovaj seed i ovaj test skup. Ne ponavlja se kao pravilo.",
            ],
            [
                "Najviši Test R² (seedovi)",
                "80/20 seed 123 · RF · 0.839",
                "Još jedan sretan shuffle. RF tu pobjeđuje LR — rang nije stabilan.",
            ],
            [
                "Najgora podjela",
                "90/10 · svi modeli padaju",
                "14 test zemalja. Ovo je jedini nedvosmisleno loš izbor.",
            ],
            [
                "Najstabilnija ocjena kvaliteta",
                "5-fold CV · LR 0.779 ± 0.038",
                "Svaka zemlja jednom bude u test foldu. Zato rangiramo po CV.",
            ],
            [
                "Preporučeni holdout",
                ("80/20 · seed 42", True),
                "Standard, nije ekstrem, LR holdout ≈ CV, reproducibilan.",
            ],
        ],
        [4.4 * cm, 4.6 * cm, 7.4 * cm],
        left_cols={0, 1, 2},
    ))
    story.append(p("Tabela 11. Konačni odgovor na „koja je najbolja podjela?“.", "caption"))

    story.append(p(
        "<b>Zaključak koji treba izgovoriti:</b> najviši broj je 70/30, ali <b>najbolja odluka je ostaviti 80/20</b> "
        "i oslanjanje na 5-fold CV. Model se nije sistematski poboljšao većim ili manjim testom — "
        "mijenjao se sastav 14–55 zemalja u testu. Na malom uzorku (137) holdout je bučan; CV je mirniji."
    ))

    story.append(Spacer(1, 6))
    story.append(callout(
        "Šta reći profesorici — podjele (45 sekundi)",
        "„Pored 80/20 uradila sam 90/10, 70/30 i 60/40, plus isti 80/20 s četiri različita seeda. "
        "Na 90/10 se svi modeli pokvare — test ima samo 14 zemalja. Na 70/30 linearna regresija dođe do R² 0.85, "
        "što izgleda bolje od 0.78, ali to je sreća tog test skupa, ne bolji model. Isti 80/20 s drugim seedom "
        "skače od 0.62 do 0.82, a ponekad Random Forest pobijedi. Zato nisam mijenjala protokol: ostaje 80/20, "
        "a rang modela držim po 5-fold CV, gdje je linearna regresija i dalje prva (0.779 ± 0.038).“",
        fill=NAVY,
    ))

    story.append(p("2.8 Ako te gura da ipak pređeš na 70/30", "h2"))
    for item in [
        "Možeš reći da si 70/30 <b>ispitala</b> i da ga ne krijete — tabela je u izvještaju.",
        "Preći na 70/30 samo zato što je R² veći bilo bi <b>data snooping</b>: biraš split nakon što vidiš test.",
        "Ako insistira na drugom omjeru, poštena alternativa nije 70/30 nego <b>ponavljani CV / više seedova</b>, što je već urađeno.",
        "Glavni naučni nalaz (LR ≥ stabla na ovom malom linearno-ish skupu) <b>opstaje</b> na svim omjerima ovog seeda: LR je uvijek iznad RF i XGB u Tabeli 9.",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(PageBreak())

    # ========== PART 3 cheat sheet ==========
    story.append(p("3. Cheat-sheet za sastanak", "h1"))
    story.append(section_rule())
    story.append(Spacer(1, 8))
    story.append(p(
        "Ova stranica je za štampu ili za ekran pored sebe. Ako zapneš, čitaj okvire redom."
    ))

    story.append(callout(
        "Rečenica 1 — uvod",
        "„Imam dva dopunjena eksperimenta: korelacije među 6 faktora (da li izbaciti kolonu) i više train/test podjela (da li 80/20 laže).“",
    ))
    story.append(Spacer(1, 8))
    story.append(callout(
        "Rečenica 2 — korelacije",
        "„Među prediktorima jedini par iznad 0.8 je GDP i Healthy life expectancy, r = 0.84. VIF je ispod 5. Kolonu nisam izbacila jer su to različiti koncepti. Generosity je nezavisna. Sa srećom najjače ide socijalna podrška (0.84), pa GDP (0.78).“",
    ))
    story.append(Spacer(1, 8))
    story.append(callout(
        "Rečenica 3 — podjele",
        "„90/10 se pokvari. 70/30 izgleda najbolje (LR 0.85), ali to je sreća testa. Isti 80/20 s drugim seedom skače 0.62–0.82. Ostaje 80/20 + 5-fold CV.“",
    ))
    story.append(Spacer(1, 8))
    story.append(callout(
        "Rečenica 4 — zatvaranje",
        "„Dakle: svih 6 kolona ostaje, 80/20 ostaje, linearna regresija i dalje najbolji model po CV. Nisam mijenjala protokol zbog jednog lijepog holdout broja.“",
        fill=NAVY,
    ))

    story.append(p("Brojevi koje treba znati napamet", "h2"))
    story.append(make_table(
        ["Stavka", "Broj"],
        [
            ["Zemlje u skupu", "137"],
            ["Faktori", "6"],
            ["Najjači korelati sreće", "Social support 0.835 · GDP 0.784"],
            ["Jedini par |r| ≥ 0.80", "GDP ↔ Healthy life expectancy  0.836"],
            ["Najviši VIF", "GDP  4.20  (prag 10)"],
            ["Izbacene kolone", "nijedna"],
            ["Glavni split", "80/20 · 109 / 28 · seed 42"],
            ["LR Test R² na 80/20", "0.780"],
            ["LR 5-fold CV R²", "0.779 ± 0.038"],
            ["90/10 LR Test R²", "0.623  (pogoršanje)"],
            ["70/30 LR Test R²", "0.850  (izgleda bolje, nije protokol)"],
            ["60/40 LR Test R²", "0.823"],
            ["80/20 LR R² po seedovima", "0.619 · 0.741 · 0.780 · 0.822"],
            ["Preporuka", "svih 6 kolona · 80/20 · rang po CV"],
        ],
        [7.5 * cm, 9.9 * cm],
        left_cols={0, 1},
    ))
    story.append(p("Tabela 12. Mini-memorija za sastanak.", "caption"))

    story.append(p("Gdje su dokazi u projektu", "h2"))
    for item in [
        "Kod korelacija: <b>src/eda.py</b> (analyze_predictor_redundancy)",
        "Kod podjela: <b>src/model.py</b> (run_split_sensitivity)",
        "Izvještaj: <b>PROJECT_REPORT.md</b> §10.3.1 i §13.4",
        "Grafikoni: <b>results/plots/predictor_correlation_heatmap.png</b>, <b>split_ratio_comparison.png</b>, <b>split_seed_comparison.png</b>",
        "Tabele: <b>results/predictor_correlations.csv</b>, <b>predictor_vif.csv</b>, <b>split_ratio_metrics.csv</b>, <b>split_seed_metrics.csv</b>",
        "Dashboard: donji dio — heatmap prediktora i linija Test R² po omjeru",
    ]:
        story.append(Paragraph(f"•  {item}", S["bullet"]))

    story.append(Spacer(1, 10))
    story.append(p(
        "Ako na kraju pita šta je naučni rezultat ova dva eksperimenta, a ne šta je procedura: "
        "<b>bogatstvo i zdravlje dijele informaciju, ali nisu ista stvar; holdout na 137 zemalja je nestabilan, "
        "pa jednostavan model + CV ostaju poštenija priča od lovljenja omjera.</b>"
    ))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=1.9 * cm,
        rightMargin=1.9 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.5 * cm,
        title="Priprema za sastanak — korelacije i train/test podjele",
        author="Money vs Happiness",
        subject="Briefing za sastanak s profesoricom",
    )
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
