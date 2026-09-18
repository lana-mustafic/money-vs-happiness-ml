"""Generate insert pages for ML_Dokumentacija.pdf in matching academic style."""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
PLOTS = ROOT / "results" / "plots"
FONTS = Path(r"C:\Windows\Fonts")
OUT_84 = ROOT / "scripts" / "_insert_8_4.pdf"
OUT_9 = ROOT / "scripts" / "_insert_9_intro.pdf"
OUT_153 = ROOT / "scripts" / "_insert_15_3.pdf"

BLUE = HexColor("#0033CC")
INK = HexColor("#000000")
LINE = HexColor("#000000")

pdfmetrics.registerFont(TTFont("Times", str(FONTS / "times.ttf")))
pdfmetrics.registerFont(TTFont("Times-Bold", str(FONTS / "timesbd.ttf")))
pdfmetrics.registerFont(TTFont("Times-Italic", str(FONTS / "timesi.ttf")))
pdfmetrics.registerFont(TTFont("Times-BoldItalic", str(FONTS / "timesbi.ttf")))
pdfmetrics.registerFont(TTFont("Calibri-Light", str(FONTS / "calibril.ttf")))


def styles() -> dict[str, ParagraphStyle]:
    s: dict[str, ParagraphStyle] = {}
    s["ch"] = ParagraphStyle(
        "ch", fontName="Calibri-Light", fontSize=13, textColor=BLUE,
        spaceAfter=12, spaceBefore=4, leading=16,
    )
    s["h"] = ParagraphStyle(
        "h", fontName="Times-Bold", fontSize=12, textColor=INK,
        spaceBefore=14, spaceAfter=8, leading=16,
    )
    s["body"] = ParagraphStyle(
        "body", fontName="Times", fontSize=12, textColor=INK,
        alignment=TA_JUSTIFY, leading=16, spaceAfter=8,
    )
    s["caption"] = ParagraphStyle(
        "caption", fontName="Times-Italic", fontSize=12, textColor=INK,
        spaceBefore=10, spaceAfter=6, leading=15,
    )
    s["th"] = ParagraphStyle(
        "th", fontName="Times-Bold", fontSize=10, textColor=INK,
        alignment=TA_CENTER, leading=13,
    )
    s["td"] = ParagraphStyle(
        "td", fontName="Times", fontSize=10, textColor=INK,
        alignment=TA_CENTER, leading=13,
    )
    s["tdl"] = ParagraphStyle(
        "tdl", fontName="Times", fontSize=10, textColor=INK,
        alignment=TA_LEFT, leading=13,
    )
    s["tdb"] = ParagraphStyle(
        "tdb", fontName="Times-Bold", fontSize=10, textColor=INK,
        alignment=TA_LEFT, leading=13,
    )
    s["li"] = ParagraphStyle(
        "li", fontName="Times", fontSize=12, textColor=INK,
        alignment=TA_JUSTIFY, leading=16,
    )
    s["fig"] = ParagraphStyle(
        "fig", fontName="Times-Italic", fontSize=11, textColor=INK,
        alignment=TA_CENTER, spaceBefore=4, spaceAfter=10, leading=14,
    )
    return s


S = styles()


def P(text: str, key: str = "body") -> Paragraph:
    return Paragraph(text, S[key])


def table(headers: list[str], rows: list[list[str]], widths: list[float], left: set[int] | None = None) -> Table:
    left = left or {0}
    data = [[Paragraph(h, S["th"]) for h in headers]]
    for r in rows:
        cells = []
        for i, v in enumerate(r):
            cells.append(Paragraph(str(v), S["tdb"] if i in left else S["td"]))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1)
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(cmds))
    return t


def fig(path: Path, width: float = 6.4 * inch, max_h: float = 3.6 * inch) -> Image:
    with PILImage.open(path) as im:
        wpx, hpx = im.size
    h = width * (hpx / wpx)
    if h > max_h:
        h = max_h
        width = h * (wpx / hpx)
    img = Image(str(path), width=width, height=h)
    img.hAlign = "CENTER"
    return img


def num_items(items: list[str]) -> list:
    out = []
    for i, text in enumerate(items, 1):
        out.append(Paragraph(f"{i}. {text}", S["body"]))
    return out


def bullet_items(items: list[str]) -> list:
    out = []
    for text in items:
        out.append(Paragraph(f"•  {text}", S["body"]))
    return out


def make_doc(path: Path, title: str) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=64,
        title=title,
    )


def story_83() -> list:
    story: list = []
    story.append(P("8.3 Važno upozorenje: Korelacija nije isto što i kauzalnost!", "h"))
    story.append(P(
        "To što neki faktori imaju visoku korelaciju sa srećom ne znači automatski da oni direktno "
        "uzrokuju sreću. Za to postoje tri glavna razloga:"
    ))
    story.extend(bullet_items([
        "<b>Skrivene varijable (Confounding Variables):</b> Bogatije zemlje obično „u paketu“ imaju i "
        "bolje zdravstvo, jaču vladavinu prava i stabilnije institucije, pa je teško razdvojiti šta "
        "tačno utiče na šta.",
        "<b>Jedna tačka u vremenu (Cross-section):</b> Podaci su samo iz 2023. godine. Prikazuju "
        "trenutno stanje među zemljama, a ne kako se situacija mijenja kroz vrijeme unutar jedne države.",
        "<b>Obrnuta uzročnost (Reversed Causality):</b> Uzročni smjer može biti obrnut — možda "
        "sretniji i zdraviji ljudi prave jaču ekonomiju, a ne samo obrnuto.",
    ]))
    story.append(P(
        "<b>Zaključak:</b> Korelacija nam daje odličnu osnovu za prave prediktivne ML modele, ali je ne "
        "smijemo tumačiti kao slijepi dokaz uzroka i posljedice."
    ))
    return story


def build_9_intro() -> None:
    story: list = []
    story.append(P("ANALIZA ODNOSA GDP-A I NACIONALNE SREĆE (GDP VS. HAPPINESS)", "ch"))
    story.append(P(
        "Kako bismo provjerili koliku stvarno snagu ima sam BDP u prognoziranju sreće, napravili smo "
        "jednostavan eksperiment sa univarijantnom linearnom regresijom (OLS model). Jedini ulazni "
        "podatak (X) bio je logaritmovani BDP po glavi stanovnika (Logged GDP per capita), dok je izlaz "
        "(y) bio indeks sreće (Happiness score)."
    ))
    story.append(P("9.1 Šta nam govori model sa samim BDP-om?", "h"))
    story.extend(bullet_items([
        "<b>Objašnjen varijabilitet (61.5%):</b> Sam BDP po glavi stanovnika objašnjava više od dvije "
        "trećine razlika u nivou sreće među 137 posmatranih zemalja.",
        "<b>Potvrda prve hipoteze (H_1):</b> Ovo direktno potvrđuje da je BDP odlična polazna tačka. "
        "Ekonomski razvoj stvara neophodne osnove — infrastrukturu, zdravstvo, obrazovanje i "
        "materijalnu sigurnost.",
    ]))
    story.append(P("9.2 Zašto sam BDP ipak nije dovoljan? (Neobjašnjenih 38.5%)", "h"))
    story.append(P(
        "Preostalih 38.5% varijanse jasno pokazuje da novac nije jedini faktor. Najbolji dokaz za to su "
        "odstupanja (outlieri) u podacima:"
    ))
    story.extend(bullet_items([
        "<b>Visok BDP, a skromnija sreća:</b> Hong Kong, sa BDP-om u samom svjetskom vrhu (10.966), "
        "ima ocjenu sreće ispod medijane (5.308) zbog ogromnih troškova života, stresa i političkih "
        "tenzija. Bocvana i Turska imaju solidnu ekonomiju, ali nižu ocjenu sreće zbog nejednakosti, "
        "inflacije i problema u institucijama.",
        "<b>Skromniji BDP, a visoka sreća:</b>",
    ]))
    make_doc(OUT_9, "ML dokumentacija — uvod poglavlja 9").build(story)
    print("wrote", OUT_9)


def build_84() -> None:
    story: list = []
    story.extend(story_83())
    story.append(P("8.4 Korelacije među prediktorima (provjera redundantnosti)", "h"))
    story.append(P(
        "Analiza u poglavljima 8.1–8.3 kvantifikuje povezanost svakog socio-ekonomskog faktora "
        "sa ciljnom varijablom <i>Happiness score</i>. To, međutim, ne odgovara na drugo, "
        "metodološki jednako važno pitanje: <b>jesu li neki od šest prediktora međusobno toliko "
        "slični da jedan od njih treba ukloniti iz modela</b>? Takva sličnost naziva se "
        "multikolinearnost (redundantnost karakteristika). Ako dva faktora nose gotovo istu "
        "informaciju, linearna regresija može dati nestabilne koeficijente, a interpretacija "
        "„šta tačno utiče na sreću“ postaje zamagljena."
    ))
    story.append(P(
        "U tu svrhu izračunata je Pearsonova korelaciona matrica isključivo među šest "
        "ulaznih karakteristika (cilj y nije uključen), te dodatni dijagnostički pokazatelj "
        "VIF (Variance Inflation Factor). Implementacija je u modulu src/eda.py, u funkciji "
        "analyze_predictor_redundancy()."
    ))

    story.append(P("8.4.1 Metoda i pragovi odlučivanja", "h"))
    story.extend(num_items([
        "<b>Pearsonov koeficijent r</b> mjeri linearnu povezanost dva prediktora. Vrijednost "
        "blizu +1 označava jaku pozitivnu sličnost, blizu −1 jaku negativnu, a blizu 0 odsustvo "
        "linearne veze.",
        "<b>Prag redundantnosti:</b> par sa |r| ≥ 0.80 tretira se kao kandidat za uklanjanje "
        "jedne od dvije kolone. To je uobičajeno metodološko pravilo, a ne apsolutni zakon.",
        "<b>VIF</b> za faktor <i>i</i> računa se kao VIF<sub>i</sub> = 1 / (1 − R²<sub>i</sub>), "
        "gdje se taj faktor regresira na preostalih pet. VIF &lt; 5 smatra se prihvatljivim; "
        "VIF &gt; 10 ukazuje na ozbiljnu multikolinearnost koja opravdava izbacivanje kolone.",
    ]))

    story.append(P("8.4.2 Pearsonova matrica među šest faktora", "h"))
    story.append(P(
        "Slika 8.1 prikazuje toplotnu mapu međusobnih korelacija. Tamnije zelene ćelije "
        "označavaju jaču pozitivnu sličnost. Ključni nalaz je da <b>samo jedan par prelazi prag "
        "|r| ≥ 0.80</b>: <i>Logged GDP per capita</i> i <i>Healthy life expectancy</i> "
        "(r = 0.836)."
    ))
    story.append(KeepTogether([
        fig(PLOTS / "predictor_correlation_heatmap.png", 5.8 * inch, 4.2 * inch),
        P(
            "Slika 8.1. Pearsonova korelaciona matrica među šest socio-ekonomskih prediktora "
            "(ciljna varijabla nije uključena).",
            "fig",
        ),
    ]))

    story.append(P("Tabela 8.2: Međusobne Pearsonove korelacije prediktora (sortirano po |r|)", "caption"))
    story.append(table(
        ["Faktor 1", "Faktor 2", "r", "|r| ≥ 0.80?"],
        [
            ["Logged GDP per capita", "Healthy life expectancy", "0.836", "da"],
            ["Logged GDP per capita", "Social support", "0.738", "ne"],
            ["Social support", "Healthy life expectancy", "0.725", "ne"],
            ["Social support", "Freedom to make life choices", "0.542", "ne"],
            ["Logged GDP per capita", "Freedom to make life choices", "0.451", "ne"],
            ["Logged GDP per capita", "Perceptions of corruption", "−0.437", "ne"],
            ["Healthy life expectancy", "Freedom to make life choices", "0.414", "ne"],
            ["Healthy life expectancy", "Perceptions of corruption", "−0.404", "ne"],
            ["Freedom to make life choices", "Perceptions of corruption", "−0.384", "ne"],
            ["Social support", "Perceptions of corruption", "−0.272", "ne"],
            ["Freedom to make life choices", "Generosity", "0.170", "ne"],
            ["Logged GDP per capita", "Generosity", "−0.156", "ne"],
            ["Healthy life expectancy", "Generosity", "−0.134", "ne"],
            ["Generosity", "Perceptions of corruption", "−0.123", "ne"],
            ["Social support", "Generosity", "0.037", "ne"],
        ],
        [1.85 * inch, 2.15 * inch, 0.7 * inch, 1.0 * inch],
        left={0, 1},
    ))
    story.append(P(
        "Od ukupno 15 parova (kombinacija C(6,2)), jedini kandidat za uklanjanje kolone jeste "
        "par BDP–očekivano zdravo trajanje života. Ostali parovi ostaju ispod praga. "
        "<i>Generosity</i> je gotovo ortogonalna na preostale faktore (sve |r| ≤ 0.17), što "
        "znači da nosi zaseban, mada prediktivno slab, signal."
    ))

    story.append(P("8.4.3 VIF dijagnostika", "h"))
    story.append(P(
        "Pearsonov r gleda parove. VIF odgovara na strože pitanje: koliko se jedan prediktor "
        "može objasniti <b>svim ostalim prediktorima odjednom</b>. To je standardna dijagnostika "
        "multikolinearnosti u linearnoj regresiji."
    ))
    story.append(P("Tabela 8.3: Variance Inflation Factor za šest prediktora", "caption"))
    story.append(table(
        ["Faktor", "VIF", "R² na ostalih 5", "Dijagnoza"],
        [
            ["Logged GDP per capita", "4.20", "0.76", "Umjereno, ispod 5"],
            ["Healthy life expectancy", "3.73", "0.73", "Nisko–umjereno"],
            ["Social support", "2.95", "0.66", "Nisko"],
            ["Freedom to make life choices", "1.59", "0.37", "Nisko"],
            ["Perceptions of corruption", "1.43", "0.30", "Nisko"],
            ["Generosity", "1.19", "0.16", "Nisko — skoro nezavisan"],
        ],
        [2.35 * inch, 0.7 * inch, 1.25 * inch, 1.7 * inch],
        left={0, 3},
    ))
    story.append(P(
        "Nijedna vrijednost VIF-a nije ni blizu praga 10. Najviši VIF ima <i>Logged GDP per "
        "capita</i> (4.20), što je još uvijek unutar prihvatljivog opsega. Drugim riječima, "
        "iako BDP i očekivano zdravo trajanje života statistički dijele sličan signal, "
        "multikolinearnost nije dovoljno jaka da bi se kolona morala ukloniti."
    ))

    story.append(KeepTogether([
        P("8.4.4 Odluka: nijedna kolona nije izbačena", "h"),
        P("Odluka da se zadrže svih šest karakteristika zasniva se na četiri argumenta:"),
        *num_items([
            "<b>Statistički prag:</b> jedini par sa |r| ≥ 0.80 jeste BDP ↔ <i>Healthy life expectancy</i> "
            "(r = 0.836), a svi VIF pokazatelji ostaju ispod 5.",
            "<b>Konceptualna razlika:</b> navedene dvije varijable nisu duplikati. Prva mjeri "
            "materijalno bogatstvo, druga zdravstveni ishod. Bogatije zemlje u pravilu imaju duži "
            "zdrav život, ali to su i dalje različite dimenzije blagostanja.",
            "<b>Svojstva modela:</b> algoritmi zasnovani na stablima (Random Forest, XGBoost) "
            "otporniji su na korelirane prediktore od obične linearne regresije. Automatsko "
            "brisanje kolone smanjilo bi interpretabilnost, a ne bi nužno poboljšalo predikciju.",
            "<b>Trag u linearnoj regresiji:</b> <i>Healthy life expectancy</i> ima r = 0.746 sa "
            "srećom, ali koeficijent u višefaktorskom LR modelu iznosi tek +0.020. Dio efekta "
            "preuzima BDP. To je klasičan znak umjerene multikolinearnosti — evidentira se u "
            "diskusiji, ali ne povlači automatsko brisanje kolone.",
        ]),
        P(
            "<b>Zaključak poglavlja 8.4:</b> provjera redundantnosti potvrđuje da skup od šest "
            "WHR faktora nije statistički redundantan do mjere koja bi zahtijevala redukciju "
            "dimenzionalnosti. <i>Generosity</i> ostaje u modelu iako je slabo povezana sa ciljem "
            "(r = 0.044), jer je riječ o standardnom WHR stubu, a ne o duplikatu ostalih prediktora. "
            "Time je sačuvana puna interpretabilnost socio-ekonomskog profila zemlje."
        ),
    ]))

    doc = SimpleDocTemplate(
        str(OUT_84),
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=64,
        title="ML dokumentacija — umetak 8.4",
    )
    doc.build(story)
    print("wrote", OUT_84)


def build_153() -> None:
    story: list = []
    story.append(P("15.3 Osjetljivost na način podjele train/test skupa", "h"))
    story.append(P(
        "Osnovna evaluacija modela u prethodnim odjeljcima provedena je na jednoj slučajnoj "
        "holdout podjeli <b>80/20</b> (<i>train_test_split</i>, <i>random_state=42</i>): 109 "
        "zemalja za treniranje i 28 zemalja za testiranje. Na malom uzorku (N = 137) jedna "
        "takva podjela može biti slučajno „laka“ ili „teška“, pa Test R² nije dovoljan kao "
        "jedini dokaz kvaliteta protokola. Stoga je dodatno ispitano <b>više omjera podjele</b> "
        "i <b>više slučajnih rasporeda</b> istog 80/20 omjera, kako bi se utvrdilo da li se "
        "model sistematski poboljšava ili pogoršava."
    ))
    story.append(P(
        "Eksperiment je implementiran funkcijom <i>run_split_sensitivity()</i> u modulu "
        "<i>src/model.py</i>. Radi fer poređenja splitova, tri modela (Linear Regression, "
        "Random Forest, XGBoost) trenirana su sa fiksnim hiperparametrima, bez ponovnog "
        "GridSearch-a na svakom omjeru. Glavni izvještaj projekta i dalje počiva na podjeli "
        "80/20, seed 42; ovaj odjeljak predstavlja provjeru robustnosti, a ne zamjenu protokola."
    ))

    story.append(P("15.3.1 Postavka eksperimenta", "h"))
    story.extend(num_items([
        "<b>Četiri omjera</b> uz isti <i>random_state=42</i>: 90/10 (123/14), 80/20 (109/28), "
        "70/30 (95/42) i 60/40 (82/55).",
        "<b>Četiri shuffle-a</b> istog 80/20 omjera: random_state vrijednosti 0, 7, 42 i 123, "
        "kako bi se provjerilo da li je seed 42 bio netipično povoljan.",
        "<b>Metrike:</b> Test R² (više = bolje) i Test MAE (niže = bolje). Bazna linija za "
        "poređenje jeste 80/20, seed 42, Linear Regression, Test R² = 0.780.",
    ]))
    story.append(P(
        "Napomena o usporedivosti: linearna regresija na 80/20 (seed 42) daje <b>identičan</b> "
        "Test R² kao u Tabeli 15.1 (0.780), jer nema hiperparametarskog podešavanja. "
        "Random Forest i XGBoost u ovom eksperimentu koriste fiksne postavke, pa se njihovi "
        "brojevi mogu blago razlikovati od podešenih (tuned) vrijednosti u glavnoj tabeli."
    ))

    story.append(P("15.3.2 Rezultati po omjeru podjele", "h"))
    story.append(P("Tabela 15.2: Test R² tri modela za četiri train/test omjera (seed = 42)", "caption"))
    story.append(table(
        ["Split", "n_train / n_test", "Linear Regression", "Random Forest", "XGBoost"],
        [
            ["90/10", "123 / 14", "0.623", "0.493", "0.581"],
            ["80/20 (baza)", "109 / 28", "0.780", "0.729", "0.675"],
            ["70/30", "95 / 42", "0.850", "0.770", "0.725"],
            ["60/40", "82 / 55", "0.823", "0.755", "0.731"],
        ],
        [1.25 * inch, 1.35 * inch, 1.45 * inch, 1.25 * inch, 0.95 * inch],
        left={0, 1},
    ))
    story.append(KeepTogether([
        P(
            "Tabela 15.3: Promjena Test R² u odnosu na baznu podjelu 80/20 (predznak minus označava pogoršanje)",
            "caption",
        ),
        table(
            ["Model", "90/10", "70/30", "60/40"],
            [
                ["Linear Regression", "−0.157", "+0.070", "+0.043"],
                ["Random Forest", "−0.236", "+0.041", "+0.026"],
                ["XGBoost", "−0.094", "+0.050", "+0.056"],
            ],
            [1.8 * inch, 1.4 * inch, 1.4 * inch, 1.4 * inch],
            left={0},
        ),
    ]))

    story.append(P("Interpretacija po omjeru:", "h"))
    story.extend(num_items([
        "<b>90/10 (najgora podjela).</b> Sva tri modela se pogoršavaju. Linearna regresija "
        "pada sa 0.780 na 0.623, a Random Forest na 0.493. Uzrok nije manjak trening podataka "
        "(train ima čak 123 zemlje), već <b>nepouzdan test od samo 14 opservacija</b>. Jedan "
        "ili dva outliera tada dominantno određuju R². Ova podjela se odbacuje.",
        "<b>80/20 (referentni protokol).</b> Linearna regresija ostvaruje Test R² = 0.780, što "
        "se gotovo poklapa sa 5-fold unakrsnom validacijom (CV R² = 0.779 ± 0.038). To je "
        "važan znak da seed 42 nije ekstremno povoljan split.",
        "<b>70/30 (najviši Test R², ali ne i bolji protokol).</b> Linearna regresija dostiže "
        "0.850. Na prvi pogled to izgleda kao poboljšanje od +0.070. Međutim, riječ je o "
        "<b>drugom sastavu testnog skupa</b> (42 zemlje), koji na ovom seedu može biti "
        "statistički „lakši“. Random Forest i XGBoost također imaju viši R², ali im MAE "
        "blago raste, što pokazuje da „bolje“ nije jednoznačno ni unutar istog omjera. "
        "Birati 70/30 nakon što je Test R² već viđen bilo bi metodološki neispravno "
        "(data snooping).",
        "<b>60/40.</b> Linearna regresija (0.823) i dalje nadmašuje 80/20 na ovom seedu, ali "
        "zaostaje za 70/30. Train skup se smanjuje na 82 zemlje, što je nepovoljno za "
        "stabilnost stabala, bez jasnog sistematskog dobitka u generalizaciji.",
    ]))

    story.append(KeepTogether([
        fig(PLOTS / "split_ratio_comparison.png", 6.3 * inch, 3.15 * inch),
        P(
            "Slika 15.1. Test R² (lijevo, više = bolje) i Test MAE (desno, niže = bolje) u "
            "ovisnosti o udjelu trening skupa. Svi modeli imaju najslabije performanse na "
            "omjeru 90/10.",
            "fig",
        ),
    ]))

    story.append(P("15.3.3 Isti omjer 80/20, različiti slučajni rasporedi", "h"))
    story.append(P(
        "Kako bi se odvojio efekat <i>omjera</i> od efekta <i>slučajnog izbora zemalja</i>, "
        "zadržan je 80/20, a mijenjan je samo <i>random_state</i>."
    ))
    story.append(P("Tabela 15.4: Test R² na 80/20 podjeli za četiri različita seeda", "caption"))
    story.append(table(
        ["random_state", "Linear Regression", "Random Forest", "XGBoost", "Najbolji model"],
        [
            ["0", "0.619", "0.635", "0.607", "Random Forest"],
            ["7", "0.741", "0.749", "0.737", "Random Forest"],
            ["42 (glavni)", "0.780", "0.729", "0.675", "Linear Regression"],
            ["123", "0.822", "0.839", "0.798", "Random Forest"],
        ],
        [1.25 * inch, 1.4 * inch, 1.25 * inch, 1.05 * inch, 1.35 * inch],
        left={0, 4},
    ))
    story.append(KeepTogether([
        fig(PLOTS / "split_seed_comparison.png", 5.8 * inch, 3.0 * inch),
        P(
            "Slika 15.2. Isti omjer 80/20, četiri različita slučajna rasporeda zemalja u testni skup.",
            "fig",
        ),
    ]))
    story.append(P(
        "Na istom 80/20 omjeru Test R² linearne regresije oscilira od <b>0.619 do 0.822</b>. "
        "Seed 42 (0.780) nalazi se u gornjoj polovini tog raspona, dakle nije ni najpovoljniji "
        "ni najnepovoljniji ishod. Dodatno, na tri od četiri seeda Random Forest nadmašuje "
        "linearnu regresiju. To nedvosmisleno pokazuje da se <b>rang modela ne smije "
        "objavljivati na temelju jednog holdout skupa</b>. Zato projekat rangira algoritme "
        "prema 5-fold unakrsnoj validaciji, gdje linearna regresija ostaje prva "
        "(CV R² = 0.779 ± 0.038)."
    ))

    story.append(P("15.3.4 Koja se podjela ispostavila kao najbolja?", "h"))
    story.append(P(
        "Potrebno je razdvojiti <b>najviši ostvareni Test R²</b> od <b>najispravnijeg "
        "evaluacijskog protokola</b>."
    ))
    story.append(KeepTogether([
        P("Tabela 15.5: Sažetak odluke o train/test podjeli", "caption"),
        table(
            ["Kriterij", "Ishod", "Tumačenje"],
            [
                ["Najviši Test R² (omjeri)", "70/30, LR, 0.850", "Sreća tog testnog skupa; nije razlog za izmjenu protokola."],
                ["Najviši Test R² (seedovi)", "80/20, seed 123, RF, 0.839", "Još jedan povoljan shuffle; rang modela nije stabilan."],
                ["Najgora podjela", "90/10, svi modeli padaju", "Test od 14 zemalja nije pouzdana evaluacija."],
                ["Najstabilnija ocjena", "5-fold CV, LR 0.779 ± 0.038", "Svaka zemlja jednom ulazi u testni fold."],
                ["Zadržani protokol", "80/20, random_state=42", "Standardna holdout podjela; Test R² usklađen s CV-om."],
            ],
            [1.7 * inch, 2.05 * inch, 2.55 * inch],
            left={0, 1, 2},
        ),
    ]))
    story.append(P(
        "<b>Zaključak poglavlja 15.3:</b> model se nije sistematski poboljšao prelaskom na "
        "70/30 ili 60/40, niti se poboljšao većim udjelom treninga (90/10). Promjene Test R² "
        "odražavaju prije svega sastav 14–55 zemalja u testnom skupu. Stoga se kao službena "
        "holdout podjela zadržava <b>80/20</b> (<i>random_state=42</i>), a konačno rangiranje "
        "modela ostaje na <b>5-fold unakrsnoj validaciji</b>. Birati omjer nakon uvida u testne "
        "metrike bilo bi narušavanje nepristrasnosti evaluacije."
    ))

    doc = SimpleDocTemplate(
        str(OUT_153),
        pagesize=letter,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=64,
        title="ML dokumentacija — umetak 15.3",
    )
    doc.build(story)
    print("wrote", OUT_153)


if __name__ == "__main__":
    build_84()
    build_9_intro()
    build_153()
