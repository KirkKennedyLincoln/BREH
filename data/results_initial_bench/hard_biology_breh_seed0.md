# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# FINAL ANSWER: Causal Effect of BMI on DLBCL Risk Using Genetic Instruments

## a) Interpretation of the Difference Between Observational (12%) and IV (5%) Estimates

The 58% reduction from the observational estimate to the IV estimate (12% → 5%) primarily indicates **confounding in the observational association**, not bias in the IV estimate itself. 

In observational studies, the BMI-DLBCL association is likely confounded by factors correlated with both BMI and DLBCL risk—such as socioeconomic status, physical activity levels, dietary patterns, or systemic inflammation markers. Genetic variants are randomly assorted at conception and therefore not confounded by these environmental and social factors.

The IV estimate of 5% represents the causal effect after removing confounding. However, the reduction could also partially reflect **violation of the exclusion restriction assumption** (pleiotropy), which would bias the IV estimate downward if variants have protective pleiotropic pathways. The observational 12% may represent both the true causal effect plus confounding bias, while the 5% IV estimate may be attenuated by pleiotropy.

## b) Core MR Assumptions Violated and Pleiotropy Effects

The three core assumptions of Mendelian randomization are:

**1. Relevance (Instrument Strength)**
- The PGS explains only 6% of BMI variance, indicating **weak instrument strength**
- This increases the variance of the IV estimate and may amplify bias from violation of other assumptions
- With 100 variants, weak instruments suggest many individual SNPs have small effects

**2. Independence (No Confounding)**
- This assumption is likely satisfied because alleles are randomly assorted at conception
- However, population stratification and linkage disequilibrium with confounding variants could violate this in practice

**3. Exclusion Restriction (No Direct Effect on Outcome)**
- **This assumption is violated by pleiotropy**
- The suspected pleiotropic variants affect inflammation and possibly other pathways that independently influence DLBCL risk
- Horizontal pleiotropy (variants affect the outcome through pathways other than BMI) biases the causal estimate

**Pleiotropy Effects on Causal Inference:**
- **Horizontal pleiotropy** introduces bias away from the true effect; variants affecting inflammation may directly increase DLBCL risk independent of BMI
- **Vertical pleiotropy** (pleiotropic effects downstream of the exposure) is acceptable in MR but rare
- The presence of pleiotropy violates the exclusion restriction, making the IV estimate unreliable unless methods account for it
- The 5% estimate may be biased if pleiotropy is directional (e.g., all variants have pro-inflammatory pleiotropic effects)

## c) Statistical Methods to Detect and Correct for Pleiotropy

**Method 1: MR-Egger Regression**
- Performs weighted linear regression of SNP-outcome effects against SNP-exposure effects
- Tests for intercept ≠ 0, which indicates directional horizontal pleiotropy
- The slope provides a pleiotropy-corrected causal estimate
- Less powerful than inverse-variance weighted (IVW) method but robust to directional pleiotropy
- Output: causal estimate, intercept, p-value for pleiotropy

**Method 2: Weighted Median and Mode-Based Estimation**
- Weighted median: identifies the causal estimate from the median variant effect, assuming <50% of variants are invalid
- Mode-based: clusters variants by effect similarity; the most common cluster provides the estimate
- These methods are robust if minority of variants (though not majority) are pleiotropic
- Provides sensitivity analysis comparing to IVW estimate

**Method 3: MR-PRESSO (Mendelian Randomization Pleiotropy Residual Sum and Outlier)**
- Calculates residual sum of squares (RSS) for each variant
- Identifies and removes outlier variants with excessive pleiotropy
- Recalculates causal estimate with remaining variants
- Tests global pleiotropy statistic
- Provides iterative correction approach

**Method 4: Contamination Mixture Method and MR-Mix**
- Assumes some fraction of variants are invalid (pleiotropic)
- Estimates both the causal effect and proportion of invalid variants simultaneously
- Provides likelihood-based inference accounting for uncertainty in variant validity
- Robust when direction and magnitude of pleiotropy varies across variants

**Method 5: Steiger Filtering**
- Tests whether each variant's effect on BMI exceeds its effect on DLBCL
- Removes variants where the causal direction appears reversed (likely pleiotropy)
- Uses R² values to quantify directionality
- Simple screening step before main analysis

**Method 6: Biological Pathway and Annotation-Based Filtering**
- Cross-reference genetic variants with databases of known biological pathways
- Exclude variants with strong evidence of involvement in inflammation pathways independent of BMI
- Use tissue-specific expression data to filter variants with off-target expression
- Knowledge-based rather than statistical approach

## d) Interpretation of Removing 20% of Suspected Pleiotropic Variants

**Estimate Changes:** 5% → 3% (40% further reduction)
**Variance:** Increases due to reduced sample size of variants (80 instead of 100)

**Interpretation:**

The **downward shift from 5% to 3%** suggests that the 20 removed variants were indeed pleiotropic, but in a **protective direction** relative to the direct BMI-DLBCL effect. These variants likely had pro-inflammatory or other pleiotropic effects that inflated the initial 5% estimate upward. Removing them reveals a smaller true causal effect.

This creates a critical **bias-variance tradeoff**:

- **Bias Reduction:** Removing pleiotropic variants reduces systematic bias and moves closer to the true causal effect (likely closer to 3% than 5%)
- **Variance Increase:** Fewer variants means less precision; the confidence interval around 3% will be wider than around 5%
- **Interpretation Challenge:** We cannot determine whether 3% is the true effect without knowing the actual structure of pleiotropy

**Statistical Implications:**
- The 3% estimate is *more credible* in terms of assumption satisfaction but *less precise*
- The wider confidence interval may encompass both 3% and 5%, making them statistically indistinguishable
- This demonstrates the importance of sensitivity analyses: robust estimates should be similar across multiple approaches

**Recommendation:** Report both estimates (5% and 3%) with confidence intervals. If they overlap substantially, conclude that the causal effect is likely in the range of 3-5% with substantial uncertainty. If 3% is substantially lower, this suggests moderate horizontal pleiotropy was present and the 3% estimate is preferable.

## e) Step-by-Step Algorithmic Analysis Plan for Robust Causal Inference

```
ALGORITHM: Robust MR Analysis for BMI → DLBCL Causal Effect

INPUT: 
  - 100 genetic variants (SNP IDs, BMI effects, DLBCL effects, standard errors)
  - Outcome: DLBCL risk
  - Exposure: BMI
  
OUTPUT: 
  - Point estimate of causal effect with 95% CI
  - Assessment of assumption violations
  - Sensitivity analysis results
  - Final robust estimate

PROCEDURE:

PHASE 1: DATA QUALITY AND INSTRUMENT ASSESSMENT
─────────────────────────────────────────────
1.1 Input Validation
    - Check all 100 variants have BMI effects, DLBCL effects, and SEs
    - Remove ambiguous alleles (A/T, C/G)
    - Harmonize allele alignment between BMI and DLBCL effect estimates
    - Remove variants with missing data

1.2 Linkage Disequilibrium (LD) Pruning
    - Calculate pairwise LD between variants (r² > 0.001)
    - Retain only independent variants (keep variant with lowest p-value from each LD block)
    - Update variant count and effect estimates
    - Output: N_independent (typically 60-90 from original 100)

1.3 Instrument Strength Assessment
    - Calculate F-statistic for each variant: F = (β_BMI / SE_BMI)²
    - Calculate Steiger-corrected R² for BMI: R² = (β_BMI)² / (SE_BMI)² × (sample size)
    - DECISION