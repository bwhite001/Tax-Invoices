"""
Fix categorization issues in the expense catalog
"""
import pandas as pd
from pathlib import Path

def fix_categorization():
    catalog_file = Path("G:/My Drive/Tax Invoices/bankstatements/extracted/expense_catalog.csv")
    
    print("="*60)
    print("Fixing Categorization Issues")
    print("="*60)
    
    # Read catalog
    df = pd.read_csv(catalog_file)
    
    print(f"\nOriginal records: {len(df)}")
    
    # Fix 1: Correct Income/Expense types
    # Negative amounts = Expenses (money going out)
    # Positive amounts = Purchases/Charges (also expenses for Zip Money)
    print("\nFixing Income/Expense types...")
    df['type'] = df['amount'].apply(lambda x: 'Payment' if x < 0 else 'Purchase')
    
    # Fix 2: Improve categorization
    print("Improving categorization...")
    
    def categorize_transaction(row):
        desc = str(row['description']).lower()
        
        # Banking/Fees
        if 'monthly account fee' in desc or 'account fee' in desc:
            return 'Banking'
        if 'international transaction fee' in desc or 'transaction fee' in desc:
            return 'Banking'
        
        # Payments/Transfers
        if 'bpay payment' in desc or 'payment (' in desc:
            return 'Transfer'
        if 'refund' in desc:
            return 'Income'
        
        # Food & Dining
        if any(word in desc for word in ['pizza', 'dominos', 'mcdonald', 'subway', 'red rooster', 'uber eats', 'uber * eats']):
            return 'Dining'
        
        # Entertainment
        if any(word in desc for word in ['steam', 'steamgames', 'netflix', 'spotify', 'game']):
            return 'Entertainment'
        
        # Shopping
        if any(word in desc for word in ['amazon', 'temu', 'redbubble', 'jaycar', 'petbarn']):
            return 'Shopping'
        
        # Transport
        if 'uber order' in desc and 'eats' not in desc:
            return 'Transport'
        
        # Utilities
        if 'queensland urban utili' in desc or 'utilities' in desc:
            return 'Utilities'
        
        # Subscriptions/Services
        if any(word in desc for word in ['amway', 'prezzee', 'goat club', 'laundry lady', 'gc communications', 'upper story']):
            return 'Shopping'
        
        return 'Other'
    
    df['category'] = df.apply(categorize_transaction, axis=1)
    
    # Save fixed catalog
    df.to_csv(catalog_file, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*60}")
    print("SUCCESS! Categorization fixed")
    print(f"{'='*60}")
    
    # Show new summary
    print("\n--- Updated Category Breakdown ---")
    category_counts = df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count} transactions")
    
    print("\n--- Type Breakdown ---")
    type_counts = df['type'].value_counts()
    for type_name, count in type_counts.items():
        print(f"  {type_name}: {count} transactions")
    
    # Show spending by category (purchases only)
    print("\n--- Spending by Category (Purchases) ---")
    purchases = df[df['type'] == 'Purchase']
    category_spending = purchases.groupby('category')['amount'].sum().sort_values(ascending=False)
    for category, total in category_spending.items():
        print(f"  {category}: ${total:.2f}")
    
    print(f"\nTotal Purchases: ${purchases['amount'].sum():.2f}")
    print(f"Total Payments: ${abs(df[df['type'] == 'Payment']['amount'].sum()):.2f}")

if __name__ == "__main__":
    fix_categorization()
