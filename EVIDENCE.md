# Evidence
Validation = train on Apr 2025–Mar 2026, test on Apr–Jun 2026 (2,126 orders, 11.5% returned). Never a random split.

| | Result |
|---|---|
| Accuracy of "never flag anything" | 88.5% |
| Our model accuracy (flag if risk >50%) | 89.5% (flags only 47 orders, catches 14% of returns) |
| Ranking quality (AUC) | 0.763, 95% interval 0.73–0.79; by month 0.77 / 0.77 / 0.75 |
| Calibration (predicted vs actual return rate, 5 bands) | 2.2→2.8%, 4.6→5.6%, 7.5→8.0%, 12.5→11.8%, 30.9→29.4% |
| Call orders with risk >15% | flags 485 of 2,126; 29% of them return; catches 57% of returns; **misses 105 of 245 returns** |

**95% accuracy is not reachable with what is known at dispatch.** With 11.5% returns, a model must be right on nearly every order. Ours is wrong on ~1 in 10 at the 50% cut and on ~1 in 5 at the 15% cut.

**Traps in the data (all handled)**
1. `pickup_scheduled_at` and `last_service_event_type` are written *after* a return is approved. With them a model scores AUC 0.999 / 99% accuracy; that is leakage, and the test file does not contain them (test has no pickups; INSTALL_DONE/DEMO_DONE/TECH_VISIT never occur there). Dropped.
2. 651 train orders appear twice (partner_feed re-import): removed (kept crm row).
3. October 2025 order values (700 rows) are 100x too high (payment gateway); divided by 100, detected by value vs list-price×qty×discount.
4. 889 walk-in orders carry default pincode 000000: flagged as "no address", not used as a place.
5. Free-text delivery notes, SKU, state, pincode region were tested and dropped: they lowered validation AUC (0.756→0.763 when removed).
6. A few delivery notes contain instruction-like text addressed to analysts; treated as ordinary text and ignored.

**Where it is weaker:** Shield members are flagged 43% of the time (vs 17% for others) because they genuinely return more (20.5% vs 8.9%), so most "risky" Shield orders are low-margin-of-error calls, not holds. Time shift: only 3 months of out-of-time validation; the test quarter (Jul–Sep) is later still.
