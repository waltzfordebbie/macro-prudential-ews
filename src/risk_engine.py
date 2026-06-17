import pandas as pd
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)
thresholds = config["thresholds"]
weights = config["weights"]
regime_bins = config["regime_bins"]
persistence_quarters = config["persistence_quarters"]


def risk_analysis(df_bis_hkcreditgap, df_bis_hkpropindex, df_hkma_hkaggbalance):
    df_bis_hkcreditgap["GAP_DELTA"] = df_bis_hkcreditgap["GAP"].diff()
    df_bis_hkpropindex["INDEX_YOY"] = df_bis_hkpropindex["INDEX"].pct_change(12)
    df_hkma_hkaggbalance["BALANCE_SLOW"] = (
        df_hkma_hkaggbalance["BALANCE"].rolling(30).mean()
    )
    df_hkma_hkaggbalance["BALANCE_FAST"] = (
        df_hkma_hkaggbalance["BALANCE"].rolling(7).mean()
    )
    df_hkma_hkaggbalance["BALANCE_CROSSOVER"] = (
        df_hkma_hkaggbalance["BALANCE_FAST"] - df_hkma_hkaggbalance["BALANCE_SLOW"]
    )
    df_bis_hkcreditgap["GAP_WARN"] = (
        df_bis_hkcreditgap["GAP"] >= thresholds["GAP"]["warn"]
    )
    df_bis_hkcreditgap["GAP_CRITICAL"] = (
        df_bis_hkcreditgap["GAP"] >= thresholds["GAP"]["critical"]
    )
    df_bis_hkcreditgap["GAP_DELTA_WARN"] = (
        df_bis_hkcreditgap["GAP_DELTA"] >= thresholds["GAP_DELTA"]["warn"]
    )
    df_bis_hkcreditgap["GAP_DELTA_CRITICAL"] = (
        df_bis_hkcreditgap["GAP_DELTA"] >= thresholds["GAP_DELTA"]["critical"]
    )
    df_bis_hkpropindex["INDEX_YOY_WARN"] = (
        df_bis_hkpropindex["INDEX_YOY"] >= thresholds["INDEX_YOY"]["warn"]
    )
    df_bis_hkpropindex["INDEX_YOY_CRITICAL"] = (
        df_bis_hkpropindex["INDEX_YOY"] >= thresholds["INDEX_YOY"]["critical"]
    )
    df_hkma_hkaggbalance["BALANCE_CROSSOVER_WARN"] = (
        df_hkma_hkaggbalance["BALANCE_CROSSOVER"]
        <= thresholds["BALANCE_CROSSOVER"]["warn"]
    )
    df_hkma_hkaggbalance["BALANCE_CROSSOVER_CRITICAL"] = (
        df_hkma_hkaggbalance["BALANCE_CROSSOVER"]
        <= thresholds["BALANCE_CROSSOVER"]["critical"]
    )
    df_hkma_hkaggbalance["BALANCE_FAST_WARN"] = (
        df_hkma_hkaggbalance["BALANCE_FAST"] < thresholds["BALANCE_FAST"]["warn"]
    )
    df_hkma_hkaggbalance["BALANCE_FAST_CRITICAL"] = (
        df_hkma_hkaggbalance["BALANCE_FAST"] < thresholds["BALANCE_FAST"]["critical"]
    )

    gap_q = df_bis_hkcreditgap.resample("QS").last()
    propidx_q = df_bis_hkpropindex.resample("QS").last()
    balance_q = df_hkma_hkaggbalance.resample("QS").last()

    score = (
        (gap_q["GAP_WARN"].astype(int) + gap_q["GAP_CRITICAL"].astype(int))
        * weights["GAP"]
        + (
            gap_q["GAP_DELTA_WARN"].astype(int)
            + gap_q["GAP_DELTA_CRITICAL"].astype(int)
        )
        * weights["GAP_DELTA"]
        + (
            propidx_q["INDEX_YOY_WARN"].astype(int)
            + propidx_q["INDEX_YOY_CRITICAL"].astype(int)
        )
        * weights["INDEX_YOY"]
        + (
            balance_q["BALANCE_CROSSOVER_WARN"].astype(int)
            + balance_q["BALANCE_CROSSOVER_CRITICAL"].astype(int)
        )
        * weights["BALANCE_CROSSOVER"]
        + (
            balance_q["BALANCE_FAST_WARN"].astype(int)
            + balance_q["BALANCE_FAST_CRITICAL"].astype(int)
        )
        * weights["BALANCE_FAST"]
    )
    max_score = sum(w * 2 for w in weights.values())
    ews_score_norm = (score / max_score * 100).round(1)

    ews_regime = pd.cut(
        ews_score_norm,
        bins=regime_bins,
        labels=["Green", "Amber", "Orange", "Red"],
        include_lowest=True,
    )
    df_ews = (
        pd.DataFrame(
            {
                "EWS_SCORE": ews_score_norm,
                "EWS_REGIME": ews_regime,
            },
            index=ews_score_norm.index,
        )
        .sort_index(ascending=False)
        .dropna()
    )
    return df_ews
