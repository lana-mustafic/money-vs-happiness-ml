"""Streamlit dashboard: Money vs Happiness (WHR 2023)."""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from data_loader import FEATURE_COLUMNS, TARGET_COLUMN, load_data  # noqa: E402

st.set_page_config(
    page_title="Money vs Happiness",
    page_icon="😊",
    layout="wide",
)


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data()


def main() -> None:
    st.title("Money vs Happiness: Globalna Analiza Sreće")
    st.caption("World Happiness Report 2023 — Easterlin paradox kroz ML")

    df = get_data()

    st.sidebar.header("Filteri")
    countries = sorted(df["Country name"].dropna().unique())
    country = st.sidebar.selectbox("Odaberi zemlju", countries, index=countries.index("Finland") if "Finland" in countries else 0)

    region_col = "Regional indicator" if "Regional indicator" in df.columns else None
    if region_col:
        regions = ["Sve"] + sorted(df[region_col].dropna().unique().tolist())
        region = st.sidebar.selectbox("Region", regions)
        plot_df = df if region == "Sve" else df[df[region_col] == region]
    else:
        plot_df = df

    row = df[df["Country name"] == country].iloc[0]

    st.subheader(f"Profil: {country}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Happiness Score", f"{row[TARGET_COLUMN]:.2f}")
    c2.metric("Logged GDP / capita", f"{row['Logged GDP per capita']:.2f}")
    c3.metric("Social support", f"{row['Social support']:.3f}")
    c4.metric("Healthy life expectancy", f"{row['Healthy life expectancy']:.1f}")

    with st.expander("Svi faktori za odabranu zemlju"):
        st.dataframe(
            pd.DataFrame(
                {
                    "Faktor": FEATURE_COLUMNS,
                    "Vrijednost": [row[c] for c in FEATURE_COLUMNS],
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

    st.subheader("Bogatstvo vs Sreća")
    fig = px.scatter(
        plot_df,
        x="Logged GDP per capita",
        y=TARGET_COLUMN,
        color="Social support",
        hover_name="Country name",
        hover_data=FEATURE_COLUMNS,
        color_continuous_scale="Tealgrn",
        title="Logged GDP per capita vs Happiness score",
    )
    # Highlight selected country
    sel = df[df["Country name"] == country]
    fig.add_scatter(
        x=sel["Logged GDP per capita"],
        y=sel[TARGET_COLUMN],
        mode="markers",
        marker=dict(size=16, color="#e63946", symbol="star", line=dict(width=1, color="white")),
        name=country,
        hovertext=country,
    )
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Top 10 najsretnijih")
        top = df.nlargest(10, TARGET_COLUMN)[["Country name", TARGET_COLUMN, "Logged GDP per capita", "Social support"]]
        st.dataframe(top, hide_index=True, use_container_width=True)
    with right:
        st.subheader("Bottom 10")
        bottom = df.nsmallest(10, TARGET_COLUMN)[["Country name", TARGET_COLUMN, "Logged GDP per capita", "Social support"]]
        st.dataframe(bottom, hide_index=True, use_container_width=True)

    st.subheader("Korelacije sa Happiness score")
    corr = df[[TARGET_COLUMN] + FEATURE_COLUMNS].corr()[TARGET_COLUMN].drop(TARGET_COLUMN).sort_values(ascending=False)
    corr_df = corr.reset_index()
    corr_df.columns = ["Faktor", "Korelacija"]
    fig_corr = px.bar(
        corr_df,
        x="Korelacija",
        y="Faktor",
        orientation="h",
        title="Pearson korelacija",
        color="Korelacija",
        color_continuous_scale="RdYlGn",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.info(
        "Socijalna podrška i GDP su najjači korelati sreće. "
        "Detaljniji ML rezultati: `results_summary.md` i `results/plots/`."
    )


if __name__ == "__main__":
    main()
