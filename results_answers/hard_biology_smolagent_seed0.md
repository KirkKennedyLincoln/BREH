# hard_biology | smolagent | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

## Comprehensive Analysis: BMI Causal Effect on DLBCL Using Mendelian Randomization

### a) Interpretation of the Difference Between Observational (12%) and IV Estimate (5%)

**Precise Diagnosis:**
The 7 percentage point difference (12% → 5%) suggests **horizontal pleiotropy bias**, NOT confounding or violation of the core instrumental variable assumptions per se.

**Explanation:**

1. **Confounding (Ruled Out):** 
   - Traditional confounding affects BOTH observational and IV estimates equally if the confounder is unmeasured
   - IV methods are specifically designed to eliminate confounding through randomization of genetic variants at birth
   - The IV estimate should be unbiased with respect to unmeasured confounding

2. **Pleiotropy (Most Likely):**
   - The genetic variants influence DLBCL through pathways OTHER than BMI
   - Example pathway: Some BMI-associated SNPs may increase systemic inflammation independently, which directly increases DLBCL risk
   - This inflates the observational association (12%) because it conflates:
     - **True causal effect** (BMI → DLBCL)
     - **Pleiotropic pathways** (SNP → Inflammation → DLBCL, independent of BMI)

3. **Why the IV Estimate is Lower:**
   - The IV estimate (5%) reflects the **direct causal effect** of BMI after accounting for (to some extent) the pleiotropic inflation
   - However, residual horizontal pleiotropy could still bias the IV estimate

4. **Bias Direction Interpretation:**
   - Observational associations are biased UPWARD due to confounding by shared causes (e.g., genetics affecting both BMI and DLBCL risk through inflammation)
   - The IV estimate may still contain bias if pleiotropy is directional (i.e., pleiotropic effects all push toward increased DLBCL risk)

---

### b) Core Mendelian Randomization Assumptions That May Be Violated

**The Three Core MR Assumptions:**

| Assumption | Status | Violation Mechanism |
|-----------|--------|-------------------|
| **Relevance (Z associated with X)** | ✓ Valid | PGS explains 6% of BMI variance (modest but acceptable) |
| **Independence (Z independent of confounders of X-Y)** | ✓ Valid (Partially) | Genetic randomization largely protects against this |
| **Exclusion Restriction (Z only affects Y through X)** | ✗ **VIOLATED** | Pleiotropy: SNPs affect DLBCL through inflammation, immune dysfunction, and other pathways independent of BMI |

**How Pleiotropy Violates the Exclusion Restriction:**

1. **Horizontal Pleiotropy:**
   - Occurs when genetic variants have **direct effects on DLBCL** that are independent of their BMI effects
   - Example: SNP in IL6 gene → increases both BMI AND systemic inflammation → increases DLBCL risk directly
   - This creates a **path Z → Y** that doesn't go through X (BMI), violating exclusion restriction

2. **Vertical Pleiotropy (Acceptable):**
   - When a SNP affects BMI, which affects intermediate phenotypes (e.g., glucose, lipids), which then affect DLBCL
   - This is acceptable because the effect still flows through BMI to outcome

3. **Types of Problematic Pleiotropy in This Setting:**
   - **Inflammatory pathways:** SNPs affecting immune activation, IL-6, TNF-α production
   - **Metabolic pleiotropy:** SNPs affecting insulin sensitivity independent of BMI
   - **Shared genetic architecture:** Both BMI and DLBCL risk share genetic basis related to immune function
   - **Obesity-induced systemic inflammation:** Unmeasured mediator that creates pleiotropic effects

---

### c) Statistical Methods and Sensitivity Analyses for Pleiotropy Detection and Correction

**Method 1: MR-Egger Regression (Allows Directional Pleiotropy)**
- **What it does:** Assumes all variants can have pleiotropic effects but estimates a non-zero intercept
- **Interpretation:** Non-zero intercept test indicates directional pleiotropy
- **Application:**
  ```
  MR-Egger estimate ≠ IVW estimate → evidence of pleiotropy
  Intercept p-value < 0.05 → significant directional pleiotropy present
  ```
- **Advantage:** Provides causal estimate even with horizontal pleiotropy
- **Disadvantage:** Lower statistical power; less precise estimates; assumes "InSIDE assumption" (Instrument Strength Independent of Direct Effect)

**Method 2: Weighted Median and Weighted Mode Estimators**
- **What they do:** Assume ≥50% of variants are valid IVs (not pleiotropic)
- **Application:**
  - Weighted Median: Take median of individual variant ratio estimates
  - Weighted Mode: Cluster variants and take modal cluster estimate
- **Interpretation:** Robustness check - if these align with IVW, confidence increases; if not, pleiotropy likely
- **Advantage:** More robust to outliers than IVW; statistically powerful
- **Disadvantage:** Less power if >50% of variants are invalid

**Method 3: MR-PRESSO (Pleiotropy RESidual Sum and Outlier)**
- **Three-component test:**
  1. **Global Test:** Detects overall horizontal pleiotropy (Cochran's Q statistic)
  2. **Outlier Test:** Identifies and removes pleiotropic variants iteratively
  3. **Distortion Test:** Compares causal estimate before/after outlier removal
- **Application:**
  ```
  algorithm: FOR each variant:
    - Calculate residual sum of squares
    - Identify variants with high residuals as pleiotropic
    - Remove outliers iteratively
    - Compare IVW estimates before/after removal
  ```
- **Advantage:** Objective variant-by-variant detection; accounts for heterogeneity
- **Disadvantage:** May over-correct by removing truly causal signals; computationally intensive

**Method 4: Radial MR (Heterogeneity-Driven Outlier Detection)**
- **What it does:** Converts 2D problem into radial coordinates; detects outliers based on individual contribution to Cochran's Q
- **Application:** Plot each variant's contribution to heterogeneity; identify outliers visually and statistically
- **Advantage:** Improved visualization; no need for LD matrix preprocessing; flexible weighting
- **Disadvantage:** Requires manual inspection of plots

**Method 5: CAUSE (Causal Analysis Using Summary Effect Estimates)**
- **What it does:** Uses mixture model to distinguish between:
  - Shared genetic architecture (correlated pleiotropy)
  - Causal effect
- **Application:**
  ```
  CAUSE model: P(Y|Z) ∝ P(Z) × P(S) × P(θ)
  Where S = shared genetic component, θ = causal effect
  ```
- **Interpretation:** If mixing component weight is high for "causal" vs "sharing" model, supports causal effect
- **Advantage:** Distinguishes between correlated and uncorrelated pleiotropy
- **Disadvantage:** Can bias causal estimate to null if misspecified

**Method 6: Multivariable MR (MVMR)**
- **What it does:** Adjusts causal effect of BMI on DLBCL while accounting for intermediate/confounding exposures
- **Application:**
  ```
  Fit: DLBCL ~ BMI + Inflammation + GeneticVariants
  Interpretation: Direct effect of BMI independent of inflammation
  ```
- **Advantage:** Removes measured pleiotropy by adjusting for mediators (e.g., inflammatory markers)
- **Disadvantage:** Requires high-quality genetic instruments for ALL exposure variables; loses power

**Method 7: Heterogeneity Testing (Cochran's Q, I² Statistic)**
- **Application:**
  ```
  Q = Σ w_i(β_i - β_IVW)²
  Large Q or I² > 0.5 suggests pleiotropy present
  ```
- **Interpretation:** Heterogeneity ≠ pleiotropy definitively, but suggests instrument invalidity

---

### d) Interpretation of the Variance-Estimate Tradeoff After Removing 20% of Variants

**