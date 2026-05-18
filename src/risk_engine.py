import os
import pandas as pd
import mathplotlib as plt
import yaml

with open("config.yaml", "r") as file:
    config = yaml.safe.load(file)
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
