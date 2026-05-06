# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# Final Answer: Causal Effect of BMI on DLBCL Risk Using Genetic Instruments

## a) Interpretation of the Difference Between Observational (12%) and IV Estimate (5%)

The substantial difference between the observational association (12% increased risk per BMI unit) and the IV estimate (5%) suggests **confounding in the observational estimate rather than bias in the IV estimate itself**.

**Precise explanation:** In observational studies, the 12% estimate is likely inflated by confounding—unmeasured or measured factors associated with both BMI and DLBCL risk (e.g., socioeconomic status, lifestyle factors, physical activity) bias the estimate upward. The IV estimate (5%) is less susceptible to these confounders because genetic variants are randomly assorted at conception and less influenced by lifestyle confounders. The IV estimate represents a more causal relationship, though it may itself be biased downward if pleiotropy is present (see section b).

The discrepancy does **not** indicate violation of the exclusion restriction per se at this stage—rather, it reveals that confounding substantially inflates observational estimates. However, the presence of pleiotropy would violate IV assumptions and could bias the 5% estimate.

## b) Core Mendelian Randomization Assumptions Violated

Three core MR assumptions may be violated:

1. **Relevance Assumption (Satisfied):** The PGS explains 6% of BMI variance, which is modest but sufficient for a weak instrument, though power will be reduced.

2. **Independence Assumption (Likely Satisfied):** Genetic variants are generally randomized at conception, protecting against confounding. This is the strength of the genetic approach.

3. **Exclusion Restriction Assumption (VIOLATED - Pleiotropy):** This is the critical violation. The research states that some genetic variants have pleiotropic effects—they influence inflammation and other traits independently affecting DLBCL risk. This constitutes **horizontal pleiotropy** (variants affect the outcome through pathways other than the exposure).

**How pleiotropy affects validity:**
- **Directional pleiotropy:** If pleiotropic effects systematically bias estimates in one direction (e.g., inflammation variants increase both BMI genetic score and DLBCL risk independently), the IV estimate will be biased away from the null.
- **Balanced pleiotropy:** Random pleiotropic effects may increase variance but not systematically bias the estimate.
- **Consequences:** The 5% IV estimate cannot be interpreted as purely causal because genetic variants affect DLBCL through multiple pathways, violating the assumption that variants influence the outcome only through BMI.

## c) Statistical Methods to Detect or Correct for Pleiotropy

Based on the accumulated evidence, two robust approaches are:

1. **MR-Egger Regression:**
   - Tests for directional pleiotropy by including an intercept term in the IV regression.
   - The intercept coefficient represents average pleiotropy across variants; a non-zero intercept indicates violation of the exclusion restriction.
   - Returns a pleiotropy-corrected causal estimate (MR-Egger slope) alongside the uncorrected estimate.
   - **Advantage:** Detects directional pleiotropy and provides corrected estimates.
   - **Limitation:** Lower statistical power than standard IVW (inverse-variance weighted) methods.

2. **MR-PRESSO (Mendelian Randomization Pleiotropy RESidual Sum and Outlier):**
   - Identifies and removes pleiotropic outlier variants by analyzing residuals from the MR regression.
   - Can detect both directional and balanced pleiotropy.
   - Performs sensitivity analysis by iteratively removing suspect variants and recalculating causal estimates.
   - Returns a pleiotropy-corrected estimate after outlier removal.
   - **Advantage:** Flexible, can handle multiple outliers, returns corrected estimates.
   - **Limitation:** Power depends on outlier detection threshold.

**Additional method:** Weighted median approach provides robust estimation when <50% of variants are pleiotropic, complementing the above methods for robustness checks.

## d) Interpretation of the Pleiotropy Variant Removal Tradeoff

Removing 20% of suspected pleiotropic variants reduced the IV estimate from 5% to 3% with increased variance. This tradeoff reveals:

**Interpretation:**
- **Bias-variance tradeoff:** The lower estimate (3%) suggests the removed variants were biasing the effect upward through pleiotropic pathways (likely inflammation-mediated effects on DLBCL). Removing them reduces bias toward the null, suggesting the true causal effect is closer to 3%.
- **Increased variance:** Removing 20 variants from 100 reduces sample size for estimation, increasing standard error and confidence interval width. This is the expected cost of stricter instrument selection.
- **Clinical implication:** The 3% estimate may be more trustworthy if the removed variants truly had invalid pleiotropic effects, despite reduced precision.
- **Methodological lesson:** This pattern is consistent with horizontal pleiotropy inflating the original 5% estimate. The convergence toward smaller estimates when removing pleiotropic variants supports the conclusion that pleiotropy was distorting the causal inference.

**Caution:** However, if the removed variants are truly valid instruments, removing them induces selection bias. This ambiguity underscores the need for the formal pleiotropy detection methods in section (c) to distinguish valid from invalid variants.

## e) Robust Step-by-Step Analysis Plan (Algorithmic Framework)

```
ALGORITHM: Robust Causal Inference for BMI → DLBCL Using Genetic Instruments

INPUT: 
  - Summary statistics for 100 BMI-associated SNPs
  - SNP effects on DLBCL risk
  - SNP effects on BMI
  - LD correlation matrix
  - Sample sizes for BMI and DLBCL GWAS

OUTPUT: 
  - Pleiotropy-adjusted causal effect estimates
  - Confidence intervals and p-values
  - Assessment of assumption violations

STEP 1: INSTRUMENT QUALITY ASSESSMENT
  1.1 Calculate F-statistics for each variant (F = β²_BMI / SE²_BMI)
      IF all F-statistics < 10: 
        → Report weak instrument bias risk
      ELSE: → Proceed with notation of instrument strength
  1.2 Screen for linkage disequilibrium (LD)
      → Clump variants at r² < 0.001 within 1 Mb windows
      → Confirm independence of 100 initial variants
  1.3 Test variant associations with BMI
      → Confirm p < 5×10⁻⁸ for each variant
      → Remove any with weaker associations

STEP 2: PRIMARY CAUSAL ESTIMATE (IVW Method)
  2.1 Perform inverse-variance weighted meta-analysis
      β_IVW = Σ(w_i × β_i) / Σ(w_i), where w_i = 1/SE_i²
  2.2 Calculate 95% CI and p-value
  2.3 Report as baseline estimate (expect ~5% per the scenario)

STEP 3: DETECT HORIZONTAL PLEIOTROPY (MR-Egger)
  3.1 Fit regression: β_outcome = α + β_exposure × β_exposure_SNP
  3.2 Test intercept α ≠ 0
      IF p(intercept) < 0.05:
        → Directional pleiotropy detected
        → Report MR-Egger slope β_Egger as pleiotropy-corrected estimate
      ELSE: → Pleiotropy less likely (but not ruled out)
  3.3 Compare IVW and MR-Egger estimates
      → Large discrepancy confirms pleiotropy influence

STEP 4: IDENTIFY PLEIOTROPIC OUTLIERS (MR-PRESSO)
  4.1 Calculate residual variance for each SNP
      → Rank SNPs by deviation from regression line
  4.2 Iteratively remove most extreme outliers
  4.3 Perform global pleiotropy test
      IF p(pleiotropy) < 0.05:
        → Pleiotropy detected
        → Return outlier-corrected estimate β_PRESSO
  4.4 Compare number of removed variants to expected proportion
      → Flag if >25% removed (suggests many invalid instruments)

STEP 5: ROBUST SENSITIVITY ANALYSES
  5.1 Weighted median method:
      → Calculate median of (β_outcome / β_exposure) ratios
      → Report as robust estimate if <50% variants invalid
  5.2 Leave-one-out analysis:
      → Iteratively remove each variant
      → Recompute estimate to identify influential outliers
      → IF any single variant drives result → flag for inspection
  5.3 Contamination mixture model:
      → Estimate proportion of invalid instruments
      → Report estimates under various contamination scenarios

STEP 6: PLEIOTROPY CORRECTION VIA VARIANT REMOVAL
  6.1 SUBSET A: Remove variants identified as outliers in STEP 4
      → Recalculate IVW estimate with remaining variants
      → Report β_corrected and variance increase
  6.2 SUBSET B: Manually remove top 20% of variants by effect size
      → Recalculate estimate (parallels scenario in section d)
      → Compare to SUBSET A results
      → IF both methods converge → stronger evidence for bias correction
      → IF methods diverge → pleiotropy mechanism unclear
  6.3 Document trade-off between bias reduction and precision loss

STEP 7: EXTERNAL VALIDATION (Pleiotropy Mechanisms)
  7.1 Query databases (GWAS catalog, PhenoScanner) for removed variants
      → Confirm removed variants associate with inflammation, immune function
      → Verify biological plausibility of pleiotropic pathways
  7.2 Cross-reference with published MR studies
      → Check if same variants identified as problematic in other BMI → disease studies
      → Assess generality of pleiotropy findings

STEP 8: SUMMARY AND INTERPRETATION
  8.1 Tabulate estimates from all methods:
      ┌─────────────────────────┬──────────┬──────────────────┐
      │ Method                  │ Estimate │ 95% CI / SE      │
      ├─────────────────────────┼──────────┼──────────────────┤
      │ IVW (all 100 variants)  │ 5%       │ [from STEP 2]    │
      │ MR-Egger                │ β_Egger  │ [from STEP 3]    │
      │ MR-PRESSO (corrected)   │ β_PRESSO │ [from STEP 4]    │
      │ Weighted Median         │ β_WM     │ [from STEP 5.1]  │
      │ After outlier removal   │ 3%*      │ [from STEP 6.1]  │
      └─────────────────────────┴──────────┴──────────────────┘
      * Expected convergence near 3% if pleiotropy corrected
  
  8.2 Consensus causal estimate
      IF IVW, MR-Egger, MR-PRESSO, and weighted median converge within 1%:
        → Report consensus estimate as primary result
        → Conclude robust causal effect
      ELSE IF substantial heterogeneity:
        → Report range of estimates
        → Conclude pleiotropy substantially biases inference
        → Recommend conservative interpretation (lower bound)
  
  8.3 Final conclusion
      Report: "The causal effect of BMI on DLBCL risk is approximately [consensus estimate]% per 
      unit BMI increase, after correcting for pleiotropy. Observational estimates of 12% are 
      substantially inflated by confounding. Pleiotropy via inflammatory pathways likely accounts 
      for differences between unadjusted and pleiotropy-corrected estimates."

OUTPUT: Final causal estimate with confidence intervals, pleiotropy assessment, 
         sensitivity analyses, and interpretation confidence level
```

---

## Summary Synthesis

**Q: Does BMI causally affect DLBCL risk?**

**A: Likely yes, but at a lower magnitude than observational studies suggest.** The genetic evidence indicates a causal effect of approximately **3–5% increased DLBCL risk per BMI unit**, substantially lower than the observational estimate of 12%. The difference arises from confounding in observational data (upward bias) and pleiotropy in genetic variants (upward bias in the unadjusted IV estimate). Variants influencing BMI through inflammatory pathways appear to have pleiotropic effects on DLBCL risk independent of BMI itself. Robust pleiotropy-adjusted methods (MR-Egger, MR-PRESSO) and sensitivity analyses are essential to isolate the true causal relationship. The 3% estimate after removing suspected pleiotropic variants likely represents the most valid causal effect, though with reduced precision. This study exemplifies the real-world complexity of Mendelian randomization in identifying causal effects while navigating assumption violations.