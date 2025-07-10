# 🧠 GLP-1 Obesity Scenario Model — Updated Plan (Logistic Adoption)

## ✅ Objective

Model U.S. **adult obesity prevalence** from 2023 to 2035 under three GLP-1 adoption scenarios (**Medical**, **Lifestyle**, **Universal**), using:

- **Logistic adoption curves**
- **28% efficacy** of GLP-1s in reducing obesity risk among users

## 📦 Inputs

From your dataset:
- `Year` (1990–2035)
- `Obesity_prevalence` (% of adult population)

Constants:
- **Efficacy**: E = 0.28
- **Max adoption by 2035**:
  - Medical: 8% (0.08)
  - Lifestyle: 30% (0.30)
  - Universal: 70% (0.70)

## 🧩 Modeling Steps

### ✅ Step 1: Define **Logistic Adoption Curves**

For each scenario, define adoption rate A(t) using:

```
A(t) = L / (1 + e^(-k(t - t₀)))
```

Where:
- L = final (max) adoption rate (e.g. 0.08, 0.30, 0.70)
- t = year
- t₀ = midpoint of adoption (e.g. 2029)
- k = steepness of curve (e.g. 0.8–1.2, adjust as needed)

This gives you smooth S-curves for:
- `GLP1_adoption_medical`
- `GLP1_adoption_lifestyle`
- `GLP1_adoption_universal`

Ensure:
- A(t) = 0 for t < 2023
- A(t) ≈ L for t ≥ 2035

### ✅ Step 2: Apply Obesity Reduction Formula

For each scenario and year:

```
Obesity_scenario(t) = Obesity_prevalence(t) × (1 - A(t) · E)
```

This adjusts the baseline obesity rate based on GLP-1 uptake and efficacy.

Create columns:
- `Obesity_medical`
- `Obesity_lifestyle`
- `Obesity_universal`

### ✅ Step 3 (Optional): Calculate Absolute Reductions

If your dataset includes adult population:

```
Cases_avoided_scenario(t) = (Obesity_prevalence(t) - Obesity_scenario(t)) × Population_adults(t)
```

Add:
- `Cases_avoided_medical`
- `Cases_avoided_lifestyle`
- `Cases_avoided_universal`

### ✅ Step 4: Export & Visualize

- Export final CSV with all columns
- Plot:
  - Line graph: Baseline vs. scenario obesity rates
  - Area or bar chart: Annual/cumulative obesity cases avoided

## 📌 Columns to Add

| Column | Description |
|--------|-------------|
| `GLP1_adoption_medical` | Logistic ramp to 8% |
| `GLP1_adoption_lifestyle` | Logistic ramp to 30% |
| `GLP1_adoption_universal` | Logistic ramp to 70% |
| `Obesity_medical` | Adjusted prevalence under medical scenario |
| `Obesity_lifestyle` | Adjusted prevalence under lifestyle scenario |
| `Obesity_universal` | Adjusted prevalence under universal scenario |
| `Cases_avoided_*` (optional) | Annual case reduction per scenario |

## 🧠 Optional Enhancements

- Tune logistic parameters k and t₀ to model fast vs. slow uptake
- Add uncertainty bands by varying E
- Extend to diabetes, healthcare cost savings, or QALYs