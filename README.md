# Macro-Prudential Early Warning System — Hong Kong

An automated Early Warning System (EWS) for monitoring systemic financial risk in Hong Kong. Built on the BIS Credit-to-GDP gap methodology and extended with property price and liquidity flow signals, the system produces a composite risk score and colour-coded regime classification (Amber / Orange / Red) on a quarterly basis.

---

## Overview

Systemic financial crises rarely arrive without warning. Credit overexpansion, property price misalignment, and liquidity deterioration tend to build over multiple quarters before stress materialises. This EWS is designed to detect that buildup — providing a forward-looking signal suitable for macro-prudential policy decisions rather than real-time crisis detection.

The model draws on the same conceptual framework used by the BIS, HKMA, and IMF for countercyclical capital buffer guidance.

---

## Signals

The composite EWS score is derived from the following indicators:

| Signal | Source | Method |
|---|---|---|
| Credit-to-GDP gap (`GAP`) | BIS | Hodrick-Prescott (HP) filter |
| Credit gap momentum (`GAP_DELTA`) | BIS | Quarter-on-quarter gap change |
| Residential property price index (`INDEX_YOY`) | BIS | Year-on-year % change |
| Liquidity balance crossover (`BALANCE_CROSSOVER`) | HKMA | Net flow threshold breach |
| Fast liquidity balance (`BALANCE_FAST`) | HKMA | Short-window flow level |

Each signal is scored on threshold breach, weighted, and summed into a composite score. The score maps to a regime:

| Score | Regime | Interpretation |
|---|---|---|
| 0 – 20 | 🟢 Green | No significant stress signals |
| 20 – 45 | 🟡 Amber | Low-to-moderate risk, monitor |
| 45 – 70 | 🟠 Orange | Elevated risk, consider tightening |
| 70 – 100 | 🔴 Red | High systemic risk, action warranted |

Thresholds, weights, regime bins, and persistence rules are fully configurable via `config.yaml`.

---

## Configuration

All threshold and weighting parameters live in `config.yaml` — no code changes required to recalibrate the model.

```yaml
thresholds:
  GAP:
    warn: 2.0
    critical: 10.0
  GAP_DELTA:
    warn: 1.5
    critical: 3.0
  INDEX_YOY:
    warn: 0.10
    critical: 0.15
  BALANCE_CROSSOVER:
    warn: -20.0
    critical: -50.0
  BALANCE_FAST:
    warn: 80.0
    critical: 60.0
weights:
  GAP: 3.0
  INDEX_YOY: 2.5
  GAP_DELTA: 2.0
  BALANCE_CROSSOVER: 1.5
  BALANCE_FAST: 1.0
regime_bins: [0, 20, 45, 70, 100]
persistence_quarters: 2
```

### Thresholds

Each signal has a `warn` and `critical` level. Breaching `warn` contributes a partial score; breaching `critical` contributes the full weighted score for that signal.

#### `GAP` — Credit-to-GDP gap (HP filtered)
The deviation of the credit-to-GDP ratio from its long-run HP-filtered trend, expressed in percentage points. The BIS recommends this as the primary countercyclical capital buffer indicator.

| Level | Value | Interpretation |
|---|---|---|
| `warn` | 2.0 pp | Early-stage credit overexpansion; monitor |
| `critical` | 10.0 pp | Severe credit excess; aligns with BIS Red zone guidance |

#### `GAP_DELTA` — Quarter-on-quarter change in credit gap
The first difference of the GAP series. Captures acceleration in credit growth even when the absolute gap level is still moderate — useful for early detection of a building cycle.

| Level | Value | Interpretation |
|---|---|---|
| `warn` | 1.5 pp | Gap widening at a concerning pace |
| `critical` | 3.0 pp | Rapid gap acceleration; strong momentum signal |

#### `INDEX_YOY` — BIS residential property price index (year-on-year change)
Annual growth rate of the BIS property price index for Hong Kong. Property price inflation is a core systemic risk indicator for HK given the economy's structural exposure to real estate.

| Level | Value | Interpretation |
|---|---|---|
| `warn` | 10% | Above-trend price appreciation |
| `critical` | 15% | Rapid price inflation consistent with bubble conditions |

#### `BALANCE_CROSSOVER` — HKMA liquidity balance crossover
Captures the point at which aggregate HKMA liquidity flows turn negative, signalling net outflows from the banking system. A negative value means outflows are occurring; a more negative value indicates severity.

| Level | Value | Interpretation |
|---|---|---|
| `warn` | −20.0 | Mild net outflow; early liquidity deterioration |
| `critical` | −50.0 | Severe net outflow; significant liquidity stress |

#### `BALANCE_FAST` — Fast-moving liquidity balance
A shorter-window liquidity measure that reacts more quickly to sudden flow changes than the crossover signal. Note the inverted direction: a *lower* value indicates faster deterioration.

| Level | Value | Interpretation |
|---|---|---|
| `warn` | 80.0 | Liquidity buffer thinning |
| `critical` | 60.0 | Liquidity buffer critically low |

---

### Weights

Signals are scored on breach and multiplied by their weight before summing into the composite `EWS_SCORE`. Higher weight = greater influence on the final score.

| Signal | Weight | Rationale |
|---|---|---|
| `GAP` | 3.0 | Primary BIS indicator; highest predictive validity in literature |
| `INDEX_YOY` | 2.5 | HK property prices are the dominant systemic risk driver |
| `GAP_DELTA` | 2.0 | Adds momentum sensitivity to the level signal |
| `BALANCE_CROSSOVER` | 1.5 | Liquidity stress indicator; secondary to credit signals |
| `BALANCE_FAST` | 1.0 | Fast-reacting but noisier; lowest weight to reduce false positives |

Total maximum weighted score normalises to 100.

---

### Regime bins

```yaml
regime_bins: [0, 20, 45, 70, 100]
```

Defines the score boundaries for regime classification:

| Score range | Regime | Policy implication |
|---|---|---|
| 0 – 20 | 🟢 Green | No significant stress signals |
| 20 – 45 | 🟡 Amber | Low-to-moderate risk; maintain monitoring |
| 45 – 70 | 🟠 Orange | Elevated risk; consider macro-prudential tightening |
| 70 – 100 | 🔴 Red | High systemic risk; strong case for intervention |

---

### Persistence

```yaml
persistence_quarters: 2
```

A regime upgrade (e.g. Amber → Orange) requires the score to breach the threshold for at least **2 consecutive quarters** before the regime changes. This prevents single-quarter data noise from triggering false escalations. Regime *downgrades* apply immediately.

---

This separation of configuration from logic makes the system straightforward to back-test under alternative parameter assumptions without modifying source code.

---

## Pipeline

```
BIS REST API  ──┐
                ├──▶  API-to-DataFrame pipeline  ──▶  Signal scoring  ──▶  EWS_SCORE / EWS_REGIME
HKMA REST API ──┘
```

- High-performance async data ingestion from BIS and HKMA public APIs
- HP filtering applied to credit and property series to extract cyclical components
- Composite scoring engine with YAML-driven threshold classification
- Output: quarterly `EWS_SCORE` (0–100) and `EWS_REGIME` label

---

## Sample Output

```
TIME_PERIOD    EWS_SCORE    EWS_REGIME
2025-10-01         30.0         Amber
2024-01-01         30.0         Amber
2022-04-01         50.0        Orange
2018-04-01         75.0           Red
2015-01-01         90.0           Red   ← cycle peak
```

The model correctly identified sustained Red regimes during HK's two major property bubble peaks (2015, 2017–2018) and elevated Orange conditions through the post-GFC credit expansion cycle (2010–2014).

---

## Methodology Notes

This model is designed as a **buildup detector**, not a real-time crisis monitor. Credit-to-GDP gap models are well-validated in the academic literature for signalling stress 2–6 quarters ahead of peak. The BIS reports approximately 70% sensitivity at a 10% false positive rate for this class of model globally; HK's property-driven cycle makes the property price index addition particularly informative.

**Known limitations:**
- Acute liquidity shocks (e.g. Q4 2008) may not be captured — the gap methodology goes quiet once credit contracts
- Regime transitions can lag on the downside; Orange may persist after conditions have already begun normalising
- With ~4 meaningful stress cycles in the 23-year sample, statistical validation is inherently limited — consistent with constraints faced by central bank EWS models globally

---

## Requirements

```
python >= 3.9
pandas
requests
pyyaml
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python src/main.py
```

Output is written to `output/ews_scores.csv`.

To adjust thresholds or signal weights, edit `config.yaml` before running.

---

## References

- BIS Working Paper — *Credit-to-GDP gaps and countercyclical capital buffers* (Basel III)
- HKMA — Residential Mortgage Survey & Monetary Statistics
- Drehmann, M. & Tsatsaronis, K. (2014) — *The credit-to-GDP gap and countercyclical capital buffers*
