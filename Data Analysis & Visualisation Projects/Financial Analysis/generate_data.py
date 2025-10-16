import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import sqlite3
import os

def generate_client_data(num_clients=1000):
    """Generate synthetic client data"""
    np.random.seed(42)

    clients = []
    for i in range(num_clients):
        join_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 6*365))
        clients.append({
            'client_id': f'C{10000 + i}',
            'age': random.randint(18, 70),
            'income_bracket': random.choice(['Low', 'Medium', 'High']),
            'risk_tolerance': random.choice(['Low', 'Medium', 'High', 'Very High']),
            'investment_experience': random.choice(['Beginner', 'Intermediate', 'Advanced']),
            'join_date': join_date,
            'country': random.choice(['USA', 'UK', 'Germany', 'Australia', 'Canada', 'Japan'])
        })

    return pd.DataFrame(clients)

def generate_trading_data(clients_df, num_transactions=100000):
    """Generate synthetic trading data"""
    transactions = []
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'BRK.B', 'NVDA', 'JPM', 'JNJ', 'V']

    for i in range(num_transactions):
        client = random.choice(clients_df['client_id'].values)
        symbol = random.choice(symbols)
        transaction_date = datetime(2020, 1, 1) + timedelta(days=random.randint(0, 6*365))

        base_prices = {
            'AAPL': 150, 'MSFT': 280, 'GOOGL': 135, 'AMZN': 120, 'TSLA': 200,
            'BRK.B': 300, 'NVDA': 400, 'JPM': 140, 'JNJ': 160, 'V': 220
        }

        price = base_prices[symbol] * random.uniform(0.8, 1.2)
        quantity = random.randint(1, 200)
        transaction_type = random.choice(['Buy', 'Sell'])

        transactions.append({
            'transaction_id': f'T{100000 + i}',
            'client_id': client,
            'symbol': symbol,
            'transaction_date': transaction_date,
            'type': transaction_type,
            'quantity': quantity,
            'price': round(price, 2),
            'amount': round(quantity * price, 2)
        })
    return pd.DataFrame(transactions)


def generate_account_data(clients_df):
    """Generate account balance and transaction data"""
    accounts = []
    deposit_withdrawals = []

    for client_id in clients_df['client_id'].values:
        #initial deposit
        initial_deposit = random.randint(5000, 50000)
        current_balance = initial_deposit
        join_date = clients_df[clients_df['client_id'] == client_id]['join_date'].iloc[0]

        accounts.append({
            'client_id': client_id,
            'account_balance': current_balance,
            'last_updated': datetime.now()
        })

        #add initial deposit
        deposit_withdrawals.append({
            'client_id': client_id,
            'date': join_date,
            'type': 'Deposit',
            'amount': initial_deposit
        })

        #generate additional transactions
        for _ in range(random.randint(0, 20)):
            transaction_date = join_date + timedelta(days=random.randint(1, 6*365))
            if transaction_date > datetime.now():
                continue

            transaction_type = random.choice(['Deposit', 'Withdrawal'])
            amount = random.randint(100, 10000) if transaction_type == 'Deposit' else random.randint(100, 5000)
            if transaction_type == 'Withdrawal' and amount > current_balance:
                amount = current_balance * 0.8 #cant withdraw more than available
            current_balance += amount if transaction_type == 'Deposit' else -amount

            deposit_withdrawals.append({
                'client_id': client_id,
                'date': transaction_date,
                'type': transaction_type,
                'amount': amount
            })
    return pd.DataFrame(accounts), pd.DataFrame(deposit_withdrawals)
    
def create_database():
    """Create SQLite database and tables"""
    #create directory if it doesnt exist
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    #save database directly inside /data
    db_path = 'data/database/financial_data.db'
    #connect to SQLite database
    conn = sqlite3.connect(db_path)

    #generate data
    print("Generating client data...")
    clients_df = generate_client_data()

    print("Generating trading data...")
    trading_df = generate_trading_data(clients_df)

    print("Generating account data...")
    accounts_df, transactions_df = generate_account_data(clients_df)

    #save to database
    print("Saving to database...")
    clients_df.to_sql('clients', conn, if_exists='replace', index=False)
    trading_df.to_sql('trades', conn, if_exists='replace', index=False)
    accounts_df.to_sql('accounts', conn, if_exists='replace', index=False)
    transactions_df.to_sql('transactions', conn, if_exists='replace', index=False)

    #save to CSV aswell
    clients_df.to_csv('data/raw/clients.csv', index=False)
    trading_df.to_csv('data/raw/trades.csv', index=False)
    accounts_df.to_csv('data/raw/accounts.csv', index=False)
    transactions_df.to_csv('data/raw/transactions.csv', index=False)

    conn.close()
    print(f"Database created successfully at {db_path}!")

if __name__ == "__main__":
    create_database()