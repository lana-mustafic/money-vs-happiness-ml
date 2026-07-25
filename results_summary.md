# Rezultati Projekta: Money vs Happiness

Sažetak nalaza iz World Happiness Report 2023 analize (Easterlin paradox + ML).

## Ključni Nalazi

### 1. Linearna Regresija je Najbolji Model

| Model | R² | MAE | RMSE |
|-------|-----|-----|------|
| **Linear Regression** | **0.780** | **0.406** | **0.551** |
| Random Forest | 0.729 | 0.424 | 0.612 |
| XGBoost | 0.686 | 0.466 | 0.659 |

- **R² = 0.780** — model objašnjava ~78% varijabiliteta u Happiness score-u
- **MAE = 0.406** — prosječna greška ~0.41 poena na skali ~1.9–7.8
- Na ovom malom cross-section uzorku (137 zemalja) jednostavniji model nadmašuje RF i XGBoost

### 2. Najvažniji Prediktori Sreće

**Feature importance** (Random Forest / XGBoost) i **koeficijenti** linearne regresije:

| Rang | Faktor | RF importance | LR koeficijent |
|------|--------|---------------|----------------|
| 1 | **Social support** | 0.62 | **+3.86** |
| 2 | **Logged GDP per capita** | 0.19 | +0.21 |
| 3 | Healthy life expectancy | 0.07 | +0.02 |
| 4 | Freedom to make life choices | 0.06 | +2.37 |
| 5 | Perceptions of corruption | 0.03 | −0.79 |
| 6 | Generosity | 0.03 | +0.17 |

**Socijalna podrška** je najjači prediktor — GDP je važan, ali nije presudan.

### 3. Easterlin Paradox — Kontekst i Nalazi

Scatter plot `Logged GDP per capita` vs `Happiness score`:

- Postoji **jaka pozitivna veza** (korelacija ≈ 0.78; GDP samostalno R² ≈ 0.62)
- Sreća **nije samo funkcija bogatstva**: zemlje sa sličnim GDP-om često imaju različite Happiness score-ove
- Klasični Easterlin paradox više govori o *dugoročnom rastu unutar zemlje* nego o tome da bogate zemlje nisu sretne
- U ovom *međunarodnom* presjeku 2023. bogatije zemlje su u prosjeku sretnije, ali **socijalna podrška** bolje razdvaja “srećne” od “manje srećnih” profila

> Zaključak za GitHub: više novca pomaže, ali **nije dovoljno** — institucije i društvene veze nose veliki dio priče.

### 4. Klaster Analiza (K-Means, k=3)

| Klaster | Broj zemalja | Prosječna sreća | Tipični primjeri |
|---------|--------------|-----------------|------------------|
| **Higher happiness** | 21 | ≈ 6.99 | Finland, Denmark, Iceland, Netherlands, Sweden |
| **Mid happiness** | 74 | ≈ 5.83 | Israel, USA, Czechia, Lithuania, Argentina |
| **Lower happiness** | 42 | ≈ 4.30 | Afghanistan, Lebanon, Sierra Leone, Benin, Bangladesh |

Zemlje se prirodno grupišu po socio-ekonomskom profilu, u skladu s nivoom sreće.

## Vizuelizacije

Svi grafikoni su u `results/plots/`:

- `happiness_distribution.png`
- `correlation_heatmap.png`
- `gdp_vs_happiness.png`
- `model_comparison.png`
- `feature_importance.png`
- `kmeans_clusters.png`

Metrike: `results/model_metrics.csv`

## Interaktivni Dashboard

```bash
streamlit run dashboard.py
```

## Kako Reproducirati

```bash
python run_pipeline.py
# ili notebook:
jupyter notebook notebooks/analysis.ipynb
```
