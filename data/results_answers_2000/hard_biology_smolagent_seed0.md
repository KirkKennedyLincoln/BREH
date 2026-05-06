# hard_biology | smolagent | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---

## Comprehensive Analysis: BMI, Polygenic Scores, and DLBCL Causality Using Mendelian Randomization

---

### **a) Interpretation of the Difference Between Observational (12%) and IV (5%) Estimates**

**Key Finding:** The observational estimate (12%) is substantially higher than the IV estimate (5%), suggesting the observational association is biased.

**Precise Explanation:**

This difference **does NOT indicate confounding in the traditional sense**, but rather reflects different types of bias:

1. **Confounding Bias (Observational Estimate):** The 12% observational association conflates:
   - True causal effect of BMI on DLBCL (what IV estimates)
   - Confounding by shared genetic and lifestyle factors affecting both BMI and DLBCL risk
   - Reverse causation (DLBCL may reduce BMI)

2. **Pleiotropy-Induced Bias (IV Estimate):** The 5% IV estimate may underestimate because:
   - The PGS explains only 6% of BMI variance (weak instrument)
   - Some genetic variants have pleiotropic effects independent of BMI
   - If pleiotropy is "balanced" (random direction), it would bias toward null
   - If pleiotropy is "unbalanced/directional," it could bias either up or down

3. **Attenuation from Weak Instrument Bias:** With R² = 0.06, the F-statistic is likely modest. The formula for weak instrument bias is:
   - **Biased_IV_effect ≈ True_effect × (F-1)/F**
   - If F ≈ 6-8 (consistent with 6% variance), the IV estimate is severely attenuated
   - **The true causal effect could be between 5% and 12%, or even outside this range**

**Conclusion:** The 12% observational difference reflects **confounding + reverse causality + selection bias**, while the 5% IV estimate reflects the **attenuated causal effect due to weak instruments** and potentially **directional pleiotropy**. Neither estimate reliably identifies the true causal effect without addressing these issues.

---

### **b) Core MR Assumptions Violated and Pleiotropy Effects**

**The Three Core Assumptions of Mendelian Randomization:**

| Assumption | Status | Violation Mechanism |
|-----------|--------|-------------------|
| **1. Relevance** (Instrument associated with exposure) | **WEAK** | PGS explains only 6% of BMI variance; many variants contribute minimally; weak F-statistic (~6-8) indicates substantial weak instrument bias |
| **2. Independence** (No confounders of instrument-outcome) | **LIKELY VALID** | Genetic randomization at conception breaks confounding; population stratification could violate this if ancestry-related |
| **3. Exclusion Restriction** (No direct pathway Z→Y except through X) | **VIOLATED** | Pleiotropic variants influence inflammation, immune function, and other pathways independently affecting DLBCL |

**Specific Violations:**

1. **Horizontal Pleiotropy (Exclusion Restriction Violation):**
   - **Classic pleiotropy:** Genetic variants for BMI (e.g., FTO, MC4R) may also influence:
     - Systemic inflammation (IL-6, TNF-α)
     - Immune cell function and lymphocyte differentiation
     - Leptin signaling affecting immune tolerance
   - These pathways directly affect DLBCL risk independent of BMI's metabolic effects
   - **Result:** The IV estimate captures **total effect (direct BMI effect + pleiotropic effects)**, not the isolated BMI effect

2. **Indirect Horizontal Pleiotropy:**
   - Variants in LD with BMI SNPs may affect other traits
   - Creates spurious associations between PGS and DLBCL

3. **Weak Instrument Bias:**
   - Amplifies any pleiotropy: biased_estimate ≈ true_effect + pleiotropy_effect/F
   - With low F, even small pleiotropic effects are magnified
   - Increases variance and lowers precision

**Pleiotropy's Effects on Validity:**

- **If balanced pleiotropy:** Random directional effects cancel → estimate biased toward null
- **If unbalanced pleiotropy (directional):** Consistent pleiotropic effects → systematic bias away from true causal effect
- **Suspected pleiotropy here is likely unbalanced** (inflammation pathways all increase DLBCL risk), causing **positive bias** in the total effect estimate

---

### **c) Two+ Statistical Methods to Detect/Correct for Pleiotropy**

#### **Method 1: MR-Egger Regression with InSIDE Assumption Testing**

**What it does:**
- Fits meta-regression of outcome-exposure association ratio (Wald ratios) against exposure-variant associations
- The **intercept ≠ 0** indicates directional pleiotropy
- The **slope** estimates causal effect adjusted for average pleiotropy

**Implementation:**
```
For each variant i:
  β_Yᵢ = regression coefficient (outcome ~ variant)
  β_Xᵢ = regression coefficient (exposure ~ variant)
  
Perform meta-regression: β_Yᵢ = α + β × β_Xᵢ + εᵢ

Intercept (α): Average pleiotropic effect per unit increase in exposure
Slope (β): Causal effect of BMI on DLBCL
```

**Advantages:**
- Tolerates all variants being invalid as long as InSIDE assumption holds (pleiotropic effects independent of exposure effects)
- Provides pleiotropy detection via Egger intercept test

**Disadvantages:**
- InSIDE assumption may be violated (e.g., variants affecting BMI through inflammation also have correlated pleiotropic effects)
- Less power than IVW; higher standard errors
- Requires ≥3 variants

**For this study:**
- Calculate MR-Egger intercept; test if significantly ≠ 0
- If intercept significant (p < 0.05), strong evidence of directional pleiotropy
- Compare Egger slope (adjusted estimate) to IVW slope (unadjusted)

---

#### **Method 2: MR-PRESSO (Pleiotropy RESidual Sum and Outlier)**

**What it does:**
- Three-component approach: (1) Global pleiotropy test, (2) Outlier detection, (3) Distortion test

**Global Test (Component 1):**
```
Calculate residual sum of squares (RSS) for each variant:
  RSS_i = (β_Yᵢ - β̂ × β_Xᵢ)²

Compare observed RSS to distribution under null (no pleiotropy)
If observed RSS > critical value → evidence of pleiotropy
```

**Outlier Removal (Component 2):**
```
Identify individual SNPs with disproportionate contributions to RSS
Remove outliers one-by-one (prioritizing highest RSS contributions)
Re-estimate causal effect after removal
```

**Distortion Test (Component 3):**
```
Test if causal estimate significantly changes before/after outlier removal
Large distortion (Δ > threshold) suggests pleiotropy was driving estimates
```

**Advantages:**
- **Doesn't require InSIDE assumption** for detection (only for interpretation)
- Identifies specific pleiotropic variants
- Robust to balanced pleiotropy
- Provides statistical test of pleiotropy presence

**Disadvantages:**
- Assumes most variants are valid (breaks down if >50% are pleiotropic)
- Computationally intensive
- Outlier removal reduces effective sample size

**For this study:**
```
Step 1: Run MR-PRESSO global test with all 100 variants
Step 2: If p < 0.05, implement outlier removal algorithm
Step 3: Retest after removing suspected pleiotropic variants
Step 4: Compare effect sizes and confidence intervals
Step 5: Run distortion test to assess significance of changes
```

---

#### **Method 3: Weighted Median and Mode-Based Estimates (Supplementary)**

**Weighted Median:**
- Ranks variants by instrument strength; estimates effect at median point
- **Robust if ≤50% of variants are invalid** (by weight)
- Implementation: Inverse-variance weighted median of Wald ratios

**Mode-Based Estimate:**
- Identifies the "mode" of effect estimates across variants
- **Robust if ≤75% are invalid** (in balanced pleiotropy scenarios)

**For this study:** Use as triangulation—if all three methods (IVW, Weighted Median, Mode) agree, pleiotropy is likely minimal.

---

#### **Method 4: Multivariable MR (Measured Pleiotropy Adjustment)**

**What it does:**
- Simultaneously model BMI and pleiotropic mediators (e.g., inflammatory markers)
- Estimates **direct effect of BMI conditional on mediators**

**Implementation:**
```
Outcomes: DLBCL risk

Exposures:
  1. BMI (primary interest)
  2. CRP (inflammation)
  3. IL-6 (inflammation)
  4. Other immune markers

Collect genetic associations for each exposure from separate GWAS
Estimate direct effect of BMI adjusted for inflammatory pathways
```

**Advantages:**
- Accounts for measured pleiotropic pathways explicitly
- Distinguishes direct vs. indirect effects
- No InSIDE assumption needed for measured confounders

**Disadvantages:**
- Requires GWAS data for multiple traits
- Unmeasured pleiotropy still problematic
- Increases model complexity

---

#### **Method 5: Leave-One-Out Sensitivity Analysis**

**What it does:**
```
For each variant i:
  Estimate causal effect excluding variant i
  Compare to full estimate
  
If removing one variant dramatically changes estimate:
  → That variant likely has pleiotropic effects
  → Suggests directional pleiotropy
```

**Graphical output:** Leave-one-out forest plot showing stability of estimate

**Advantages:**
- Simple, intuitive
- Identifies influential pleiotropic variants
- No strong assumptions required

**For this study:**
- Systematically remove each of 100 variants
- Plot effect estimates with CIs
- Flag variants causing large shifts (>30% change)
- Expected pattern: if inflammation-related variants clustered among outliers, suggests pleiotropic pathway

---

### **d) Tradeoff: Removing 20% of Variants (IV Estimate 5% → 3%, Variance Increases)**

**Interpretation:**

| Aspect | Before Removal | After Removal | Interpretation |
|--------|---|---|---|
| **Effect Estimate** | 5% | 3% | **40% reduction** in point estimate |
| **Variance** | Low | Higher | **Standard error increases** (fewer instruments) |
| **Bias-Variance Tradeoff** | Better bias | Better precision | **Competing objectives** |

**Analysis:**

1. **What the decrease means:**
   - Removed 20 variants likely had **unbalanced positive pleiotropic effects**
   - These variants were inflating the IV estimate upward
   - 3% represents a **more valid causal estimate** with reduced pleiotropy bias
   - Suggests true BMI effect on DLBCL is ~3%, not 5%

2. **Why variance increased:**
   - F-statistic decreases: F = (R² / k) / [(1-R²) / (n-k-1)]
   - Fewer instruments → weaker overall instrument strength
   - Loss of information from 20 removed variants
   - **Wider confidence intervals** (less precision)

3. **Statistical Tradeoff:**
   ```
   MSE = Bias² + Variance
   
   Before: MSE ≈ (2%)² + Low_Var  [high bias, low variance]
   After:  MSE ≈ (0%)² + Higher_Var [low bias, higher variance]
   ```
   
   - If variance increase is modest (<50%), **bias reduction dominates**
   - The 3% estimate is likely closer to truth with wider CI (e.g., 0.5%-5.5%) than 5% with narrow CI (4%-6%)

4. **Practical Implications:**
   - **Stronger causal inference:** 3% is more robustly estimated
   - **Still significant?** If CI excludes 0, causal effect is real despite increased uncertainty
   - **Reduced sample size paradox:** Removing bad instruments can improve inference quality
   - **External validity:** Must verify the 20 removed variants truly have pleiotropic mechanisms (biological validation)

5. **Decision Framework:**
   ```
   IF Variance_Increase < 30% AND Effect_Still_Significant:
     → Prefer the 3% estimate (better causal inference)
   
   ELSE IF Variance_Increase > 100% OR Effect_Becomes_Nonsignificant:
     → Caution: Removed instruments may be valid
     → Use sensitivity analysis approach instead
   ```

**Recommendation:** Report **both** estimates with sensitivity analyses:
- Primary: 3% (pleiotropy-adjusted)
- Sensitivity: 5% (all variants)
- Include 95% CIs for both
- Note: Heterogeneity statistics (I² statistic) should decrease after removal, confirming pleiotropy reduction

---

### **e) Step-by-Step Algorithmic Analysis Plan**

```
ALGORITHM: Robust Causal Inference of BMI → DLBCL via Genetic Instruments

INPUT:
  - PGS composed of 100 independent genetic variants
  - GWAS summary statistics for BMI (exposure)
  - GWAS summary statistics for DLBCL (outcome)
  - Individual-level data or LD reference panel

OUTPUT:
  - Point estimate of causal effect (β_BMI→DLBCL)
  - 95% confidence interval
  - Pleiotropy assessment
  - Sensitivity analysis results

================================================================================
STEP 1: INSTRUMENT VALIDATION & QC
================================================================================

1.1 Check Relevance Assumption
  FOR each of 100 variants:
    - Extract β_X (exposure-variant association)
    - Calculate F-statistic: F_i = β_X² / SE²_X
    - Report: Mean F, median F, min F
  
  IF Mean_F < 10:
    → FLAG: Weak instrument concern
    → DECISION: Proceed but acknowledge weak instrument bias
               (estimate may be attenuated)

1.2 Check Variant Independence
  - Perform LD clumping: keep variants with r² < 0.001 within 10 Mb
  - Remove any variants in high LD with others
  - Verify 100 variants remain independent
  
  OUTPUT: List of final independent variants (N_final)

1.3 Data Harmonization
  FOR each variant:
    - Ensure consistent effect allele coding between exposure and outcome GWAS
    - Align strand orientation
    - Remove palindromic SNPs or flag ambiguous variants
  
  OUTPUT: Harmonized exposure-outcome dataset

================================================================================
STEP 2: PRIMARY CAUSAL EFFECT ESTIMATION (IVW Method)
================================================================================

2.1 Calculate Wald Ratios
  FOR each variant i:
    Wald_i = β_Yi / β_Xi
  WHERE:
    β_Yi = outcome-variant association
    β_Xi = exposure-variant association

2.2 Inverse-Variance Weighted Meta-Analysis
  β_IVW = Σ(Wald_i × w_i) / Σ(w_i)
  WHERE:
    w_i = 1 / (SE²_Yi + (β_Yi/β_Xi)² × SE²_Xi)  [delta method]
  
  SE_IVW = 1 / √(Σ w_i)
  
  OUTPUT:
    - β_IVW = primary causal estimate
    - 95% CI = [β_IVW - 1.96×SE_IVW, β_IVW + 1.96×SE_IVW]
    - P-value for β_IVW ≠ 0

2.3 Test for Heterogeneity
  Q_statistic = Σ w_i × (Wald_i - β_IVW)²
  df = N_final - 1
  I² = (Q - df) / Q  [proportion variance due to heterogeneity]
  
  IF I² > 50% (substantial heterogeneity):
    → ALERT: Suggests pleiotropy, invalid instruments, or effect heterogeneity
    → DECISION: Prioritize pleiotropy-robust methods below

================================================================================
STEP 3: PLEIOTROPY DETECTION (Global Tests)
================================================================================

3.1 MR-Egger Intercept Test
  Fit meta-regression: Wald_i = α + β × β_Xi + ε_i
  
  Extract:
    - α (intercept): average pleiotropic effect
    - β (slope): causal effect adjusted for average pleiotropy
    - SE_α: standard error of intercept
  
  Test H₀: α = 0
    t = α / SE_α
    p_Egger = 2-tailed p-value
  
  IF p_Egger < 0.05:
    → ALERT: Significant directional pleiotropy detected
    → DECISION: Use Egger estimate (β) as alternative to IVW
               (β_Egger typically more robust than β_IVW when pleiotropy present)

3.2 MR-PRESSO Global Pleiotropy Test
  Fit IVW model: β_Y ~ β_X
  Calculate residual sum of squares:
    RSS_obs = Σ [(β_Yi - β̂×β_Xi) / SE_Yi]²
  
  Simulate null distribution (no pleiotropy):
    RSS_null ~ χ²_(N_final)
  
  p_PRESSO_global = P(RSS_sim ≥ RSS_obs)
  
  IF p_PRESSO_global < 0.05:
    → ALERT: Global pleiotropy detected
    → DECISION: Proceed to outlier removal (Step 3.3)
  ELSE:
    → CONCLUSION: No evidence of directional pleiotropy
    → DECISION: IVW estimate valid; proceed to Step 5 (Sensitivity)

================================================================================
STEP 4: PLEIOTROPY CORRECTION (Outlier Removal)
================================================================================

4.1 MR-PRESSO Outlier Detection
  FOR iteration t = 1 to MAX_ITER (typically ≤ 10):
    
    4.1.1 Calculate RSS contribution per variant
      RSS_i = [(β_Yi - β̂_IVW × β_Xi) / SE_Yi]²
    
    4.1.2 Identify variant with highest RSS
      i_outlier = argmax(RSS_i)
    
    4.1.3 Test if removal significantly improves fit
      β̂_t = Re-estimate IVW excluding variant i_outlier
      p_outlier = Test statistical significance of removal
    
    4.1.4 Decision rule
      IF p_outlier < 0.05:
        → Remove variant i_outlier
        → UPDATE: variant list, continue iteration
        → RECORD: Removed variant ID
      ELSE:
        → No more significant outliers
        → BREAK loop
    
    4.1.5 Check stopping criterion
      IF Number_Removed > 0.5 × N_final:
        → ALERT: Too many outliers (>50%); method unreliable
        → DECISION: Trust original analysis; note potential unmeasured pleiotropy

4.2 Distortion Test (Post-Outlier Removal)
  β̂_final = Causal estimate after outlier removal
  Distortion = |β̂_final - β̂_IVW| / SE_IVW
  
  IF Distortion > 2:
    → ALERT: Causal estimate substantially changed
    → INTERPRETATION: Removed outliers were substantially biasing result
    → CONCLUSION: β̂_final likely more valid

================================================================================
STEP 5: SENSITIVITY ANALYSES (Robustness Checks)
================================================================================

5.1 Weighted Median Estimator
  Sort variants by instrument strength (w_i)
  Estimate effect at weighted 50th percentile
  
  ROBUST TO: Up to 50% invalid instruments (by weight)
  
  IF β_WM ≈ β_IVW:
    → Confidence: Pleiotropy minimal; both estimates agree
  IF β_WM ≠ β_IVW (>20% difference):
    → Caution: Possible pleiotropy or bias

5.2 Mode-Based Estimator
  Cluster Wald ratios into modes
  Select largest mode
  Average estimates within mode
  
  ROBUST TO: Up to 75% invalid instruments (in balanced scenario)
  
  OUTPUT: β_Mode with CI

5.3 Leave-One-Out Analysis
  FOR each variant i = 1 to N_final:
    β_(-i) = Estimate effect excluding variant i
    SE_(-i) = Standard error
    Plot: Forest plot with β_(-i) points and CIs
  
  IDENTIFY:
    - Variants causing large shifts (>30% change) → likely pleiotropic
    - Stability of estimate → if all β_(-i) cluster tightly, robust to outliers
  
  OUTPUT: Leave-one-out forest plot with flagged outliers

5.4 Multivariable MR (Optional but Recommended)
  
  4.4.1 Identify pleiotropic pathways
    Literature review / biological knowledge:
    - Inflammation: CRP, IL-6, TNF-α
    - Immune function: immunoglobulin levels
    - Other BMI mediators: insulin resistance, lipid levels
  
  4.4.2 Collect GWAS statistics for mediators
    FOR each suspected mediator (M):
      - Extract β_M (mediator-variant association)
      - SE_M (standard error)
  
  4.4.3 Multivariable IVW Analysis
    Extend Wald ratio: Wald_i = β_Yi / (β_Xi, β_M1_i, β_M2_i, ...)
    Perform inverse-variance weighted meta-analysis including all exposures
    
    Estimate:
      β_BMI_direct = Direct effect of BMI (adjusted for mediators)
      β_M1_direct, β_M2_direct = Direct effects of mediators
  
  4.4.4 Comparison
    IF β_BMI_direct << β_IVW:
      → Substantial mediator effects; IVW captured pleiotropic pathways
    IF β_BMI_direct ≈ β_IVW:
      → Minimal mediation; direct effect of BMI dominant

================================================================================
STEP 6: VALIDITY ASSESSMENT & InSIDE ASSUMPTION CHECK
================================================================================

6.1 InSIDE Assumption (for MR-Egger interpretation)
  
  Plot: Exposure-variant association (β_X) vs. Wald ratio (β_Y/β_X)
  
  IF strong visual correlation:
    → InSIDE violated; pleiotropic effects correlated with exposure effects
    → DECISION: Don't interpret Egger intercept as average pleiotropy
    → USE: Egger estimate for robustness, not pleiotropy estimation

6.2 Weak Instrument Assessment
  Calculate conditional F-statistic for multivariate case:
    F_cond_BMI = (β_X^T Σ^-1 β_X) / k
  
  IF F_cond_BMI > 10:
    → CONCLUSION: Weak instrument bias minimal
  IF F_cond_BMI < 5:
    → ALERT: Weak instruments; estimates likely attenuated
    → DECISION: Report as lower-bound estimates

================================================================================
STEP 7: COMPARATIVE SUMMARY & FINAL ESTIMATE SELECTION
================================================================================

7.1 Tabulate All Estimates
  
  ┌─────────────────┬──────────┬──────────┬─────────┬─────────────┐
  │ Method          │ β̂       │ SE       │ 95% CI  │ Notes       │
  ├─────────────────┼──────────┼──────────┼─────────┼─────────────┤
  │ IVW (primary)   │ β_IVW    │ SE_IVW   │ CI_IVW  │ All variants│
  │ IVW (outliers   │ β_final  │ SE_final │ CI_final│ After removal│
  │  removed)       │          │          │         │             │
  │ MR-Egger        │ β_Egger  │ SE_Egger │ CI_Egger│ Adjusted    │
  │                 │          │          │         │ for pleiotropy
  │ Weighted Median │ β_WM     │ SE_WM    │ CI_WM   │ Robust 50%  │
  │ Mode-Based      │ β_Mode   │ SE_Mode  │ CI_Mode │ Robust 75%  │
  │ Multivariable   │ β_MVMR   │ SE_MVMR  │ CI_MVMR │ Mediation-  │
  │                 │          │          │         │ adjusted    │
  └─────────────────┴──────────┴──────────┴─────────┴─────────────┘

7.2 Convergence Assessment
  
  Agreement Threshold: All estimates within 25% of each other?
  
  IF YES (High Concordance):
    → Estimate is robust
    → PRIMARY ESTIMATE: β_IVW (or β_final if outliers removed)
    → CONFIDENCE: High causal estimate validity
  
  IF NO (Low Concordance):
    → Pleiotropy likely substantial
    → PRIMARY ESTIMATE: β_Egger or β_MVMR (pleiotropy-robust)
    → CONFIDENCE: Report range of plausible effects
    → INTERPRETATION: Acknowledge pleiotropy uncertainty

7.3 Final Causal Effect Report
  
  "The genetically predicted effect of BMI on DLBCL risk is:
   
   PRIMARY ESTIMATE: β = [X]% per unit increase in BMI
   95% CI: [Lower]% to [Upper]%
   
   This estimate was obtained via [method chosen in 7.2]
   and is robust to [pleiotropy/weak instruments/etc.]
   
   Sensitivity analyses show:
   - Weighted Median: β = [Y]% (robust to 50% invalid instruments)
   - Mode-Based: β = [Z]% (robust to 75% invalid instruments)
   - Leave-one-out: Estimates cluster tightly around [range]%
   
   Pleiotropy assessment:
   - MR-Egger intercept p = [p-value]; [significant/not significant]
   - I² = [value]%; [homogeneous/heterogeneous]
   - MR-PRESSO global test p = [p-value]
   
   [Number] potentially pleiotropic variants identified and removed.
   
   CONCLUSION: Evidence [weak/moderate/strong] for causal effect of BMI
   on DLBCL risk, estimated at [X]% per unit increase."

================================================================================
STEP 8: QUALITY CONTROL & REPORTING CHECKLIST
================================================================================

□ Instrument relevance: F-statistic ≥ 10?
□ Sample overlap: Exposure & outcome from different samples?
□ Harmonization complete: Alleles aligned?
□ Pleiotropy tests conducted: Egger intercept, I², MR-PRESSO?
□ Sensitivity analyses: ≥3 methods applied?
□ Leave-one-out check: No single-variant drivers?
□ Biological validity: Pleiotropic pathways documented?
□ Publication bias: Funnel plot symmetry (if GWAS significant)?
□ STROBE-MR checklist completed: All reporting criteria met?
□ Code & data: Analysis reproducible?

================================================================================
ALGORITHMIC PSEUDOCODE IMPLEMENTATION
================================================================================

function robust_mr_analysis(exposure_gwas, outcome_gwas, ld_matrix):
    
    # Step 1: QC
    variants = harmonize_and_qc(exposure_gwas, outcome_gwas)
    F_stats = calculate_f_statistics(variants)
    report_f_statistic_summary(F_stats)
    
    # Step 2: Primary analysis
    ivw_result = inverse_variance_weighted(variants)
    heterogeneity = calculate_i_squared(variants)
    
    # Step 3: Pleiotropy detection
    egger_result = mr_egger_regression(variants)
    mrpresso_global = mr_presso_global_test(variants)
    
    # Step 4: Conditional analysis
    IF mrpresso_global.p_value < 0.05:
        outliers = mr_presso_outlier_detection(variants, max_iter=10)
        variants_clean = remove_outliers(variants, outliers)
        ivw_result_clean = inverse_variance_weighted(variants_clean)
        distortion_test = test_effect_change(ivw_result, ivw_result_clean)
    ELSE:
        ivw_result_clean = ivw_result
        outliers = {}
    
    # Step 5: Sensitivity
    wm_result = weighted_median(variants)
    mode_result = mode_based_estimate(variants)
    loo_results = leave_one_out_analysis(variants)
    
    # Step 6: Validity checks
    inside_plot = plot_inside_assumption(variants)
    cond_f = conditional_f_statistic(variants)
    
    # Step 7: Comparison
    estimates_table = compile_comparison_table([ivw_result, ivw_result_clean,
                                                egger_result, wm_result, mode_result])
    agreement = assess_estimate_concordance(estimates_table)
    
    # Step 8: Final estimate selection
    IF agreement == "HIGH":
        primary_estimate = ivw_result_clean if outliers else ivw_result
    ELSE:
        primary_estimate = egger_result  # or multivariable_mr
    
    # Report
    return {
        "primary_estimate": primary_estimate,
        "sensitivity_estimates": [wm_result, mode_result, egger_result],
        "pleiotropy_evidence": {"egger_p": egger_result.p_egger, 
                                "mrpresso_p": mrpresso_global.p_value,
                                "i_squared": heterogeneity},
        "outliers_removed": outliers,
        "validity_checks": {"inside_assumption": inside_plot,
                           "conditional_f": cond_f},
        "agreement_assessment": agreement
    }

END ALGORITHM
```

---

### **Summary Table: Recommended Actions**

| Issue | Method | Expected Output |
|-------|--------|---|
| **Effect estimate** | IVW + Egger + Weighted Median | 3 point estimates for comparison |
| **Pleiotropy presence** | MR-PRESSO global + Egger intercept | p-values; if p<0.05 → pleiotropy present |
| **Pleiotropic variants** | MR-PRESSO outlier test + Leave-one-out | Specific SNP IDs to examine; biological validation |
| **Pleiotropy-adjusted effect** | MR-Egger slope or MVMR | Direct effect of BMI on DLBCL independent of inflammatory pathways |
| **Robustness** | Weighted Median + Mode-based | Confirmation that 3-5% estimate holds under different pleiotropy scenarios |
| **Weak instruments** | F-statistic + Conditional F | Assessment of attenuation; report as lower-bound if F<10 |

---

### **Conclusion**

The researcher should:
1. **Report both 5% (all variants) and 3% (pleiotropy-corrected) estimates** with full confidence intervals
2. **Prioritize pleiotropy-robust methods** (Egger, Weighted Median) given suspected inflammatory pleiotropy
3. **Use biological data** (literature, pathway analysis) to validate which variants are actually pleiotropic vs. false positives
4. **Apply multivariable MR** adjusting for inflammation markers if data available
5. **Acknowledge uncertainty**: True causal effect likely 2-6% per BMI unit; pleiotropy creates substantial inferential challenge

The **bias-variance tradeoff when removing 20% of variants (5% → 3% effect, higher variance) is justifiable** if it removes directional pleiotropy, yielding a more valid causal estimate despite reduced precision.
