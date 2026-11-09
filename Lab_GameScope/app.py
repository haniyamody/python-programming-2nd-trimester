from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="GameScope | Video Game Sales",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

BG = "#11161D"
PANEL = "#19212B"
PANEL_2 = "#202A36"
TEXT = "#E8EEF5"
MUTED = "#A1AFBE"
PURPLE = "#42B8B0"
PURPLE_2 = "#258C87"
LIME = "#8DD6CB"
PINK = "#85A9D6"
GRID = "#344150"

st.markdown(
    f"""
    <style>
    :root {{ color-scheme: dark; }}
    .stApp {{ background: {BG}; color: {TEXT}; }}
    [data-testid="stHeader"] {{ background: {BG}; }}
    [data-testid="stSidebar"] {{ background: #151C25; border-right: 1px solid #2C3947; }}
    h1,h2,h3 {{ color: {TEXT} !important; letter-spacing: -0.02em; }}
    p, label, [data-testid="stCaptionContainer"] {{ color: {MUTED}; }}
    .block-container {{ max-width: 1450px; padding-top: 1.6rem; padding-bottom: 2rem; }}
    [data-testid="stMetric"] {{ background: {PANEL}; border: 1px solid #2C3947; border-radius: 10px; padding: 15px 17px; min-height: 100px; }}
    [data-testid="stMetricLabel"] {{ color: {MUTED} !important; font-size: .82rem; }}
    [data-testid="stMetricValue"] {{ color: {TEXT} !important; font-weight: 700; }}
    [data-testid="stMetricDelta"] {{ color: {LIME} !important; }}
    [data-testid="stTabs"] button {{ color: {MUTED}; font-weight: 500; }}
    [data-testid="stTabs"] button[aria-selected="true"] {{ color: {TEXT}; border-bottom-color: {PURPLE}; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{ background: {PANEL}; border: 1px solid #2C3947; border-radius: 11px; padding: .9rem 1rem; }}
    [data-testid="stExpander"] {{ background: {PANEL}; border: 1px solid #2C3947; border-radius: 9px; }}
    .stButton button {{ border-radius: 7px; }}
    hr {{ border-color: #2C3947; }}
    .eyebrow {{ color: {PURPLE}; font-size: .7rem; letter-spacing: .11em; font-weight: 700; text-transform: uppercase; }}
    .hero {{ background: {PANEL}; border: 1px solid #2C3947; border-left: 3px solid {PURPLE}; border-radius: 10px; padding: 19px 23px; margin: 0 0 19px 0; }}
    .hero-title {{ color: {TEXT}; font-size: 1.8rem; line-height: 1.15; letter-spacing: -.025em; font-weight: 700; margin: 6px 0; }}
    .hero-copy {{ color: {MUTED}; font-size: .9rem; }}
    .mini-label {{ color: {MUTED}; font-size: .72rem; letter-spacing:.08em; }}
    .mini-value {{ color: {TEXT}; font-size: 1.15rem; font-weight: 650; }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {{ background:#1B2530; border-color:#344351; border-radius:7px; }}
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {{ background:#1B2530; border-color:#344351; border-radius:7px; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data["Publisher"] = data["Publisher"].fillna("Unknown")
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    return data


data_path = Path(__file__).with_name("vgsales.csv")
if not data_path.exists():
    st.error("Couldn't find vgsales.csv beside app.py. Put both files in the same folder.")
    st.stop()
df = load_data(str(data_path))


def draw_chart(kind, data, title, xlabel, ylabel, color=PURPLE, second=None):
    fig, ax = plt.subplots(figsize=(8.2, 3.3))
    fig.patch.set_facecolor(PANEL)
    ax.set_facecolor(PANEL)
    if kind == "bar":
        bars = ax.bar(data.index.astype(str), data.values, color=color, width=.68, zorder=3)
        ax.bar_label(bars, fmt="%.1f", padding=3, color=TEXT, fontsize=8)
    elif kind == "line":
        ax.plot(data.index, data.values, color=color, linewidth=2.5, marker="o", markersize=3.5, zorder=4)
        ax.fill_between(data.index, data.values, color=color, alpha=.13)
    elif kind == "scatter":
        ax.scatter(data[0], data[1], c=color, alpha=.43, s=20, edgecolors="none")
        max_value = max(float(data[0].max()), float(data[1].max())) if len(data[0]) else 0
        ax.plot([0, max_value], [0, max_value], color=LIME, alpha=.55, linestyle="--", linewidth=1)
    ax.set_title(title, loc="left", color=TEXT, fontsize=12, fontweight="bold", pad=13)
    ax.set_xlabel(xlabel, color=MUTED, fontsize=9, labelpad=8)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=9, labelpad=8)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="y", color=GRID, alpha=.75, linestyle=(0, (3, 4)), linewidth=.7, zorder=0)
    ax.spines[:].set_visible(False)
    ax.margins(x=.06, y=.16)
    fig.tight_layout()
    return fig


# Sidebar filters: single selections keep the controls quiet and avoid removable chips.
st.sidebar.markdown(f'<div style="font-size:1.35rem;font-weight:700;color:{TEXT};">GameScope</div><div class="eyebrow" style="margin-top:3px">Video game sales</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("#### Filters")
genres = sorted(df["Genre"].dropna().unique())
platforms = sorted(df["Platform"].dropna().unique())
years = df["Year"].dropna().astype(int)
genre_options = ["All genres"] + genres
platform_options = ["All platforms"] + platforms
selected_genre = st.sidebar.selectbox("Genre", genre_options, key="filter_genre")
selected_platform = st.sidebar.selectbox("Platform", platform_options, key="filter_platform")
year_range = st.sidebar.slider("Release year", int(years.min()), int(years.max()), (int(years.min()), int(years.max())), key="filter_year")
search = st.sidebar.text_input("Game title", placeholder="Search titles", key="filter_search")
include_unknown = st.sidebar.checkbox("Include unknown release years", value=True, key="filter_unknown")
if st.sidebar.button("Reset filters", use_container_width=True):
    for key in ["filter_genre", "filter_platform", "filter_year", "filter_search", "filter_unknown"]:
        st.session_state.pop(key, None)
    st.rerun()
st.sidebar.markdown("---")
st.sidebar.caption("Sales are in millions of units.")

filtered = df.copy()
if selected_genre != "All genres":
    filtered = filtered[filtered["Genre"] == selected_genre]
if selected_platform != "All platforms":
    filtered = filtered[filtered["Platform"] == selected_platform]
year_mask = filtered["Year"].between(*year_range)
if include_unknown:
    year_mask |= filtered["Year"].isna()
filtered = filtered[year_mask]
if search.strip():
    filtered = filtered[filtered["Name"].str.contains(search.strip(), case=False, na=False)]

total_games = len(filtered)
global_sales = filtered["Global_Sales"].sum()
average_sales = filtered["Global_Sales"].mean() if total_games else 0
median_sales = filtered["Global_Sales"].median() if total_games else 0
genre_count = filtered["Genre"].nunique()

st.markdown("## Video game sales")
st.caption(f"Historical sales by title, platform, genre and region · {total_games:,} records in the current selection")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Games", f"{total_games:,}", f"of {len(df):,} total")
k2.metric("Global sales", f"{global_sales:,.1f}M", "million units")
k3.metric("Mean sales per game", f"{average_sales:.2f}M", f"median {median_sales:.2f}M")
k4.metric("Genres", f"{genre_count}", f"{filtered['Platform'].nunique()} platforms")

st.write("")
overview_tab, analysis_tab, explorer_tab, data_tab = st.tabs(["◈  Overview", "⌁  Market analysis", "⌕  Game explorer", "▦  Dataset details"])

if filtered.empty:
    st.warning("No games match these filters. Widen the year range or select more genres and platforms.")
else:
    with overview_tab:
        left, right = st.columns([1.55, 1], gap="large")
        with left:
            with st.container(border=True):
                st.markdown("##### Sales by region")
                regions = pd.Series({"North America": filtered.NA_Sales.sum(), "Europe": filtered.EU_Sales.sum(), "Japan": filtered.JP_Sales.sum(), "Other": filtered.Other_Sales.sum()}).sort_values(ascending=False)
                # Use per-bar colors to distinguish each regional market.
                fig, ax = plt.subplots(figsize=(8.2, 3.3)); fig.patch.set_facecolor(PANEL); ax.set_facecolor(PANEL)
                bars = ax.bar(regions.index, regions.values, color=[PURPLE, PINK, LIME, "#F2B65D"][:len(regions)], width=.68, zorder=3)
                ax.bar_label(bars, fmt="%.0f", padding=3, color=TEXT, fontsize=8)
                ax.set_title("Where games sell", loc="left", color=TEXT, fontsize=12, fontweight="bold", pad=13)
                ax.set_ylabel("Sales (millions)", color=MUTED, fontsize=9); ax.tick_params(colors=MUTED, labelsize=8)
                ax.grid(axis="y", color=GRID, alpha=.75, linestyle=(0,(3,4)), linewidth=.7, zorder=0); ax.spines[:].set_visible(False); fig.tight_layout()
                st.pyplot(fig, use_container_width=True); plt.close(fig)
                st.caption("North America, Europe, Japan and Other market sales summed across the filtered titles.")
        with right:
            with st.container(border=True):
                st.markdown("##### Best-selling title")
                top = filtered.loc[filtered["Global_Sales"].idxmax()]
                st.markdown(f"**{top['Name']}**")
                st.caption(f"{top['Platform']} · {top['Genre']} · {int(top['Year']) if pd.notna(top['Year']) else 'Year unknown'}")
                st.metric("Global sales", f"{top['Global_Sales']:.2f}M")
                st.markdown("---")
                gs = filtered.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)
                lead = gs.index[0]
                st.markdown("**Highest-selling genre**")
                st.write(f"{lead} · {gs.iloc[0]:,.1f}M")
        with st.container(border=True):
            st.markdown("##### Genre leaderboard")
            genre_sales = filtered.groupby("Genre")["Global_Sales"].sum().sort_values().tail(6)
            st.bar_chart(genre_sales, horizontal=True, color=PURPLE, height=240)
            st.caption("Top genres by total global sales. The ranking updates with the sidebar filters.")

    with analysis_tab:
        st.markdown("### Market patterns")
        st.caption("Compare categories, track yearly totals and inspect regional relationships.")
        c1, c2 = st.columns(2, gap="large")
        with c1, st.container(border=True):
            st.markdown("##### Genre sales")
            genre_sales = filtered.groupby("Genre")["Global_Sales"].sum().sort_values(ascending=False)
            st.pyplot(draw_chart("bar", genre_sales, "Global sales by genre", "Genre", "Sales (millions)"), use_container_width=True)
            plt.close("all")
            st.caption(f"{genre_sales.index[0]} leads this view with {genre_sales.iloc[0]:,.1f} million sales.")
        with c2, st.container(border=True):
            st.markdown("##### Sales over time")
            annual = filtered.dropna(subset=["Year"]).groupby("Year")["Global_Sales"].sum().sort_index()
            if not annual.empty:
                st.pyplot(draw_chart("line", annual, "Global sales by release year", "Release year", "Sales (millions)", PINK), use_container_width=True)
                plt.close("all")
                peak_year = int(annual.idxmax())
                st.caption(f"Peak year in this selection: {peak_year}, at {annual.max():,.1f} million sales.")
            else:
                st.info("No dated titles match the selected filters.")
        with st.container(border=True):
            st.markdown("##### Regional relationship")
            sample = filtered.sample(min(len(filtered), 2500), random_state=42)
            scatter = (sample["NA_Sales"], sample["EU_Sales"])
            st.pyplot(draw_chart("scatter", scatter, "North America vs Europe", "North American sales (millions)", "European sales (millions)", LIME), use_container_width=True)
            plt.close("all")
            st.caption("Each point represents one game. The dashed diagonal marks equal sales in both regions; games farther above it sold more in Europe.")
        with st.expander("How to read these charts"):
            st.write("Sales are reported in millions of units. Category charts show summed sales, yearly totals include titles with a known release year, and the scatter plot compares each title's North American and European sales.")

    with explorer_tab:
        st.markdown("### Find a title")
        st.caption("Search and sort the filtered catalog, then inspect the title-level sales breakdown.")
        a, b, c = st.columns([1.3, 1, 1])
        sort_by = a.selectbox("Sort by", ["Global sales (high to low)", "Global sales (low to high)", "Game title", "Release year"])
        rows = b.select_slider("Rows to show", options=[10, 20, 50, 100], value=20)
        selected_genre = c.selectbox("Spotlight genre", ["All genres"] + sorted(filtered["Genre"].unique()))
        display = filtered.copy()
        if selected_genre != "All genres":
            display = display[display["Genre"] == selected_genre]
        sort_cols = {"Global sales (high to low)": ("Global_Sales", False), "Global sales (low to high)": ("Global_Sales", True), "Game title": ("Name", True), "Release year": ("Year", True)}
        col, ascending = sort_cols[sort_by]
        display = display.sort_values(col, ascending=ascending, na_position="last")
        table = display[["Rank", "Name", "Platform", "Year", "Genre", "Publisher", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]].head(rows)
        st.dataframe(table, use_container_width=True, hide_index=True, height=470, column_config={"Global_Sales": st.column_config.NumberColumn("Global · M", format="%.2f"), "NA_Sales": st.column_config.NumberColumn("North America · M", format="%.2f"), "EU_Sales": st.column_config.NumberColumn("Europe · M", format="%.2f"), "JP_Sales": st.column_config.NumberColumn("Japan · M", format="%.2f"), "Other_Sales": st.column_config.NumberColumn("Other · M", format="%.2f"), "Year": st.column_config.NumberColumn("Year", format="%.0f")})
        st.caption(f"Showing {min(rows, len(display)):,} of {len(display):,} matching records.")
        with st.expander("Category counts in the current selection"):
            counts = filtered.groupby("Genre").size().sort_values(ascending=False).rename("Titles")
            st.dataframe(counts, use_container_width=True)

    with data_tab:
        st.markdown("### Dataset profile")
        d1, d2, d3 = st.columns(3)
        d1.metric("Source records", f"{len(df):,}")
        d2.metric("Fields", f"{df.shape[1]}")
        d3.metric("Missing release years", f"{df['Year'].isna().sum():,}")
        with st.expander("Preview source data", expanded=True):
            st.dataframe(df.head(12), use_container_width=True, hide_index=True)
        with st.expander("Summary statistics"):
            st.dataframe(df.describe().T, use_container_width=True)
        with st.expander("Data quality and column guide"):
            quality = pd.DataFrame({"Missing values": df.isna().sum(), "Unique values": df.nunique()})
            st.dataframe(quality, use_container_width=True)
            st.markdown("**Sales fields** are measured in millions of units. **Year** is the release year when available. **Rank** is the dataset's original global-sales rank.")

st.markdown("<div style='text-align:center;color:#77717F;padding:24px 0 6px;font-size:.78rem'>GAMESCOPE · VIDEO GAME SALES EXPLORER · BUILT WITH STREAMLIT, PANDAS & MATPLOTLIB</div>", unsafe_allow_html=True)
