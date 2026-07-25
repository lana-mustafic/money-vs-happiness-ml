# Rezultati Projekta: Money vs Happiness

Sažetak nalaza iz World Happiness Report 2023 analize (Easterlin paradox + ML).

## Ključni Nalazi

### 1. Linearna Regresija je Najbolji Model

**5-fold cross-validation (mean ± std) + holdout test (20%):**

| Model | CV R² | CV MAE | Test R² | Test MAE | Test RMSE |
|-------|-------|--------|---------|----------|-----------|
| **Linear Regression** | **0.779 ± 0.038** | **0.389 ± 0.017** | **0.780** | **0.406** | **0.551** |
| XGBoost (tuned) | 0.757 ± 0.047 | 0.403 ± 0.035 | 0.751 | 0.422 | 0.587 |
| Random Forest (tuned) | 0.753 ± 0.068 | 0.405 ± 0.038 | 0.735 | 0.413 | 0.605 |

- **R² = 0.78** — model objašnjava ~78% varijabiliteta u Happiness score-u
- **MAE = 0.41** — prosječna greška ~0.41 poena na skali ~1.9–7.8
- Na ovom malom cross-section uzorku (137 zemalja) jednostavniji model nadmašuje RF i XGBoost
- GridSearch tuning poboljšao je RF/XGBoost u odnosu na fiksne hiperparametre

### 2. Najvažniji Prediktori Sreće

**Feature importance** (Random Forest / XGBoost) i **koeficijenti** linearne regresije:

| Rang | Faktor | RF importance | LR koeficijent |
|------|--------|---------------|----------------|
| 1 | **Social support** | 0.65 | **+3.86** |
| 2 | **Logged GDP per capita** | 0.19 | +0.21 |
| 3 | Healthy life expectancy | 0.07 | +0.02 |
| 4 | Freedom to make life choices | 0.05 | +2.37 |
| 5 | Perceptions of corruption | 0.02 | −0.79 |
| 6 | Generosity | 0.02 | +0.17 |

**Socijalna podrška** je najjači prediktor — GDP je važan, ali nije presudan.

### 3. Easterlin Paradox — Kontekst i Nalazi

Scatter plot `Logged GDP per capita` vs `Happiness score`:

- Postoji **jaka pozitivna veza** (korelacija ≈ 0.78; GDP samostalno R² ≈ 0.62)
- Sreća **nije samo funkcija bogatstva**: zemlje sa sličnim GDP-om često imaju različite Happiness score-ove
- Klasični Easterlin paradox više govori o *dugoročnom rastu unutar zemlje* nego o tome da bogate zemlje nisu sretne

> Zaključak: više novca pomaže, ali **nije dovoljno** — institucije i društvene veze nose veliki dio priče.

### 4. Klaster Analiza (K-Means)

Elbow + silhouette analiza (`kmeans_elbow.png`) preporučuje **k=2** (silhouette = 0.342):

| Klaster | Broj zemalja | Prosječna sreća |
|---------|--------------|-----------------|
| Lower happiness | 49 | ≈ 4.42 |
| Higher happiness | 88 | ≈ 6.16 |

Za k=3 (alternativa, manji silhouette) dobijaju se profile ≈ 4.3 / 5.8 / 7.0.

## Metodološka Poboljšanja

- **SimpleImputer** unutar `sklearn.Pipeline` — imputacija fitovana samo na train fold (nema leakage)
- **5-fold cross-validation** — pouzdanije metrike na malom uzorku
- **GridSearchCV** — hyperparameter tuning za Random Forest i XGBoost
- **Elbow + silhouette** — objektivan odabir broja klastera
- **Logging** umjesto print — strukturiran output u pipeline-u
- **Unit testovi** — `pytest tests/ -v`

## Vizuelizacije

Svi grafikoni su u `results/plots/`:

- `happiness_distribution.png`
- `correlation_heatmap.png`
- `gdp_vs_happiness.png`
- `model_comparison.png`
- `feature_importance.png`
- `kmeans_elbow.png`
- `kmeans_clusters.png`

Metrike: `results/model_metrics.csv`

## Interaktivni Dashboard

```bash
streamlit run dashboard.py
```

## Kako Reproducirati

```bash
python run_pipeline.py
pytest tests/ -v
# ili notebook:
jupyter notebook notebooks/analysis.ipynb
```
