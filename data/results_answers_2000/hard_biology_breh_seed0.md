# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# Final Answer: Causal Effect of BMI on DLBCL Risk Using Genetic Instruments

## a) Interpretation of the Difference Between Observational (12%) and IV (5%) Estimates

The 57% reduction from the observational estimate (12%) to the IV estimate (5%) suggests **confounding and/or reverse causation in the observational association**, rather than a violation of IV assumptions per se. This pattern is classic: the observational estimate is inflated because BMI is confounded by factors that independently increase DLBCL risk (e.g., socioeconomic status, lifestyle factors, comorbidities, or immune dysfunction). The IV estimate, using only the genetic component of BMI that is randomized at conception, eliminates these confounders and provides a cleaner causal estimate. The IV approach removes confounding bias but may not address **pleiotropy**, which is a separate threat to validity.

## b) Core Mendelian Randomization Assumptions Violated

The three core MR assumptions are:

1. **Relevance (Instrument Strength)**: The PGS explains only 6% of BMI variance, yielding an F-statistic of approximately 6.4 (using the formula F ≈ R²(N−k−1)/((1−R²)k) for large N). This is below the conventional threshold of 10, indicating **weak instrument bias**. Weak instruments amplify pleiotropy effects and reduce precision.

2. **Independence (No Confounding of Instrument-Outcome)**: Violated by **horizontal pleiotropy**. The suspected pleiotropic variants influence inflammation and other pathways that independently affect DLBCL risk, breaking the assumption that genetic variants only affect DLBCL through BMI.

3. **Exclusion Restriction (No Direct Effect)**: Directly violated by the pleiotropic variants. Pleiotropy operates through two mechanisms:
   - **Horizontal pleiotropy**: Direct effects on DLBCL through non-BMI pathways (e.g., immune regulation, inflammation)
   - **Vertical pleiotropy**: Pleiotropic pathways that operate through intermediate traits affecting both BMI and DLBCL

Pleiotropy biases the causal estimate in unpredictable directions. In this scenario, inflammation-related pleiotropy may inflate the observed association, but directional bias depends on the sign and magnitude of pleiotropic effects.

## c) Statistical Methods to Detect and Correct for Pleiotropy

**Method 1: MR-Egger Regression with Intercept Testing**
- Perform weighted regression of variant-outcome effects on variant-exposure effects, including an intercept term
- A non-zero intercept indicates directional horizontal pleiotropy
- The slope provides a pleiotropy-adjusted causal estimate under the "Instrument Strength Independent of Direct Effect" (InSIDE) assumption
- Apply this to the 100 BMI variants; a significant intercept (p < 0.05) would suggest pleiotropy

**Method 2: MR-PRESSO (Pleiotropy Residual Sum and Outlier)**
- Identify outlier variants whose effects are inconsistent with the causal model
- Remove outliers iteratively and re-estimate the causal effect
- Compare the "distortion ratio" (ratio of estimates before and after outlier removal); large distortions indicate pleiotropy
- Provides both detection and correction simultaneously

**Method 3: Weighted Median and Mode-Based Estimation**
- Robust to pleiotropy if fewer than 50% of weights come from pleiotropic variants
- Compute causal estimates using the weighted median of variant-specific Wald ratios
- Mode-based estimation identifies the most common causal effect among variants, resistant to pleiotropic outliers
- These methods are more conservative but more robust to violation of exclusion restriction

**Method 4: Heterogeneity Testing (Q-statistic)**
- Calculate Cochran's Q to test whether variant-specific Wald estimates are homogeneous
- High heterogeneity (Q p-value < 0.05) suggests pleiotropy or other violations
- Cannot distinguish pleiotropy from other sources of heterogeneity but flags model violation

**Method 5: MR-RAPS (Robust Adjusted Profile Score)**
- Incorporates measurement error and weak instrument bias
- Down-weights variants with large standard errors, reducing pleiotropy influence
- Provides robust estimates when instrument strength is weak (as in this case with F ≈ 6.4)

## d) Interpretation of Removing Pleiotropic Variants: Bias-Variance Tradeoff

Removing 20% of variants (20 suspected pleiotropic variants) reduces the estimate from 5% to 3%, with increased variance. This tradeoff reveals:

**Bias Reduction Component**: The 2 percentage point decrease (5% → 3%) suggests that the removed variants contained positive horizontal pleiotropy, inflating the BMI effect estimate. The true causal effect may be closer to 3% or lower.

**Variance Inflation Component**: Increased variance reflects loss of statistical power—removing 20% of instruments reduces information content. With fewer variants, the estimate becomes less precise, widening confidence intervals.

**Signal Interpretation**: 
- If the 3% estimate has a significantly wider confidence interval that still excludes zero, pleiotropy removal improved validity at acceptable precision cost
- If the confidence interval becomes very wide or includes zero, the tradeoff may not be worthwhile, and robust methods (e.g., weighted median, MR-RAPS) would be preferable
- The direction of bias (downward) suggests that the pleiotropic variants' effects on DLBCL are in the same direction as their effects on BMI, consistent with inflammation as a confounder

**Recommendation**: Continue analysis with both estimates (5% and 3%) presented with sensitivity analyses, using the 3% estimate as a lower-bound causal effect if methodological concerns about pleiotropy are substantive.

## e) Step-by-Step Algorithmic Analysis Plan

```
ALGORITHM: Robust Causal Inference for BMI → DLBCL via Genetic Instruments

INPUT: 
  - 100 independent SNPs with BMI and DLBCL effect estimates and standard errors
  - BMI GWAS summary statistics and DLBCL case-control GWAS summary statistics
  - Prior suspicion of pleiotropy via inflammation-related pathways

STEP 1: Data Quality Control
  1a. Harmonize alleles across BMI and DLBCL GWAS datasets
  1b. Remove SNPs with MAF < 0.01 or missing data
  1c. Check for strand ambiguity; remove palindromic SNPs with ambiguous allele coding
  1d. Verify no palindromic SNPs remain; if present, use allele frequencies to resolve
  OUTPUT: Cleaned dataset of N valid SNPs (expected ~95-100)

STEP 2: Instrument Strength Assessment
  2a. Calculate F-statistic for overall instrument strength: F = R²/k / (1-R²)/(N-k-1)
      where R² = 0.06, k = number of SNPs, N = sample size
  2b. IF F < 10: FLAG weak instrument bias; proceed with RAPS methods in Step 6
  2c. Calculate variant-specific F-statistics: F_i = (β_exposure,i / SE_exposure,i)²
  2d. Remove variants with F_i < 10 if >20% of total variants affected
  OUTPUT: Assessment of weak instrument bias risk; decision on method selection

STEP 3: Primary Two-Sample MR Estimate (Baseline)
  3a. Calculate Wald ratio for each SNP: θ_i = β_DLBCL,i / β_BMI,i
  3b. Inverse-variance weight each Wald ratio: w_i = 1/SE²_θ,i
  3c. Estimate causal effect: β_IVW = Σ(w_i × θ_i) / Σ(w_i)
  3d. Calculate standard error using inverse-variance formula
  3e. Report 95% CI and p-value
  OUTPUT: Primary IV estimate with uncertainty (expected ~5% per unit BMI)

STEP 4: Pleiotropy Detection (Heterogeneity Testing)
  4a. Compute Cochran's Q-statistic: Q = Σ w_i(θ_i - β_IVW)²
  4b