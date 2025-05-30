import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import plotly.express as px
from wordcloud import WordCloud
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO

#page config
st.set_page_config(
    page_title="Netflix Content Analysis Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'About': "A comprehensive analysis of Netflix content by Niah Price"}
)

#load logo for branding
@st.cache_data
def load_logo():
    try:
        #direct image url
        logo_url = "https://upload.wikimedia.org/wikipedia/commons/1/10/Meta-image-netflix-symbol-black.png"
        response = requests.get(logo_url)
        img = Image.open(BytesIO(response.content))

        #resize and convert to rgb
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img = img.resize((200, 105)) #aspect ratio (original is 1198 x 627)
        return img
    except Exception as e:
        st.sidebar.warning(f"Couldn't load logo: {str(e)}")
        return None

netflix_logo = load_logo()
if netflix_logo:
    st.sidebar.image(netflix_logo, use_container_width=True)
else:
    st.sidebar.markdown("### Netflix Analysis")

#load data
@st.cache_data
def load_data():
    github_url = "https://raw.githubusercontent.com/amourrxniah/Portfolio/main/netflix_titles.csv"
    
    with st.spinner('Loading data...'):
        try:
            data = pd.read_csv(github_url)
            st.success("Using dataset from Github")
        except:
            try:
                data = pd.read_csv(github_url)
                st.success("Using local dataset")
            except:
                data = pd.read_csv("netflix_titles.csv") #fallback to local file
    return data
df = load_data()

#data preprocessing
def preprocess_data(df):
    if df.empty:
        return df
    
    #handle missing values
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna('Unknown').astype(str)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')

    #extract temporal features
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month_name()
    df['day_added'] = df['date_added'].dt.day

    #duration processing
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)
    df['duration_type'] = df['duration'].str.extract('(min|Season|Seasons)')

    #extract first listed genre
    df['primary_genre'] = df['listed_in'].str.split(',').str[0].str.strip()

    return df
df = preprocess_data(df)

#sidebar filters
st.sidebar.title("🔍Filters")
show_type = st.sidebar.selectbox("Content Type", ["All"] + list(df['type'].unique()))

#country selector with search
all_countries = sorted(df['country'].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Countries",
    options=all_countries,
    default=["United States", "United Kingdom", "India", "Japan"],
    format_func=lambda x: f"{x} ({len(df[df['country']==x])})"
)

#rating selector with explanations
rating_explanations = {
    'TV-MA': 'Mature Audience',
    'TV-14': 'Parents Strongly Cautioned',
    'TV-PG': 'Parental Guidance',
    'R': 'Restricted',
    'PG-13': 'Parents Strongly Cautioned',
}
selected_ratings = st.sidebar.multiselect(
    "Ratings",
    options=sorted(df['rating'].dropna().astype(str).unique().tolist()),
    format_func=lambda x: f"{x} - {rating_explanations.get(x, '')}"
    )

#enhanced year range with decade selection
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
decades = list(range(min_year - min_year%10, max_year + 10, 10))
selected_decade = st.sidebar.selectbox("Decade", decades, index=len(decades)-2)
year_range = st.sidebar.slider(
    "Release Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(selected_decade, selected_decade+9)
)

#apply filters
filtered_df = df.copy()
if show_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == show_type]
if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
if selected_ratings:
    filtered_df = filtered_df[filtered_df['rating'].isin(selected_ratings)]
filtered_df = filtered_df[
    (filtered_df['release_year'] >= year_range[0]) &
    (filtered_df['release_year'] <= year_range[1])
]

#main app
st.title("🎬 Netflix Content Analysis")
st.markdown("""
    <style>
    .metric-card {
        background: #d8bfd8;
        color: #000;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

#key metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Total Titles</h3>
            <h1>{len(filtered_df):,}</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Movies</h3>
            <h1>{len(filtered_df[filtered_df['type'] == 'Movie']):,}</h1>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h3>TV Shows</h3>
            <h1>{len(filtered_df[filtered_df['type'] == 'TV Show']):,}</h1>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Avg. Release Year</h3>
            <h1>{int(filtered_df['release_year'].mean())}</h1>
        </div>
    """, unsafe_allow_html=True)

#content spotlight
if not filtered_df.empty:
    spotlight = filtered_df.sample(1).iloc[0]
    st.markdown(f"""
        <div style="background:#d8bfd8; color:#000; padding:15px; border-radius:10px; margin:10px 0;">
            <h3>🌟 Spotlight: {spotlight['title']} ({spotlight['release_year']})</h3>
            <p><b>Type:</b> {spotlight['type']} | <b>Rating:</b> {spotlight['rating']}</p>
            <p><b>Genre:</b> {spotlight['listed_in']}</p>
            <p><b>Description:</b> {spotlight['description']}</p>
        </div>
    """, unsafe_allow_html=True)

#tabs for different analysis
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview", 
    "🎭 Content", 
    "🌍 Geography", 
    "⏳ Timeline",
    "🔍 Deep Dive"
])

with tab1:
    st.subheader("Content Overview")

    #type distribution
    fig1 = px.pie(filtered_df, names='type', title='Content Type Distribution', color_discrete_sequence=['#ffd700', '#8b4513'])
    st.plotly_chart(fig1, use_container_width=True)

    #rating distribution
    fig2 = px.histogram(filtered_df, x='rating', color='type',
                        title='Content Rating Distribution', barmode='group',
                        color_discrete_sequence=['#4682b4', '#ffa500'])
    st.plotly_chart(fig2, use_container_width=True)

    #added month distribution
    fig10 = px.histogram(filtered_df, x='month_added', color='type',
                         title='Content Added by Month',
                         color_discrete_sequence=['#008000', '#f08080'])
    st.plotly_chart(fig10, use_container_width=True)

with tab2:
    st.subheader("Content Analysis")

    #duration analysis
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Movie Duration Distribution")
        movie_duration = filtered_df[filtered_df['type'] == 'Movie']
        fig3 = px.histogram(movie_duration, x='duration_num', nbins=20,
                            labels={'duration_num': 'Duration (minutes)'},
                            color_discrete_sequence=['#8a2be2'])
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.markdown("### TV Show Seasons Distribution")
        tv_seasons = filtered_df[filtered_df['type'] == 'TV Show']
        fig4 = px.histogram(tv_seasons, x='duration_num', nbins=20,
                           labels={'duration_num': 'Number of Seasons'},
                           color_discrete_sequence=['#48d1cc'])
        st.plotly_chart(fig4, use_container_width=True)

    #genre word cloud
    st.markdown("### Genre Word Cloud")
    genres_text = ' '.join(filtered_df['listed_in'].dropna())
    wordcloud = WordCloud(width=800, height=400,
                          background_color='white',
                          colormap='inferno').generate(genres_text)
    fig5, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig5)

    #top genres
    st.markdown("### Top Genres")
    top_genres = filtered_df['primary_genre'].value_counts().head(10)
    fig11 = px.bar(top_genres, x=top_genres.index, y=top_genres.values,
                   color=top_genres.index,
                   color_discrete_sequence=px.colors.sequential.PuRd_r,
                   title="Top 10 Genres")
    st.plotly_chart(fig11, use_container_width=True)

with tab3:
    st.subheader("Geographical Analysis")
    
    #country distribution
    country_counts = filtered_df['country'].value_counts().head(15)
    fig6 = px.bar(country_counts, x=country_counts.index, y=country_counts.values,
                 title='Top 15 Countries by Content Production',
                 labels={'x': 'Country', 'y': 'Number of Titles'},
                 color=country_counts.index,
                 color_discrete_sequence=px.colors.sequential.BuGn_r)
    st.plotly_chart(fig6, use_container_width=True)
    
    #map visualization
    try:
        #country mapping for plotly
        country_mapping = {
            'United States': 'USA',
            'United Kingdom': 'UK',
            'Hong Kong': 'China',
            'West Germany': 'Germany',
            'Soviet Union': 'Russia'
        }
        
        df_map = filtered_df.copy()
        df_map['country'] = df_map['country'].replace(country_mapping)
        
        #split countries and explode
        df_map['country'] = df_map['country'].str.split(', ')
        df_map = df_map.explode('country')
        df_map['country'] = df_map['country'].str.strip()
        
        country_counts = df_map['country'].value_counts().reset_index()
        country_counts.columns = ['country', 'count']
        
        fig7 = px.choropleth(country_counts, 
                            locations='country',
                            locationmode='country names',
                            color='count',
                            hover_name='country',
                            title='Content by Country',
                            color_continuous_scale='viridis')
        st.plotly_chart(fig7, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not display map: {str(e)}")

    #content by country and type
    st.markdown("### Content by Country and Type")
    country_type = filtered_df.groupby(['country', 'type']).size().unstack().fillna(0)
    country_type = country_type.sort_values(by='Movie', ascending=False).head(15)
    fig12 = px.bar(country_type, x=country_type.index, y=['Movie', 'TV Show'],
                   title='Content by Country and Type',
                   color_discrete_sequence=['#ff69b4', '#87cefa'])
    st.plotly_chart(fig12, use_container_width=True)

with tab4:
    st.subheader("Temporal Analysis")

    #content added over time
    added_overtime = filtered_df.groupby(['year_added', 'type']).size().unstack().fillna(0)
    fig8 = px.line(added_overtime, x=added_overtime.index, y=added_overtime.columns,
                   title='Content Added to Netflix Over Time',
                   labels={'value': 'Number of Titles', 'year_added': 'Year', 'variable': 'Type'},
                   color_discrete_sequence=['#9400d3', '#daa520'])
    st.plotly_chart(fig8, use_container_width=True)

    #release year distribution
    fig9 = px.histogram(filtered_df, x='release_year', color='type',
                        title='Content Release Year Distribution',
                        labels={'release_year': 'Release Year', 'count': 'Number if Titles'},
                        nbins=30,
                        color_discrete_sequence=['#bc8f8f', '#808080'])
    st.plotly_chart(fig9, use_container_width=True)

    #content added by month and year
    st.markdown("### Content Added by Month and Year")
    month_year = filtered_df.groupby(['year_added', 'month_added']).size().unstack().fillna(0)
    fig13 = px.imshow(month_year, 
                     labels=dict(x="Month", y="Year", color="Count"),
                     x=month_year.columns,
                     y=month_year.index,
                     color_continuous_scale='magma')
    st.plotly_chart(fig13, use_container_width=True)

with tab5:
    st.subheader("Advanced Insights")

    #content growth analysis
    st.markdown("### Content Growth Patterns")
    growth_df = filtered_df.groupby(['year_added', 'type']).size().unstack().fillna(0)
    growth_df['Total'] = growth_df.sum(axis=1)
    st.area_chart(growth_df, color=['#6495ed', '#ff1493', '#8b008b'])

    #director analysis
    st.markdown("### Top Directors")
    top_directors = filtered_df['director'].value_counts().head(10)
    fig14 = px.bar(top_directors, x=top_directors.index, y=top_directors.values,
                  color=top_directors.index,
                  color_discrete_sequence=px.colors.sequential.Purples_r)
    st.plotly_chart(fig14, use_container_width=True)

    #content recommendation based on filters
    st.markdown("### Recommended Titles")
    rec_df = filtered_df.sort_values('release_year', ascending=False).head(5)
    st.dataframe(rec_df[['title', 'type', 'release_year', 'rating', 'listed_in']])

#raw data view
st.subheader("Raw Data")
if st.checkbox("Show raw data"):
    st.write(filtered_df)

#footer
st.markdown("---")
st.markdown("""
    <div style="text-align:center">
        <p>Created by <b>Niah Price</b> | 
        <a href="https://github.com/amourrxniah/Portfolio" target="_blank">GitHub Portfolio</a></p>
        <p>Data Source: <a href="https://www.kaggle.com/datasets/shivamb/netflix-shows" target="_blank">Kaggle Netflix Dataset</a></p>
    </div>
""", unsafe_allow_html=True)