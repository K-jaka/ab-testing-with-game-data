import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep

df = pd.read_csv("data/cookie_cats.csv")
df = df[df["sum_gamerounds"] < 10000]

ctrl = df[df["version"] == "gate_30"]
treat = df[df["version"] == "gate_40"]

# ---------- binary outcomes: two-proportion z-test ----------
for metric in ["retention_7", "retention_1"]:          # primary first
    c_succ, c_n = ctrl[metric].sum(), len(ctrl)
    t_succ, t_n = treat[metric].sum(), len(treat)
    c_rate, t_rate = c_succ / c_n, t_succ / t_n

    stat, p = proportions_ztest([t_succ, c_succ], [t_n, c_n])
    lo, hi = confint_proportions_2indep(t_succ, t_n, c_succ, c_n,
                                        compare="diff", method="wald")

    print(f"\n--- {metric} ---")
    print(f"gate_30 (control):   {c_rate:.4f}")
    print(f"gate_40 (treatment): {t_rate:.4f}")
    print(f"Difference:          {(t_rate-c_rate)*100:+.2f}pp")
    print(f"95% CI:              [{lo*100:+.2f}pp, {hi*100:+.2f}pp]")
    print(f"z = {stat:.3f}, p = {p:.4f}")
    print("Significant at 0.05" if p < 0.05 else "Not significant at 0.05")

# ---------- continuous outcome: skewed, so rank-based ----------
u, p_mw = mannwhitneyu(treat["sum_gamerounds"], ctrl["sum_gamerounds"],
                       alternative="two-sided")
print(f"\n--- sum_gamerounds (guardrail) ---")
print(f"Median  gate_30: {ctrl['sum_gamerounds'].median():.0f}"
      f" | gate_40: {treat['sum_gamerounds'].median():.0f}")
print(f"Mann-Whitney U = {u:.0f}, p = {p_mw:.4f}")

# ---------- bootstrap the primary metric ----------
rng = np.random.default_rng(42)
c_vals = ctrl["retention_7"].to_numpy()
t_vals = treat["retention_7"].to_numpy()

diffs = np.array([
    rng.choice(t_vals, len(t_vals), replace=True).mean()
    - rng.choice(c_vals, len(c_vals), replace=True).mean()
    for _ in range(10_000)
])

print(f"\n--- bootstrap: retention_7 (10,000 resamples) ---")
print(f"Mean difference:  {diffs.mean()*100:+.2f}pp")
print(f"95% percentile CI: [{np.percentile(diffs,2.5)*100:+.2f}pp, "
      f"{np.percentile(diffs,97.5)*100:+.2f}pp]")
print(f"P(gate_40 worse): {(diffs < 0).mean():.3f}")