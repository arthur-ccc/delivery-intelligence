# Temporal diagnostics and late-delivery model development

The [diagnostics notebook](../notebooks/06_temporal_diagnostics.ipynb) reproduces the experiments using the same purchase-date partitions as the [original baseline](01_baseline_report.md). The new models use training orders that were already delivered when validation began. Model selection uses Average Precision (AP), and threshold selection maximizes F1. Both use the validation orders with known outcomes when the test period began. The test comparison is retrospective because the baseline report already used the test set.

## Changes across periods

- The late-delivery rate was **7.83% in training, 4.31% in validation, and 4.28% in testing**. Class imbalance makes high alert precision difficult. The validation and test rates differed by only 0.03 percentage points.
- The baseline's average score rose from **0.184** in the June portion of the test set to **0.223** in August. The share of flagged orders rose from **19.82% to 53.35%**. The observed late-delivery rates were **0.97% and 6.19%**, respectively.
- Purchase month and year showed the largest distribution shifts between training and testing, with KS statistics of **0.513** and **0.647**, respectively. Promised lead time (KS **0.337**) and freight cost (KS **0.181**) showed the largest shifts among the remaining features. Median promised lead time was **26 days** in the June portion of the test set, **20 days** in July, and **14 days** in August.
- The baseline purchase-date split included **3,100 training orders and 1,930 validation orders** whose deliveries had yet to be recorded at the next cutoff. The notebook uses a conservative cutoff based on recorded delivery timestamps. This reduces the availability of recent examples and may underrepresent orders that take longer to deliver.

## Controlled comparison

Promised lead time is the difference in calendar days between the estimated delivery date and the purchase date. The model uses this difference as a feature. The actual delivery timestamp is used to verify the label and determine which orders had known outcomes at each cutoff.

| Experiment | Validation AP with known outcomes |
|---|---:|
| Logistic regression with original features | 0.0613 |
| Logistic regression without purchase year | 0.0704 |
| Logistic regression without purchase month | 0.0707 |
| Logistic regression without purchase year and month | 0.0701 |
| Logistic regression without purchase year and month, with promised lead time | **0.1268** |
| Gradient boosting without purchase year and month | 0.0581 |
| Gradient boosting without purchase year and month, with promised lead time | 0.1107 |

With the same cutoffs and other features held fixed, adding promised lead time raised logistic regression AP from **0.0701 to 0.1268**. Gradient boosting also improved with the feature, and logistic regression achieved the highest AP. The validation cohort used for model selection had a late-delivery rate of **4.28%**.

## Historical test performance

| Metric | Original baseline | Logistic regression with promised lead time |
|---|---:|---:|
| Average Precision | 0.0408 | 0.0680 |
| ROC-AUC | 0.4620 | 0.6235 |
| Alert precision | 3.17% | 4.88% |
| Recall | 34.68% | 29.35% |
| F1 | 0.0582 | 0.0837 |
| False positives | 6,559 | 3,547 |
| Late orders identified | 215 | 182 |

Restricting the baseline to known labels left test AP nearly unchanged (0.0412). Removing purchase month alone or removing both purchase month and year reduced alert volume. Both models reached an AP of 0.0389, below the late-delivery rate of 4.28%. Reliance on calendar features helps explain the excess alerts, and dropping those features alone failed to improve the risk ranking.

The candidate generated 3,012 fewer false positives and identified 33 fewer late orders. About one in 20 alerts corresponded to a late order. The threshold maximizes validation F1 and still needs to be evaluated against the number of alerts the operation can handle.

## Evaluation scope

The estimated delivery field needs to be verified as the promise available at checkout. A later update would introduce future information. The historical cohort covers delivered orders with valid dates and effectively ends in August 2018. To assess stability, evaluate successive forecast origins with sufficiently mature purchase cohorts and fix the selection criteria before evaluating a final period.
