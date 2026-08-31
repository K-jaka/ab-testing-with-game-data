import pandas as pd
from scipy.optimize import brentq
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

df = pd.read_csv("data/cookie_cats.csv")
df = df[df["sum_gamerounds"] < 10000]          # drop the 49,854 outlier

n_per_group = int(df["version"].value_counts().min())

def required_n(baseline, lift, alpha=0.05, power=0.8):
    """Sample size per arm to detect `lift` (absolute) from `baseline`."""
    es = proportion_effectsize(baseline + lift, baseline)
    return NormalIndPower().solve_power(effect_size=es, alpha=alpha,
                                        power=power, ratio=1)

def mde(baseline, n, alpha=0.05, power=0.8):
    """Smallest absolute effect detectable at this sample size."""
    return brentq(lambda d: required_n(baseline, d, alpha, power) - n, 1e-6, 0.1)

for metric in ["retention_1", "retention_7"]:
    baseline = df[df["version"] == "gate_30"][metric].mean()
    observed = (df[df["version"] == "gate_40"][metric].mean() - baseline)

    print(f"\n--- {metric} ---")
    print(f"Baseline (gate_30):      {baseline:.4f}")
    print(f"Observed effect:         {observed*100:+.2f}pp")
    print(f"n per arm:               {n_per_group:,}")
    print(f"MDE at n={n_per_group:,}:      {mde(baseline, n_per_group)*100:.2f}pp")
    print(f"n needed for 1pp lift:   {required_n(baseline, 0.01):,.0f} per arm")