# --- import necessary libraries ---
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# --- page config ---
st.set_page_config(page_title="Mental Health in Tech Dashboard", layout="wide")
st.title("🧠 Mental Health in Tech Survey Dashboard")
st.markdown("Explore mental health trends in the tech industry based on survey data. Use the filters to dive deeper into specific demographics.")

# --- load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("survey.csv")
    df = df.drop_duplicates() #clean repeated values
    return df

df = load_data()

# --- sidebar filter options ---
with st.sidebar:
    st.header("🔍 Filters")

    with st.expander("👤 Demographics"):
        # --- age filter ---
        min_age = int(df["Age"].min())
        max_age = int(df["Age"].max())
        age_range = st.slider("Age Range", min_age, max_age, (20, 40))

        # --- gender filter ---
        genders = df["Gender"].dropna().unique()
        selected_genders = st.multiselect("Gender(s)", sorted(genders), default=list(genders))
        
    with st.expander("🧠 Mental Health"):
        # --- treatment filter ---
        treatment_options = df["treatment"].dropna().unique()
        selected_treatment = st.selectbox("Treatment Received?", ["All"] + list(treatment_options))

# --- apply filters ---
df_filtered = df[
    (df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1]) &
    (df["Gender"].isin(selected_genders))
]
if selected_treatment != "All":
    df_filtered = df_filtered[df_filtered["treatment"] == selected_treatment]

# --- dataset preview ---
st.subheader("👀 Dataset Preview")
st.dataframe(df.head(), use_container_width=True)

# --- metrics ---
st.subheader("📈 Key Metrics")
st.markdown("Quick summary of filtered survey responses:")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Responses", len(df_filtered))

with col2:
    treated = df_filtered[df_filtered["treatment"] == "Yes"]
    st.metric("Treated for Mental Health", len(treated))

with col3:
    untreated = df_filtered[df_filtered["treatment"] == "No"]
    st.metric("Not Treated", len(untreated))

# --- color palettes ---
color_map_treatment = {"Yes": "#db7093", "No": "#ba55d3"}
palette_age = ["#4682b4", "#daa520"] 
palette_pie = ["#90ee90", "#f08080"]
palette_interfere = ["#5f9ea0", "#db7093"] 
palette_family = ["#bc8f8f", "#da70d6"]
palette_company = ["#cd5c5c", "#b8860b", "#778899", "#8b008b", "#6b8e23", "#008b8b"]

# --- charts ---
st.subheader("📊 Visual Insights")
st.markdown("These visuals help uncover trends across different factors like age, gender, company size, and family history.")

# --- bar: treatment by age group ---
df_filtered["AgeGroup"] = pd.cut(df_filtered["Age"], bins=[0, 20, 30, 40, 50, 100],
                                 labels=["<20", "21–30", "31–40", "41–50", "50+"])
treatment_by_age = df_filtered.groupby(["AgeGroup", "treatment"]).size().reset_index(name="Count")

fig1 = px.bar(
    treatment_by_age,
    x="AgeGroup",
    y="Count",
    color="treatment",
    barmode="group",
    title="Treatment by Age Group",
    color_discrete_sequence=palette_age
)
st.plotly_chart(fig1, use_container_width=True)

# --- pie: treatment distribution ---
treatment_pie = df_filtered["treatment"].value_counts().reset_index()
treatment_pie.columns = ["Treatment", "Count"]

fig2 = px.pie(
    treatment_pie,
    names="Treatment",
    values="Count",
    title="Overall Treatment Distribution",
    color_discrete_sequence=palette_pie
)
st.plotly_chart(fig2, use_container_width=True)

# --- histogram: work interference vs treatment ---
st.subheader("💼 Work Interference vs Treatment")
st.markdown("Does the respondant feel that mental health interferes with work performance?")
interference_data = df_filtered[df_filtered["work_interfere"].notna()]

fig3 = px.histogram(
    interference_data,
    x="work_interfere",
    color="treatment",
    barmode="group",
    title="Does Mental Health Interfere With Work?",
    color_discrete_sequence=palette_interfere
)
st.plotly_chart(fig3, use_container_width=True)

# --- family history vs treatment ---
st.subheader("👨‍👩‍👧 Family History vs Treatment")
family_treatment = df_filtered[df_filtered["family_history"].notna()]

fig4 = px.histogram(
    family_treatment,
    x="family_history",
    color="treatment",
    barmode="group",
    title="Do Those With Family History of Mental Illness Seek Treatment?",
    color_discrete_sequence=palette_family
)
st.plotly_chart(fig4, use_container_width=True)

# --- mental health consequences by company size ---
st.subheader("🏢 Mental Health Consequences by Employer Size")
df_conseq = df_filtered[df_filtered["mental_health_consequence"].notna()]

fig5 = px.histogram(
    df_conseq,
    x="mental_health_consequence",
    color="no_employees",
    barmode="group",
    title="Perceived Mental Health Consequences by Company Size",
    color_discrete_sequence=palette_company
)
st.plotly_chart(fig5, use_container_width=True)

# --- feature description ---
st.subheader("📊 Age & Numeric Feature Distribution")
st.markdown("Distributions of numeric values like age to help identify skewed trends.")

numeric_df = df_filtered.select_dtypes(include='number')
if not numeric_df.empty:
    fig6, ax = plt.subplots(figsize=(8, 4))
    for column in numeric_df.columns:
        sns.kdeplot(numeric_df[column], label=column, fill=True)
    ax.legend()
    st.pyplot(fig6)
else:
    st.info("No numeric data available.")

# --- word cloud: benefits description ---
st.subheader("☁️ Word Cloud: Mental Health Benefits Description")
st.markdown("Common terms used to describe benefits received from employers.")

if "benefits" in df_filtered.columns:
    text = " ".join(str(b) for b in df_filtered["benefits"].dropna())
    if text.strip():
        wordcloud = WordCloud(background_color="white", width=800, height=400).generate(text)
        fig7, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig7)
    else:
        st.info("No valid descriptions found for 'benefits'.")
else:
    st.info("No 'benefits' column found in the dataset")

# --- download filtered data ---
st.subheader("⬇️ Download Filtered Data")
st.markdown("Interested in exploring the data further? Download the full survey dataset below:")

csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download CSV",
    data=csv,
    file_name="mental_health_survey.csv",
    mime="text/csv"
) 

# --- geo distribution of treatment ---
if "Country" in df_filtered.columns:
    st.subheader("🗺️ Treatment Distribution by Country")
    st.markdown("Explore how treatment varies by location across the globe.")

    selected_geo_treatment = st.radio(
        "Select treatment status for map", ["Yes", "No"], horizontal=True
    )
    geo_data = df_filtered[df_filtered["treatment"] == selected_geo_treatment]
    geo_grouped = geo_data.groupby("Country").size().reset_index(name="Count")
    fig8 = px.choropleth(
        geo_grouped,
        locations="Country",
        locationmode="country names",
        color="Count",
        hover_name="Country",
        color_continuous_scale="Viridis",
        title="Global Treatment Distribution by Country"
    )
    st.plotly_chart(fig8, use_container_width=True)
else:
    st.info("Country data not available for mapping.")


# --- footer --- 
st.markdown("<br><br><br>", unsafe_allow_html=True)  # Move the --- line up
st.markdown(
    """
    <style>
    .footer {
        position: absolute;
        margin-bottom: 0;
        margin-top: 1rem;
        width: 100%;
        text-align: center;
        padding: 1.5rem 0;
        font-size: 1.1rem;
        color: #aaa;
    }
    .footer a {
        margin: 0 15px;
        color: #bbb;
        text-decoration: none;
    }
    </style>

    <div class="footer">
        <p>&copy; 2025 <strong>Niah Price</strong>. All rights reserved.</p>
        <div>
            <a href="https://github.com/amourrxniah" target="_blank">🌐 GitHub</a>
            <a href="https://linkedin.com/in/niahprice0675" target="_blank">💼 LinkedIn</a>
            <a href="https://www.instagram.com/nprvx" target="_blank">📸 Instagram</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)