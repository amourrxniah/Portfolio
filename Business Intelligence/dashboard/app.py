import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import sys
import os

#add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.data_processor import DataProcessor
from config import Config

class RealTimeBIDashboard:

    #move USERS inside the class to avoid import issues
    USERS = {
        'manager': {'password': 'manager123', 'role': 'manager', 'name': 'Business Manager'},
        'analyst': {'password': 'analyst123', 'role': 'analyst', 'name': 'Data Analyst'},
        'viewer': {'password': 'viewer123', 'role': 'viewer', 'name': 'Viewer'}
    }

    def __init__(self):
        self.processor = DataProcessor()
        self.set_page_config()
    
    def set_page_config(self):
        st.set_page_config(
            page_title="Real-Time COVID-19 Dashboard - COVID-API.com",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def authenticate_user(self, username, password):
        """simple authentication"""
        if username in self.USERS and self.USERS[username]['password'] == password:
            return {
                'username': username,
                'role': self.USERS[username]['role'],
                'name': self.USERS[username]['name']
            }
        return None
    
    def login_section(self):
        """display login section"""
        st.sidebar.title("🔐 Dashboard Login")
        
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = self.authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid credentials")
        
        #demo credentials info
        st.sidebar.markdown("---")
        st.sidebar.info("**Demo Credentials:**")
        st.sidebar.write("👨‍💼 Manager: `manager` / `manager123`")
        st.sidebar.write("🔍 Analyst: `analyst` / `analyst123`")
        st.sidebar.write("👀 Viewer: `viewer` / `viewer123`")
        
        #API status
        st.sidebar.markdown("---")
        st.sidebar.info("**API Status:** COVID-API.com")
        st.sidebar.write("✅ Real-time data")
        st.sidebar.write("🔄 Auto-updating")
        st.sidebar.write("🌍 Global coverage")
    
    def logout_section(self):
        """display logout section"""
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        #auto-refresh toggle
        st.sidebar.markdown("---")
        st.sidebar.info("**Manual refresh required**")
        if st.sidebar.button("🔄 Refresh Data"):
            st.rerun()
    
    def display_kpi_cards(self, kpis):
        """display KPI cards"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌍 Total Cases",
                f"{kpis.get('total_cases', 0):,}",
                help="Cumulative confirmed cases worldwide"
            )
        
        with col2:
            death_rate = kpis.get('death_rate', 0)
            st.metric(
                "⚰️ Death Rate",
                f"{death_rate:.2f}%",
                help="Case fatality rate"
            )
        
        with col3:
            recovery_rate = kpis.get('recovery_rate', 0)
            st.metric(
                "💊 Recovery Rate",
                f"{recovery_rate:.1f}%",
                help="Percentage of cases recovered"
            )
        
        with col4:
            active_cases = kpis.get('active_cases', 0)
            st.metric(
                "🦠 Active Cases",
                f"{active_cases:,}",
                help="Currently active cases"
            )
    
    def create_global_trend_chart(self, historical_data):
        """create global trends chart"""
        if not historical_data:
            return None
        
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        if 'new_cases' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'], y=df['new_cases'],
                name='Daily New Cases',
                line=dict(color='red', width=2)
            ))
        
        if '7day_avg_cases' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['date'], y=df['7day_avg_cases'],
                name='7-Day Average',
                line=dict(color='blue', width=3, dash='dash')
            ))
        
        fig.update_layout(
            title='Global COVID-19 Trends (Last 30 Days)',
            xaxis_title='Date',
            yaxis_title='Number of Cases',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_country_comparison_chart(self, country_data):
        """create country comparison chart"""
        if not country_data or 'top_by_cases' not in country_data:
            return None
        
        df = pd.DataFrame(country_data['top_by_cases'])
        
        fig = px.bar(
            df, x='country', y='cases',
            title='Top 10 Countries by Total Cases',
            color='cases',
            color_continuous_scale='reds'
        )
        
        fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Total Cases',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_death_rate_chart(self, country_data):
        """create death rate comparison chart"""
        if not country_data or 'top_by_cases' not in country_data:
            return None
        
        df = pd.DataFrame(country_data['top_by_cases'])
        
        fig = px.bar(
            df, x='country', y='death_rate',
            title='Death Rate by Country (%)',
            color='death_rate',
            color_continuous_scale='blues'
        )
        
        fig.update_layout(
            xaxis_title='Country',
            yaxis_title='Death Rate (%)',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def manager_dashboard(self):
        """dashboard for managers - high-level overview"""
        st.title("👨‍💼 Manager Dashboard - COVID-API.com Data")
        st.markdown("### Executive Summary")
        
        #real-time KPIs
        with st.spinner("🔄 Loading real-time data from COVID-API.com..."):
            kpis = self.processor.get_global_kpis()
        
        self.display_kpi_cards(kpis)
        
        st.markdown("---")
        
        #charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Global Trends")
            historical_data = self.processor.get_historical_trends('global', 30)
            if historical_data:
                fig = self.create_global_trend_chart(historical_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Historical data not available")
        
        with col2:
            st.subheader("🏴 Country Comparison")
            country_data = self.processor.get_country_comparison(10)
            if country_data:
                fig = self.create_country_comparison_chart(country_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        #additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Death Rate Analysis")
            if country_data:
                fig = self.create_death_rate_chart(country_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Case Distribution")
            if kpis:
                labels = ['Recovered', 'Active', 'Deaths']
                values = [
                    kpis.get('total_recovered', 0),
                    kpis.get('active_cases', 0),
                    kpis.get('total_deaths', 0)
                ]
                
                #filter out zero values to avoid chart errors
                filtered_labels = []
                filtered_values = []
                for label, value in zip(labels, values):
                    if value > 0:
                        filtered_labels.append(label)
                        filtered_values.append(value)
                
                if filtered_values:
                    fig = px.pie(
                        values=filtered_values, 
                        names=filtered_labels,
                        title='Case Distribution Worldwide'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for pie chart")
        
        #data source and timestamp
        st.markdown("---")
        st.caption(f"**Data Source:** {kpis.get('data_source', 'Unknown')} | "
                  f"**Last Updated:** {kpis.get('last_updated', 'Unknown')} | "
                  f"**Data Date:** {kpis.get('date', 'Unknown')}")
    
    def analyst_dashboard(self):
        """dashboard for analysts - detailed analysis"""
        st.title("🔍 Analyst Dashboard - Detailed Epidemiology Analysis")
        
        #data controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            days = st.selectbox("Time Period", [7, 30, 90, 180], index=1)
            #ensure days isnt None, use default if needed
            days = days if days is not None else 30
        
        with col2:
            countries = self.processor.get_available_countries()
            country_options = ['global'] + (countries[:50] if countries else [])
            selected_country = st.selectbox("Select Country", country_options, index=0)

            #ensure selected_country is not None, use default if needed
            selected_country = selected_country if selected_country is not None else 'global'
        
        with col3:
            metric = st.selectbox("Primary Metric", 
                                ['cases', 'deaths', 'recovery_rate', 'active_cases'])
            metric = metric if metric is not None else 'cases'
        
        #detailed analysis
        with st.spinner("📊 Loading detailed analysis from COVID-API.com..."):
            kpis = self.processor.get_global_kpis()
            country_data = self.processor.get_country_comparison(20)
            historical_data = self.processor.get_historical_trends(selected_country, days)
        
        #statistical summary
        st.subheader("📈 Statistical Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if country_data and 'summary_stats' in country_data:
                stats = country_data['summary_stats']
                st.metric("Countries Tracked", stats.get('total_countries', 0))
        
        with col2:
            if kpis:
                st.metric("Global Cases", f"{kpis.get('total_cases', 0):,}")
        
        with col3:
            if kpis:
                st.metric("Global Deaths", f"{kpis.get('total_deaths', 0):,}")
        
        with col4:
            if country_data and 'summary_stats' in country_data:
                stats = country_data['summary_stats']
                st.metric("Avg Death Rate", f"{stats.get('average_death_rate', 0):.2f}%")
        
        #advanced visualizations
        st.subheader("🔬 Advanced Analytics")
        
        if country_data and 'top_by_cases' in country_data:
            df = pd.DataFrame(country_data['top_by_cases'])
            
            #correlation analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                
                fig = px.imshow(
                    corr_matrix,
                    title="Correlation Matrix - Country Data",
                    color_continuous_scale='RdBu',
                    aspect="auto"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        #historical trends for selected country
        st.subheader("📅 Historical Trends")
        
        if historical_data:
            df = pd.DataFrame(historical_data)
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                #determine which columns are available for plotting
                available_columns = [col for col in ['confirmed', 'deaths', 'recovered', 'new_cases'] if col in df.columns]
                
                if available_columns:
                    fig = px.line(
                        df, 
                        x='date', 
                        y=available_columns[:3],  #plot up to 3 columns
                        title=f'COVID-19 Trends for {selected_country}'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No suitable data columns available for plotting")
            else:
                st.warning("No historical data available for the selected country")
        
        #raw data access
        st.subheader("📁 Data Export")
        
        if country_data and 'top_by_cases' in country_data:
            df = pd.DataFrame(country_data['top_by_cases'])
            
            st.dataframe(df, use_container_width=True)
            
            #export options
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Country Data (CSV)",
                data=csv,
                file_name=f"covid_country_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    def viewer_dashboard(self):
        """dashboard for viewers - simplified view"""
        st.title("👀 Public Health Dashboard - COVID-API.com")
        st.markdown("### Current Global Situation")
        
        with st.spinner("Loading current data from COVID-API.com..."):
            kpis = self.processor.get_global_kpis()
        
        #simplified KPIs
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Total Cases:** {kpis.get('total_cases', 0):,}")
        
        with col2:
            st.warning(f"**Total Deaths:** {kpis.get('total_deaths', 0):,}")
        
        with col3:
            st.success(f"**Recovered:** {kpis.get('total_recovered', 0):,}")
        
        #simple chart
        st.subheader("Recent Trends")
        historical_data = self.processor.get_historical_trends('global', 14)
        
        if historical_data:
            df = pd.DataFrame(historical_data)
            if 'new_cases' in df.columns:
                fig = px.line(df, x='date', y='new_cases', 
                             title='New Cases (Last 14 Days)')
                st.plotly_chart(fig, use_container_width=True)
        
        #key metrics
        st.subheader("Key Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Death Rate", f"{kpis.get('death_rate', 0):.2f}%")
            st.metric("Active Cases", f"{kpis.get('active_cases', 0):,}")
        
        with col2:
            st.metric("Recovery Rate", f"{kpis.get('recovery_rate', 0):.1f}%")
            st.metric("Cases/Million", f"{kpis.get('cases_per_million', 0):,}")
    
    def run(self):
        """main application runner"""
        #initialize session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'user' not in st.session_state:
            st.session_state.user = None
        
        #authentication check
        if not st.session_state.authenticated:
            self.login_section()
            
            #welcome page
            st.title("🌍 Real-Time COVID-19 Intelligence Dashboard")
            st.markdown("""
            ### Powered by COVID-API.com
            
            This dashboard provides **real-time analytics** on global COVID-19 data from COVID-API.com, including:
            
            - 📊 **Live statistics** updated automatically
            - 📈 **Interactive visualizations** of trends and patterns
            - 🌍 **Country-by-country** comparisons and analysis
            - 🔄 **Auto-updating** data every 5 minutes
            
            **Features:**
            - **Real API Data**: Uses COVID-API.com free public API
            - **Auto-Refresh**: Data updates every 5 minutes automatically
            - **Role-Based Views**: Different dashboards for managers, analysts, and viewers
            - **Export Capabilities**: Download data as CSV for analysis
            
            **How to use:**
            1. Login using the sidebar with demo credentials
            2. Choose your role for customized views
            3. Explore the real-time data visualizations
            4. Data updates automatically - no manual refresh needed!
            
            *Data is sourced from COVID-API.com and updates automatically every 5 minutes.*
            """)
            
        else:
            #check if user exists and has the expected structure
            user = st.session_state.user
            
            #safety check for user object
            if user and isinstance(user, dict) and 'name' in user and 'role' in user:
                st.sidebar.success(f"Welcome, **{user['name']}**!")
                self.logout_section()
                
                #role-based dashboard routing with safety checks
                user_role = user.get('role', 'viewer')
                
                if user_role == 'manager':
                    self.manager_dashboard()
                elif user_role == 'analyst':
                    self.analyst_dashboard()
                else:  #viewer or fallback
                    self.viewer_dashboard()
            else:
                #handle invalid user state
                st.sidebar.error("Invalid user session. Please log in again.")
                if st.sidebar.button("Return to Login"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

if __name__ == "__main__":
    dashboard = RealTimeBIDashboard()
    dashboard.run()