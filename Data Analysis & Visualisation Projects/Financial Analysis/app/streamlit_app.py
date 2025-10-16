import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sqlite3 import connect
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Financial Client Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    client_data = pd.read_csv('../data/processed/client_data_with_churn.csv')
    trades = pd.read_csv('../data/processed/trades_processed.csv')
    transactions = pd.read_csv('../data/processed/transactions_processed.csv')
    return client_data, trades, transactions

client_data, trades, transactions = load_data()

# Convert date columns
client_data['join_date'] = pd.to_datetime(client_data['join_date'])
trades['transaction_date'] = pd.to_datetime(trades['transaction_date'])
transactions['date'] = pd.to_datetime(transactions['date'])

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Overview", "Client Demographics", "Trading Activity", 
                                 "Financial Patterns", "Client Segmentation", "Churn Analysis"])

# Main content
st.title("Financial Client Analytics Dashboard")

if page == "Overview":
    st.header("Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", len(client_data))
    
    with col2:
        st.metric("Total Trade Value", f"${client_data['total_trade_value'].sum():,.0f}")
    
    with col3:
        st.metric("Average Account Balance", f"${client_data['account_balance'].mean():,.0f}")
    
    with col4:
        churn_rate = client_data['churned'].mean() * 100
        st.metric("Churn Rate", f"{churn_rate:.1f}%")
    
    # Key metrics over time
    st.subheader("Trading Activity Over Time")
    trade_daily = trades.groupby(trades['transaction_date'].dt.date).size().reset_index()
    trade_daily.columns = ['date', 'count']
    
    fig = px.line(trade_daily, x='date', y='count', title='Daily Trade Volume')
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk tolerance distribution
    st.subheader("Client Risk Profile")
    risk_counts = client_data['risk_tolerance'].value_counts().reset_index()
    risk_counts.columns = ['risk_tolerance', 'count']
    
    fig = px.pie(risk_counts, values='count', names='risk_tolerance', 
                 title='Distribution of Risk Tolerance')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Client Demographics":
    st.header("Client Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        fig = px.histogram(client_data, x='age', nbins=20, title='Age Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        # Income distribution
        income_counts = client_data['income_bracket'].value_counts().reset_index()
        income_counts.columns = ['income_bracket', 'count']
        fig = px.bar(income_counts, x='income_bracket', y='count', title='Income Brackets')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Country distribution
        country_counts = client_data['country'].value_counts().reset_index().head(10)
        country_counts.columns = ['country', 'count']
        fig = px.bar(country_counts, x='country', y='count', title='Top 10 Countries')
        st.plotly_chart(fig, use_container_width=True)
        
        # Tenure distribution
        fig = px.histogram(client_data, x='tenure_days', nbins=20, title='Client Tenure (Days)')
        st.plotly_chart(fig, use_container_width=True)

elif page == "Trading Activity":
    st.header("Trading Activity Analysis")
    
    # Trade type distribution
    trade_type = trades['type'].value_counts().reset_index()
    trade_type.columns = ['type', 'count']
    fig = px.pie(trade_type, values='count', names='type', title='Trade Type Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    # Most traded symbols
    top_symbols = trades['symbol'].value_counts().reset_index().head(10)
    top_symbols.columns = ['symbol', 'count']
    fig = px.bar(top_symbols, x='symbol', y='count', title='Top 10 Most Traded Symbols')
    st.plotly_chart(fig, use_container_width=True)
    
    # Trading by risk tolerance
    risk_trade = client_data.groupby('risk_tolerance').agg({
        'trade_count': 'mean',
        'avg_trade_value': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=risk_trade['risk_tolerance'],
        y=risk_trade['trade_count'],
        name='Average Trade Count'
    ))
    fig.add_trace(go.Bar(
        x=risk_trade['risk_tolerance'],
        y=risk_trade['avg_trade_value'],
        name='Average Trade Value'
    ))
    fig.update_layout(barmode='group', title='Trading Activity by Risk Tolerance')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Financial Patterns":
    st.header("Financial Patterns")
    
    # Account balance distribution
    fig = px.histogram(client_data, x='account_balance', nbins=30, title='Account Balance Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    # Deposit/withdrawal patterns
    transaction_daily = transactions.groupby([transactions['date'].dt.date, 'type']).size().unstack(fill_value=0).reset_index()
    transaction_daily.columns = ['date', 'Deposit', 'Withdrawal']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=transaction_daily['date'], y=transaction_daily['Deposit'], name='Deposits'))
    fig.add_trace(go.Scatter(x=transaction_daily['date'], y=transaction_daily['Withdrawal'], name='Withdrawals'))
    fig.update_layout(title='Daily Deposit/Withdrawal Activity')
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    numeric_cols = client_data.select_dtypes(include=[np.number]).columns
    corr_matrix = client_data[numeric_cols].corr()
    
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title='Correlation Matrix')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Client Segmentation":
    st.header("Client Segmentation")
    
    # Cluster summary
    cluster_summary = client_data.groupby('cluster').agg({
        'age': 'mean',
        'account_balance': 'mean',
        'trade_count': 'mean',
        'avg_trade_value': 'mean',
        'tenure_days': 'mean',
        'client_id': 'count'
    }).round(2).reset_index()
    
    cluster_summary.columns = ['Cluster', 'Avg Age', 'Avg Balance', 'Avg Trade Count', 
                              'Avg Trade Value', 'Avg Tenure', 'Client Count']
    
    st.subheader("Cluster Characteristics")
    st.dataframe(cluster_summary)
    
    # Cluster visualization
    fig = px.scatter(client_data, x='age', y='account_balance', color='cluster',
                     hover_data=['risk_tolerance', 'trade_count'],
                     title='Client Segmentation by Age and Account Balance')
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk score by cluster
    risk_by_cluster = client_data.groupby('cluster')['behavioral_risk_score'].mean().reset_index()
    fig = px.bar(risk_by_cluster, x='cluster', y='behavioral_risk_score', 
                 title='Average Behavioral Risk Score by Cluster')
    st.plotly_chart(fig, use_container_width=True)

elif page == "Churn Analysis":
    st.header("Churn Prediction Analysis")
    
    # Churn rate by segment
    churn_by_segment = client_data.groupby('churn_risk_segment')['churned'].mean().reset_index()
    fig = px.bar(churn_by_segment, x='churn_risk_segment', y='churned', 
                 title='Actual Churn Rate by Risk Segment')
    st.plotly_chart(fig, use_container_width=True)
    
    # Feature importance
    features = ['age', 'account_balance', 'tenure_days', 'trade_count', 
                'avg_trade_value', 'avg_daily_trades', 'transaction_count',
                'deposit_ratio', 'behavioral_risk_score']
    
    # Simulate feature importance (in a real scenario, this would come from your model)
    importance = [0.15, 0.18, 0.12, 0.22, 0.08, 0.10, 0.05, 0.06, 0.04]
    feature_importance = pd.DataFrame({'feature': features, 'importance': importance})
    feature_importance = feature_importance.sort_values('importance', ascending=True)
    
    fig = px.bar(feature_importance, x='importance', y='feature', 
                 title='Feature Importance for Churn Prediction')
    st.plotly_chart(fig, use_container_width=True)
    
    # High-risk clients table
    st.subheader("High Churn Risk Clients")
    high_risk_clients = client_data[client_data['churn_risk_segment'] == 'Very High'][[
        'client_id', 'age', 'risk_tolerance', 'account_balance', 
        'trade_count', 'churn_risk'
    ]].sort_values('churn_risk', ascending=False).head(10)
    
    st.dataframe(high_risk_clients)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Financial Client Analytics Dashboard | Created with Streamlit")