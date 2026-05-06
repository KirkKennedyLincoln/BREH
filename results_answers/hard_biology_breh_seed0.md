# hard_biology | breh | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

# FINAL ANSWER

## a) Interpretation of the Difference Between Observational (12%) and IV Estimate (5%)

The substantial difference between the observational estimate (12% increased risk per BMI unit) and the instrumental variable estimate (5%) suggests **confounding in the observational analysis rather than bias in the IV estimate itself**. 

In observational studies, the association between BMI and DLBCL risk is likely inflated by confounders—factors that influence both BMI and DLBCL risk independently (e.g., socioeconomic status, physical activity, diet, comorbidities). The IV approach using genetic variants bypasses these confounders because genetic variants are randomized at conception and should not be directly influenced by lifestyle or socioeconomic factors.

The IV estimate (5%) represents a more conservative causal effect because it isolates the effect of BMI that operates through biological pathways, removing confounding bias. The 12% observational estimate conflates the true causal effect with confounding bias, making it an upward-biased estimate of the true causal relationship.

## b) Violation of Mendelian Randomization Assumptions and Pleiotropy Effects

The three core MR assumptions are:

**1. Relevance (Strength of Instrument):** The PGS explains only 6% of BMI variance, indicating a weak instrument. This reduces statistical power and increases sensitivity to violations of other assumptions. With 100 independent variants, this weak signal means each variant has minimal effect, and the IV estimate will be imprecise.

**2. Independence (No Confounding of the IV-Outcome Association):** Suspected pleiotropy violates this assumption. If genetic variants influencing BMI also influence inflammation (or other pathways) that independently affect DLBCL risk, then the genetic variants are not exogenous. They affect DLBCL through multiple pathways, not solely through BMI.

**3. Exclusion Restriction (No Direct Effect of IV on Outcome except through exposure):** This is the assumption most clearly violated by pleiotropy. If variants have pleiotropic effects on inflammation or immune function independent of their effect on BMI, then they directly influence DLBCL risk, violating the exclusion restriction. The estimated causal effect would then capture both the BMI→DLBCL pathway and direct pleiotropic pathways.

**How Pleiotropy Affects Validity:** Horizontal pleiotropy (variants affecting DLBCL through pathways other than BMI) biases the causal estimate away from the true effect. In this scenario, if pleiotropic variants increase inflammation, which increases DLBCL risk independent of BMI, the IV estimate becomes a mixture of the true BMI effect and the direct pleiotropic effect, potentially obscuring or distorting the causal relationship.

## c) Statistical Methods to Detect and Correct for Pleiotropy

**Method 1: MR-Egger Regression**
MR-Egger regression relaxes the assumption that all variants have zero intercept in the IV-outcome association. It estimates both a slope (causal effect) and an intercept term. A significant non-zero intercept indicates horizontal pleiotropy. The MR-Egger-corrected estimate adjusts for the average pleiotropic effect across variants, though it requires the "InSIDE" assumption (that variant-exposure associations are independent of pleiotropic effects). Apply this as a sensitivity analysis: if the MR-Egger estimate differs substantially from the inverse-variance weighted (IVW) estimate, pleiotropy is likely present.

**Method 2: MR-PRESSO (Mendelian Randomization Pleiotropy RESidual Sum and Outlier)**
MR-PRESSO comprises three components:
- **Global test:** Detects presence of horizontal pleiotropy by testing whether residuals from the causal model are heterogeneous
- **Outlier test:** Identifies and removes variants that are outliers (suspected of having strong pleiotropic effects)
- **Distortion test:** Compares the causal estimate before and after outlier removal to assess whether pleiotropy substantially distorts the result

Run MR-PRESSO to identify outlier variants and re-estimate the causal effect after their removal, comparing the distortion in estimates.

**Method 3: Weighted Median Estimator**
This method is robust to pleiotropy if up to 50% of variants are invalid. It orders variants by their contribution to the causal estimate and uses the median to estimate the effect. It performs well when a minority of variants are pleiotropic, providing a sensitivity check against the main IVW estimate.

**Additional Sensitivity Analyses:**
- **Leave-one-out analysis:** Sequentially remove each variant and re-estimate; variants whose removal substantially changes the estimate are suspected pleiotropic outliers
- **Heterogeneity testing:** Use I² statistics and Cochran's Q test to assess statistical heterogeneity among variant-specific causal estimates, which signals pleiotropy

## d) Interpretation of the Bias-Variance Tradeoff from Variant Removal

Removing 20% of suspected pleiotropic variants reduced the IV estimate from 5% to 3% while increasing variance (reducing precision). This tradeoff reveals important information:

**The direction of bias correction (5% → 3%):** The pleiotropic variants were positively biasing the causal estimate upward. Removing them yields a more conservative estimate of 3%. This suggests these 20 variants had horizontal pleiotropic effects that inflated the apparent BMI→DLBCL association, likely through pathways such as inflammation or immune activation independent of BMI's effect.

**The variance increase:** With only 80 variants remaining (versus 100), the instrument is weaker, reducing statistical power and precision. The wider confidence interval around the 3% estimate reflects this loss of information.

**Interpretation:** The 3% estimate is likely more valid (less biased by pleiotropy) but less precise. If this 3% estimate is statistically significantly different from zero and consistent across multiple sensitivity analyses, it provides stronger causal evidence than the 5% estimate despite lower precision. However, the choice between 5% and 3% depends on: (1) confidence that the removed variants are truly pleiotropic, (2) whether the 3% estimate remains statistically significant, and (3) biological plausibility. The reduced estimate also suggests that much of the observational association (12%) indeed reflects confounding or pleiotropic pathways unrelated to BMI's direct causal effect.

## e) Step-by-Step Algorithmic Analysis Plan for Robust Causal Effect Estimation

**STEP 1: Instrument Strength Assessment**
- Calculate F-statistics for each variant individually (F = β²/SE²)
- Calculate the overall F-statistic for the PGS (expected to be moderate given 6% variance explained; target F > 10 for strong instruments, though 6–10 is workable with caution)
- If F-statistic is weak (< 10), document potential weak-instrument bias and proceed cautiously with interpretation
- Assess whether PGS variants show independent associations with BMI (check for linkage disequilibrium and independence)

**STEP 2: Pleiotropy Detection (Multi-Method)**
- **2a. Apply MR-Egger regression:** Estimate causal effect and intercept term; test whether intercept is significantly non-zero (p < 0.05 indicates pleiotropy)
- **2b. Apply MR-PRESSO global test:** Test heterogeneity in variant-specific causal estimates; significant heterogeneity (p < 0.05) signals pleiotropy
- **2c. Calculate I² and Cochran's Q statistics:** Quantify statistical heterogeneity among variants
- **2d. Perform leave-one-out analysis:** Remove each variant sequentially and identify those whose removal substantially shifts the estimate (> 20% change) as suspected pleiotropic outliers
- **2e. Cross-reference with biological databases:** Check whether identified outlier variants have known associations with inflammation, immune markers, or other traits that could pleiotropically affect DLBCL

**STEP 3: Variant Selection and Refinement**
- **3a. Apply MR-PRESSO outlier test:** Formally identify and flag outlier variants
- **3b. Sensitivity analysis - Progressive removal:** Create 3 variant sets: (i) all 100 variants, (ii) variants not flagged by MR-PRESSO, (iii) variants not flagged by leave-one-out analysis
- **3c. Re-estimate causal effect for each set:** Document how estimates change
- **3d. Decision rule:** If removal of pleiotropic variants substantially reduces the estimate and reduces heterogeneity, prioritize the refined set; if removal creates instability or high variance, retain all variants but interpret with pleiotropy caveat

**STEP 4: Multi-Method Causal Estimation (Sensitivity Analysis)**
- **4a. Inverse-Variance Weighted (IVW) method:** Primary estimate, weighting each variant by the inverse of its squared SE
- **4b. MR-Egger regression:** Pleiotropy-adjusted estimate (less efficient but robust to average horizontal pleiotropy)
- **4c. Weighted median estimator:** Robust if ≤ 50% of variants are invalid; provides consistency check
- **4d. Mode-based estimator:** Another robust method for comparison if many weak variants present
- **4e. Summarize all estimates:** Tabulate and compare across methods to assess consistency

**STEP 5: Assumption Checking and Reporting**
- **5a. Exclusion restriction:** Report sensitivity of results to removal of suspected pleiotropic variants; if major shifts occur, flag assumption violation
- **5b. No measurement error:** Verify that BMI and DLBCL phenotypes are well-defined and accurately measured in source studies
- **5c. Horizontal pleiotropy inference:** Report MR-Egger intercept, heterogeneity statistics, and number of outlier variants
- **5d. Power assessment:** Calculate statistical power given weak F-statistic; report confidence interval width as measure of precision

**STEP 6: Directionality and Reverse Causality Check**
- **6a. Perform reverse MR (DLBCL → BMI):** Construct genetic instrument for DLBCL and test whether it predicts BMI; significant reverse effect would suggest reverse causation or bidirectional confounding
- **6b. Interpret:** If reverse effect is much weaker or absent, forward direction (BMI → DLBCL) is more likely causal

**STEP 7: Integration with Observational Data**
- **7a. Compare IV estimate to observational association:** Document the 5% vs. 12% difference
- **7b. Interpret as confounding evidence:** Explain that higher observational estimate suggests positive confounding bias in observational analysis
- **7c. Discuss potential confounders:** List likely confounders (socioeconomic status, physical activity, diet, comorbidities) that could inflate observational association
- **7d. Conclude:** State that IV estimate (5%, or 3% if pleiotropic variants removed and robust) represents less-biased causal effect, but acknowledge weak instrument limitations

**STEP 8: Reporting and Interpretation**
- **8a. Primary result:** Report the most robust estimate (e.g., IVW after pleiotropy-variant removal if justified, or MR-Egger if pleiotropy is detected and cannot be removed)
- **8b. Sensitivity range:** Provide 95% confidence interval and range across methods (e.g., "causal effect estimate ranges from 3% to 5% across methods")
- **8c. Limitations:** Clearly state: weak instrument (low variance explained), possible horizontal pleiotropy, small sample size concerns, lack of individual-level data confirmation
- **8d. Biological interpretation:** Discuss whether 3–5% causal effect is biologically plausible and clinically meaningful compared to 12% observational association
- **8e. Recommendations:** Propose validation studies, replication in independent cohorts, and functional experiments to test mechanisms (e.g., does genetically higher BMI increase systemic inflammation in DLBCL patients?)

This algorithmic approach ensures transparent, multi-faceted evaluation of the causal hypothesis while rigorously addressing pleiotropy and instrument weakness—the primary threats to valid MR inference in this scenario.