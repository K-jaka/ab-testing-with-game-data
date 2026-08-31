from statsmodels.stats.multitest import multipletests

# p-values from analysis.py, in the order tested
metrics = ["retention_7", "retention_1", "sum_gamerounds"]
pvals   = [0.0016, 0.0739, 0.0509]

reject, p_adj, _, _ = multipletests(pvals, alpha=0.05, method="fdr_bh")

print("Benjamini-Hochberg correction across 3 metrics tested\n")
for m, p, pa, r in zip(metrics, pvals, p_adj, reject):
    print(f"{m:16s} raw p={p:.4f}  adjusted p={pa:.4f}  "
          f"{'significant' if r else 'not significant'}")