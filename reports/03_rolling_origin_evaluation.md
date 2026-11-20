# Rolling-origin evaluation of the promised-lead-time model

The [evaluation notebook](../notebooks/07_rolling_origin_evaluation.ipynb) tests the logistic regression selected in the [temporal diagnosis](02_temporal_diagnostics.md) across eight purchase cohorts from January to August 2018. The paired regression uses the same preprocessing and inputs, with promised lead time omitted. Both variants exclude purchase month and year.

## Protocol

Each test cohort starts on the first day of the month. Training uses an expanding history of purchases delivered before the calibration month. The calibration cohort comes from two months before the test month. The intervening month gives deliveries time to mature. Each variant's alert threshold maximizes F1 among calibration orders delivered before the first day of the test month. The model and threshold remain fixed throughout that month. Test metrics use the eventual outcomes of delivered orders.

For the June fold, training ends before April 1, calibration uses April purchases delivered before June 1, and the fixed model scores June purchases. The maturation month is a protocol choice. Orders still undelivered at the cutoff are excluded from threshold tuning, which can under-represent slow deliveries.

## Monthly results

| Test month | Orders | Late orders | Late rate | AP without promise | AP with promise | Alert rate with promise |
|---|---:|---:|---:|---:|---:|---:|
| January | 7,069 | 403 | 5.70% | 0.0749 | 0.0847 | 60.83% |
| February | 6,555 | 926 | 14.13% | 0.1731 | 0.1967 | 68.39% |
| March | 7,003 | 1,328 | 18.96% | 0.2654 | 0.2872 | 34.01% |
| April | 6,798 | 306 | 4.50% | 0.1258 | 0.1724 | 31.42% |
| May | 6,749 | 443 | 6.56% | 0.0921 | 0.1478 | 35.96% |
| June | 6,096 | 71 | 1.16% | 0.0250 | 0.0748 | 1.67% |
| July | 6,156 | 208 | 3.38% | 0.0459 | 0.0752 | 23.98% |
| August | 6,351 | 393 | 6.19% | 0.0453 | 0.0711 | 23.60% |

Adding promised lead time improved Average Precision (AP) in all eight months and exceeded the no-skill reference (the late rate) in each month. Mean monthly AP increased from **0.1059 to 0.1387**. The weakest margin above the late rate was in August, with AP **0.0711** and ROC-AUC **0.5290**. At the selected thresholds, July F1 fell from **0.1039 to 0.0903** despite higher AP.

| Metric | Without promise | With promise |
|---|---:|---:|
| Mean monthly ROC-AUC | 0.5774 | 0.6497 |
| Mean monthly F1 | 0.1392 | 0.1828 |
| Correct late alerts | 1,944 | 2,342 |
| False alerts | 19,125 | 16,463 |
| Aggregate precision | 9.23% | 12.45% |
| Aggregate recall | 47.67% | 57.43% |
| Aggregate alert rate | 39.92% | 35.63% |

Mean metrics weight each month equally. Aggregate metrics use summed confusion counts over **52,777 orders** and **4,078 delays**. The model with promised lead time found **398 more delays** and generated **2,662 fewer false alerts**. Its monthly alert rate still ranged from **1.67% to 68.39%**. The gain in ranking was consistent, while the workload from thresholds calibrated to maximize F1 varied substantially.

## Alert budget fixed before each window

The experiment uses a 10% capacity scenario with the promised-lead-time model and the same eight folds. Each month starts with a minimum score set to the 90th percentile of scores in its calibration cohort. The policy processes orders in purchase order. An eligible order can trigger an alert when cumulative alerts are below one per ten orders observed so far. Unused capacity carries forward within the month. A prefix check verifies the cap after every order. This policy changes how alerts are issued and uses the same model scores as the F1 policy.

| Metric | F1 threshold | 10% budget |
|---|---:|---:|
| Alerts | 18,805 | 4,539 |
| Alert rate | 35.63% | 8.60% |
| True late alerts | 2,342 | 685 |
| False alerts | 16,463 | 3,854 |
| Aggregate precision | 12.45% | 15.09% |
| Aggregate recall | 57.43% | 16.80% |
| Mean monthly F1 | 0.1828 | 0.1504 |

| Test month | Alert rate | Precision | Recall | Alerts / capacity |
|---|---:|---:|---:|---:|
| January | 6.37% | 13.11% | 14.64% | 450 / 706 |
| February | 9.99% | 20.15% | 14.25% | 655 / 655 |
| March | 9.98% | 27.04% | 14.23% | 699 / 700 |
| April | 9.97% | 14.90% | 33.01% | 678 / 679 |
| May | 8.25% | 18.31% | 23.02% | 557 / 674 |
| June | 4.13% | 7.94% | 28.17% | 252 / 609 |
| July | 9.97% | 6.19% | 18.27% | 614 / 615 |
| August | 9.98% | 6.94% | 11.20% | 634 / 635 |

The budget policy cut total alerts by 75.86% and increased precision by 2.64 percentage points, while recall fell by 40.63 points. It stayed within capacity in every month. In January and June, fewer than 10% of orders met the minimum score. In May, 11.36% met the score floor, but their arrival order limited use of capacity as it accrued. June was the only month in which the budget policy alerted on more orders than the F1 policy, raising recall from 19.72% to 28.17% while precision fell from 13.73% to 7.94%.

## Promised delivery date provenance

Olist's public dataset card describes the estimated delivery date as a trigger for the post-purchase satisfaction survey. The accessible documentation does not establish whether the exported field preserves the original checkout promise or a later revision. The local orders CSV contains 99,441 rows, one per order ID, with no missing estimated dates or estimates before the purchase day. These checks establish consistency within the snapshot. The CSV contains no promise version history, so checkout-time availability remains unverified. A checkout or order-created event with the original promise, or an explicit confirmation from the data owner, would resolve the question. [Olist dataset card](https://www.kaggle.com/olistbr/brazilian-ecommerce/home/)

## Fixed daily review capacity

The same out-of-sample scores were used to simulate 10, 20 and 30 reviews per calendar day. The immediate policy issues alerts in purchase order, using a score floor fixed from the preceding calibration cohort and stopping when the daily cap is reached. The daily queue ranks purchases at the next midnight and fills up to the cap with orders still undelivered at that time. It assumes delivery status is observable by the review cutoff. Both policies discard unused capacity at the end of the day.

| Reviews per day | Policy | Reviews | Late orders found | False alerts | Precision | Recall | Mean wait |
|---:|---|---:|---:|---:|---:|---:|---:|
| 10 | Immediate | 1,847 | 292 | 1,555 | 15.81% | 7.16% | 0 h |
| 10 | Daily queue | 2,410 | 418 | 1,992 | 17.34% | 10.25% | 8.17 h |
| 20 | Immediate | 3,788 | 517 | 3,271 | 13.65% | 12.68% | 0 h |
| 20 | Daily queue | 4,811 | 725 | 4,086 | 15.07% | 17.78% | 8.21 h |
| 30 | Immediate | 5,664 | 703 | 4,961 | 12.41% | 17.24% | 0 h |
| 30 | Daily queue | 7,211 | 965 | 6,246 | 13.38% | 23.66% | 8.16 h |

At 20 reviews per day, the queue found 208 more late orders and required 1,023 more reviews, including 815 additional false alerts. Queue precision varied from 4.50% in June to 34.84% in March. It found more late orders in all eight months at that cap. The comparison measures the combined effect of ranking at the cutoff and filling more slots because the queue has no minimum score. It does not isolate the effect of ranking at equal realized review volume. The simulations measure detection, and the dataset does not show whether an intervention after review would prevent a delay.

## Scope

The eight test cohorts contain distinct orders, and successive training histories overlap. The evaluation is retrospective because the feature and model were chosen using earlier analyses of this dataset. August ends on the 29th, and the source cohort contains only delivered orders with valid dates. The workload figures therefore use the historical delivered-order cohort as their denominator. Actual review capacity, review cadence, and the time available for an intervention remain to be established.
