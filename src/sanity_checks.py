import pandas as pd
from scipy.stats import chisquare

df = pd.read_csv("data/cookie_cats.csv")

print("Shape:", df.shape)
print("\nDtypes:\n", df.dtypes)
print("\nNulls:\n", df.isnull().sum())

# Duplicate users — a user in both arms breaks independence
dupes = df["userid"].duplicated().sum()
print(f"\nDuplicate userids: {dupes}")

# Sample Ratio Mismatch: is the split actually 50/50?
counts = df["version"].value_counts()
print("\nGroup sizes:\n", counts)
print("Split:", (counts / counts.sum()).round(4).to_dict())

expected = [counts.sum() / 2] * 2
stat, p = chisquare(f_obs=counts.values, f_exp=expected)
print(f"\nSRM chi-square: stat={stat:.3f}, p={p:.4f}")
print("SRM detected — investigate before trusting results" if p < 0.001
      else "No SRM — randomisation looks healthy")

# Outcome rates per group
print("\nRetention by group:")
print(df.groupby("version")[["retention_1", "retention_7"]].mean().round(4))

# Engagement distribution — check for absurd values
print("\nsum_gamerounds:")
print(df["sum_gamerounds"].describe())
print("Top 5 values:", sorted(df["sum_gamerounds"], reverse=True)[:5])