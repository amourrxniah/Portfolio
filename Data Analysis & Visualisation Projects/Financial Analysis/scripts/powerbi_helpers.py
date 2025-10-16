import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime

def prepare_powerbi_data():
    #get current director
    dir = os.path.dirname(os.path.abspath(__file__))

    #navigate to root directory
    project_root = os.path.join(dir, '..')

    #define correct paths
    db_path = os.path.join(project_root, 'data', 'database', 'financial_data.db')
    client_analysis_path = os.path.join(project_root, 'data', 'processed', 'client_data_with_churn.csv')
    powerbi_dir = os.path.join(project_root, 'data', 'powerbi')

    #create powerbi directory if it doesnt exist
    os.makedirs(powerbi_dir, exist_ok=True)

    print(f"Database path: {db_path}")
    print(f"Client analysis path: {client_analysis_path}")
    print(f"PowerBI directory: {powerbi_dir}")
    
    #connect to database
    try:
        conn = sqlite3.connect(db_path)
        print("Successfully connected to database")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    #load all tables
    try:
        clients = pd.read_sql_query('SELECT * FROM clients', conn)
        trades = pd.read_sql_query('SELECT * FROM trades', conn)
        accounts = pd.read_sql_query('SELECT * FROM accounts', conn)
        transactions = pd.read_sql_query('SELECT * FROM transactions', conn)
        print("Successfully loaded data from database")
    except Exception as e:
        print(f"Error loading data from database: {e}")
        conn.close()
        return
    
    #load client analysis data
    try:
        client_analysis = pd.read_csv(client_analysis_path)
        print("Successfully loaded client analysis data")
    except Exception as e:
        print(f"Error loading client analysis data: {e}")
        conn.close()
        return
    
    #close database connection
    conn.close()

    #convert date columns
    trades['transaction_date'] = pd.to_datetime(trades['transaction_date'])
    transactions['date'] = pd.to_datetime(transactions['date'])
    clients['join_date'] = pd.to_datetime(clients['join_date'])

    #create calendar table for time intelligence
    min_date = min(trades['transaction_date'].min(), transactions['date'].min(), clients['join_date'].min())
    max_date = max(trades['transaction_date'].max(), transactions['date'].max())
    
    calendar = pd.DataFrame({
        'date': pd.date_range(start=min_date, end=max_date)
    })
    calendar['year'] = calendar['date'].dt.year
    calendar['quarter'] = calendar['date'].dt.quarter
    calendar['month'] = calendar['date'].dt.month
    calendar['month_name'] = calendar['date'].dt.month_name()
    calendar['week'] = calendar['date'].dt.isocalendar().week
    calendar['day_of_week'] = calendar['date'].dt.day_name()
    calendar['is_weekend'] = calendar['date'].dt.dayofweek >= 5

    #create aggregated tables for better performance
    daily_trades = trades.groupby(trades['transaction_date'].dt.date).agg({
        'transaction_id': 'count',
        'amount': 'sum',
        'quantity': 'sum'
    }).reset_index()
    daily_trades.columns = ['date', 'trade_count', 'total_trade_value', 'total_quantity']
    
    daily_transactions = transactions.groupby(transactions['date'].dt.date).agg({
        'amount': 'sum',
        'type': lambda x: (x == 'Deposit').sum()  #count deposits
    }).reset_index()
    daily_transactions.columns = ['date', 'total_transaction_value', 'deposit_count']

    #merge client data with analysis data
    client_full = clients.merge(client_analysis, on='client_id', how='left', suffixes=('', '_analysis'))

    #export to CSV for powerbi
    client_full.to_csv(os.path.join(powerbi_dir, 'clients_enhanced.csv'), index=False)
    trades.to_csv(os.path.join(powerbi_dir, 'trades.csv'), index=False)
    transactions.to_csv(os.path.join(powerbi_dir, 'transactions.csv'), index=False)
    accounts.to_csv(os.path.join(powerbi_dir, 'accounts.csv'), index=False)
    calendar.to_csv(os.path.join(powerbi_dir, 'calendar.csv'), index=False)
    daily_trades.to_csv(os.path.join(powerbi_dir, 'daily_trades.csv'), index=False)
    daily_transactions.to_csv(os.path.join(powerbi_dir, 'daily_transactions.csv'), index=False)
    
    print("Power BI data preparation completed!")
    print(f"Files saved to {powerbi_dir}")

if __name__ == "__main__":
    prepare_powerbi_data()