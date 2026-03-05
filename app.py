import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("NCAA Women's Lacrosse Offensive Efficiency Dashboard")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("data/ncaa_womens_lacrosse_team_stats_2026.csv")
    return df

df = load_data()

# -------------------------------------------------
# CLEAN + METRICS
# -------------------------------------------------

df.columns = df.columns.str.lower()

# If totals already exist, comment these out
df["estimated_possessions"] = df["shots_on_goal"] + df["caused_turnovers"]
df["offensive_efficiency"] = df["goals"] / df["estimated_possessions"]
df["shot_efficiency"] = df["goals"] / df["shots_on_goal"]
df["turnover_rate"] = df["caused_turnovers"] / df["estimated_possessions"]
df["pace"] = df["estimated_possessions"] / df["games_played"]

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header("Filters")

if "conference" in df.columns:
    conferences = ["All"] + sorted(df["conference"].dropna().unique())
    selected_conf = st.sidebar.selectbox("Conference", conferences)

    if selected_conf != "All":
        df = df[df["conference"] == selected_conf]

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

col1, col2, col3 = st.columns(3)

col1.metric("Highest Offensive Efficiency", 
            round(df["offensive_efficiency"].max(), 3))

col2.metric("Average Shot Efficiency", 
            round(df["shot_efficiency"].mean(), 3))

col3.metric("Fastest Pace", 
            round(df["pace"].max(), 1))

# -------------------------------------------------
# RANKED BAR CHART
# -------------------------------------------------

df_sorted = df.sort_values("offensive_efficiency", ascending=False)

fig = px.bar(
    df_sorted,
    x="offensive_efficiency",
    y="team",
    orientation="h",
    color="offensive_efficiency",
    color_continuous_scale="Reds",
    title="Offensive Efficiency Rankings"
)

fig.update_layout(
    yaxis=dict(autorange="reversed"),
    height=800,
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# SCATTER: PACE vs EFFICIENCY
# -------------------------------------------------

fig2 = px.scatter(
    df,
    x="pace",
    y="offensive_efficiency",
    hover_name="team",
    size="goals",
    title="Pace vs Offensive Efficiency"
)

st.plotly_chart(fig2, use_container_width=True)