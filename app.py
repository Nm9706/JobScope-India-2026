import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="JobScope India 2026",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
st.markdown("""
<style>

.main {
    padding-top: 1rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1 {
    color: #0E76A8;
    text-align: center;
}

h2, h3 {
    color: #1F4E79;
}

/* Metric value */
[data-testid="stMetricValue"] {
    color: black !important;
    font-weight: bold;
}

/* Metric label */
[data-testid="stMetricLabel"] {
    color: black !important;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("📊 JobScope India 2026")
st.subheader("AI-Powered Indian Tech Job Intelligence Dashboard")
st.info(
    "📌 This dashboard analyzes over 23,000 Indian technology job postings. "
    "Salary insights are based only on jobs where salary information is disclosed."
)
# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_csv("jobscope_india_2026_cleaned.xls")
# Treat undisclosed salaries as missing values
df["salary_midpoint_lpa"] = df["salary_midpoint_lpa"].replace(0, np.nan)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.header("🔍 Dashboard Filters")

search_job = st.sidebar.text_input("🔎 Search Job Title")

selected_city = st.sidebar.selectbox(
    "📍 City",
    ["All"] + sorted(df["primary_city"].dropna().unique().tolist())
)

selected_experience = st.sidebar.selectbox(
    "💼 Experience",
    ["All"] + sorted(df["experience_tier"].dropna().unique().tolist())
)

selected_domain = st.sidebar.selectbox(
    "💻 Skill Domain",
    ["All"] + sorted(df["skill_domain"].dropna().unique().tolist())
)

# Salary Slider
min_salary = float(df["salary_midpoint_lpa"].min())
max_salary = float(df["salary_midpoint_lpa"].max())

salary_range = st.sidebar.slider(
    "💰 Salary Range (LPA)",
    min_value=min_salary,
    max_value=max_salary,
    value=(min_salary, max_salary)
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------
filtered_df = df.copy()

if selected_city != "All":
    filtered_df = filtered_df[
        filtered_df["primary_city"] == selected_city
    ]

if selected_experience != "All":
    filtered_df = filtered_df[
        filtered_df["experience_tier"] == selected_experience
    ]

if selected_domain != "All":
    filtered_df = filtered_df[
        filtered_df["skill_domain"] == selected_domain
    ]

if search_job:
    filtered_df = filtered_df[
        filtered_df["job_title"].str.contains(
            search_job,
            case=False,
            na=False
        )
    ]

filtered_df = filtered_df[
    (filtered_df["salary_midpoint_lpa"] >= salary_range[0]) &
    (filtered_df["salary_midpoint_lpa"] <= salary_range[1])
]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_jobs = len(filtered_df)
total_companies = filtered_df["company_name"].nunique()
total_cities = filtered_df["primary_city"].nunique()
avg_salary = round(filtered_df["salary_midpoint_lpa"].mean(), 2)
fresher_jobs = filtered_df["is_fresher_friendly"].sum()
salary_disclosed = filtered_df["salary_midpoint_lpa"].notna().sum()
# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("💼 Total Jobs", total_jobs)

with col2:
    st.metric("🏢 Companies", total_companies)

with col3:
    st.metric("📍 Cities", total_cities)

with col4:
    st.metric("💰 Avg Salary", f"{avg_salary} LPA")

with col5:
    st.metric("💰 Salary Disclosed", salary_disclosed)

# --------------------------------------------------
# AI INSIGHTS
# --------------------------------------------------

st.divider()

st.header("🧠 AI Insights")

if not filtered_df.empty:

    top_city = filtered_df["primary_city"].mode()[0]

    top_company = filtered_df["company_name"].mode()[0]

    highest_domain = (
        filtered_df.groupby("skill_domain")["salary_midpoint_lpa"]
        .mean()
        .idxmax()
    )

    fresher_percent = round(
        filtered_df["is_fresher_friendly"].mean() * 100,
        1
    )

    st.success(f"""
🏙️ Highest Hiring City : {top_city}

🏢 Top Hiring Company : {top_company}

💰 Highest Paying Skill Domain : {highest_domain}

📈 Average Salary : {avg_salary} LPA

🎓 Fresher Friendly Jobs : {fresher_percent}%
""")

else:
    st.warning("No data available for the selected filters.")

# --------------------------------------------------
# RECENT JOB LISTINGS
# --------------------------------------------------

st.divider()

st.header("📋 Recent Job Listings")

display_df = filtered_df[
    [
        "job_title",
        "company_name",
        "primary_city",
        "experience_tier",
        "salary_midpoint_lpa",
        "skill_domain",
    ]
].copy()

display_df.columns = [
    "Job Title",
    "Company",
    "City",
    "Experience",
    "Salary (LPA)",
    "Skill Domain",
]
display_df["Salary (LPA)"] = display_df["Salary (LPA)"].fillna("Not Disclosed")
st.dataframe(
    display_df.head(20),
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "📥 Download Filtered Dataset",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_jobs.csv",
    mime="text/csv",
)
# --------------------------------------------------
# DASHBOARD ANALYTICS
# --------------------------------------------------

st.divider()
st.header("📊 Dashboard Analytics")

# ==================================================
# TOP HIRING CITIES
# ==================================================

city_jobs = (
    filtered_df["primary_city"]
    .value_counts()
    .head(10)
    .reset_index()
)

city_jobs.columns = ["City", "Jobs"]

fig1 = px.bar(
    city_jobs,
    x="City",
    y="Jobs",
    color="Jobs",
    text="Jobs",
    title="🏙️ Top 10 Hiring Cities"
)

fig1.update_layout(
    template="plotly_white",
    title_x=0.5
)

# ==================================================
# HIGHEST PAYING SKILL DOMAINS
# ==================================================

salary_domain = (
    filtered_df.groupby("skill_domain")["salary_midpoint_lpa"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

salary_domain.columns = [
    "Skill Domain",
    "Average Salary"
]

fig2 = px.bar(
    salary_domain,
    x="Skill Domain",
    y="Average Salary",
    color="Average Salary",
    text_auto=".2f",
    title="💰 Highest Paying Skill Domains"
)

fig2.update_layout(
    template="plotly_white",
    title_x=0.5
)

# ==================================================
# FRESHER FRIENDLY COMPANIES
# ==================================================

fresher = (
    filtered_df[
        filtered_df["is_fresher_friendly"] == True
    ]
    .groupby("company_name")
    .size()
    .sort_values(ascending=False)
    .head(10)
    .reset_index(name="Jobs")
)

fig3 = px.bar(
    fresher,
    x="company_name",
    y="Jobs",
    color="Jobs",
    text="Jobs",
    title="🎓 Top Fresher-Friendly Companies"
)

fig3.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_tickangle=-30
)

# ==================================================
# EXPERIENCE VS SALARY
# ==================================================

exp_salary = (
    filtered_df.groupby("experience_tier")[
        "salary_midpoint_lpa"
    ]
    .mean()
    .reset_index()
)

fig4 = px.bar(
    exp_salary,
    x="experience_tier",
    y="salary_midpoint_lpa",
    color="salary_midpoint_lpa",
    text_auto=".2f",
    title="📈 Experience vs Salary"
)

fig4.update_layout(
    template="plotly_white",
    title_x=0.5
)

# ==================================================
# EXPERIENCE DISTRIBUTION
# ==================================================

exp_dist = (
    filtered_df["experience_tier"]
    .value_counts()
    .reset_index()
)

exp_dist.columns = [
    "Experience Tier",
    "Jobs"
]

fig5 = px.pie(
    exp_dist,
    names="Experience Tier",
    values="Jobs",
    hole=0.45,
    title="🥧 Experience Tier Distribution"
)

fig5.update_layout(
    template="plotly_white",
    title_x=0.5
)

# ==================================================
# TOP HIRING COMPANIES
# ==================================================

top_companies = (
    filtered_df["company_name"]
    .value_counts()
    .head(10)
    .reset_index()
)

top_companies.columns = [
    "Company",
    "Jobs"
]

fig6 = px.bar(
    top_companies,
    x="Company",
    y="Jobs",
    color="Jobs",
    text="Jobs",
    title="🏢 Top Hiring Companies"
)

fig6.update_layout(
    template="plotly_white",
    title_x=0.5,
    xaxis_tickangle=-30
)

# ==================================================
# DISPLAY CHARTS
# ==================================================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig6, use_container_width=True)

with col2:
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
    st.plotly_chart(fig5, use_container_width=True)

    # --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h4>📊 JobScope India 2026</h4>
        <p>AI-Powered Indian Tech Job Intelligence Dashboard</p>

        <p><b>Developed by Neeraja</b></p>

        <p>B.Sc Computer Science with Data Science</p>

        <p>Built with using Streamlit, Pandas ,numpy & Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)