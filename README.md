# Money vs Happiness - Easterlin Paradox (ML)

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

Nedostajuće vrijednosti (npr. jedna u `Healthy life expectancy`) popunjavaju se srednjom vrijednošću kolone — u EDA/dashboard putu. Za modelovanje, imputacija ide kroz `sklearn` Pipeline fitovan **samo na train skupu** (bez data leakage).

## Struktura projekta

```text
money-vs-happiness-ml/
├── data/
│   └── WHR2023.csv
├── notebooks/
│   └── analysis.ipynb
├── src/
│   ├── data_loader.py      # učitavanje i priprema podataka
│   ├── eda.py              # eksploratorna analiza
│   ├── model.py            # treniranje, CV, klasteri
│   └── logging_config.py   # centralni logging
├── tests/
│   ├── test_data_loader.py
│   ├── test_eda.py
│   └── test_model.py
├── results/
│   ├── model_metrics.csv
│   ├── predictor_correlations.csv
│   ├── predictor_vif.csv
│   └── plots/
├── dashboard.py            # Streamlit interaktivni dashboard
├── run_pipeline.py         # glavni entry point
├── main.py                 # alias za run_pipeline
├── results_summary.md      # sažetak nalaza
├── LICENSE                 # MIT
├── README.md
└── requirements.txt
```

## Metodologija

1. **Priprema** (`data_loader.py`) — učitavanje CSV-a, odabir feature/target kolona. Imputacija odvojena za EDA (cijeli skup) i ML (Pipeline na train).
2. **EDA** (`eda.py`) — deskriptivna statistika, distribucija sreće, korelaciona matrica, **međusobne korelacije 6 faktora + VIF** (nijedna kolona nije izbačena), scatter GDP vs Happiness (linear + kvadratni fit).
3. **Modelovanje** (`model.py`) — `sklearn.Pipeline` sa `SimpleImputer` + regressor; 5-fold cross-validation; 80/20 holdout test; GridSearch za RF/XGBoost.
4. **Evaluacija** — R², MAE, RMSE (CV mean ± std + test set).
5. **Interpretacija** — feature importance (RF / XGBoost) + K-Means klasteri sa elbow/silhouette analizom.

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
python main.py
```

Pokreni testove:

```bash
pytest tests/ -v
```

Interaktivna analiza:

```bash
jupyter notebook notebooks/analysis.ipynb
```

Streamlit dashboard:

```bash
streamlit run dashboard.py
```

Sažetak nalaza: [`results_summary.md`](results_summary.md)

## Rezultati

Nakon pokretanja, rezultati se nalaze u:

- `results/model_metrics.csv` — CV i test metrike po modelu
- `results/predictor_correlations.csv` — međusobne Pearson korelacije 6 faktora
- `results/predictor_vif.csv` — VIF (provjera da li izbaciti kolonu)
- `results/plots/` — grafikoni (distribucija, heatmap, prediktori, GDP–sreća, model comparison, feature importance, K-Means elbow, klasteri)

Pokreni `python run_pipeline.py` da regenerišeš metrike i grafikone.

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

### Međusobne korelacije 6 faktora (da li izbaciti kolonu?)

Jedini par iznad |r| ≥ 0.80 je **Logged GDP per capita ↔ Healthy life expectancy** (r = 0.836). Ostali parovi su niži. VIF je svugdje ispod 5 (najviši: GDP 4.20). **Nijedna kolona nije izbačena** — faktori mjere različite koncepte, a stabla podnose ovu korelaciju.

### Feature importance (Random Forest / XGBoost)

Najvažnije karakteristike: **Social support**, zatim **Logged GDP per capita**, potom **Healthy life expectancy**.

### Easterlin paradox

Scatter GDP–Happiness pokazuje jaku pozitivnu vezu. Kvadratni fit na ovom *cross-section* uzorku ne pokazuje jasno “spljoštavanje” kod najbogatijih — paradox je historijski više o *unutar-zemaljskom* vremenskom trendu nego o međunarodnom poređenju.

## Ograničenja

- **Mali uzorak** (~137 zemalja) — visoka varijansa metrika; CV mean ± std je pouzdaniji od jednog split-a.
- **Cross-section, ne time series** — ne testira Easterlin paradox u pravom smislu (unutar-zemaljski trend kroz decenije).
- **Generosity** ima skoro nultu korelaciju (≈0.04) — marginalan prediktor u ovom skupu.
- **K-Means** je unsupervised EDA alat; broj klastera bira se elbow/silhouette analizom.
- WHR kolone tipa *Explained by: …* nisu korištene kao features (izbjegava se circular reasoning).

## Zaključak

Bogatstvo je važan, ali ne i jedini prediktor nacionalne sreće. **Socijalna podrška** je najjači signal u ovom modelu, ispred GDP-a. Linearna regresija često nadmašuje složenije modele na malom cross-section skupu — koristan nalaz o overfittingu.

## Licenca

MIT — vidi [`LICENSE`](LICENSE).

## Reference

- Helliwell, J. F., Layard, R., Sachs, J. D., et al. (Eds.). (2023). *World Happiness Report 2023*. SDSN.
- Easterlin, R. A. (1974). Does Economic Growth Improve the Human Lot?
