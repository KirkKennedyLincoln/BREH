# hard_biology | smolagent | seed=0

**Prompt:** A researcher is investigating whether body mass index (BMI) has a causal effect on the risk of diffuse large B-cell lymphoma (DLBCL) using genetic data. They construct a polygenic score (PGS) for BMI using 100 independent genetic variants. The following summary information is available: 1) The PGS explains 6% of the variance in BMI in the population. 2) The observational association between BMI and DLBCL shows that each 1-unit increase in BMI is associated with a 12% increase in risk. 3) Using the PGS as an instrumental variable, the estimated effect of genetically predicted BMI on DLBCL risk is a 5% increase per BMI unit. 4) Some of the genetic variants used in the PGS are suspected to have pleiotropic effects (they influence other traits such as inflammation, which may independently affect DLBCL risk). Tasks: a) Explain whether the difference between the observational estimate (12%) and the instrumental variable estimate (5%) suggests confounding, bias, or violation of assumptions. Be precise. b) Identify which core assumptions of Mendelian randomization may be violated in this scenario and how pleiotropy affects the validity of the causal inference. c) Propose at least two statistical methods or sensitivity analyses that could be used to detect or correct for pleiotropy in this setting. d) Suppose removing 20% of the variants suspected of pleiotropy reduces the IV estimate to 3% and increases its variance. Interpret this tradeoff. e) Design a step-by-step analysis plan (algorithmically) that an agent could follow to robustly estimate the causal effect of BMI on DLBCL using genetic instruments. 

---


# COMPREHENSIVE ANALYSIS: BMI, DLBCL, AND MENDELIAN RANDOMIZATION CAUSAL INFERENCE

## a) DIFFERENCE BETWEEN OBSERVATIONAL (12%) AND IV (5%) ESTIMATES: CONFOUNDING VS. BIAS VS. ASSUMPTION VIOLATION

**Precise Interpretation:**

The 57% attenuation in the causal estimate (from 12% to 5% per BMI unit) reflects **violation of Mendelian randomization assumptions, specifically horizontal pleiotropy**, rather than simple confounding or bias in the classical sense.

**Mechanistic Explanation:**

- **Observational estimate (12%)**: Reflects the total association between BMI and DLBCL, which includes:
  - True causal effect of BMI → DLBCL
  - Confounding bias from unmeasured/measured confounders
  - Reverse causation (DLBCL → BMI)

- **IV estimate (5%)**: Attempts to isolate the causal effect by using genetic variants as randomized instruments. However, the attenuation suggests:
  
  1. **Pleiotropy-induced bias**: The PGS variants have direct effects on DLBCL independent of BMI, reducing the IV estimate below the true causal effect
  2. **Balanced vs. directional pleiotropy**: The fact that we observe *attenuation* (not reversal) suggests directional pleiotropy where pleiotropic effects bias the estimate toward the null
  3. **Weak instrument bias**: With only 6% variance explained in BMI, weak instrument bias may attenuate the IV estimate
  4. **Violation of exclusion restriction**: The assumption that genetic variants affect DLBCL only through BMI is demonstrably violated

**Why this is NOT simple confounding:**
- Classical confounding would bias observational estimates in one direction; we see a specific pattern consistent with horizontal pleiotropy
- The IV approach is *designed* to overcome confounding; the residual difference signals assumption violation in the genetic analysis

**Conclusion:** The difference suggests the IV estimate is biased *downward* by pleiotropic effects, while the observational estimate is biased in mixed directions by confounding and reverse causation. The true causal effect likely lies between 5% and 12%, but **the direction and magnitude of pleiotropy-induced bias cannot be determined from these estimates alone**.

---

## b) CORE MENDELIAN RANDOMIZATION ASSUMPTIONS VIOLATED AND PLEIOTROPY'S ROLE

**Three Core MR Assumptions:**

1. **Relevance Assumption (WEAK):**
   - PGS explains 6% of BMI variance—this is weak but potentially acceptable
   - With 100 variants, F-statistic ≈ (N × R²) / (m × (1-R²)) suggests weak instrument bias may contribute to IV estimate attenuation
   - **Pleiotropy impact**: Cannot be detected or corrected by relevance assessment alone

2. **Independence Assumption (POTENTIALLY VIOLATED):**
   - States: Genetic variants must be independent of confounders of the BMI-DLBCL relationship
   - **Pleiotropy violation**: If variants influence other traits (inflammation, immune function) that are confounders of BMI-DLBCL, the independence assumption fails
   - **Mechanism**: Variants → {Inflammation, Immune dysregulation} → DLBCL, in parallel to variants → BMI → DLBCL
   - This is **correlated horizontal pleiotropy** (pleiotropy acts through confounding pathways)

3. **Exclusion Restriction Assumption (CLEARLY VIOLATED):**
   - States: Genetic variants affect DLBCL *only* through BMI (no direct/pleiotropic effects)
   - **The scenario explicitly states some variants have pleiotropic effects on inflammation and other traits**
   - **Types of pleiotropy affecting validity:**
     - **Horizontal pleiotropy (direct)**: Variants → other traits → DLBCL, independent of BMI pathway
     - **Mediated pleiotropy**: Variants → inflammation → both BMI (via metabolic effects) and DLBCL (via immune effects)
     - **Correlated pleiotropy**: Variant effects on pleiotropy correlated with variant effects on BMI (violates InSIDE assumption for MR-Egger)

**How Pleiotropy Affects Validity:**

| Pleiotropy Type | Effect on Causal Estimate | Effect on IV Validity |
|---|---|---|
| **Horizontal (balanced)** | May cancel out → unbiased | Invalid IVs |
| **Horizontal (directional)** | Systematic bias toward/away from null | Invalid IVs—biased estimate |
| **Mediated** | Depends on mediator effect direction | Biases toward null if mediator negatively affects outcome |
| **Correlated** | Violates InSIDE assumption; MR-Egger gives biased estimates | Most problematic for all IV methods |

**In this scenario:**
- 20% removal of pleiotropic variants → estimate drops from 5% to 3%, suggesting:
  - The removed variants had *positive* pleiotropic effects (they were exaggerating the IV estimate)
  - This implies the true causal effect may be even smaller than 5%
  - OR the remaining variants are now too weak (variance lost)

---

## c) TWO+ STATISTICAL METHODS TO DETECT/CORRECT FOR PLEIOTROPY

### **Method 1: MR-Egger Regression with InSIDE Assessment**

**Principle:**
- Fits weighted linear regression: β̂_Y,j = α (intercept) + β₁ × β̂_X,j + error_j
- Non-zero intercept indicates directional pleiotropy
- Causal estimate is the slope (β₁), which is unbiased under InSIDE assumption

**Application to BMI-DLBCL:**
1. Regress genetic associations with DLBCL on genetic associations with BMI
2. Test if intercept ≠ 0 (implies directional pleiotropy)
3. Report both intercept (average pleiotropic effect) and slope (causal effect under InSIDE)
4. Assess plausibility of InSIDE: Do variant effects on pleiotropy correlate with effects on BMI?

**Advantages:**
- Provides formal test of directional pleiotropy
- Estimates causal effect under relaxed assumption
- Interpretable intercept = average pleiotropic bias

**Limitations:**
- InSIDE assumption untestable and often violated (especially with correlated pleiotropy)
- Reduced power to detect causal effects (larger confidence intervals)
- Sensitive to outlying variants; weak instruments reduce precision

**Expected Results:** If intercept is significantly positive, this suggests genetic variants have pleiotropic effects that bias the observational estimate toward positive associations with DLBCL beyond their BMI effects.

---

### **Method 2: MR-PRESSO (Pleiotropy RESidual Sum and Outlier) with Iterative Outlier Removal**

**Principle:**
- Global pleiotropy test: Compares observed heterogeneity (Q-statistic) to expected distribution under null
- Outlier detection: Identifies individual variants contributing disproportionately to heterogeneity
- Outlier removal: Sequentially removes variants and recalculates causal estimate
- Distortion test: Assesses whether outlier removal significantly changes the estimate

**Application to BMI-DLBCL:**

**Algorithm:**
1. Calculate Q-statistic: Q = Σ_j w_j × (β̂_Y,j - β̂_IVW × β̂_X,j)²  
   (measures deviation from causal estimate for each variant)
2. Simulate expected Q distribution under no pleiotropy
3. Compare observed Q to simulated null (p-value for global pleiotropy)
4. For each variant j, calculate Q_j (contribution to heterogeneity); variants with high Q are outliers
5. Remove variant with highest Q; recalculate causal estimate
6. Repeat until no significant heterogeneity remains
7. Report original estimate, outlier-removed estimate, and distortion test p-value

**Expected Results in BMI-DLBCL context:**
- Global test: p < 0.05, indicating significant pleiotropy
- Outlier detection: ~20 variants flagged (likely those affecting inflammation/immune traits)
- Sequential removal: Estimate shifts from 5% → 4% → 3%, approaching the true effect
- Distortion test: Significant (p < 0.05), indicating outliers meaningfully distort the estimate

**Advantages:**
- Objective, algorithmic outlier detection (no manual curation)
- Tests both presence and impact of pleiotropy
- More efficient than simple outlier removal (removes only problematic variants)
- Identifies specific variants for functional investigation

**Limitations:**
- Assumes majority of variants are valid instruments (may fail with >50% invalid)
- Computational complexity increases with variant count
- Outlier removal can induce cherry-picking bias if not carefully reported

---

### **Method 3 (Alternative): Contamination Mixture Model (or MRMix)**

**Principle:**
- Uses mixture model: assumes proportion of variants are "valid" (effect = true causal effect + noise) and proportion are "invalid" (effect = random large value)
- Estimates simultaneously:
  - True causal effect (β_causal)
  - Proportion of valid variants (π_valid)
  - Distribution of invalid variant effects
- Does not require removing variants; uses likelihood to weight valid vs. invalid

**Application to BMI-DLBCL:**

**Model:**
- For each variant j, likelihood is mixture:
  - L(β̂_Y,j | valid) ~ Normal(β_causal × β̂_X,j, SE²)
  - L(β̂_Y,j | invalid) ~ Normal(0, σ²_large)
- Joint likelihood: π_valid × L_valid + (1-π_valid) × L_invalid
- Maximize over β_causal, π_valid, σ²_large

**Expected Results:**
- Point estimate: 4.5% ± 1.8% (95% CI)
- π_valid: 78% (indicating ~22% of variants are pleiotropic—consistent with stated 20%)
- Identifies variants with high posterior probability of being invalid
- Confidence intervals may be asymmetric (reflects multimodal likelihood)

**Advantages:**
- Robust with up to 50% invalid instruments
- Weights variants rather than removes them (less power loss)
- Formal probabilistic framework
- Can identify distinct causal mechanisms if likelihood is multimodal

**Limitations:**
- Requires specification of invalid instrument distribution (assumptions matter)
- Less established than MR-Egger; fewer software implementations
- Interpretability lower than outlier-based methods

---

### **Method 4 (Sensitivity): Multivariable MR (MVMR)**

**Principle:**
- Include suspected confounders/mediators (inflammation markers) as additional exposures
- Estimates *direct* effect of BMI on DLBCL adjusting for pleiotropic pathways
- If pleiotropic effect is entirely through inflammation, direct effect should be null or smaller

**Application:**
1. Obtain instruments for: BMI, CRP (inflammation marker), other immune traits
2. Fit model: DLBCL ~ β₁×BMI + β₂×Inflammation + ...
3. β₁ is direct causal effect of BMI independent of inflammation

**Expected Result:** If significant pleiotropy is via inflammation, direct effect would drop substantially (e.g., 5% → 2-3%)

---

## d) INTERPRETATION OF VARIANT REMOVAL TRADEOFF (20% Removal → 3%, Higher Variance)

**Observed Data:**
- Original IV estimate: 5% (with 100 variants, R² = 6% in BMI)
- After removing 20% of suspected pleiotropic variants: 3% (with 80 variants, lower R²)
- Variance: Increased

**Interpretation:**

### **1. Direction of Bias from Removed Variants:**
The estimate *decreased* (5% → 3%), indicating removed variants had **positive pleiotropic effects** biasing the original estimate *upward* toward the observational estimate.

- These variants likely affect inflammation/immune traits that increase DLBCL risk
- Their direct effects on DLBCL outweighed their effects on BMI
- Removing them reveals the "cleaner" causal pathway: BMI → DLBCL (3%)

### **2. Increase in Variance (Loss of Precision):**

**Why variance increased:**
- Went from 100 → 80 instruments (20% reduction)
- Variance of IV estimate ∝ 1/(Σ_j w_j × β̂_X,j²)
- Losing 20 variants reduces this sum, increasing variance
- New R² in BMI is now ~4.8% (6% × 80/100), making instruments weaker
- **Weak instrument bias**: With weaker instruments, estimates have higher variance AND become more biased toward observational estimates

### **3. Bias-Variance Tradeoff:**

| Metric | 100 Variants (5%) | 80 Variants (3%) |
|---|---|---|
| **Point estimate** | 5.0% | 3.0% |
| **R² in BMI** | 6.0% | ~4.8% |
| **Variance** | σ² | ~1.25 × σ² |
| **95% CI width** | ~2σ | ~2.4σ (wider) |
| **Bias from pleiotropy** | +2% (estimated) | 0% (pleiotropic variants removed) |
| **Bias from weak instruments** | Minimal | Moderate (+0.5-1%) |

**Net effect:**
- Reduction in pleiotropy bias: 2% improvement in estimate validity
- Increase in weak instrument bias: 0.5-1% attenuation toward null
- Increase in sampling variance: ~25% wider confidence intervals

### **4. Is this Improvement Worth It?**

**Arguments FOR removing variants (accepting higher variance):**
- More *valid* causal estimate: pleiotropic bias removed
- Estimate closer to true causal effect (3% likely more accurate than 5%)
- Can investigate removed variants' mechanisms (inflammation, immune function)
- Confidence intervals, though wider, are centered on unbiased estimate

**Arguments AGAINST (favoring all 100 variants):**
- Power to detect causal effect reduced (wider CI may now include null: e.g., [0.1%, 5.8%])
- Weak instrument bias may reintroduce bias toward null (confounding-like bias)
- If true causal effect is ~3%, original 5% is reasonably close; loss of precision may not be justified
- Publishing wider CIs may be viewed as weaker evidence

### **5. Recommendation:**

**Report both estimates prominently:**
- Primary: 80 variants, 3% (cleaner instrument set, less pleiotropic bias, higher variance)
- Sensitivity: 100 variants, 5% (larger n, smaller variance, pleiotropic bias present)
- **Visually**: Forest plot showing estimates are consistent in direction; both suggest modest positive causal effect

**True causal effect likely: 3-4%** (between the two estimates, accounting for pleiotropy and weak instrument bias)

---

## e) STEP-BY-STEP ALGORITHMIC ANALYSIS PLAN FOR ROBUST CAUSAL ESTIMATION

### **ROBUST MENDELIAN RANDOMIZATION ANALYSIS PIPELINE: BMI → DLBCL**

```
ALGORITHM: Robust_MR_Analysis_Pipeline
INPUT: 
  - PGS variants for BMI (n=100)
  - GWAS summary statistics: β_BMI (variant-BMI effect), β_DLBCL (variant-DLBCL effect)
  - Sample sizes: N_BMI, N_DLBCL
OUTPUT: 
  - Robust causal estimate with uncertainty quantification
  - Assessment of pleiotropy and validity violations
  - Sensitivity analyses across assumptions

===== STAGE 1: DATA PREPARATION AND QUALITY CONTROL =====

Step 1.1: Filter and harmonize variants
  INPUT: 100 PGS variants with β_BMI, SE_BMI, β_DLBCL, SE_DLBCL
  
  FOR each variant j:
    1. Check variant is present in both BMI and DLBCL GWAS
    2. Align alleles: ensure effect alleles are consistent
    3. Calculate F-statistic: F_j = β_BMI,j² / SE_BMI,j²
    4. Flag weak instruments: F_j < 10 (weak instrument threshold)
    5. Remove variants with: |R_BMI-DLBCL| > 0.8 (LD contamination)
    6. Remove if MAF < 0.01 or | β_BMI| or |β_DLBCL| is extreme (>5 SD)
  
  OUTPUT: Filtered variant set (typically 90-100 variants, if LD structure handled)
  
Step 1.2: Calculate polygenic score strength
  R² = Σ_j [β_BMI,j × (N_BMI - 2) / (F_j + N_BMI - 2)]
  
  IF R² < 2%:
    ALERT: Severe weak instrument bias likely; IV estimates unreliable
  IF 2% ≤ R² ≤ 5%:
    CAUTION: Weak instrument bias possible; report with sensitivity
  IF R² > 5%:
    ACCEPTABLE: Proceed (this scenario: R² = 6%)

===== STAGE 2: PRIMARY PLEIOTROPY DETECTION =====

Step 2.1: Test for global directional pleiotropy (MR-Egger)
  Fit weighted regression: β̂_DLBCL,j = α_intercept + β_causal × β̂_BMI,j + ε_j
  
  WEIGHTS: w_j = 1 / SE_DLBCL,j²
  
  OUTPUT: 
    - α_intercept (mean pleiotropic effect)
    - SE(α), p-value for intercept ≠ 0
    - β_Egger (causal estimate under InSIDE)
    - SE(β_Egger)
  
  IF p_intercept < 0.05:
    CONCLUSION: Significant directional pleiotropy detected
    MAGNITUDE: α_intercept indicates average pleiotropic bias
    BIAS_direction: sign(α) indicates whether pleiotropy biases estimate up or down

Step 2.2: Test for global heterogeneity (Cochran's Q)
  Q = Σ_j w_j × (β_ratio,j - β_IVW)²
  
  WHERE: β_ratio,j = β̂_DLBCL,j / β̂_BMI,j (per-variant causal estimate)
         β_IVW = Σ_j w_j × β_ratio,j / Σ_j w_j (inverse-variance weighted)
  
  Degrees of freedom = 100 - 1 = 99
  
  IF p_Q < 0.05:
    CONCLUSION: Significant heterogeneity across variants
    INTERPRETATION: Either pleiotropy, or weak instruments, or true effect heterogeneity

Step 2.3: Calculate I² heterogeneity index
  I² = (Q - df) / Q × 100%
  
  I² > 50%: High heterogeneity (pleiotropy likely)
  I² > 75%: Very high heterogeneity (strong pleiotropy suspected)

===== STAGE 3: INDIVIDUAL VARIANT PLEIOTROPY DETECTION =====

Step 3.1: MR-PRESSO global and outlier test
  FOR each variant j:
    1. Calculate residual sum of squares (RSS_j) relative to IVW estimate
    2. RSS_j = [β_DLBCL,j - β_IVW × β_BMI,j]² / SE_DLBCL,j²
    3. Simulate RSS distribution under null (no pleiotropy) with 10,000 permutations
    4. Calculate empirical p-value: p_j = (# permutations with RSS_sim > RSS_obs) / 10,000
  
  OUTPUT: Variant-level p-values; variants with p_j < 0.05 are outliers
  
  GLOBAL TEST: Combine p-values via Fisher method: -2 Σ log(p_j)
  
Step 3.2: Identify and characterize outlier variants
  Outliers ← variants with p_j < 0.05 (e.g., expected ~5 variants under null)
  
  FOR each outlier:
    1. Record β̂_BMI,j, β̂_DLBCL,j (direction and magnitude of effects)
    2. Look up variant in literature/GWAS databases for known pleiotropy
    3. Check associations with inflammation markers (CRP, IL-6, TNF-α) in GWAS
    4. Note proximity to immune/inflammatory genes
  
  OUTPUT: Characterized outlier list (e.g., 20 variants suspected of pleiotropy)

Step 3.3: Steiger filtering (directionality test)
  FOR each variant j:
    1. Calculate R²_BMI,j = 2 × β̂_BMI,j² × p_MAF × (1 - p_MAF)
    2. Calculate R²_DLBCL,j similarly
    3. Steiger filter: KEEP if R²_BMI,j > R²_DLBCL,j (variant explains more variance in exposure)
    4. REMOVE if R²_DLBCL,j ≥ R²_BMI,j (suggests reverse causation or pleiotropy)
  
  Expected result: Removes ~1-2 variants with strong primary association to DLBCL

===== STAGE 4: PRIMARY CAUSAL EFFECT ESTIMATES =====

Step 4.1: Inverse-variance weighted (IVW) estimate (assumes all instruments valid)
  β̂_IVW = Σ_j [w_j × β_DLBCL,j / β_BMI,j] / Σ_j w_j
  
  SE(β̂_IVW) = 1 / √[Σ_j w_j]
  
  EXPECTATION for this study:
    β̂_IVW ≈ 0.12 (matches observed; all variants included)
    This is LIKELY BIASED due to pleiotropy

Step 4.2: Weighted median estimate (robust to up to 50% invalid instruments)
  1. Order variants by |β̂_BMI,j|
  2. Calculate cumulative weights: Σ_i w_i for i ≤ j
  3. Find median: variant where cumulative weight crosses 50%
  4. β̂_median = weighted median of β_ratio,j
  
  EXPECTATION: β̂_median ≈ 0.08-0.10 (less biased than IVW if pleiotropy widespread)

Step 4.3: Weighted mode-based estimate (robust under plurality assumption)
  1. Density function of β_ratio,j estimated via kernel density
  2. Find mode (peak) of density
  3. Calculate 95% CI via bootstrap
  
  EXPECTATION: β̂_mode ≈ 0.05-0.08

Step 4.4: MR-Egger estimate (robust if InSIDE satisfied)
  β̂_Egger = slope from Step 2.1 regression
  
  EXPECTATION: β̂_Egger ≈ 0.03-0.05 (accounts for pleiotropy via intercept)
  
  CAVEAT: InSIDE assumption plausibility should be assessed:
    - Is E(α_j | β_BMI,j) = 0? (pleiotropic effects independent of variant strength)
    - If many variants affect inflammation (common cause of both BMI and DLBCL), InSIDE violated

Step 4.5: Contamination mixture model estimate (MRMix)
  Likelihood: L(β_causal | data) = Π_j [π × L_valid(j) + (1-π) × L_invalid(j)]
  
  Maximize over: β_causal, π (proportion valid), σ_invalid
  
  OUTPUT: 
    - β̂_CMM (point estimate)
    - Posterior probability each variant is valid
    - CI (may be asymmetric/multimodal)
  
  EXPECTATION: β̂_CMM ≈ 0.04-0.06, with π ≈ 0.80 (80% valid)

===== STAGE 5: SENSITIVITY ANALYSES =====

Step 5.1: Leave-one-variant-out (LOVO) analysis
  FOR each variant j:
    1. Remove variant j from analysis
    2. Recalculate β̂_IVW, β̂_median, β̂_Egger
    3. Store results
  
  OUTPUT: Sensitivity plot showing how each variant influences estimate
  
  INTERPRETATION:
    - Narrow spread: robust estimate, pleiotropy distributed across many variants
    - Wide spread with outliers: one or few variants drive estimate (potential pleiotropic outliers)
  
  EXPECTED PATTERN: Scatter around 0.05-0.12; outlier removal shifts toward 0.03-0.05

Step 5.2: Iterative outlier removal (MR-PRESSO outlier test)
  ITERATION 1: Original 100 variants
    - Identify outlier with smallest p-value
    - Remove and recalculate β̂_IVW
    - Repeat until no p_j < 0.05
  
  OUTPUT: Sequential estimates as outliers removed
    Hypothetical pattern:
      - 100 variants: 5.0%
      - 85 variants (outliers removed): 4.2%
      - 80 variants: 3.5%
      - 78 variants: 3.0% (converges)
  
  DISTORTION TEST: Compare β̂_original vs β̂_outlier_removed
    Δβ = |5.0% - 3.0%| = 2.0 percentage points
    p_distortion < 0.05 if this difference is significant
  
  CONCLUSION: If converges to 3%, pleiotropy explained ~2% of original estimate

Step 5.3: Subset analyses by variant annotation
  SUBSET 1: Variants in/near immune/inflammatory genes (suspected pleiotropic)
    - Remove ~25 variants near IL genes, TNF, CRP loci
    - Recalculate β̂_IVW
    - EXPECTED: Estimate drops to ~4%
  
  SUBSET 2: Variants in classical BMI loci (less likely pleiotropic for DLBCL)
    - Keep only ~75 variants in FTO, MC4R, TMEM18, etc.
    - EXPECTED: Estimate stable at ~4-5%
  
  COMPARISON: If immune-gene removal causes larger change, suggests pleiotropy mechanism

Step 5.4: Multivariable MR adjusting for inflammation
  MVMR MODEL: DLBCL ~ β₁×BMI + β₂×CRP + β₃×IL6 + ...
  
  INSTRUMENTS: 
    - BMI: 80 variants (after outlier removal)
    - CRP: 56 genome-wide significant variants
    - IL-6: 20+ variants
  
  OUTPUT: Direct effect of BMI on DLBCL, conditional on inflammation markers
  
  EXPECTED: β₁_MVMR ≈ 0.02-0.03 (if pleiotropy largely through inflammation)
  
  INTERPRETATION:
    - If β₁_MVMR >> β₁_univariate: pleiotropy NOT through inflammation
    - If β₁_MVMR << β₁_univariate: pleiotropy partly mediated by inflammation

===== STAGE 6: ASSUMPTION VALIDATION AND ROBUSTNESS =====

Step 6.1: Assess InSIDE assumption (for MR-Egger validity)
  Calculate correlation: Corr(α̂_j, β_BMI,j)
  
  WHERE: α̂_j estimated from univariable regression of β_DLBCL,j on intercept
  
  IF |Corr| > 0.2 AND p < 0.05:
    VIOLATION: InSIDE violated; MR-Egger estimate biased
    ALTERNATIVE: Use median or mode-based estimate instead
  
  EXPECTED: Likely Corr > 0.2 (variants affecting inflammation likely have stronger BMI effects)

Step 6.2: Assess weak instrument bias via bias correction
  Bias_estimate = bias_formula(R², N, α, σ²_U)
  
  (Requires specification of unmeasured confounding strength; often sensitivity-analyzed)
  
  TYPICAL RANGE: Weak instrument bias may attenuate estimate by 5-15% when R² = 6%

Step 6.3: Evaluate pleiotropy via MR-TRYX (optional, if GWAS data available)
  For each outlier variant, search GWAS database for associated traits
  
  EXPECTED: Outlier variants associated with:
    - Inflammatory markers (CRP, IL-6, TNF-α)
    - Immune cell counts (lymphocytes, monocytes)
    - Other cancers (immune-related)
  
  INTERPRETATION: Confirms pleiotropy mechanism

===== STAGE 7: SYNTHESIS AND ROBUST CAUSAL ESTIMATE =====

Step 7.1: Create summary table of all estimates
  
  | Method | Estimate | 95% CI | Assumption |
  |---|---|---|---|
  | IVW (all 100) | 5.0% | [3.5%, 6.5%] | All instruments valid |
  | IVW (80 outlier-removed) | 3.0% | [1.2%, 4.8%] | ~80% valid instruments |
  | Weighted median | 8.0% | [5.0%, 11.0%] | >50% valid |
  | Weighted mode | 5.5% | [2.5%, 8.5%] | Plurality valid |
  | MR-Egger | 4.0% | [1.0%, 7.0%] | InSIDE (likely violated) |
  | CMM (MRMix) | 4.5% | [2.5%, 6.5%] | Mixture distribution |
  | MVMR (adjusted for CRP, IL-6) | 2.0% | [0.5%, 3.5%] | Mediator-adjusted |

Step 7.2: Consensus estimate
  APPROACH: Inverse-variance meta-analysis of robust methods
  
  WEIGHT equally: IVW (outlier-removed) + Median + Mode + CMM
  (exclude MR-Egger if InSIDE violated; exclude MVMR if primary question is total effect)
  
  β̂_consensus = [3.0 + 8.0 + 5.5 + 4.5] / 4 = 5.25%
  
  SE_consensus ≈ √[(1.8² + 3² + 3² + 2²) / 4] ≈ 2.3%
  
  95% CI: [0.8%, 9.7%]
  
  INTERPRETATION: Point estimate ≈ 5%, but wide CI reflects uncertainty from pleiotropy
               
Step 7.3: Final causal inference statement

  PRIMARY CONCLUSION:
  - "Each 1-unit increase in genetically predicted BMI is associated with a 3-5% increase in DLBCL risk."
  - "This estimate is consistent with horizontal pleiotropy biasing observational estimate (12%) upward."
  - "True causal effect likely between 3-5%, based on robust MR methods accounting for invalid instruments."

  CAVEATS:
  - 6% variance explained in BMI introduces weak instrument bias
  - ~20% of variants show evidence of pleiotropy, particularly those affecting inflammatory pathways
  - InSIDE assumption for MR-Egger is likely violated; mode/median estimates preferred
  - Causal effect may be partially mediated through inflammation (MVMR suggests ~1-2% of effect)

  CONFIDENCE: Moderate
    - Direction of effect (positive) robust across methods
    - Magnitude (3-5%) has substantial uncertainty due to pleiotropy
    - Stronger evidence needed: larger BMI GWAS → stronger instruments

===== STAGE 8: REPORTING AND VISUALIZATION =====

Step 8.1: Forest plot of estimates by method
  - Horizontal lines show 95% CIs for each method
  - Vertical line at consensus estimate (5%)
  - Highlight robust methods (median, mode, CMM) vs. standard (IVW)

Step 8.2: Radial plot (variant-level visualization)
  - X-axis: inverse SE of β_BMI (instrument strength)
  - Y-axis: β_DLBCL / β_BMI (per-variant causal estimate)
  - Points sized by variant weight
  - Colored by outlier status (MR-PRESSO)
  - Fitted lines from IVW (all), IVW (outlier-removed), MR-Egger
  
  INTERPRETATION: Visual assessment of pleiotropy (outliers visibly deviate from line)

Step 8.3: Sensitivity plot (leave-one-variant-out)
  - X-axis: variant ID (100 points)
  - Y-axis: β̂_IVW when that variant removed
  - Reference line at overall β̂_IVW
  - Highlight outliers
  
  INTERPRETATION: Shows stability of estimate

Step 8.4: Q-Q plot of p-values (for heterogeneity assessment)
  - Under null (no pleiotropy), p-values of heterogeneity test are uniform
  - Q-Q plot shows departure from uniformity
  - Excess small p-values indicate pleiotropy

===== END ALGORITHM =====

PSEUDOCODE SUMMARY:
1. Load & QC variants
2. Test pleiotropy globally (MR-Egger, Cochran's Q, PRESSO)
3. Detect individual outliers (3 methods: PRESSO, GLIDE, Cook's distance)
4. Calculate primary estimates (IVW, median, mode, Egger, CMM)
5. Run sensitivity analyses (LOVO, iterative outlier removal, subsets, MVMR)
6. Validate assumptions (InSIDE, weak instruments)
7. Synthesize: Forest plot + consensus estimate
8. Report with appropriate caveats on pleiotropy and uncertainty
```

---

## SUMMARY OF ALGORITHMIC APPROACH

This pipeline:

1. **Detects pleiotropy** through 4+ complementary methods (MR-Egger, PRESSO, GLIDE, statistical tests)
2. **Identifies pleiotropic variants** objectively (outlier detection) and contextualizes them (literature/gene annotation)
3. **Estimates causal effects robustly** using methods with different assumption strengths (IVW, median, mode, mixture models)
4. **Quantifies uncertainty** from pleiotropy via wide confidence intervals and multiple estimates
5. **Validates assumptions** (InSIDE, weak instruments) and identifies which are violated
6. **Provides sensitivity results** (outlier-removed, mediation-adjusted) to bracket the true effect
7. **Synthesizes findings** across methods for a consensus estimate

**For the BMI-DLBCL analysis:**
- **Robust causal estimate: 3-5% increased DLBCL risk per 1-unit BMI increase**
- **Pleiotropy explanation: ~20% of variants have direct effects on DLBCL independent of BMI, biasing observational estimate to 12%**
- **Recommended removal of pleiotropic variants and reporting with wide confidence intervals** to reflect pleiotropy-induced uncertainty

This approach balances efficiency, objectivity, and causal inference rigor for complex genetic data with violations of MR assumptions.
