# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# FINAL ANSWER: Causal Effect of BMI on DLBCL Using Genetic Instruments

## a) Interpretation of the Difference Between Observational (12%) and IV (5%) Estimates

The 2.4-fold difference between the observational estimate (12%) and the instrumental variable estimate (5%) does **not** indicate confounding in the traditional sense. Rather, it suggests:

**Observational bias upward**: The observational association of 12% is likely inflated by confounding and/or reverse causality. Unmeasured confounders (lifestyle factors, socioeconomic status, dietary patterns) that influence both BMI and DLBCL risk would bias the observational estimate upward.

**IV estimate closer to truth**: The IV estimate (5%) is more resistant to confounding because genetic variants are randomized at conception. However, the IV estimate being lower suggests the true causal effect of BMI on DLBCL is substantially smaller than the observed correlation.

**Violation of IV assumptions**: The discrepancy primarily reflects either (1) violation of the exclusion restriction (pleiotropy), or (2) weak instrument bias combined with winner's curse (the PGS explains only 6% of BMI variance, which is modest). The 6% R² indicates the instrument has limited strength, which could attenuate IV estimates toward the null under certain conditions.

---

## b) Violated Mendelian Randomization Assumptions and Pleiotropy Effects

The three core MR assumptions are:

**1. Relevance (Assumption 1): VIOLATED to a moderate degree**
- The PGS explains only 6% of BMI variance, indicating weak instrument strength
- Weak instruments can lead to large standard errors and bias (Weak Instrument Bias)
- The F-statistic should exceed 10; with 6% variance explained, this instrument may be underpowered

**2. Exclusion Restriction (Assumption 2): VIOLATED**
- The explicit mention of suspected pleiotropic variants violates the exclusion restriction
- Pleiotropic variants influence DLBCL risk through pathways other than BMI (e.g., via inflammation)
- This creates a "backdoor" path: Genetic variant → [Inflammation/immune dysfunction] → DLBCL, independent of BMI
- Such horizontal pleiotropy biases the IV estimate; the direction depends on whether pleiotropic effects increase or decrease DLBCL risk

**3. Independence (Assumption 3): Likely satisfied**
- Genetic variants are randomized at conception, so they should be independent of confounders
- However, population stratification (if not controlled) could violate this

**How Pleiotropy Affects Validity**:
- If the pleiotropic variants increase both inflammation and DLBCL risk, the IV estimate is biased upward
- If pleiotropic variants decrease DLBCL risk through competing mechanisms, the IV estimate is biased downward
- The net bias direction is unknown without biological knowledge of each variant's pleiotropic effects
- Pleiotropy explains why removing suspected pleiotropic variants changes the estimate (see section d)

---

## c) Statistical Methods to Detect and Correct for Pleiotropy

**Method 1: MR-Egger Regression**
- Performs weighted linear regression of SNP-DLBCL effects on SNP-BMI effects, forcing regression through origin (standard IV) or allowing intercept
- The intercept term estimates unbalanced horizontal pleiotropy
- If intercept ≠ 0, pleiotropy is present
- The MR-Egger slope provides a corrected causal estimate, though at cost of reduced power and additional assumption (InSIDE: Instrument Strength Independent of Direct Effect)
- Apply: Regress (SNP effects on DLBCL) on (SNP effects on BMI); test if intercept differs from zero

**Method 2: Weighted Median and Mode-Based Estimation**
- Weighted Median: Uses the variant whose cumulative weight reaches 50%, making it robust to pleiotropy in up to 50% of variants
- Mode-Based Estimation: Identifies the "mode" of the distribution of variant-specific causal estimates, robust to pleiotropy if no single pleiotropic pathway dominates
- Both are less efficient than standard IV but tolerate arbitrary patterns of pleiotropy
- Apply: Calculate individual SNP causal effects (β_DLBCL/β_BMI) and identify the median/mode of this distribution

**Method 3: MR-PRESSO (Pleiotropy Residual Sum and Outlier)**
- Detects outlier variants (those with disproportionate residual variation) that may be pleiotropic
- Performs a global test for pleiotropy and identifies and removes outliers
- Recalculates IV estimate after removing detected pleiotropic variants
- Apply: Run PRESSO algorithm; iteratively identify and remove variants with high residual deviation; report effect estimates before and after outlier removal

**Method 4: Contamination Mixture Method (MR-Mix)**
- Assumes causal variants come from a true effect distribution and pleiotropic variants from a "null" distribution
- Uses finite mixture model to separately estimate the proportion of variants with direct effects on outcome
- Provides pleiotropy-corrected estimate
- Apply: Fit mixture model to distribution of SNP-specific estimates; report causal effect from true-effect component

---

## d) Interpretation of Removing 20% of Pleiotropic Variants

**Observation**: Removing 20% of variants reduces estimate from 5% to 3% and increases variance.

**Interpretation**:

**Direction of bias correction**: The decrease from 5% to 3% indicates the removed variants were **inflating** the causal estimate. This suggests the suspected pleiotropic variants had effects on DLBCL that were **in the same direction as the BMI effect** (i.e., they increased DLBCL risk independent of BMI). Removing them reveals a smaller true causal effect.

**The 3% figure**: This may be closer to the true causal effect, but assumes the removed variants were indeed pleiotropic and the retained variants satisfy MR assumptions.

**Increased variance trade-off**: Removing 20% of variants reduces statistical power (n decreases from 100 to 80). This increases the standard error and confidence interval width, even though the point estimate is lower. This is a classic bias-variance trade-off:
- **Reduced bias**: Pleiotropic confounding is partially mitigated
- **Increased variance**: Fewer variants = less information = wider confidence intervals
- **Lower precision**: The 3% estimate has wider uncertainty bands than the 5% estimate

**Critical assessment**: Without validation that the removed 20% are truly pleiotropic (vs. merely underpowered or affected by weak instrument bias), we cannot confidently claim 3% is superior to 5%. The direction of change (decreasing with removal) suggests pleiotropic inflation was present, but the trade-off necessitates sensitivity analyses across different variant subsets and robust pleiotropy testing.

---

## e) Step-by-Step Robust Analysis Algorithm

**ALGORITHM: Robust Causal Effect Estimation of BMI on DLBCL via Genetic Instruments**

```
INPUT: 
  - 100 independent BMI-associated SNPs with effect sizes (β_BMI, SE_BMI)
  - DLBCL GWAS summary statistics (β_DLBCL, SE_DLBCL)
  - Candidate pleiotropic variants identified
OUTPUT:
  - Causal effect estimate with confidence interval
  - Assessment of MR assumption violations
  - Sensitivity analysis results

STEP 1: Data Quality Control
  1.1 Harmonize alleles between BMI and DLBCL datasets (align effect alleles)
  1.2 Remove ambiguous SNPs (A/T, G/C) prone to strand misalignment
  1.3 Remove SNPs with |LD r| > 0.001 with other SNPs (ensure independence)
  1.4 Retain only SNPs with P < 5×10⁻⁸ for BMI (strong association)
  1.5 Remove SNPs with zero effect on DLBCL due to missing data
  OUTPUT: Curated set of valid instrumental variants (likely N < 100)

STEP 2: Assess Instrument Strength
  2.1 Calculate F-statistic for each SNP: F_i = (β_BMI,i / SE_BMI,i)²
  2.2 Calculate mean F-statistic: F_mean = mean(F_i)
  2.3 IF F_mean < 10: WARN of weak instrument bias
  2.4 Calculate PGS R² in external validation sample if available
  2.5 IF R² < 5%: Consider adding additional variants or acknowledge power limitations
  OUTPUT: Assessment of relevance assumption (Assumption 1)

STEP 3: Standard MR Analysis (Inverse-Variance Weighted)
  3.1 For each SNP i, calculate SNP-specific causal estimate: γ_i = β_DLBCL,i / β_BMI,i
  3.2 Calculate inverse-variance weighted average:
      β_IV = Σ(w_i × γ_i) / Σ(w_i), where w_i = 1 / SE_DLBCL,i²
  3.3 Calculate 95% CI using delta method: SE_IV = 1 / √Σ(w_i)
  OUTPUT: Point estimate (5%) with confidence interval, standard error

STEP 4: Test for Horizontal Pleiotropy (Exclusion Restriction)
  4.1 PERFORM MR-Egger Regression:
      - Regress β_DLBCL,i on β_BMI,i (weighted by w_i)
      - Allow non-zero intercept
      - Test if intercept ≠ 0 (indicates unbalanced pleiotropy)
      - Report MR-Egger point estimate as alternative
  4.2 PERFORM MR-PRESSO:
      - Calculate residuals for each SNP
      - Identify outliers (high residual deviation, P < 0.05)
      - Report number of outliers detected
      - Re-estimate effect after removing outliers
  4.3 CALCULATE Heterogeneity statistic (Q):
      Q = Σ w_i(γ_i - β_IV)²
      - High Q suggests heterogeneity, consistent with pleiotropy
  OUTPUT: Evidence of pleiotropy; list of detected pleiotropic variants

STEP 5: Pleiotropy-Robust Estimation Methods
  5.1 WEIGHTED MEDIAN APPROACH:
      - Sort SNPs by cumulative weight
      - Identify SNP where cumulative weight = 50%
      - Use that SNP's effect as robust estimate
      - Report 95% CI from bootstrap (1000 iterations)
  5.2 MODE-BASED ESTIMATION:
      - Calculate SNP-specific effects: γ_i = β_DLBCL,i / β_BMI,i
      - Create density plot of γ values
      - Identify mode (peak) of distribution
      - Report mode as pleiotropy-robust estimate
  5.3 MR-MIX (if sufficient variants):
      - Fit finite mixture model to γ distribution
      - Estimate proportion of true causal variants
      - Report mixture-corrected estimate
  OUTPUT: Three robust estimates; compare to IVW

STEP 6: Sensitivity Analysis on Variant Selection
  6.1 Progressively remove SNPs identified as pleiotropic:
      - Remove 0%, 10%, 20%, 30% of suspected pleiotropic variants
      - Re-estimate causal effect at each step
      - Plot effect estimate vs. % variants removed
      - Assess if effect stabilizes
  6.2 Stratify by variant characteristics:
      - Separate variants by biological pathway (inflammatory vs. metabolic)
      - Estimate causal effect within each stratum
      - Check for consistency across strata
  OUTPUT: Sensitivity plot; evidence of stability/instability

STEP 7: Population Stratification Check
  7.1 Perform MR analysis separately in ancestry-stratified subgroups (if data available)
  7.2 Test for heterogeneity of causal estimates across populations
  7.3 If heterogeneous: Report estimates by ancestry; note violation of Independence assumption
  OUTPUT: Ancestry-specific estimates; evidence of population structure

STEP 8: Check for Weak Instrument Bias and Winner's Curse
  8.1 Recalculate using LD clumping r² = 0.01 (stricter; removes collinear variants)
  8.2 Use split-sample validation (estimate SNP effects in one cohort; test in another)
  8.3 Apply shrinkage correction to SNP effects if winner's curse suspected
  OUTPUT: Bias-corrected estimate; comparison to main analysis

STEP 9: Report Summary Estimates
  9.1 Create summary table:
      | Method           | Estimate | 95% CI        | N_variants | Assumptions |
      | IVW              | 5%       | [X, Y]        | 100        | All 3       |
      | MR-Egger         | ...      | [X, Y]        | 100        | 1,3 only    |
      | Weighted Median  | ...      | [X, Y]        | 100        | 1 only      |
      | Mode-based       | ...      | [X, Y]        | 100        | 1 only      |
      | After removing 20% pleiotropy | 3% | [X, Y] | 80 | 2,3         |
  
  9.2 Interpretation:
      - IF estimates converge across methods → robust causal effect
      - IF estimates diverge → pleiotropy or weak instruments present
      - Favor estimate from method making fewest assumptions (Weighted Median/Mode)

STEP 10: Final Conclusion and Recommendations
  10.1 Synthesize findings:
       - Observational estimate (12%) is likely inflated by confounding
       - IV estimates (5% to 3%) suggest causal effect ~3–5% per BMI unit
       - Pleiotropy detected; effect robust to removal of pleiotropic variants
  10.2 Caveats:
       - Weak instrument strength (R² = 6%) limits precision
       - Unmeasured pleiotropy possible
       - Results require replication in independent cohort
  10.3 Recommend:
       - Obtain larger GWAS samples to strengthen instrument
       - Use genomic functional annotation to classify variants (reduce pleiotropy burden)
       - Conduct bidirectional MR: does DLBCL risk increase BMI? (test reverse causality)
       - External validation in independent cohort

OUTPUT: Robust causal estimate with uncertainty, assumption assessment, and sensitivity evidence
```

---

## Summary

**a)** The 12% vs 5% difference reflects observational confounding bias, not assumption violation per se, though weak instruments and possible pleiotropy contribute.

**b)** Pleiotropy violates the exclusion restriction (Assumption 2); weak instrument strength is a secondary concern affecting Assumption 1.

**c)** Use MR-Egger, MR-PRESSO, Weighted Median, and Mode-based estimation to detect and correct pleiotropy.

**d)** Removing pleiotropic variants reduces the estimate to 3%, indicating they inflated the causal effect; the increased variance reflects the bias-variance trade-off of using fewer instruments.

**e)** The algorithm systematically tests assumptions, identifies pleiotropy, applies robust methods, and validates findings before reporting a final causal estimate of **approximately 3–5% per BMI unit**, substantially lower than the observational 12%.