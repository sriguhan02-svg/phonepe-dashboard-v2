"""Run this once to print the real numbers you can use in your resume/README."""
import pandas as pd

tx = pd.read_csv("processed/agg_transaction.csv")
ins = pd.read_csv("processed/agg_insurance.csv")

# Top 5 states by total transaction amount
by_state = tx.groupby("state")["amount"].sum().sort_values(ascending=False)
top5_share = by_state.head(5).sum() / by_state.sum() * 100
print(f"Top 5 states share of total transaction value: {top5_share:.1f}%")
print(by_state.head(5))

# YoY growth in transaction amount
by_year = tx.groupby("year")["amount"].sum().sort_index()
print("\nYearly transaction amount:")
print(by_year)
yoy = by_year.pct_change().dropna() * 100
print("\nYoY growth %:")
print(yoy.round(1))

# Insurance vs transaction volume gap
total_tx_count = tx["count"].sum()
total_ins_count = ins["count"].sum()
print(f"\nInsurance txns as % of payment txns: {total_ins_count/total_tx_count*100:.2f}%")
print(f"Total records processed across pipeline: {len(tx)+len(ins)}")
