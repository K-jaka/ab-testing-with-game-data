# A/B Test Analysis — Mobile Game Progression Gate

Analysis of a randomised experiment testing whether moving a mobile game's first progression gate from level 30 to level 40 improves player retention.

**Recommendation: do not ship.** Moving the gate to level 40 reduced 7-day retention by 0.82 percentage points (95% CI [−1.33, −0.31], p = 0.0016). All measured metrics moved in the same negative direction.

---

## The question

Cookie Cats places a progression gate that forces players to wait — or pay — before continuing. Moving it later (level 40 instead of 30) lets players get further before hitting friction, which might improve retention. Or the gate might be what creates the anticipation that brings players back.

The experiment tests which.

**Data:** 90,189 players randomly assigned on install to `gate_30` (control) or `gate_40` (treatment). Source: [Kaggle — Mobile Games A/B Testing, Cookie Cats](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats).

---

## Experiment design

| | |
|---|---|
| **Unit of randomisation** | Player, assigned at install |
| **Primary metric** | 7-day retention |
| **Guardrail metrics** | 1-day retention, game rounds played (14 days) |
| **Sample size** | 44,699 per arm (after exclusions) |
| **α / power** | 0.05 / 0.80 |

The primary metric was fixed before analysis. 7-day retention was chosen over 1-day because the gate sits at level 30 — most players do not reach it within a single day, so a 1-day effect would be surprising and a 7-day effect is where the mechanism should show up.

### Power

| Metric | Baseline | MDE at n = 44,699 | Observed effect |
|---|---|---|---|
| 7-day retention | 19.02% | 0.74pp | −0.82pp |
| 1-day retention | 44.82% | 0.93pp | −0.59pp |

The experiment is adequately powered for the primary metric and **underpowered for 1-day retention** — the observed 0.59pp effect sits below the 0.93pp threshold the sample can reliably detect. This matters for interpretation and is addressed in the results.

---

## Sanity checks

Run before any outcome analysis (`src/sanity_checks.py`).

**Sample Ratio Mismatch.** Expected a 50/50 split; observed 50.44% / 49.56% — an imbalance of ~790 players. Chi-square goodness-of-fit: **p = 0.0086**.

This does not cross the conventional SRM alarm threshold of p < 0.001. That threshold is deliberately stricter than 0.05 because SRM checks run on every experiment, and a 0.05 threshold would flag one in twenty healthy tests as broken. At p = 0.0086 the imbalance is not dismissible either — in a production setting this would warrant checking the assignment service and logging pipeline before trusting results. It is recorded here as a limitation rather than a blocker.

**Duplicate users.** None. No player appears in both arms, so independence holds.

**Missing data.** None across all five columns.

**Outlier.** One player recorded 49,854 game rounds in 14 days — roughly 148 rounds per hour, continuously, for two weeks. The next highest value is 2,961. This is implausible for a human player and is treated as a bot or logging error. **Excluded from all analysis.** Because the primary metric is binary retention, this exclusion has negligible effect on the headline result; it matters for the game-rounds guardrail, where a single extreme value would distort any mean-based comparison.

---

## Results

### Primary metric — 7-day retention

| | |
|---|---|
| Control (`gate_30`) | 19.02% |
| Treatment (`gate_40`) | 18.20% |
| **Difference** | **−0.82pp** |
| 95% CI | [−1.33pp, −0.31pp] |
| z / p | −3.157 / **0.0016** |

The confidence interval excludes zero across its full range: the data is consistent with a reduction between 0.31 and 1.33 percentage points, and inconsistent with any improvement.

**Bootstrap validation** (10,000 resamples) reproduces this by a fully non-parametric route: mean difference −0.82pp, 95% percentile interval [−1.32pp, −0.32pp], and **99.9% of resamples show `gate_40` performing worse**. Two independent methods, same answer.

### Guardrails

**1-day retention:** −0.59pp, 95% CI [−1.24pp, +0.06pp], p = 0.0739. Not significant at α = 0.05.

This should not be read as "no effect." The interval is almost entirely below zero, and the power analysis shows the experiment could not reliably detect an effect this small. The correct statement is that the experiment was underpowered for this metric — a directionally negative result that the sample size cannot confirm.

**Game rounds played:** median 17 (control) vs 16 (treatment), Mann-Whitney U p = 0.0509. A rank-based test was used because the distribution is severely right-skewed (mean 51.9, median 16). Borderline, and directionally negative.

### Multiple comparisons

Three hypotheses were tested, so p-values were adjusted with the Benjamini-Hochberg procedure to control the false discovery rate:

| Metric | Raw p | Adjusted p | Significant |
|---|---|---|---|
| 7-day retention | 0.0016 | 0.0048 | Yes |
| 1-day retention | 0.0739 | 0.0739 | No |
| Game rounds | 0.0509 | 0.0739 | No |

The primary result survives correction comfortably. The conclusion rests on the metric declared primary in advance, not on a metric selected after seeing the data.

---

## Why there is no subgroup analysis

Segmenting by engagement level is the obvious next step and appears in many analyses of this dataset. It is not valid here.

`sum_gamerounds` is measured **after** assignment, which means the treatment influences it. Splitting on a post-treatment variable breaks the comparability that randomisation established: within a given engagement bucket, the control and treatment players are no longer exchangeable, because different players sorted into that bucket for different reasons. Any resulting subgroup effect confounds the treatment effect with selection.

This dataset contains no pre-treatment covariates — only `userid`, `version`, and post-assignment outcomes. There is therefore nothing available to segment on legitimately, and no subgroup analysis is reported.

In a production setting, the fix is to log pre-treatment attributes (acquisition channel, device, install cohort) at assignment time, and pre-register which segments will be examined.

---

## Recommendation

**Do not move the gate to level 40.**

7-day retention falls by 0.82pp, a statistically significant result that survives multiple-comparison correction and is confirmed by bootstrap. Both guardrails move in the same direction. Nothing in the data supports the change.

At a baseline of 19.02%, a 0.82pp reduction is a relative decline of about 4.3% in 7-day retained players — material at scale.

The mechanism is worth noting for future tests: the gate may function as a break that builds anticipation to return, rather than as pure friction. That hypothesis is testable — for example, by varying gate duration rather than gate position.

---

## Limitations

- **Borderline SRM (p = 0.0086).** Below the conventional alarm threshold but not clean. In production this would be investigated before acting on results.
- **No pre-treatment covariates**, so no valid heterogeneity analysis and no ability to verify covariate balance beyond group size.
- **Short horizon.** Retention is measured at 1 and 7 days only. A change that reduces 7-day retention could in principle behave differently at 30 or 90 days.
- **Single cohort, unknown period.** No information on test duration, seasonality, or whether the effect is stable over time. Novelty effects cannot be ruled out.
- **No A/A validation.** A pre-period A/A test would confirm the assignment mechanism produces no spurious difference; none is available here.
- **Underpowered for 1-day retention**, so that guardrail is directionally suggestive rather than conclusive.

---

## Repository

```
├── data/
│   └── cookie_cats.csv
└── src/
    ├── sanity_checks.py      # SRM, duplicates, nulls, outliers
    ├── power.py              # MDE and required sample size
    ├── analysis.py           # z-tests, confidence intervals, bootstrap, Mann-Whitney
    └── multiple_testing.py   # Benjamini-Hochberg correction
```

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/sanity_checks.py
python src/power.py
python src/analysis.py
python src/multiple_testing.py
```

**Stack:** Python, pandas, NumPy, SciPy, statsmodels