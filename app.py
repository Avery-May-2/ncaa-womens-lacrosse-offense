import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

st.title("NCAA Women's Lacrosse Offensive Efficiency Dashboard")

st.markdown(
"""
This dashboard analyzes **NCAA Women's Lacrosse offensive performance** using efficiency metrics.

Key metrics include:
- **Offensive Efficiency** — Goals per estimated possession
- **Shot Efficiency** — Goals per shot on goal
- **Pace** — Estimated possessions per game
"""
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/ncaa_womens_lacrosse_team_stats_2026.csv")
        df.columns = df.columns.str.lower().str.strip()
        return df
    except FileNotFoundError:
        st.error("CSV file not found! Make sure your workflow created it correctly.")
        st.stop()

df = load_data()

# -------------------------------------------------
# CLEAN + METRICS
# -------------------------------------------------
numeric_cols = df.columns.drop("team", errors="ignore")
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["team"])

# Ensure required columns exist
df["shots_on_goal"] = df.get("shots_on_goal", pd.Series(dtype="float"))
df["caused_turnovers"] = df.get("caused_turnovers", pd.Series(dtype="float"))
df["goals"] = df.get("goals", pd.Series(dtype="float"))
df["games_played"] = df.get("games_played", pd.Series(dtype="float"))

# Estimated possessions
df["estimated_possessions"] = df["shots_on_goal"].fillna(0) + df["caused_turnovers"].fillna(0)

# Offensive efficiency
df["offensive_efficiency"] = df["goals"].div(df["estimated_possessions"]).replace([float("inf"), -float("inf")], None)

# Shot efficiency
df["shot_efficiency"] = df["goals"].div(df["shots_on_goal"]).replace([float("inf"), -float("inf")], None)

# Turnover rate
df["turnover_rate"] = df["caused_turnovers"].div(df["estimated_possessions"]).replace([float("inf"), -float("inf")], None)

# -------------------------------------------------
# Pace — fully safe for deployment
# -------------------------------------------------
df["pace"] = df.apply(
    lambda row: row["estimated_possessions"] / row["games_played"]
    if pd.notna(row["games_played"]) and row["games_played"] > 0
    else row["estimated_possessions"],  # fallback if games_played missing
    axis=1
)

if "games_played" not in df.columns:
    st.warning("`games_played` column not found. Pace is estimated using possessions only.")

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("Filters")
filtered_df = df.copy()

# Conference filter
if "conference" in filtered_df.columns:
    conferences = ["All"] + sorted(filtered_df["conference"].dropna().unique())
    selected_conf = st.sidebar.selectbox("Conference", conferences)
    if selected_conf != "All":
        filtered_df = filtered_df[filtered_df["conference"] == selected_conf]

# Team search
team_search = st.sidebar.text_input("Search Team")
if team_search:
    filtered_df = filtered_df[filtered_df["team"].str.contains(team_search, case=False, na=False)]

# Team filter
teams = sorted(filtered_df["team"].dropna().unique())
selected_teams = st.sidebar.multiselect("Select Teams", teams, default=teams)
filtered_df = filtered_df[filtered_df["team"].isin(selected_teams)]

df = filtered_df

# Top 25 offenses toggle
top25 = st.sidebar.checkbox("Show Top 25 Offenses Only")
if top25:
    df = df.sort_values("offensive_efficiency", ascending=False).head(25)

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Highest Offensive Efficiency", round(df["offensive_efficiency"].max(skipna=True), 3))
col2.metric("Average Shot Efficiency", round(df["shot_efficiency"].mean(skipna=True), 3))
col3.metric(
    "Fastest Pace",
    round(df["pace"].max(skipna=True), 1) if df["pace"].notna().any() else "N/A"
)

st.subheader("Top Offensive Teams")
top_teams = df.sort_values("offensive_efficiency", ascending=False).head(10)
st.dataframe(
    top_teams[["team","goals","shots_on_goal","offensive_efficiency","shot_efficiency","pace"]],
    use_container_width=True
)

# -------------------------------------------------
# BAR CHART — Efficiency Rankings
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
fig.update_layout(yaxis=dict(autorange="reversed"), height=800, template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# SCATTER — Pace vs Efficiency
# -------------------------------------------------
fig2 = px.scatter(
    df,
    x="pace",
    y="offensive_efficiency",
    hover_name="team",
    size=df["goals"].fillna(0),
    color="offensive_efficiency",
    color_continuous_scale="Reds",
    title="Pace vs Offensive Efficiency"
)
fig2.update_layout(template="plotly_dark", height=600)
st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# BAR CHART — Shot Efficiency
# -------------------------------------------------
df_shot = df.sort_values("shot_efficiency", ascending=False)
fig3 = px.bar(
    df_shot,
    x="shot_efficiency",
    y="team",
    orientation="h",
    title="Shot Efficiency Ranking",
    color="shot_efficiency",
    color_continuous_scale="Blues"
)
fig3.update_layout(template="plotly_white", yaxis=dict(autorange="reversed"), height=800)
st.plotly_chart(fig3, use_container_width=True)