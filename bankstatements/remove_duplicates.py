"""
Remove duplicate transactions from extracted CSV
"""
import pandas as pd
from pathlib import Path

def remove_duplicates():
    input_file = Path("G:/My Drive/Tax Invoices/bankstatements/extracted/zip_transactions.csv")
    
    print("="*60)
    print("Removing Duplicate Transactions")
    print("="*60)
    
    # Read the CSV
    df = pd.read_csv(input_file)
    
    print(f"\nOriginal transactions: {len(df)}")
    
    # Remove duplicates based on all columns
    df_clean = df.drop_duplicates()
    
    print(f"After removing exact duplicates: {len(df_clean)}")
    
    # Sort by date
    df_clean['date'] = pd.to_datetime(df_clean['date'])
    df_clean = df_clean.sort_values('date')
    df_clean['date'] = df_clean['date'].dt.strftime('%Y-%m-%d')
    
    # Save cleaned data
    df_clean.to_csv(input_file, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*60}")
    print(f"SUCCESS! Cleaned file saved")
    print(f"Final transaction count: {len(df_clean)}")
    print(f"{'='*60}")
    
    # Show summary
    print(f"\nDate range: {df_clean['date'].min()} to {df_clean['date'].max()}")
    
    # Convert amount to numeric for calculations
    df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')
    
    print(f"Total amount: ${df_clean['amount'].sum():.2f}")
    print(f"Payments (negative): {len(df_clean[df_clean['amount'] < 0])}")
    print(f"Purchases (positive): {len(df_clean[df_clean['amount'] > 0])}")
    
    # Show top merchants
    print("\nTop 10 Merchants by Transaction Count:")
    merchant_counts = df_clean['description'].value_counts().head(10)
    for merchant, count in merchant_counts.items():
        print(f"  {merchant[:50]}: {count}")

if __name__ == "__main__":
    remove_duplicates()
