# Money vs Happiness — Easterlin Paradox (ML)

Istraživanje odnosa bogatstva i sreće kroz mašinsko učenje na podacima **World Happiness Report 2023**.

## Uvod

**Easterlin paradox** sugerira da, nakon određenog nivoa bogatstva, dodatni rast GDP-a ne donosi proporcionalno povećanje subjektivne sreće. Ovaj projekat:

1. radi EDA nad WHR 2023 podacima,
2. trenira modele za predviđanje *Happiness score*,
3. interpretira koje karakteristike najviše utiču na sreću,
4. vizuelno testira da li se veza GDP ↔ sreća "spljoštava" kod najbogatijih zemalja.

## Skup podataka

| Stavka | Opis |
|--------|------|
| Izvor | World Happiness Report 2023 |
| Fajl | `data/WHR2023.csv` |
| Jedinica | država (≈137 zemalja) |
| Cilj | `Happiness score` |
| Features | `Logged GDP per capita`, `Social support`, `Healthy life expectancy`, `Freedom to make life choices`, `Generosity`, `Perceptions of corruption` |

Nedostajuće vrijednosti (npr. jedna u `Healthy life expectancy`) popunjavaju se srednjom vrijednošću kolone.

## Struktura projekta

```text
money-vs-happiness-ml/
├── data/
│   └── WHR2023.csv
├── notebooks/
│   └── analysis.ipynb
├── src/
│   ├── data_loader.py
│   ├── eda.py
│   └── model.py
├── results/
│   ├── model_metrics.csv
│   └── plots/
├── README.md
└── requirements.txt
```

## Metodologija

1. **Priprema** (`data_loader.py`) — učitavanje CSV-a, imputacija, odabir feature/target kolona.
2. **EDA** (`eda.py`) — deskriptivna statistika, distribucija sreće, korelaciona matrica, scatter GDP vs Happiness (linear + kvadratni fit).
3. **Modelovanje** (`model.py`) — 80/20 train–test split; modeli:
   - Linear Regression (baseline)
   - Random Forest Regressor
   - XGBoost Regressor
4. **Evaluacija** — R², MAE, RMSE na testnom skupu.
5. **Interpretacija** — feature importance (RF / XGBoost) + opcioni K-Means klasteri zemalja.

## Instalacija i pokretanje

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

Pokreni cijeli pipeline iz korijena projekta:

```bash
python run_pipeline.py
# ili:
cd src
python data_loader.py
python eda.py
python model.py
```

Ili otvori interaktivnu analizu:

```bash
jupyter notebook notebooks/analysis.ipynb
```

## Rezultati

Nakon pokretanja, rezultati se nalaze u:

- `results/model_metrics.csv` — uporedba modela
- `results/plots/` — svi grafikoni (distribucija, heatmap, GDP–sreća, feature importance, klasteri, …)

### Korelacije sa Happiness score (WHR 2023)

| Faktor | Korelacija |
|--------|------------|
| Social support | **0.83** |
| Logged GDP per capita | **0.78** |
| Healthy life expectancy | **0.75** |
| Freedom to make life choices | 0.66 |
| Perceptions of corruption | −0.47 |
| Generosity | 0.04 |

GDP samostalno objašnjava ≈61% varijanse sreće (R² ≈ 0.615).

### Performanse modela (test set, 20%)

| Model | R2 | MAE | RMSE |
|-------|-----|-----|------|
| Linear Regression | **0.780** | **0.406** | **0.551** |
| Random Forest | 0.729 | 0.424 | 0.612 |
| XGBoost | 0.686 | 0.466 | 0.659 |

Na ovom (malom) cross-section skupu linearna regresija je najbolja; XGBoost ne nadmašuje jednostavnije modele — koristan nalaz za analizu overfittinga / kompleksnosti.

### Feature importance (Random Forest / XGBoost)

Najvažnije karakteristike: **Social support**, zatim **Logged GDP per capita**, potom **Healthy life expectancy**.

### Easterlin paradox

Scatter GDP–Happiness pokazuje jaku pozitivnu vezu. Kvadratni fit na ovom *cross-section* uzorku ne pokazuje jasno “spljoštavanje” kod najbogatijih — paradox je historijski više o *unutar-zemaljskom* vremenskom trendu nego o međunarodnom poređenju. Ipak, sreća nije samo funkcija GDP-a: socijalna podrška ima i veću korelaciju i veću feature importance.

### K-Means (3 klastera)

Zemlje se prirodno grupišu u profile niže / srednje / više sreće (prosjeci ≈ 4.3 / 5.8 / 7.0), u skladu sa socio-ekonomskim faktorima.

## Zaključak

Bogatstvo je važan, ali ne i jedini prediktor nacionalne sreće. **Socijalna podrška** je najjači signal u ovom modelu, ispred GDP-a. Linearna veza GDP–sreća i dalje drži na međunarodnom nivou 2023., dok Easterlin paradox ostaje relevantan kao hipoteza o *dugoročnom* rastu unutar bogatih društava, a ne kao jednostavno “bogate zemlje nisu sretne”.

## Reference

- Helliwell, J. F., Layard, R., Sachs, J. D., et al. (Eds.). (2023). *World Happiness Report 2023*. SDSN.
- Easterlin, R. A. (1974). Does Economic Growth Improve the Human Lot?
