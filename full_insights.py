import pandas as pd

agg_tx = pd.read_csv("processed/agg_transaction.csv")
agg_user = pd.read_csv("processed/agg_user.csv")
agg_ins = pd.read_csv("processed/agg_insurance.csv")
map_tx = pd.read_csv("processed/map_transaction.csv")
map_user = pd.read_csv("processed/map_user.csv")
map_ins = pd.read_csv("processed/map_insurance.csv")
top_tx = pd.read_csv("processed/top_transaction.csv")
top_user = pd.read_csv("processed/top_user.csv")
top_ins = pd.read_csv("processed/top_insurance.csv")

print("=== Device brand concentration (agg_user) ===")
brand = agg_user.groupby("brand")["count"].sum().sort_values(ascending=False)
top3_share = brand.head(3).sum() / brand.sum() * 100
print(f"Top 3 brands share of registered users: {top3_share:.1f}%")
print(brand.head(5), "\n")

print("=== Registered user growth (map_user) ===")
by_year_users = map_user.groupby("year")["registered_users"].sum().sort_index()
print(by_year_users)
print("YoY %:", by_year_users.pct_change().dropna().mul(100).round(1).to_dict(), "\n")

print("=== Engagement: app opens per registered user (map_user, latest year) ===")
latest_year = map_user["year"].max()
ly = map_user[map_user["year"] == latest_year]
engagement = ly["app_opens"].sum() / ly["registered_users"].sum()
print(f"{latest_year}: {engagement:.2f} app opens per registered user\n")

print("=== Top district by transaction amount (top_transaction) ===")
d = top_tx[top_tx["level"] == "district"]
top_district = d.groupby("entity")["amount"].sum().sort_values(ascending=False).head(5)
print(top_district, "\n")

print("=== Top pincode by transaction amount (top_transaction) ===")
p = top_tx[top_tx["level"] == "pincode"]
top_pin = p.groupby("entity")["amount"].sum().sort_values(ascending=False).head(5)
print(top_pin, "\n")

print("=== Top district by registered users (top_user) ===")
du = top_user[top_user["level"] == "district"]
top_district_users = du.groupby("entity")["registered_users"].sum().sort_values(ascending=False).head(5)
print(top_district_users, "\n")

print("=== Insurance growth trend (agg_insurance) ===")
ins_by_year = agg_ins.groupby("year")["amount"].sum().sort_index()
print(ins_by_year)
print("YoY %:", ins_by_year.pct_change().dropna().mul(100).round(1).to_dict(), "\n")

print("=== State-level insurance penetration (map_insurance vs map_transaction) ===")
tx_state = map_tx.groupby("state")["amount"].sum()
ins_state = map_ins.groupby("state")["amount"].sum()
penetration = (ins_state / tx_state * 100).sort_values(ascending=False)
print("Highest insurance-to-transaction ratio states:")
print(penetration.head(5))
print("\nLowest (biggest growth opportunity):")
print(penetration.tail(5))
