# hard_biology | smolagent | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

## Comprehensive Analysis of Mendelian Randomization with Pleiotropy in BMI-DLBCL Study

Based on extensive research on Mendelian randomization, instrumental variable assumptions, and pleiotropy, here is a complete answer to all sub-questions:

---

### **a) Difference Between Observational (12%) and IV Estimate (5%): Confounding vs. Pleiotropy**

**The 7 percentage point difference (12% → 5%) suggests CONFOUNDING, not pleiotropy violation per se, but with important nuances:**

1. **Observational Confounding (12% estimate):**
   - The observational association includes confounded pathways
   - BMI correlates with unmeasured/residual confounders (e.g., socioeconomic factors, diet quality, physical activity patterns) that independently affect DLBCL risk
   - These confounders inflate the observational estimate

2. **IV Estimate Advantage (5% estimate):**
   - The PGS, being randomized at conception, breaks associations with confounders
   - This estimate is closer to the true causal effect—**more credible but not necessarily unbiased**

3. **Critical Distinction:**
   - The difference reflects **confounding reduction**, not evidence of pleiotropy violation
   - However, if some of the 100 genetic variants have **horizontal pleiotropic effects** (directly affecting DLBCL through pathways unrelated to BMI, or via inflammation), the IV estimate (5%) could still be **biased upward or downward** depending on pleiotropy direction
   - The fact that the IV estimate is smaller suggests possible **negative pleiotropy** (some variants increase DLBCL risk independently of BMI) or simply residual confounding uncontrolled by the IV approach

**Precise Interpretation:**
- Observational estimate (12%) = True causal effect + confounding bias + pleiotropy
- IV estimate (5%) = True causal effect + pleiotropy (if InSIDE violated) ± sampling error
- The reduction is **primarily confounding correction**, but pleiotropy remains a threat to validity

---

### **b) Core MR Assumptions Violated and Pleiotropy Impact**

**Three Core Instrumental Variable Assumptions in MR:**

| Assumption | Definition | Violation in This Scenario |
|-----------|-----------|--------------------------|
| **IV1: Relevance** | Genetic variants must be associated with BMI | Partially satisfied: PGS explains only 6% BMI variance = WEAK INSTRUMENT |
| **IV2: Independence** | Genetic variants must not be associated with confounders of BMI-DLBCL | VIOLATED: Some variants associated with inflammation, immune function |
| **IV3: Exclusion Restriction** | Genetic variants affect DLBCL only through BMI | VIOLATED: Horizontal pleiotropy via inflammation |

**Pleiotropy Mechanisms Violating Assumptions:**

1. **Horizontal Pleiotropy (Primary Issue):**
   - Genetic variants influence DLBCL through **multiple independent pathways**:
     - Direct path: Variant → BMI → DLBCL (intended)
     - Pleiotropic path: Variant → Inflammation → DLBCL (unintended, violates IV3/exclusion restriction)
     - Example: FTO variant (increases BMI) also upregulates inflammatory markers independent of weight

2. **Correlated Pleiotropy (InSIDE Violation):**
   - If variants with stronger effects on BMI also have stronger pleiotropic effects on inflammation, the **SNP-exposure effects correlate with pleiotropy**
   - This induces **directional bias** in IV estimates

3. **Weak Instrument Bias (IV1 Weakness):**
   - 6% variance explained is relatively low for MR
   - Weak instruments amplify:
     - Sampling error
     - Bias from even small violations of IV2/IV3
     - Loss of statistical power

4. **Vertical vs. Horizontal Pleiotropy:**
   - **Vertical pleiotropy** (acceptable): Variant → BMI → metabolic pathway → DLBCL (true causal chain)
   - **Horizontal pleiotropy** (problematic): Variant → Inflammation → DLBCL (independent of BMI)

**How Pleiotropy Affects Causal Inference:**
- If inflammation-linked variants are in the PGS and inflammation independently raises DLBCL risk, the IV estimate is **biased toward the null** (5% may underestimate true BMI effect)
- Conversely, if variants reduce inflammation while increasing BMI, pleiotropy could **bias estimates away from null**
- The direction and magnitude of bias depend on:
  - Proportion of variants with pleiotropy (20% suspected in this case)
  - Magnitude of pleiotropic effects
  - Direction of pleiotropy (concordant or discordant)

---

### **c) Two+ Statistical Methods/Sensitivity Analyses for Detecting/Correcting Pleiotropy**

**Method 1: MR-Egger Regression**
- **Principle:** Extends IVW by allowing a non-zero intercept
- **Technical approach:** Regresses IV-outcome associations on IV-exposure associations with forced intercept
- **Detection:** Egger intercept ≠ 0 indicates directional pleiotropy
- **Bias correction:** Slope estimate represents causal effect adjusted for directional pleiotropy
- **Application:**
  ```
  If MR-Egger intercept p < 0.05: Pleiotropy present
  Compare IVW (3 or 5%) vs. MR-Egger slope estimate
  Difference suggests magnitude of pleiotropy bias
  ```
- **Advantages:** Simple, directional pleiotropy test
- **Limitations:** Assumes equal pleiotropy across all variants (strong assumption); lower power with few instruments

**Method 2: Weighted Median (WM) Estimator**
- **Principle:** Robust to pleiotropy in ≤50% of instruments
- **Technical approach:** Calculates inverse-variance weighted median of Wald ratios across variants
- **When to use:** If pleiotropy is sparse (affects subset of variants)
- **Application:** Compare estimates across methods:
  - IVW: assumes no pleiotropy
  - Weighted Median: allows 50% pleiotropy
  - MR-Egger: allows arbitrary directional pleiotropy
  - If WM ≈ IVW, little evidence of pleiotropy; if WM differs from IVW, suggests pleiotropy in minority of variants

**Method 3: MR-PRESSO (Pleiotropy Residual Sum and Outlier)**
- **Principle:** Tests for horizontal pleiotropy via global heterogeneity test; removes outlier variants
- **Technical approach:** 
  - Calculates residuals from IV estimates
  - Global test: Tests heterogeneity of residuals
  - Distortion test: Compares original and pleiotropy-adjusted estimates
  - Outlier removal: Iteratively removes variants with largest residuals
- **Application:**
  ```
  Step 1: Run global test p < 0.05 → Pleiotropy detected
  Step 2: Compare original IVW vs. MR-PRESSO corrected estimate
  Step 3: Identify which variants are outliers (potential pleiotropy sources)
  ```
- **Advantages:** Identifies specific pleiotropy-driven variants; allows correction
- **Limitations:** Assumes pleiotropy in outliers only; not robust to pervasive pleiotropy

**Method 4: Mode-Based Estimation (MBE)**
- **Principle:** Assumes majority of variants have no pleiotropy ("zero modal pleiotropy" assumption)
- **Robust to:** Pleiotropy in minority of variants
- **Application:** Compare MBE with IVW; large difference suggests widespread pleiotropy
- **Limitations:** Requires large number of variants to estimate mode reliably

**Method 5: Multivariable MR (MVMR) — Pleiotropy via Mediator Adjustment**
- **Principle:** If inflammation is hypothesized mediator of pleiotropy, adjust for it
- **Technical approach:** Perform MR with BMI and inflammation jointly as exposures; estimate direct effect of BMI on DLBCL independent of inflammation
- **Application:**
  ```
  Univariable MR: BMI → DLBCL = 5% (confounded by pleiotropy via inflammation)
  Multivariable MR: BMI → DLBCL (adjusted for inflammation) = true direct effect
  If MVMR ≈ 5%, pleiotropy via inflammation not major issue
  If MVMR > 5%, inflammation masks true BMI effect
  ```
- **Advantages:** Mechanistic insight; identifies specific pleiotropic pathways
- **Limitations:** Requires instruments for inflammation; assumes no unmeasured confounding of inflammation-DLBCL

**Method 6: Sensitivity Analysis — Leave-One-Out Analysis**
- **Principle:** Iteratively remove each variant and recalculate IV estimate
- **Detection:** If removing 20% of variants (suspected pleiotropy) causes large estimate change, those variants likely carry pleiotropy
- **Application:** Plot estimates with/without each variant; outliers indicate pleiotropy sources

---

### **d) Interpretation of Variant Removal Tradeoff**

**Empirical 