# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# Final Answer: Causal Effect of BMI on DLBCL Risk Using Genetic Instruments

## a) Interpretation of the Difference Between Observational (12%) and IV (5%) Estimates

The 57% reduction in the estimated effect (from 12% to 5%) between the observational and instrumental variable estimates suggests **confounding in the observational association rather than violation of IV assumptions per se**. 

In observational studies, BMI is associated with numerous unmeasured or inadequately controlled confounders (socioeconomic status, lifestyle factors, dietary patterns, physical activity, comorbidities) that may independently affect DLBCL risk. The observational estimate of 12% likely captures both the true causal effect of BMI and positive confounding bias from these factors. The IV estimate of 5%, being based on random allocation of genetic variants at conception (following Mendelian inheritance), is protected against these confounders and thus represents a more plausible causal effect. This pattern—where IV estimates are smaller than observational estimates—is common and reflects the removal of confounding bias. However, the IV estimate may itself be biased downward if pleiotropy is present, making the true causal effect potentially larger than 5% but smaller than 12%.

## b) Core Mendelian Randomization Assumptions and Pleiotropy Violation

The three core MR assumptions are:

**1. Relevance (Association with exposure):** The PGS explains only 6% of BMI variance, indicating weak instruments. While 100 variants provide some statistical power, this explains modest variation, potentially causing attenuation bias in the IV estimate and reduced precision.

**2. Independence (No confounding of instruments):** This assumes genetic variants are not associated with confounders. However, genetic variants affecting obesity-related pathways may be pleiotropic, affecting metabolic, inflammatory, and immune pathways independently relevant to DLBCL development.

**3. Exclusion Restriction (No direct effect on outcome except through exposure):** This is violated when variants have pleiotropic effects. The problem statement explicitly indicates that "some genetic variants have pleiotropic effects—they influence other traits such as inflammation, which may independently affect DLBCL risk." This is horizontal pleiotropy: genetic variants affect DLBCL risk through pathways other than BMI (e.g., inflammation → DLBCL independent of BMI's effect on DLBCL).

**Pleiotropy's Impact:** Horizontal pleiotropy introduces bias directly into the IV estimate. Pleiotropic variants that increase DLBCL risk through inflammation (independent of BMI) will artificially inflate the estimated causal effect of BMI. Conversely, variants with pleiotropic protective effects would attenuate the estimate. The presence of pleiotropy undermines the validity of the causal inference because the IV estimate no longer isolates the effect of BMI alone but conflates it with independent pathway effects.

## c) Statistical Methods to Detect and Correct for Pleiotropy

**Method 1: MR-Egger Regression**
MR-Egger regression relaxes the exclusion restriction assumption by allowing a non-zero intercept, which directly detects horizontal pleiotropy. The intercept term quantifies the average pleiotropic effect across instruments. If the MR-Egger intercept is significantly different from zero, horizontal pleiotropy is present. The slope coefficient provides a pleiotropy-adjusted causal estimate. However, MR-Egger has reduced statistical power and requires more stringent assumptions about the distribution of pleiotropic effects (InSIDE assumption).

**Method 2: MR-Pleiotropy RESidual Sum and Outlier (MR-PRESSO) Test**
MR-PRESSO detects individual variants with outlier causal estimates (suggesting pleiotropic effects) through a residual sum of squares test. It iteratively identifies and removes variants with large deviations from the overall estimate. After outlier removal, it re-estimates the causal effect with the remaining "valid" variants. This approach is useful when pleiotropy is concentrated in a subset of variants rather than distributed across all instruments.

**Method 3: Iterative Mendelian Randomization and Pleiotropy (IMRP)**
IMRP iteratively searches for horizontally pleiotropic variants by comparing causal effect estimates and identifying variants whose exclusion improves homogeneity of estimates across the instrument set. It systematically removes suspected pleiotropic variants until the remaining set produces stable, consistent estimates.

## d) Interpretation of the Pleiotropy Removal Trade-off

Removing 20% of variants (suspected pleiotropic ones) reduces the IV estimate from 5% to 3% and increases variance. This trade-off reflects:

**Effect size reduction:** The 40% decrease (5% → 3%) suggests that the removed variants were contributing upward bias to the original estimate. These variants likely had pleiotropic effects that independently increased DLBCL risk (e.g., through inflammation), inflating the estimate of BMI's effect. Removing them yields a more conservative, potentially more accurate causal estimate.

**Variance increase:** Removing 20 variants from a set of 100 reduces the precision of estimation (larger standard errors, wider confidence intervals). This reflects the classic bias-variance trade-off: we reduce bias at the cost of increased uncertainty.

**Interpretation:** The 3% estimate is likely more reliable than 5% because it removes known confounders (pleiotropic effects), but the increased uncertainty means we have less confidence in the precise magnitude. The true causal effect likely lies in the range suggested by the 3% estimate ± larger confidence interval. This smaller estimate (3%) is now closer to the lower bound of what the true effect could be, with confounding-inflated observational estimates (12%) representing an upper bound. A reasonable interpretation is that BMI's true causal effect on DLBCL is probably in the range of 3–5%, substantially lower than the confounded observational estimate of 12%.

## e) Step-by-Step Algorithmic Analysis Plan for Robust Causal Effect Estimation

```
ALGORITHM: Robust Mendelian Randomization Analysis for BMI → DLBCL Causality

INPUT: 
  - PGS with 100 BMI-associated genetic variants
  - Variant-BMI associations (β_gx, SE_gx)
  - Variant-DLBCL associations (β_gy, SE_gy)
  - Summary statistics for pleiotropy-suspected variants
  - Population LD structure (for sensitivity checks)

STEP 1: ASSESS INSTRUMENT STRENGTH
  1.1 Calculate F-statistic for each variant: F = (β_gx)² / (SE_gx)²
  1.2 Calculate mean F-statistic across all variants
  1.3 IF mean F < 10: flag weak instrument bias; consider adjustments
  1.4 IF many variants have F < 10: consider weighted analysis downweighting weak variants

STEP 2: ESTIMATE BASELINE IV CAUSAL EFFECT (Inverse-Variance Weighted, IVW)
  2.1 Perform standard IVW meta-analysis: β_IV = Σ(β_gx × β_gy × w_i) / Σ(β_gx² × w_i)
      where w_i = 1 / SE_gy²
  2.2 Calculate 95% CI and standard error
  2.3 Document baseline estimate (expected ~5% based on problem)
  2.4 OUTPUT: β_IVW = 5% (95% CI: [a, b])

STEP 3: TEST FOR HORIZONTAL PLEIOTROPY
  3.1 Perform MR-Egger regression:
      - Regress β_gy on β_gx with intercept (not constrained to zero)
      - Extract intercept and test H0: intercept = 0
  3.2 Perform MR-PRESSO global test:
      - Calculate residual sum of squares
      - Test for significance via simulation
  3.3 Calculate Cochran's Q statistic for heterogeneity:
      Q = Σ w_i × (β_gy/β_gx - β_IV)²
  3.4 IF Q significant or MR-Egger intercept significant: pleiotropy is present
  3.5 OUTPUT pleiotropy test results

STEP 4: IDENTIFY PLEIOTROPIC VARIANTS (Outlier Detection)
  4.1 For each variant, calculate Wald ratio: θ_i = β_gy / β_gx
  4.2 Compare θ_i to overall IVW estimate β_IV
  4.3 Calculate standardized residuals: z_i = |θ_i - β_IV| / SE(θ_i)
  4.4 Flag variants with |z_i| > 3 as potential outliers (pleiotropic)
  4.5 Perform MR-PRESSO outlier detection algorithm:
      - Iteratively remove variants with largest contribution to heterogeneity
      - Re-estimate β_IV after each removal
      - Stop when Q-statistic becomes non-significant
  4.6 Cross-reference flagged variants with prior knowledge on pleiotropic pathways
      (e.g., inflammation-related genes)
  4.7 OUTPUT: List of suspected pleiotropic variants and removal justification

STEP 5: PERFORM SENSITIVITY ANALYSES WITH MULTIPLE METHODS
  5.1 MR-Egger regression:
      - Estimate pleiotropy-adjusted causal effect
      - IF MR-Egger intercept ≠ 0: pleiotropy confirmed; use slope as alternative estimate
      - OUTPUT: β_Egger (usually has wider CI due to lower power)
  
  5.2 Weighted Median Method:
      - Calculate causal effect using median of variant-specific estimates
      - Robust to up to 50% pleiotropic variants
      - OUTPUT: β_weighted_median
  
  5.3 Simple Mode Method:
      - Group variant-specific estimates into modes
      - Select mode with largest cluster as causal effect
      - Assumes plurality of variants share true causal effect
      - OUTPUT: β_simple_mode
  
  5.4 MR-PRESSO with outlier removal:
      - Re-estimate IV causal effect after removing outliers
      - OUTPUT: β_PRESSO_corrected, list of removed variants

STEP 6: EVALUATE CONSISTENCY ACROSS METHODS
  6.1 Tabulate all causal estimates: β_IVW, β_Egger, β_median, β_mode, β_PRESSO
  6.2 Assess directional consistency (all estimates have same sign)
  6.3 Assess magnitude consistency (estimates within reasonable range of each other)
  6.4 IF estimates highly discordant: pleiotropy likely, use more conservative estimate
  6.5 IF estimates concordant: pleiotropy likely minimal, use IVW as primary estimate
  6.6 OUTPUT: Sensitivity analysis table with all estimates and 95% CIs

STEP 7: VARIANT REMOVAL AND RE-ANALYSIS
  7.1 Create three instrument sets:
      - Full set (100 variants)
      - Conservative set (remove outliers identified in Step 4)
      - Aggressive set (remove 20% of variants with highest pleiotropy suspicion)
  7.2 Repeat Steps 2–6 for each instrument set
  7.3 Document how causal estimates change:
      - Expected: removing pleiotropic variants should reduce estimate magnitude
      - Increased variance expected due to loss of information
  7.4 OUTPUT: Comparative estimates: β_full, β_conservative, β_aggressive

STEP 8: POWER AND PRECISION ASSESSMENT
  8.1 For each instrument set, calculate statistical power:
      - Power = P(reject H0 | true effect exists), based on sample sizes and F-statistics
  8.2 Calculate 95% CI width for each estimate
  8.3 Assess whether estimates remain statistically significant after pleiotropy adjustment
  8.4 IF power becomes insufficient after variant removal: acknowledge precision loss
  8.5 OUTPUT: Power estimates and CI widths for all models

STEP 9: DIRECTIONAL PLEIOTROPY ASSESSMENT
  9.1 For each pleiotropic variant, determine direction of pleiotropy:
      - If variant increases both BMI and DLBCL → positive pleiotropy (inflates causal estimate)
      - If variant increases BMI but decreases DLBCL → negative pleiotropy (deflates estimate)
  9.2 Assess whether pleiotropic effects are randomly distributed or systematically biased
  9.3 IF systematic bias detected: note direction of bias in final estimate
  9.4 OUTPUT: Pleiotropy direction assessment

STEP 10: ROBUSTNESS AND INTERPRETATION
  10.1 Compare IV causal estimates (range: 3–5%) with observational estimate (12%)
  10.2 Conclude that observational estimate is biased upward by confounding
  10.3 State primary causal estimate: select most robust estimate from sensitivity analyses
       (likely β_PRESSO or β_conservative after removing outliers)
  10.4 Report 95% CI around primary estimate
  10.5 Interpret magnitude: e.g., "Each 1-unit increase in genetically predicted BMI 
       is causally associated with a 3–5% increase in DLBCL risk, substantially lower 
       than the confounded observational estimate."
  10.6 Acknowledge remaining uncertainty from weak instruments and potential residual pleiotropy
  10.7 OUTPUT: Final causal estimate with interpretive statement

STEP 11: VISUALIZATION AND REPORTING
  11.1 Create forest plot of variant-specific estimates
  11.2 Create scatter plot: β_gy vs β_gx with fitted IVW, MR-Egger, and outlier-removed lines
  11.3 Create sensitivity analysis comparison plot (bar chart of all methods' estimates)
  11.4 Table summarizing pleiotropy tests (MR-Egger intercept, Q-test, MR-PRESSO)
  11.5 Create funnel plot (β_gy/β_gx vs 1/SE_gy) to visualize outliers and asymmetry
  11.6 OUTPUT: Complete publication-quality figures and supplementary tables

OUTPUT: 
  - Primary causal estimate: β_causal (3–5% per BMI unit)
  - 95% Confidence interval
  - Pleiotropy test results (MR-Egger intercept p-value, Q-test p-value)
  - Sensitivity analysis estimates and comparison
  - List of identified pleiotropic variants
  - Interpretation: "BMI has a causal effect on DLBCL risk, but smaller than observational 
    confounding suggested. Genetic pleiotropy was detected and addressed through multiple 
    sensitivity methods, all yielding consistent causal estimates in the 3–5% range."
  - Limitations: weak instruments (R² = 6%), residual pleiotropy risk, sample size constraints

END ALGORITHM
```

---

## Summary Interpretation

The analysis demonstrates that BMI likely has a **genuine causal effect on DLBCL risk of approximately 3–5% per unit BMI increase**, substantially lower than the confounded observational estimate of 12%. The difference reflects confounding in observational data (not IV assumption violation). Horizontal pleiotropy from inflammation-related genetic pathways inflates even the IV estimate, necessitating sensitivity analyses. Removing pleiotropic variants reduces the estimate further (3%) with increased uncertainty—a reasonable trade-off for reduced bias. The robust analytical approach outlined combines multiple pleiotropy detection and correction methods to triangulate the most reliable causal estimate, acknowledging both the evidence for pleiotropy and the inherent limitations of weak genetic instruments.