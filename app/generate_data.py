"""
Data Generation Script - Creates realistic complex datasets for DataFlint testing
"""

import csv
import random
from datetime import datetime, timedelta
import os

# Ensure data directory exists
os.makedirs('/data', exist_ok=True)

# Configuration
NUM_CUSTOMERS = 500
NUM_TRANSACTIONS = 10000
SEED = 42

random.seed(SEED)


def generate_customers():
    """Generate customer data"""
    print("Generating customer data...")
    
    countries = ["USA", "UK", "Canada", "Germany", "France", "India", "Australia", "Brazil", "Japan", "Mexico"]
    segments = ["VIP", "Regular", "New"]
    
    customers = []
    for i in range(NUM_CUSTOMERS):
        customer_id = f"CUST_{i+1:06d}"
        name = f"Customer_{i+1}"
        email = f"customer{i+1}@domain{random.randint(1,10)}.com"
        country = random.choice(countries)
        segment = random.choice(segments)
        
        customers.append({
            'customer_id': customer_id,
            'customer_name': name,
            'email': email,
            'country': country,
            'segment': segment
        })
    
    # Write to CSV
    with open('/data/customers.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['customer_id', 'customer_name', 'email', 'country', 'segment'])
        writer.writeheader()
        writer.writerows(customers)
    
    print(f"✓ Generated {len(customers)} customers")
    return customers


def generate_transactions(customers):
    """Generate transaction data"""
    print("Generating transaction data...")
    
    categories = ["Electronics", "Fashion", "Home", "Sports", "Books", "Beauty", "Toys", "Food", "Automotive", "Health"]
    products = [f"PROD_{i+1:04d}" for i in range(100)]
    
    transactions = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(NUM_TRANSACTIONS):
        transaction_id = f"TXN_{i+1:08d}"
        customer = random.choice(customers)
        product_id = random.choice(products)
        category = random.choice(categories)
        amount = round(random.uniform(10, 5000), 2)
        timestamp = base_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        
        transactions.append({
            'transaction_id': transaction_id,
            'customer_id': customer['customer_id'],
            'product_id': product_id,
            'category': category,
            'amount': amount,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # Write to CSV
    with open('/data/transactions.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['transaction_id', 'customer_id', 'product_id', 'category', 'amount', 'timestamp'])
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"✓ Generated {len(transactions)} transactions")
    return transactions


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Complex Dataset for DataFlint Testing")
    print("=" * 60)
    
    customers = generate_customers()
    transactions = generate_transactions(customers)
    
    print("\n" + "=" * 60)
    print("✓ Data generation completed successfully")
    print(f"  Customers: {len(customers)}")
    print(f"  Transactions: {len(transactions)}")
    print("=" * 60)
