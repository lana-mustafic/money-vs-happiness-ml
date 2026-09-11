# Money vs Happiness

## Može li bogatstvo predvidjeti nacionalnu sreću?

**Akademski izvještaj o projektu mašinskog učenja**

**Projekat:** Money vs Happiness – Can Wealth Predict National Happiness?  
**Izvor podataka:** World Happiness Report 2023  
**Jezik implementacije:** Python  
**Datum dokumenta:** generisano na osnovu stanja repozitorija

---

## Sadržaj

1. [Uvod](#1-uvod)
2. [Definicija problema](#2-definicija-problema)
3. [Istraživačka pitanja i hipoteze](#3-istraživačka-pitanja-i-hipoteze)
4. [Ciljevi projekta](#4-ciljevi-projekta)
5. [Opis skupa podataka](#5-opis-skupa-podataka)
6. [Izvori podataka](#6-izvori-podataka)
7. [Učitavanje podataka](#7-učitavanje-podataka)
8. [Čišćenje i pretprocesiranje podataka](#8-čišćenje-i-pretprocesiranje-podataka)
9. [Integracija skupova podataka](#9-integracija-skupova-podataka)
10. [Eksploratorna analiza podataka (EDA)](#10-eksploratorna-analiza-podataka-eda)
11. [Inženjering karakteristika](#11-inženjering-karakteristika)
12. [Ciljna varijabla](#12-ciljna-varijabla)
13. [Podjela na trening i test skup](#13-podjela-na-trening-i-test-skup)
14. [Metodologija mašinskog učenja](#14-metodologija-mašinskog-učenja)
15. [Korišteni modeli](#15-korišteni-modeli)
16. [Treniranje modela](#16-treniranje-modela)
17. [Evaluacija modela](#17-evaluacija-modela)
18. [Poređenje modela](#18-poređenje-modela)
19. [Važnost karakteristika i interpretabilnost](#19-važnost-karakteristika-i-interpretabilnost)
20. [Analiza GDP vs sreća](#20-analiza-gdp-vs-sreća)
21. [Ekonomski vs socijalni faktori](#21-ekonomski-vs-socijalni-faktori)
22. [Analiza Bosne i Hercegovine](#22-analiza-bosne-i-hercegovine)
23. [Predikcije](#23-predikcije)
24. [Dashboard](#24-dashboard)
25. [Tehnička arhitektura](#25-tehnička-arhitektura)
26. [Reproducibilnost](#26-reproducibilnost)
27. [Ograničenja](#27-ograničenja)
28. [Etička i metodološka razmatranja](#28-etička-i-metodološka-razmatranja)
29. [Konačni rezultati](#29-konačni-rezultati)
30. [Diskusija](#30-diskusija)
31. [Budući rad](#31-budući-rad)
32. [Zaključak](#32-zaključak)
33. [Reference](#33-reference)

---

## 1. Uvod

Ovaj projekat istražuje odnos između nacionalnog bogatstva, socio-ekonomskih indikatora i subjektivne sreće na nivou država. Motivacija projekta leži u klasičnom ekonomskom i sociološkom pitanju poznatom kao **Easterlin paradox**, prema kojem povećanje materijalnog bogatstva nakon određene tačke ne mora donijeti proporcionalno povećanje subjektivne sreće.

Projekat ne ograničava analizu na jednostavno rangiranje zemalja po bogatstvu i sreći. Umjesto toga, primjenjuje metode mašinskog učenja kako bi se procijenilo u kojoj mjeri socio-ekonomski indikatori sadrže **prediktivnu informaciju** o nacionalnom *Happiness score*-u iz World Happiness Report 2023 (WHR 2023).

Implementacija obuhvata:

- učitavanje i priprema WHR 2023 podataka,
- eksploratornu analizu i vizualizacije,
- treniranje i evaluaciju tri regresiona modela,
- analizu važnosti karakteristika,
- nenadzirano klasterovanje zemalja (K-Means),
- interaktivni Streamlit dashboard,
- unit testove i centralizovani logging.

Svi numerički rezultati u ovom izvještaju preuzeti su iz stvarnih fajlova projekta (`results/model_metrics.csv`, Python modula i generisanih grafikona), osim gdje je eksplicitno naznačeno da nešto nije bilo moguće provjeriti iz repozitorija.

---

## 2. Definicija problema

**Problem:** Na osnovu socio-ekonomskih karakteristika zemalja, koliko precizno se može predvidjeti nacionalni *Happiness score*?

Projekat tretira problem kao **superviziranu regresiju**:

- **Ulaz (X):** šest numeričkih indikatora iz WHR 2023.
- **Izlaz (y):** *Happiness score*.

Problem nije formulisan kao klasifikacija niti kao vremenska serija. Radi se o **cross-section** analizi: jedan presjek podataka za više zemalja u jednoj godini (2023).

Važna distinkcija:


| Pojam                      | Značenje u ovom projektu                                          |
| -------------------------- | ----------------------------------------------------------------- |
| **Korelacija**             | Statistička povezanost između dvije varijable u presjeku podataka |
| **Predikcija**             | Procjena ciljne varijable na osnovu treniranog modela             |
| **Važnost karakteristike** | Relativni doprinos karakteristike unutar modela                   |
| **Kauzalnost**             | *Nije dokazana* ovim projektom                                    |


Modeli pokazuju **prediktivnu i asocijativnu** vezu, ali ne dokazuju da povećanje GDP-a *uzrokuje* veću sreću.

---

## 3. Istraživačka pitanja i hipoteze

### 3.1 Glavno istraživačko pitanje

**Može li nacionalno bogatstvo i socio-ekonomski profil zemlje predvidjeti nivo nacionalne sreće?**

### 3.2 Specifično pitanje

**Jesu li najbogatije zemlje nužno i najsretnije zemlje?**

### 3.3 Operacionalizacija

- Bogatstvo je reprezentovano kolonom `**Logged GDP per capita`** (logaritam GDP-a po glavi stanovnika), a ne sirovim GDP-om u USD.
- Sreća je reprezentovana kolonom `**Happiness score**` iz WHR 2023.

### 3.4 Hipoteze (analitičke, ne eksperimentalne)

1. Postoji pozitivna statistička veza između `Logged GDP per capita` i `Happiness score`.
2. Socijalni i institucionalni faktori (npr. socijalna podrška, sloboda, percepcija korupcije) doprinose predikciji sreće pored ekonomskog faktora.
3. Složeniji nelinearni modeli (Random Forest, XGBoost) mogu, ali ne moraju, nadmašiti linearnu regresiju na malom uzorku od ~137 zemalja.

Ove hipoteze se testiraju kroz EDA, korelacije, regresione modele i analizu važnosti karakteristika — ne kroz eksperimentalni dizajn.

---

## 4. Ciljevi projekta

Prema README-u i strukturi koda, projekat ima sljedeće ciljeve:

1. **EDA** — istražiti distribucije, korelacije i odnos bogatstva i sreće.
2. **Modelovanje** — trenirati i uporediti Linear Regression, Random Forest i XGBoost.
3. **Evaluacija** — izračunati R², MAE i RMSE (cross-validation + holdout test).
4. **Interpretacija** — analizirati važnost karakteristika i klasterizaciju zemalja.
5. **Komunikacija rezultata** — generisati grafikone, `results_summary.md` i Streamlit dashboard.
6. **Reproducibilnost** — omogućiti pokretanje cijelog pipeline-a kroz `run_pipeline.py` i unit testove.

---

## 5. Opis skupa podataka

### 5.1 Pregled korištenih i nekorištenih podataka


| Skup podataka               | Lokacija                           | Korišten u finalnom modelu? |
| --------------------------- | ---------------------------------- | --------------------------- |
| World Happiness Report 2023 | `data/WHR2023.csv`                 | **Da**                      |
| World Bank GDP per capita   | `data/raw/gdp_per_capita.csv.csv`  | **Ne**                      |
| World Bank unemployment     | `data/raw/unemployment.csv.csv`    | **Ne**                      |
| World Bank inflation        | `data/raw/inflation.csv.csv`       | **Ne**                      |
| World Bank population       | `data/raw/population.csv.csv`      | **Ne**                      |
| World Bank internet users   | `data/raw/internet_users.csv.csv`  | **Ne**                      |
| World Bank life expectancy  | `data/raw/life_expectancy.csv.csv` | **Ne**                      |
| Stariji happiness CSV       | `data/raw/world_happiness.csv.csv` | **Ne**                      |


**Zaključak audita:** Finalni model koristi **isključivo** `data/WHR2023.csv`. Fajlovi u `data/raw/` postoje u repozitoriju, ali **nijedan Python modul ih ne učitava niti spaja** (potvrđeno pretragom cijelog koda).

### 5.2 WHR2023.csv — osnovne karakteristike


| Stavka                      | Vrijednost                             |
| --------------------------- | -------------------------------------- |
| Broj redova (zemalja)       | **137**                                |
| Broj kolona (sirovi CSV)    | **21**                                 |
| Jedinica analize            | Država                                 |
| Godina                      | **2023** (World Happiness Report 2023) |
| Duplikati po `Country name` | **0**                                  |


### 5.3 Sirove kolone u WHR2023.csv

1. `Country name`
2. `iso alpha`
3. `Regional indicator`
4. `Happiness score`
5. `Standard error of ladder score`
6. `upperwhisker`
7. `lowerwhisker`
8. `Logged GDP per capita`
9. `Social support`
10. `Healthy life expectancy`
11. `Freedom to make life choices`
12. `Generosity`
13. `Perceptions of corruption`
14. `Ladder score in Dystopia`
15. `Explained by: Log GDP per capita`
16. `Explained by: Social support`
17. `Explained by: Healthy life expectancy`
18. `Explained by: Freedom to make life choices`
19. `Explained by: Generosity`
20. `Explained by: Perceptions of corruption`
21. `Dystopia + residual`

### 5.4 Kolone korištene u modelovanju


| Tip                               | Naziv kolone                                                                                                                                    |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Ciljna varijabla**              | `Happiness score`                                                                                                                               |
| **Karakteristike (6)**            | `Logged GDP per capita`, `Social support`, `Healthy life expectancy`, `Freedom to make life choices`, `Generosity`, `Perceptions of corruption` |
| **Metapodaci (ne ulaze u model)** | `Country name`, `Regional indicator`, `iso alpha`                                                                                               |


Kolone tipa `**Explained by: ...`** namjerno **nisu korištene** kao karakteristike (README navodi da bi to moglo dovesti do circular reasoning, jer su te kolone definisane kao dekompozicija happiness score-a).

### 5.5 Tipovi varijabli


| Varijabla            | Tip                  | Uloga                                 |
| -------------------- | -------------------- | ------------------------------------- |
| `Country name`       | Kategorijska (tekst) | Identifikacija zemlje                 |
| `Regional indicator` | Kategorijska (tekst) | Regionalna analiza / dashboard filter |
| `iso alpha`          | Kategorijska (tekst) | ISO kod zemlje                        |
| Sve modeling kolone  | Numeričke (float)    | Regresioni ulaz/izlaz                 |


### 5.6 Nedostajuće vrijednosti (sirovi podaci)


| Kolona                                  | Broj missing vrijednosti |
| --------------------------------------- | ------------------------ |
| `Healthy life expectancy`               | **1**                    |
| `Explained by: Healthy life expectancy` | **1**                    |
| `Dystopia + residual`                   | **1**                    |


Sve ostale kolone u sirovom skupu imaju potpune vrijednosti za svih 137 zemalja (prema auditu repozitorija).

### 5.7 Deskriptivna statistika (nakon EDA imputacije)

Statistike su izračunate putem `get_full_dataframe()` (mean imputacija za EDA):


| Varijabla                    | Mean   | Std   | Min    | Max    |
| ---------------------------- | ------ | ----- | ------ | ------ |
| Happiness score              | 5.540  | 1.140 | 1.859  | 7.804  |
| Logged GDP per capita        | 9.450  | 1.207 | 5.527  | 11.660 |
| Social support               | 0.799  | 0.129 | 0.341  | 0.983  |
| Healthy life expectancy      | 64.968 | 5.729 | 51.530 | 77.280 |
| Freedom to make life choices | 0.787  | 0.112 | 0.382  | 0.961  |
| Generosity                   | 0.022  | 0.142 | −0.254 | 0.531  |
| Perceptions of corruption    | 0.725  | 0.177 | 0.146  | 0.929  |


---

## 6. Izvori podataka

### 6.1 Primarni izvor — World Happiness Report 2023


| Stavka              | Opis                                                                          |
| ------------------- | ----------------------------------------------------------------------------- |
| **Organizacija**    | Sustainable Development Solutions Network (SDSN) / World Happiness Report tim |
| **Naziv**           | World Happiness Report 2023                                                   |
| **Godina**          | 2023                                                                          |
| **Fajl u projektu** | `data/WHR2023.csv`                                                            |


**Zašto je odabran:** WHR 2023 direktno sadrži i ciljnu varijablu (*Happiness score*) i objašnjavajuće faktore (GDP, socijalna podrška, zdravlje, sloboda, velikodušnost, korupcija) u jedinstvenom, međunarodno usporedivom formatu.

**Šta doprinosi projektu:** Omogućava regresiono modelovanje sreće na osnovu ekonomskih i socijalnih indikatora bez potrebe za ručnim spajanjem više izvora.

### 6.2 Potencijalni, ali nekorišteni izvori — World Bank (data/raw/)

U folderu `data/raw/` nalaze se CSV fajlovi u World Bank / World Development Indicators formatu, npr.:

- `gdp_per_capita.csv.csv` — GDP per capita (current US$), indikator `NY.GDP.PCAP.CD`
- `unemployment.csv.csv`
- `inflation.csv.csv`
- `population.csv.csv`
- `internet_users.csv.csv`
- `life_expectancy.csv.csv`

Ovi fajlovi sadrže metadata redove (npr. `"Data Source","World Development Indicators"`) i vremenske kolone po godinama (1960–2025). **Međutim, nijedan od ovih fajlova nije integrisan u finalni modeling pipeline.**

Također postoji `data/raw/world_happiness.csv.csv` sa starijim happiness kolonama (`Economy`, `Family`, `Health`, itd.), ali ni on **nije korišten** u finalnom kodu.

### 6.3 HDI (Human Development Index)

**HDI nije pronađen u repozitoriju** kao fajl koji se koristi u kodu. Nema `hdi.csv` niti UNDP integracije u Python modulima. Stoga se HDI **ne može analizirati** u ovom izvještaju.

### 6.4 Konceptualna razlika između varijabli (teorijski okvir)

Iako projekat koristi samo WHR varijable, korisno je objasniti razliku između koncepata koji se pominju u akademskom zadatku:


| Koncept         | Tipično značenje              | Korišten u projektu?                |
| --------------- | ----------------------------- | ----------------------------------- |
| GDP per capita  | Ekonomska produkcija po osobi | Da, kao **Logged GDP per capita**   |
| Unemployment    | Stopa nezaposlenosti          | Ne (postoji u raw/, nekorišten)     |
| Inflation       | Rast cijena                   | Ne (postoji u raw/, nekorišten)     |
| Population      | Broj stanovnika               | Ne (postoji u raw/, nekorišten)     |
| Internet usage  | Digitalna povezanost          | Ne (postoji u raw/, nekorišten)     |
| Life expectancy | Očekivani životni vijek       | Da, kao **Healthy life expectancy** |
| HDI             | Kompozitni indeks razvoja     | Ne                                  |
| Social support  | Percepcija društvene podrške  | Da                                  |
| Freedom         | Sloboda životnih izbora       | Da                                  |
| Generosity      | Velikodušnost                 | Da                                  |
| Corruption      | Percepcija korupcije          | Da                                  |
| Happiness score | Subjektivna evaluacija života | Da (cilj)                           |


---

## 7. Učitavanje podataka

### 7.1 Biblioteka i metoda

Podaci se učitavaju pomoću **pandas** biblioteke, funkcijom:

```python
pd.read_csv(data_path)
```

Implementacija u `src/data_loader.py`:

```python
def load_raw_data(path: Path | str | None = None) -> pd.DataFrame:
    data_path = Path(path) if path else DEFAULT_DATA_PATH
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {data_path}")
    return pd.read_csv(data_path)
```

### 7.2 Parametri učitavanja

Za WHR2023.csv korišten je standardni `read_csv()` **bez dodatnih parametara** (npr. bez eksplicitnog `sep`, `encoding` ili `skiprows`). CSV je u običnom comma-separated formatu sa header redom.

### 7.3 Putanje u projektu


| Konstanta           | Vrijednost                              |
| ------------------- | --------------------------------------- |
| `DEFAULT_DATA_PATH` | `PROJECT_ROOT / "data" / "WHR2023.csv"` |
| `PROJECT_ROOT`      | Roditeljski folder od `src/`            |


### 7.4 Dva puta učitavanja

Projekat razlikuje dva scenarija:


| Funkcija                             | Imputacija         | Namjena                                     |
| ------------------------------------ | ------------------ | ------------------------------------------- |
| `load_for_modeling()`                | **Bez** imputacije | ML pipeline (imputacija u sklearn Pipeline) |
| `load_and_prepare()` / `load_data()` | Mean imputacija    | EDA, dashboard, notebook                    |


Ova distinkcija je važna za metodološku ispravnost i sprečavanje data leakage-a.

---

## 8. Čišćenje i pretprocesiranje podataka

### 8.1 Pregled pipeline-a

```
WHR2023.csv (sirovo)
    → load_raw_data()
    → [EDA put] handle_missing_values() → prepare_features()
    → [ML put] prepare_features() → SimpleImputer u Pipeline (samo train)
```

### 8.2 Operacije koje JESU implementirane

#### 8.2.1 Odabir relevantnih kolona

**Problem:** Sirovi CSV sadrži 21 kolonu, od kojih mnoge nisu potrebne za modelovanje (npr. confidence intervali, explained-by dekompozicije).

**Rješenje:** Funkcija `prepare_features()` eksplicitno bira 6 karakteristika + cilj + metapodatke.

**Zašto:** Smanjuje dimenzionalnost i izbjegava circular reasoning sa `Explained by:` kolonama.

#### 8.2.2 Imputacija nedostajućih vrijednosti

**Problem:** Jedna zemlja ima missing vrijednost u `Healthy life expectancy` (i povezanim explained-by kolonama u sirovom CSV-u).

**Detekcija:** `df[col].isna().any()` u `handle_missing_values()` i unit test `test_modeling_path_preserves_raw_missing`.

**Rješenje (dva puta):**


| Put           | Metoda                                                             | Kada                            |
| ------------- | ------------------------------------------------------------------ | ------------------------------- |
| EDA/dashboard | Mean imputacija na cijelom skupu                                   | `handle_missing_values()`       |
| ML            | `SimpleImputer(strategy="mean")` u Pipeline, fit **samo na train** | `build_pipeline()` u `model.py` |


**Zašto mean imputacija:** Jednostavna i opravdana za jednu missing vrijednost u numeričkoj koloni; test `test_imputer_fits_on_train_only` potvrđuje da ML imputacija koristi srednju vrijednost **samo iz trening skupa**.

**Efekat:** Skup ostaje sa 137 redova; nijedna zemlja nije uklonjena.

#### 8.2.3 Alternativni naziv ciljne varijable

**Problem:** Neki happiness CSV-ovi koriste `Ladder score` umjesto `Happiness score`.

**Rješenje:** Ako `Happiness score` ne postoji, automatski rename iz `Ladder score` (test: `test_prepare_features_renames_ladder_score`).

**Napomena:** WHR2023.csv već koristi `Happiness score`; ova logika je za robusnost.

#### 8.2.4 Validacija kolona

Ako nedostaju obavezne kolone, `prepare_features()` baca `KeyError` sa listom nedostajućih kolona.

### 8.3 Operacije koje NISU implementirane

Sljedeće operacije **nisu pronađene** u kodu finalnog pipeline-a:

- uklanjanje metadata redova (nije potrebno za WHR CSV; bilo bi potrebno za World Bank raw fajlove, ali oni nisu korišteni),
- uklanjanje duplikata (nema duplikata),
- filtriranje regionalnih agregata World Bank-a,
- standardizacija imena zemalja,
- spajanje po country code,
- log-transformacija GDP-a (GDP je već u log-obliku u WHR),
- eksplicitno uklanjanje outliera.

---

## 9. Integracija skupova podataka

### 9.1 Status integracije

**Integracija više skupova podataka NIJE implementirana u finalnom projektu.**

Finalni modeling dataset potiče isključivo iz jednog fajla: `data/WHR2023.csv`.

Fajlovi u `data/raw/` (World Bank indikatori, stariji happiness CSV) postoje u repozitoriju, ali:

- nisu referencirani u Python kodu,
- nisu spajani (`merge`/`join`) sa WHR podacima,
- nisu uključeni u `FEATURE_COLUMNS`.

### 9.2 Zašto se ovo posebno navodi

Originalni akademski zadaci često uključuju spajanje World Bank i WHR podataka po `Country Code`. U **stvarnoj implementaciji ovog repozitorija** to nije urađeno. Svi zaključci o nezaposlenosti, inflaciji, internet korištenju, HDI-u ili sirovom GDP-u u USD **ne mogu se izvijestiti** jer te varijable nisu u finalnom modelu.

### 9.3 Finalni master dataset


| Stavka                  | Vrijednost                                  |
| ----------------------- | ------------------------------------------- |
| Izvor                   | WHR2023.csv                                 |
| Redovi                  | 137                                         |
| Kolone za modelovanje   | 6 karakteristika                            |
| Cilj                    | Happiness score                             |
| Metapodaci              | Country name, Regional indicator, iso alpha |
| Ključ za identifikaciju | `Country name` (tekstualni)                 |


---

## 10. Eksploratorna analiza podataka (EDA)

EDA je implementirana u `src/eda.py` i pokreće se kroz `run_eda()` iz `run_pipeline.py` i notebook `notebooks/analysis.ipynb`.

### 10.1 Deskriptivna statistika

Funkcija `basic_statistics()` poziva `df.describe()` i logira oblik skupa (137 zemalja × 10 kolona u EDA dataframe-u).

### 10.2 Distribucija Happiness score

**Grafikon:** `results/plots/happiness_distribution.png`

**Šta prikazuje:** Histogram sa KDE krivuljom distribucije `Happiness score`, uz vertikalne linije za mean i median.

**Zašto:** Procjena simetrije, raspona i centralne tendencije ciljne varijable prije modelovanja.

**Uočeni obrazac:** Happiness score je approximately normalno raspoređen sa mean ≈ 5.54 i std ≈ 1.14, u rasponu [1.86, 7.80].

**Figure 1 – Distribucija Happiness score (WHR 2023)**

### 10.3 Korelaciona matrica

**Grafikon:** `results/plots/correlation_heatmap.png`

**Metoda:** Pearson korelacija (`df[cols].corr()`) između cilja i 6 karakteristika.

**Interpretacija korelacije:**

- Vrijednost blizu **+1**: jaka pozitivna linearna povezanost
- Vrijednost blizu **−1**: jaka negativna linearna povezanost
- Vrijednost blizu **0**: slaba linearna povezanost

**Korelacije sa Happiness score (stvarne vrijednosti):**


| Varijabla                    | Pearson r  |
| ---------------------------- | ---------- |
| Social support               | **0.835**  |
| Logged GDP per capita        | **0.784**  |
| Healthy life expectancy      | **0.746**  |
| Freedom to make life choices | **0.663**  |
| Generosity                   | **0.044**  |
| Perceptions of corruption    | **−0.472** |


**Zaključak (asocijativan, ne kauzalan):** Socijalna podrška i GDP imaju najjaču statističku povezanost sa srećom u ovom presjeku. Generosity ima gotovo nultu korelaciju.

**Figure 2 – Korelaciona matrica happiness i socio-ekonomskih faktora**

### 10.3.1 Korelacije među 6 prediktora (provjera redundantnosti)

Cilj ove provjere nije predikcija sreće, nego odgovor na pitanje: **jesu li neki od 6 socio-ekonomskih faktora međusobno toliko slični da jedan treba izbaciti?**

**Grafikon:** `results/plots/predictor_correlation_heatmap.png`

**Tabele:** `results/predictor_correlations.csv`, `results/predictor_vif.csv`

**Metoda:** Pearson korelacija samo među `FEATURE_COLUMNS` (cilj isključen). Parovi sa **|r| ≥ 0.80** tretiraju se kao kandidati za redundantnost. Dodatno se računa **VIF** (Variance Inflation Factor): VIF_i = 1 / (1 − R²_i), gdje se faktor i regresira na preostalih 5. Uobičajeni prag za izbacivanje je **VIF > 10**.

**Svi parovi prediktora (sortirano po |r|):**


| Faktor 1                     | Faktor 2                     | Pearson r | \|r\| ≥ 0.80 |
| ---------------------------- | ---------------------------- | --------- | ------------ |
| Logged GDP per capita        | Healthy life expectancy      | **0.836** | da           |
| Logged GDP per capita        | Social support               | 0.738     | ne           |
| Social support               | Healthy life expectancy      | 0.725     | ne           |
| Social support               | Freedom to make life choices | 0.542     | ne           |
| Logged GDP per capita        | Freedom to make life choices | 0.451     | ne           |
| Logged GDP per capita        | Perceptions of corruption    | −0.437    | ne           |
| Healthy life expectancy      | Freedom to make life choices | 0.414     | ne           |
| Healthy life expectancy      | Perceptions of corruption    | −0.404    | ne           |
| Freedom to make life choices | Perceptions of corruption    | −0.384    | ne           |
| Social support               | Perceptions of corruption    | −0.272    | ne           |
| Freedom to make life choices | Generosity                   | 0.170     | ne           |
| Logged GDP per capita        | Generosity                   | −0.156    | ne           |
| Healthy life expectancy      | Generosity                   | −0.134    | ne           |
| Generosity                   | Perceptions of corruption    | −0.123    | ne           |
| Social support               | Generosity                   | 0.037     | ne           |


**VIF:**


| Faktor                       | VIF   | Interpretacija      |
| ---------------------------- | ----- | ------------------- |
| Logged GDP per capita        | 4.20  | umjereno, ispod 5   |
| Healthy life expectancy      | 3.73  | nisko–umjereno      |
| Social support               | 2.95  | nisko               |
| Freedom to make life choices | 1.59  | nisko               |
| Perceptions of corruption    | 1.43  | nisko               |
| Generosity                   | 1.19  | nisko               |


**Odluka: nijedna kolona nije izbačena.** Jedini par iznad praga je GDP ↔ Healthy life expectancy (r = 0.836). Oni statistički dijele sličnu informaciju (bogatije zemlje imaju duži zdrav život), ali mjere **različite koncepte**. VIF je svugdje **ispod 5**, daleko od praga 10. Stabla (RF, XGBoost) nisu osjetljiva na ovu vrstu korelacije kao linearna regresija. U LR se ipak vidi trag multikolinearnosti: Healthy life expectancy ima r = 0.746 sa srećom, ali koeficijent samo +0.020 — dio efekta preuzima GDP. To je razlog da se par zabilježi, ne da se kolona obriše.

**Figure 2b – Pearson matrica među 6 socio-ekonomskih prediktora**

### 10.4 Boxplotovi karakteristika

**Grafikon:** `results/plots/feature_boxplots.png`

**Šta prikazuje:** Boxplot distribucija svih 6 karakteristika.

**Zašto:** Uvid u raspon, mediane i potencijalne outlier-e po karakteristikama.

**Figure 3 – Boxplot distribucije karakteristika**

### 10.5 GDP vs Happiness (Easterlin vizualizacija)

**Grafikon:** `results/plots/gdp_vs_happiness.png`

**Šta prikazuje:**

- Scatter plot: `Logged GDP per capita` (x) vs `Happiness score` (y)
- Crvena linija: linearna regresija (OLS)
- Zelena isprekidana linija: kvadratni polinomijalni fit (stepen 2)
- Anotacije za neke ekstremne zemlje (top 3 po sreći i top 3 po GDP)

**Numerički nalazi iz koda:**


| Mjera                        | Vrijednost |
| ---------------------------- | ---------- |
| R² (samo GDP, linearno)      | **0.615**  |
| Kvadratni koeficijent a (x²) | **+0.113** |


**Interpretacija kvadratnog koeficijenta:**

- Kod `a > 0` kvadratna krivulja je **konveksna** (nagib raste sa GDP-om u ovom fit-u).
- To **ne pokazuje** klasično „spljoštavanje“ (diminishing returns) na desnom kraju raspodjele u ovom cross-section uzorku.
- README i `results_summary.md` eksplicitno navode da Easterlin paradox u pravom smislu odnosi više na **vremenske trendove unutar zemlje**, ne na međunarodno poređenje u jednoj godini.

**Figure 4 – Bogatstvo vs sreća: linearni i kvadratni fit**

### 10.6 Analiza outlier-a (iz podataka, ne vizuelno)

Zemlje sa **visokim GDP** (iznad mediana) ali **srećom ispod mediana** (5.684):


| Zemlja                    | Happiness | Logged GDP |
| ------------------------- | --------- | ---------- |
| Hong Kong S.A.R. of China | 5.308     | 10.966     |
| Türkiye                   | 4.614     | 10.307     |
| Russia                    | 5.661     | 10.210     |
| Bulgaria                  | 5.466     | 10.087     |
| Dominican Republic        | 5.569     | 9.811      |
| North Macedonia           | 5.254     | 9.703      |
| Georgia                   | 5.109     | 9.646      |
| Botswana                  | 3.435     | 9.629      |
| Bosnia and Herzegovina    | 5.633     | 9.616      |
| Armenia                   | 5.342     | 9.615      |


Zemlje sa **nižim GDP** (ispod mediana) ali **srećom iznad mediana**:


| Zemlja      | Happiness | Logged GDP |
| ----------- | --------- | ---------- |
| Kosovo      | 6.368     | 9.359      |
| Nicaragua   | 6.259     | 8.618      |
| Guatemala   | 6.150     | 9.116      |
| El Salvador | 6.122     | 9.089      |
| Honduras    | 6.023     | 8.635      |
| Uzbekistan  | 6.014     | 8.948      |
| Mongolia    | 5.840     | 9.372      |
| Kyrgyzstan  | 5.825     | 8.486      |
| Moldova     | 5.819     | 9.499      |
| Vietnam     | 5.763     | 9.287      |


---

## 11. Inženjering karakteristika

### 11.1 Šta je implementirano

Projekat koristi **minimalan** feature engineering:


| Transformacija            | Opis                                                    | Razlog                                                               |
| ------------------------- | ------------------------------------------------------- | -------------------------------------------------------------------- |
| Odabir 6 WHR kolona       | Ručni feature selection u `FEATURE_COLUMNS`             | WHR već pruža standardizovane objašnjavajuće faktore                 |
| Provjera redundantnosti   | Pearson parovi među 6 faktora + VIF (`eda.py`)          | Jedini par \|r\| ≥ 0.8 je GDP–HLE (0.836); VIF < 5; **nijedna kolona nije izbačena** |
| Log GDP već transformisan | `Logged GDP per capita` dolazi log-transformisan iz WHR | WHR koristi log GDP u svojoj metodologiji                            |
| StandardScaler            | Primijenjen **samo** u K-Means klasterovanju            | K-Means je osjetljiv na različite skale                              |
| SimpleImputer (mean)      | U ML Pipeline-u                                         | Rješava 1 missing u Healthy life expectancy bez ručnog brisanja reda |


### 11.2 Šta NIJE implementirano

- Normalizacija/standardizacija za regresione modele
- One-hot encoding kategorijalnih varijabli (regioni nisu uključeni u model)
- Ručno kreirani ratio indikatori
- PCA ili automatski feature selection algoritmi (ručna provjera redundantnosti putem Pearson |r| i VIF **jeste** urađena; nijedna kolona nije izbačena)
- SHAP, permutation importance

### 11.3 Data leakage i skaliranje

Regresioni modeli **ne koriste** StandardScaler. Imputacija je u `Pipeline` i fit-uje se **samo na trening podatke** unutar svakog CV fold-a i finalnog treninga. Unit test `test_imputer_fits_on_train_only` to eksplicitno provjerava.

K-Means klasterovanje koristi imputaciju na cijelom skupu i StandardScaler — što je prihvatljivo jer je **nenadzirana EDA analiza**, a ne evaluacija generalizacije modela.

---

## 12. Ciljna varijabla


| Stavka                 | Vrijednost                                        |
| ---------------------- | ------------------------------------------------- |
| **Naziv**              | `Happiness score`                                 |
| **Alternativni naziv** | `Ladder score` (automatski mapiranje ako postoji) |
| **Tip**                | Kontinuirana numerička varijabla                  |
| **Skala**              | Tipično ~1.9 do ~7.8 u ovom skupu                 |
| **Izvor mjerenja**     | Gallup World Poll, agregirano u WHR 2023          |
| **Tip zadatka**        | **Regresija**                                     |


**Zašto regresija:** Cilj je realan broj na intervalu, a metrike (MAE, RMSE, R²) su standardne za regresione modele.

**Priprema za modelovanje:** Cilj se izdvaja kao pandas `Series` u `prepare_features()` bez dodatne transformacije (nema log-transformacije happiness score-a).

---

## 13. Podjela na trening i test skup


| Parametar       | Vrijednost                                 |
| --------------- | ------------------------------------------ |
| Funkcija        | `sklearn.model_selection.train_test_split` |
| Train %         | **80%**                                    |
| Test %          | **20%**                                    |
| `test_size`     | 0.2                                        |
| `random_state`  | **42**                                     |
| Trening uzoraka | **109**                                    |
| Test uzoraka    | **28**                                     |
| Stratifikacija  | **Nije korištena** (regresija)             |


### 13.1 Cross-validation

Pored holdout testa, projekat koristi **5-fold cross-validation** (`KFold`, `n_splits=5`, `shuffle=True`, `random_state=42`) za procjenu R², MAE i RMSE na cijelom skupu.

GridSearchCV za Random Forest i XGBoost koristi **3-fold CV** unutar trening skupa.

### 13.2 Zašto je ovaj pristup odabran

Sa samo 137 zemalja, jedan slučajni 80/20 split može dati varijabilne rezultate. Zato projekat izvještava **CV mean ± std** kao pouzdaniju mjeru, uz holdout test za dodatnu provjeru.

### 13.3 Sprečavanje data leakage

- Imputacija je unutar `sklearn.Pipeline`, fitovana unutar svakog CV fold-a na trening fold-u.
- Test skup se ne koristi za imputaciju, tuning niti treniranje finalnih procjena prije evaluacije.

---

## 14. Metodologija mašinskog učenja

### 14.1 Opšti tok

```
WHR2023.csv
  → load_for_modeling()
  → train_test_split (80/20, random_state=42)
  → za svaki model:
      → 5-fold CV (Pipeline + SimpleImputer + model)
      → GridSearchCV na train (RF, XGBoost; LR bez tuninga)
      → evaluacija na holdout testu
  → feature importance (RF, XGBoost)
  → K-Means klasterovanje (StandardScaler + KMeans)
  → čuvanje metrika i grafikona
```

### 14.2 Pipeline arhitektura

```python
Pipeline([
    ("imputer", SimpleImputer(strategy="mean")),
    ("model", estimator),
])
```

### 14.3 Evaluirane metrike


| Metrika | Korištena?   | Interpretacija                                 |
| ------- | ------------ | ---------------------------------------------- |
| R²      | Da           | Udio objašnjene varijanse; više = bolje        |
| MAE     | Da           | Prosječna apsolutna greška; niže = bolje       |
| RMSE    | Da           | Korijen srednje kvadratne greške; niže = bolje |
| MSE     | Ne (izravno) | RMSE je korijen MSE                            |
| MAPE    | Ne           | Nije implementirano                            |


---

## 15. Korišteni modeli

Projekat trenira **tačno tri** regresiona modela. Sljedeći modeli **nisu** implementirani: Decision Tree Regressor (samostalan), Gradient Boosting (sklearn), SVR, neuralne mreže.

---

### 15.1 Linear Regression (Linearna regresija)


| Stavka             | Opis                                                                              |
| ------------------ | --------------------------------------------------------------------------------- |
| **Tip**            | Linearni regresioni model (OLS)                                                   |
| **Biblioteka**     | `sklearn.linear_model.LinearRegression`                                           |
| **Zašto odabran**  | Baseline model; interpretabilan; dobar za male uzorke                             |
| **Pretpostavke**   | Linearna veza između X i y; greške ne moraju biti savršeno normalne za predikciju |
| **Hiperparametri** | Default (bez GridSearch)                                                          |
| **Skaliranje**     | Nije potrebno                                                                     |
| **Prednosti**      | Interpretabilni koeficijenti; mali rizik overfittinga                             |
| **Ograničenja**    | Ne modeluje nelinearnosti i interakcije eksplicitno                               |


---

### 15.2 Random Forest Regressor


| Stavka                                                     | Opis                                                           |
| ---------------------------------------------------------- | -------------------------------------------------------------- |
| **Tip**                                                    | Ensemble bagging sa decision tree regresorima                  |
| **Biblioteka**                                             | `sklearn.ensemble.RandomForestRegressor`                       |
| **Početni hiperparametri**                                 | `n_estimators=200`, `max_depth=8`, `random_state=42`           |
| **GridSearch prostor**                                     | `n_estimators`: [100, 200]; `max_depth`: [4, 8, None]          |
| **Odabrani hiperparametri (najbolji na train GridSearch)** | `n_estimators=200`, `max_depth=4`                              |
| **Skaliranje**                                             | Nije potrebno                                                  |
| **Prednosti**                                              | Hvata nelinearnosti i interakcije                              |
| **Ograničenja**                                            | Na malom uzorku može overfitovati; manje interpretabilan od LR |


---

### 15.3 XGBoost Regressor


| Stavka                                                     | Opis                                                                                             |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Tip**                                                    | Gradient boosted trees                                                                           |
| **Biblioteka**                                             | `xgboost.XGBRegressor`                                                                           |
| **Početni hiperparametri**                                 | `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.9`, `colsample_bytree=0.9` |
| **GridSearch prostor**                                     | `n_estimators`: [100, 200]; `max_depth`: [3, 4, 6]; `learning_rate`: [0.05, 0.1]                 |
| **Odabrani hiperparametri (najbolji na train GridSearch)** | `n_estimators=100`, `max_depth=3`, `learning_rate=0.05`                                          |
| **Skaliranje**                                             | Nije potrebno                                                                                    |
| **Prednosti**                                              | Snažan na tabularnim podacima                                                                    |
| **Ograničenja**                                            | Na 137 uzoraka može biti manje stabilan od jednostavnijih modela                                 |


---

## 16. Treniranje modela

Treniranje se odvija u `train_and_evaluate()` (`src/model.py`):

1. Učitavanje X, y preko `load_for_modeling()`.
2. Split 109/28.
3. Za svaki model:
  - 5-fold CV na cijelom X, y (sa imputacijom u pipeline-u).
  - GridSearchCV na train (RF, XGBoost) ili direktno fit (LR).
  - Evaluacija na test skupu.
4. Čuvanje metrika u `results/model_metrics.csv`.
5. Generisanje grafikona.

**Napomena:** Trenirani modeli **nisu sačuvani** kao `.pkl` fajlovi u repozitoriju. Nema foldera sa perzistentnim model artifact-ima.

---

## 17. Evaluacija modela

### 17.1 Objašnjenje metrika


| Metrika  | Šta mjeri                                         | Bolje |
| -------- | ------------------------------------------------- | ----- |
| **R²**   | Proporcija varijanse objašnjene modelom           | Više  |
| **MAE**  | Prosječna |stvarna − predviđena|                  | Niže  |
| **RMSE** | √(prosječni kvadrat greške); kažnjava veće greške | Niže  |


### 17.2 Stvarni rezultati — 5-fold CV (mean ± std)

Izvor: `results/model_metrics.csv`


| Model                 | R² (mean) | R² (std) | MAE (mean) | MAE (std) | RMSE (mean) | RMSE (std) |
| --------------------- | --------- | -------- | ---------- | --------- | ----------- | ---------- |
| **Linear Regression** | **0.779** | 0.038    | **0.389**  | 0.017     | **0.514**   | 0.035      |
| Random Forest         | 0.753     | 0.068    | 0.405      | 0.038     | 0.540       | 0.059      |
| XGBoost               | 0.750     | 0.043    | 0.415      | 0.035     | 0.548       | 0.052      |


### 17.3 Stvarni rezultati — holdout test (20%)


| Model                 | Test R²   | Test MAE  | Test RMSE | Rang (Test R²) |
| --------------------- | --------- | --------- | --------- | -------------- |
| **Linear Regression** | **0.780** | **0.406** | **0.551** | **1**          |
| XGBoost               | 0.751     | 0.422     | 0.587     | 2              |
| Random Forest         | 0.735     | 0.413     | 0.605     | 3              |


**Figure 5 – Poređenje modela (CV metrike)** — `results/plots/model_comparison.png`

---

## 18. Poređenje modela

### 18.1 Najbolji model

**Linear Regression** je najbolji po R² i MAE, i na CV i na test skupu.

### 18.2 Zašto je LR najbolji (na ovom uzorku)

Mogući razlozi, u skladu sa stvarnim rezultatima:

1. **Mali uzorak (137 zemalja)** — složeniji modeli imaju više slobode da uče šum.
2. **Relativno linearna struktura** — GDP i socijalni faktori imaju jake linearne korelacije sa srećom.
3. **Overfitting** — Random Forest i XGBoost imaju veći RMSE i niži test R² od LR.
4. **Visoka std RF R² (0.068)** — RF je manje stabilan across folds.

### 18.3 Da li je razlika substantijalna?

Razlika u test R² između LR (0.780) i XGBoost (0.751) je ~~0.03, što je umjerena na ovom uzorku. Razlika u MAE (~~0.02 poena) je mala u odnosu na skalu happiness score-a.

### 18.4 Preporučeni finalni model

**Linear Regression** — najbolji generalizacioni performans, najjednostavniji, najinterpretabilniji.

---

## 19. Važnost karakteristika i interpretabilnost

### 19.1 Metode korištene u projektu


| Metoda                             | Model             | Implementirano?                 |
| ---------------------------------- | ----------------- | ------------------------------- |
| Koeficijenti LR                    | Linear Regression | Da                              |
| Apsolutne vrijednosti koeficijenta | Linear Regression | Da (u `get_feature_importance`) |
| Impurity-based importance          | Random Forest     | Da                              |
| Feature importance                 | XGBoost           | Da                              |
| SHAP                               | —                 | **Ne**                          |
| Permutation importance             | —                 | **Ne**                          |


### 19.2 Random Forest — važnost karakteristika


| Karakteristika               | Importance |
| ---------------------------- | ---------- |
| Social support               | **0.646**  |
| Logged GDP per capita        | 0.193      |
| Healthy life expectancy      | 0.066      |
| Freedom to make life choices | 0.050      |
| Perceptions of corruption    | 0.023      |
| Generosity                   | 0.021      |


### 19.3 XGBoost — važnost karakteristika


| Karakteristika               | Importance |
| ---------------------------- | ---------- |
| Social support               | **0.443**  |
| Healthy life expectancy      | 0.238      |
| Logged GDP per capita        | 0.156      |
| Perceptions of corruption    | 0.068      |
| Freedom to make life choices | 0.055      |
| Generosity                   | 0.041      |


### 19.4 Linear Regression — koeficijenti (nakon Pipeline imputacije)


| Karakteristika               | Koeficijent |
| ---------------------------- | ----------- |
| Intercept                    | −2.551      |
| Social support               | **+3.124**  |
| Freedom to make life choices | +2.084      |
| Logged GDP per capita        | +0.333      |
| Generosity                   | +0.298      |
| Healthy life expectancy      | +0.020      |
| Perceptions of corruption    | −0.671      |


**Napomena o interpretaciji:** Koeficijenti pokazuju **smjer i relativni doprinos** u linearnom modelu, uz fiksne ostale varijable. To **nije dokaz** da povećanje socijalne podrške *uzrokuje* višu sreću.

**Figure 6 – Važnost karakteristika (RF i XGBoost)** — `results/plots/feature_importance.png`

---

## 20. Analiza GDP vs sreća

### 20.1 Korelacija

Pearson r (**Logged GDP per capita**, **Happiness score**) = **0.784**

### 20.2 Jednostavna linearna regresija (samo GDP)

R² = **0.615** — GDP samostalno objašnjava ~61.5% varijanse sreće u ovom presjeku.

### 20.3 Scatter plot i nelinearnost

Kvadratni fit ima koeficijent a = **+0.113** (konveksnost), što **ne potvrđava** spljoštavanje odnosa na visokom nivou GDP-a u ovom uzorku.

### 20.4 Odgovor: Jesu li najbogatije zemlje nužno najsretnije?

**Ne nužno**, ali su u prosjeku sretnije.

Dokazi iz projekta:

- Top 10 po GDP i top 10 po sreći imaju **preklapanje od 5 zemalja**: Denmark, Luxembourg, Netherlands, Norway, Switzerland.
- Zemlje koje su bogate ali manje sretne od mediana uključuju Hong Kong, Türkiye, Russia, Bulgaria, Botswana, BiH, itd.
- Zemlje sa umerenim GDP-om ali srećom iznad mediana uključuju Kosovo, Nicaragua, Guatemala, Uzbekistan, Vietnam, itd.

**Zaključak:** Bogatstvo je jak, ali ne i jedini faktor. Visok GDP ne garantuje visoku sreću za svaku zemlju.

---

## 21. Ekonomski vs socijalni faktori

### 21.1 Dostupne kategorije u finalnom modelu

**Ekonomski (u WHR smislu):**

- `Logged GDP per capita`

**Socijalni / institucionalni / zdravstveni:**

- `Social support`
- `Healthy life expectancy`
- `Freedom to make life choices`
- `Generosity`
- `Perceptions of corruption`

**Nisu dostupni u finalnom modelu:** unemployment, inflation, population, internet usage, HDI.

### 21.2 Poređenje prediktivne korisnosti


| Dokaz              | Ekonomski (GDP)     | Socijalni faktori                   |
| ------------------ | ------------------- | ----------------------------------- |
| Najjača korelacija | r = 0.784 (2. rang) | r = 0.835 (Social support, 1. rang) |
| RF importance      | 0.193 (2. rang)     | 0.646 (Social support, 1. rang)     |
| LR koeficijent     | +0.333              | +3.124 (Social support)             |


**Zaključak:** U ovom projektu **socijalni faktori** (posebno socijalna podrška) pokazuju jaču prediktivnu i statističku povezanost sa srećom nego GDP, iako je GDP i dalje značajan.

---

## 22. Analiza Bosne i Hercegovine

### 22.1 Podaci za BiH (WHR 2023, stvarne vrijednosti)


| Varijabla                    | Vrijednost                 |
| ---------------------------- | -------------------------- |
| Country name                 | Bosnia and Herzegovina     |
| Regional indicator           | Central and Eastern Europe |
| iso alpha                    | BIH                        |
| **Happiness score**          | **5.633**                  |
| Logged GDP per capita        | 9.616                      |
| Social support               | 0.880                      |
| Healthy life expectancy      | 67.275                     |
| Freedom to make life choices | 0.746                      |
| Generosity                   | 0.206                      |
| Perceptions of corruption    | 0.918                      |


### 22.2 Varijable koje NISU dostupne za BiH u projektu

Sljedeće **ne mogu se izvijestiti** jer nisu u finalnom skupu:

- unemployment
- inflation
- internet usage
- HDI
- sirovi GDP u USD (World Bank)

### 22.3 Poređenje


| Referentna grupa                    | Prosječna sreća |
| ----------------------------------- | --------------- |
| Globalni prosjek (137 zemalja)      | 5.540           |
| **BiH**                             | **5.633**       |
| Central and Eastern Europe (regija) | 6.134           |


BiH je:

- **blago iznad** globalnog prosjeka sreće,
- **ispod** regionalnog prosjeka za Central and Eastern Europe,
- **5. od dna** u svojoj regiji (14. rang po sreći u regiji od zemalja u tom regionu).

Regionalni top 5: Czechia (6.845), Lithuania (6.763), Slovenia (6.650), Romania (6.589), Slovakia (6.469).

Regionalni bottom 5 uključuju BiH (5.633), Bulgaria (5.466), Albania (5.277), North Macedonia (5.254).

### 22.4 Profil BiH

BiH ima **relativno visok GDP** (9.616, iznad mediana 9.567) i **visoku socijalnu podršku** (0.880), ali sreća (5.633) je blizu mediana (5.684) i ispod regionalnog prosjeka. BiH se pojavljuje i u listi zemalja sa visokim GDP-om ali srećom ispod mediana — što ilustruje da bogatstvo samo ne objašnjava sreću.

---

## 23. Predikcije

### 23.1 Da li projekat generiše predikcije?

Da — u kodu (`evaluate_model()`, `pipe.predict()`), ali **nema posebnog CSV fajla sa predikcijama za sve zemlje** u `results/`.

### 23.2 Primjer: BiH (Linear Regression, treniran na cijelom pipeline-u)


| Stavka                 | Vrijednost |
| ---------------------- | ---------- |
| Stvarna sreća          | 5.633      |
| Predviđena sreća       | 5.743      |
| Greška (actual − pred) | −0.110     |


Model blago **precjenjuje** sreću BiH za ~0.11 poena — greška je mala u odnosu na test MAE (0.406).

### 23.3 Tačnost predikcija

Sa test MAE ≈ 0.41 i R² ≈ 0.78, model je **umjereno dobar** za akademsku analizu cross-section podataka, ali nije dovoljno precizan za visokorizične individualne ili policymakerske odluke bez dodatne validacije.

---

## 24. Dashboard

### 24.1 Tehnologija


| Komponenta    | Tehnologija                       |
| ------------- | --------------------------------- |
| Framework     | **Streamlit** (`dashboard.py`)    |
| Vizualizacija | **Plotly Express**                |
| Podaci        | `load_data()` iz `data_loader.py` |


### 24.2 Svrha

Interaktivni pregled WHR 2023 podataka za korisnika koji želi istražiti odnos bogatstva i sreće po zemljama i regionima.

### 24.3 Integracija modela

Dashboard **NE integriše** trenirane ML modele za predikciju. Prikazuje **stvarne podatke** iz CSV-a (sa EDA mean imputacijom). Nema prikaza predviđenog happiness score-a iz modela.

### 24.4 Korisničko iskustvo

1. **Sidebar:** odabir zemlje; filter po regionu (`Regional indicator`).
2. **Metrike:** Happiness Score, Logged GDP, Social support, Healthy life expectancy za odabranu zemlju.
3. **Expander:** tabela svih 6 faktora za odabranu zemlju.
4. **Scatter plot:** GDP vs Happiness, boja = Social support; odabrana zemlja označena zvijedom.
5. **Tabele:** Top 10 i Bottom 10 zemalja po sreći.
6. **Bar chart:** Pearson korelacije faktora sa happiness score-om.
7. **Heatmap + tabela:** Pearson korelacije među 6 prediktora (provjera da li izbaciti kolonu).

### 24.5 Pokretanje

```bash
streamlit run dashboard.py
```

---

## 25. Tehnička arhitektura

### 25.1 Struktura repozitorija

```
money-vs-happiness-ml/
├── data/
│   ├── WHR2023.csv              # primarni skup (korišten)
│   └── raw/                     # World Bank i stari CSV (NE korišteni u ML)
├── src/
│   ├── data_loader.py           # učitavanje i priprema
│   ├── eda.py                   # eksploratorna analiza
│   ├── model.py                 # treniranje, CV, klasteri
│   └── logging_config.py        # logging
├── notebooks/
│   └── analysis.ipynb           # interaktivna analiza
├── tests/
│   ├── test_data_loader.py
│   ├── test_eda.py
│   └── test_model.py
├── results/
│   ├── model_metrics.csv
│   ├── predictor_correlations.csv
│   ├── predictor_vif.csv
│   └── plots/                   # generisani grafikoni
├── dashboard.py                 # Streamlit app
├── run_pipeline.py              # glavni entry point
├── main.py                      # alias za run_pipeline
├── results_summary.md           # sažetak nalaza
├── README.md
├── requirements.txt
└── LICENSE                      # MIT
```

**Napomena:** Folderi `models/`, `figures/`, `reports/` **nisu** dio trenutne strukture projekta.

### 25.2 Tok podataka (tekstualni dijagram)

```
[WHR2023.csv]
      │
      ▼
[data_loader.py] ──► load_raw_data() / load_for_modeling() / load_data()
      │
      ├──► [eda.py] ──► statistike + PNG grafikoni
      │                      │
      │                      ├──► predictor_correlations.csv, predictor_vif.csv
      │                      └──► correlation / predictor heatmaps
      │
      ├──► [model.py] ──► Pipeline → CV → GridSearch → test evaluacija
      │                      │
      │                      ├──► model_metrics.csv
      │                      ├──► model_comparison.png
      │                      ├──► feature_importance.png
      │                      └──► kmeans_elbow.png, kmeans_clusters.png
      │
      └──► [dashboard.py] ──► Streamlit interaktivni prikaz
```

### 25.3 Uloga ključnih modula


| Modul               | Uloga                                               |
| ------------------- | --------------------------------------------------- |
| `data_loader.py`    | Učitavanje CSV, odabir kolona, imputacija (EDA put) |
| `eda.py`            | Statistike, korelacije, redundantnost prediktora, scatter, boxplotovi |
| `model.py`          | Treniranje, evaluacija, feature importance, K-Means |
| `logging_config.py` | Strukturirani log output                            |
| `run_pipeline.py`   | Orkestracija EDA + ML                               |
| `dashboard.py`      | Korisnički interfejs za istraživanje podataka       |


---

## 26. Reproducibilnost

### 26.1 Zahtjevi

Fajl `requirements.txt` (pinovane verzije):

```
pandas==2.2.3
numpy==2.1.3
matplotlib==3.9.2
seaborn==0.13.2
scikit-learn==1.5.2
xgboost==2.1.2
jupyter==1.1.1
notebook==7.2.2
streamlit==1.40.1
plotly==5.24.1
pytest==8.3.3
```

**Napomena:** Tačna verzija Pythona nije eksplicitno navedena u repozitoriju. Razvojno okruženje je testirano sa Python 3.12.

### 26.2 Instalacija i pokretanje

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run_pipeline.py     # regeneriše metrike i grafikone
pytest tests/ -v           # unit testovi
streamlit run dashboard.py # dashboard
jupyter notebook notebooks/analysis.ipynb
```

### 26.3 Redoslijed izvršavanja

1. `data/WHR2023.csv` mora postojati.
2. `run_pipeline.py` pokreće `run_eda()` pa `run_full_pipeline()`.
3. Rezultati se pojavljuju u `results/` i `results/plots/`.

### 26.4 Testovi


| Test fajl             | Šta provjerava                                           |
| --------------------- | -------------------------------------------------------- |
| `test_data_loader.py` | Učitavanje, kolone, imputacija, rename Ladder score      |
| `test_eda.py`         | Parovi prediktora, prag \|r\| ≥ 0.8, odluka da se ne izbacuje kolona |
| `test_model.py`       | Pipeline struktura, CV, train/evaluate, imputer na train |


---

## 27. Ograničenja

1. **Mali uzorak** — 137 zemalja; visoka varijabilnost metrika.
2. **Cross-section** — jedna godina; nema panela kroz vrijeme.
3. **Easterlin paradox** — nije pravilno testiran bez vremenske dimenzije.
4. **Nekorišteni World Bank podaci** — raw fajlovi postoje, ali nisu integrisani.
5. **Jedna missing vrijednost** — imputirana mean strategijom.
6. **Generosity** — gotovo nema korelacije (r ≈ 0.04).
7. **Nema SHAP/permutation importance** — interpretacija ograničena na RF/XGB importance i LR koeficijente.
8. **Nema perzistentno sačuvanih modela** — reprodukcija zahtijeva ponovno treniranje.
9. **Dashboard bez ML predikcija** — samo EDA prikaz.
10. **Korelacija ≠ kauzalnost** — fundamentalno metodološko ograničenje.
11. **Multikolinearnost GDP–HLE** (r = 0.836) — zabilježena, ali kolona nije izbačena; može smanjiti stabilnost LR koeficijenata za Healthy life expectancy.

---

## 28. Etička i metodološka razmatranja

1. **Numerička mjera sreće** reducira složen fenomen na skalar; kulturne razlike u konotaciji „sreće“ mogu uticati na WHR.
2. **Međunarodno poređenje** može stvoriti pojednostavljene rang-liste koje ignorišu lokalni kontekst.
3. **Feature importance i koeficijenti** ne smiju se interpretirati kao dokaz političkih intervencija bez eksperimentalnog dizajna.
4. **Ranking zemalja** po modelu može imati socio-političke implikacije; rezultati su analitički alat, ne apsolutna istina.
5. **Percepcija korupcije** i **socijalna podrška** su subjektivne mjere iz anketa — podložne measurement error-u.

---

## 29. Konačni rezultati

### 29.1 Najbolji model

**Linear Regression** — Test R² = **0.780**, Test MAE = **0.406**, Test RMSE = **0.551**.

### 29.2 Koliko precizno se sreća može predvidjeti?

Model objašnjava ~**78%** varijanse na test skupu; prosječna greška ~**0.41** poena na skali happiness score-a.

### 29.3 Da li je GDP jak prediktor?

**Da**, ali ne i najjači. Korelacija r = 0.784; RF importance = 0.193 (2. rang); LR koeficijent = +0.333.

### 29.4 Jesu li najbogatije zemlje nužno najsretnije?

**Ne.** Postoji jaka pozitivna veza, ali 5 od 10 najbogatijih nije u top 10 po sreći. Postoje bogate zemlje sa niskom srećom i umereno siromašne sa relativno visokom srećom.

### 29.5 Najvažnije karakteristike

1. **Social support** (RF: 0.646; XGB: 0.443; LR: +3.124)
2. **Logged GDP per capita**
3. **Healthy life expectancy**

### 29.6 Šta je iznenađujuće (na osnovu rezultata)

- Linearna regresija nadmašuje Random Forest i XGBoost na ovom uzorku.
- Generosity ima gotovo nultu korelaciju sa srećom.
- Kvadratni GDP fit ne pokazuje spljoštavanje (a > 0).
- K-Means preporučuje k = 2, ne k = 3.

### 29.7 Ključni zaključci


| #   | Nalaz                                                             |
| --- | ----------------------------------------------------------------- |
| 1   | Socio-ekonomski profil objašnjava ~78% varijanse sreće (LR, test) |
| 2   | Socijalna podrška je jači prediktor od GDP-a                      |
| 3   | Bogatstvo pomaže, ali ne garantuje sreću                          |
| 4   | Easterlin paradox nije potvrđen u cross-section smislu            |
| 5   | Jednostavan model je najbolji na malom uzorku                     |


---

## 30. Diskusija

Projekat uspješno demonstrira primjenu regresionog ML-a na WHR 2023 podacima. Metodološki, projekat je **napredovao** u odnosu na osnovnu verziju kroz:

- Pipeline sa SimpleImputer (bez leakage),
- 5-fold cross-validation,
- GridSearchCV za tree modele,
- unit testove i logging.

Međutim, **integracija World Bank podataka nije realizovana**, iako raw fajlovi postoje. To znači da pitanja o nezaposlenosti, inflaciji, internet pristupu i HDI-u ostaju otvorena za budući rad.

Odnos GDP–sreća je jak u međunarodnom presjeku 2023. To **ne proturječi** Easterlin paradoxu, jer paradox opisuje longitudinalne obrasce unutar zemalja, dok ovaj projekat analizira cross-section između zemalja.

Socijalna podrška dominira u korelaciji i feature importance, što sugerira da subjektivna sreća na nacionalnom nivou zavisi od **društvenog konteksta**, ne samo od materijalnog bogatstva — ali ova tvrdnja ostaje **asocijativna**, ne kauzalna.

---

## 31. Budući rad

Sljedeće stavke **nisu implementirane**, ali predstavljaju realne smjerove unapređenja:


| Prioritet | Predlog                                                               |
| --------- | --------------------------------------------------------------------- |
| Visok     | Integracija World Bank podataka iz `data/raw/` sa WHR po country code |
| Visok     | Panel analiza (više godina WHR) za pravilniji test Easterlin paradoxa |
| Srednji   | SHAP ili permutation importance za interpretaciju                     |
| Srednji   | Cross-validation sa hyperparameter tuning u jedinstvenom nested CV    |
| Srednji   | Perzistencija modela (`.pkl`) i predikcije u dashboardu               |
| Nizak     | Uključivanje regional dummy varijabli                                 |
| Nizak     | Kausalne metode (instrumental variables, quasi-experiments)           |


---

## 32. Zaključak

Projekat **Money vs Happiness** istražuje da li socio-ekonomski indikatori mogu predvidjeti nacionalni *Happiness score* koristeći World Happiness Report 2023 podatke za **137 zemalja**.

**Metodologija** obuhvata EDA, tri regresiona modela (Linear Regression, Random Forest, XGBoost), 5-fold cross-validation, holdout test (80/20), feature importance analizu i K-Means klasterovanje.

**Glavni nalaz:** **Linearna regresija** je najbolji model (Test R² = 0.780, MAE = 0.406). **Socijalna podrška** je najjači prediktor, ispred **Logged GDP per capita**. Bogatstvo je važno, ali **najbogatije zemlje nisu nužno najsretnije**.

**Ograničenja** uključuju mali uzorak, cross-section dizajn, nekorištene World Bank podatke i nemogućnost kauzalnih zaključaka.

Projekat pokazuje da mašinsko učenje može kvantitativno opisati odnos bogatstva i sreće, ali da **društveni faktori** nose jednako važnu, ako ne i veću, prediktivnu ulogu — što potvrđuje da sreća nije reducibilna isključivo na ekonomski rast.

---

## 33. Reference

1. Helliwell, J. F., Layard, R., Sachs, J. D., Aknin, L. B., De Neve, J.-E., & Wang, S. (Eds.). (2023). *World Happiness Report 2023* (11th ed.). Sustainable Development Solutions Network. — primarni izvor podataka (`data/WHR2023.csv`).
2. Easterlin, R. A. (1974). Does Economic Growth Improve the Human Lot? — teorijski okvir (Easterlin paradox) referenciran u README-u.
3. scikit-learn developers. *scikit-learn* documentation — LinearRegression, RandomForestRegressor, SimpleImputer, Pipeline, GridSearchCV, KFold, cross_validate, KMeans, StandardScaler. Korištene verzije prema `requirements.txt` (scikit-learn==1.5.2).
4. Chen, T., & Guestrin, C. XGBoost — korišten preko `xgboost==2.1.2`.
5. Streamlit Inc. *Streamlit* documentation — korišten za `dashboard.py` (streamlit==1.40.1).
6. Plotly Technologies Inc. *Plotly* — korišten za interaktivne grafikone u dashboardu (plotly==5.24.1).
7. World Bank. *World Development Indicators* — potencijalni izvor za fajlove u `data/raw/` (npr. GDP per capita, NY.GDP.PCAP.CD). **Napomena:** ovi fajlovi postoje lokalno, ali nisu korišteni u finalnom modelu.

---

## Pregled generisanih figura


| Figura   | Fajl                         | Opis                                         |
| -------- | ---------------------------- | -------------------------------------------- |
| Figure 1 | `happiness_distribution.png`         | Distribucija Happiness score                          |
| Figure 2 | `correlation_heatmap.png`            | Pearson korelaciona matrica (cilj + 6 faktora)        |
| Figure 2b | `predictor_correlation_heatmap.png` | Pearson matrica među 6 prediktora (redundantnost)    |
| Figure 3 | `feature_boxplots.png`               | Boxplotovi karakteristika                             |
| Figure 4 | `gdp_vs_happiness.png`       | GDP vs sreća sa linearnim i kvadratnim fitom |
| Figure 5 | `model_comparison.png`       | Poređenje modela (CV metrike)                |
| Figure 6 | `feature_importance.png`     | Važnost karakteristika (RF, XGBoost)         |
| Figure 7 | `kmeans_elbow.png`           | Elbow i silhouette analiza za K-Means        |
| Figure 8 | `kmeans_clusters.png`        | Klasteri zemalja na GDP–Happiness scatteru   |


---

## Pregled ključnih tabela (sa stvarnim vrijednostima)

### Tabela A — Pregled skupa podataka


| Stavka           | Vrijednost                  |
| ---------------- | --------------------------- |
| Izvor            | WHR 2023                    |
| Zemlje           | 137                         |
| Karakteristike   | 6                           |
| Cilj             | Happiness score             |
| Missing (sirovo) | 1 (Healthy life expectancy) |


### Tabela B — Opis karakteristika


| Karakteristika               | Tip       | Uloga                  |
| ---------------------------- | --------- | ---------------------- |
| Logged GDP per capita        | Numerička | Ekonomski faktor       |
| Social support               | Numerička | Socijalni faktor       |
| Healthy life expectancy      | Numerička | Zdravstveni faktor     |
| Freedom to make life choices | Numerička | Institucionalni faktor |
| Generosity                   | Numerička | Socijalni faktor       |
| Perceptions of corruption    | Numerička | Institucionalni faktor |


### Tabela C — Poređenje modela (test + CV)

Vidi Sekcije 17.2 i 17.3.

### Tabela D — Feature importance (Random Forest)

Vidi Sekciju 19.2.

### Tabela E — Međusobne korelacije prediktora

Vidi Sekciju 10.3.1. Jedini par sa |r| ≥ 0.80 je Logged GDP per capita ↔ Healthy life expectancy (r = 0.836). Nijedna kolona nije izbačena (svi VIF < 5).

---

*Kraj izvještaja. Svi numerički podaci verificirani iz repozitorija i `results/model_metrics.csv`.*