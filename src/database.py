import io
import pandas as pd


def data_to_df(bis_results, hkma_results):
    df_bis_hkcreditgap = pd.read_csv(io.StringIO(bis_results[0]))
    df_bis_hkcreditgap.index = pd.PeriodIndex(
        df_bis_hkcreditgap["TIME_PERIOD"], freq="Q"
    ).to_timestamp()
    df_bis_hkcreditgap = df_bis_hkcreditgap[["OBS_VALUE"]].copy()
    df_bis_hkcreditgap.columns = ["GAP"]

    df_bis_hkpropindex = pd.read_csv(io.StringIO(bis_results[1]))
    df_bis_hkpropindex.index = pd.to_datetime(
        df_bis_hkpropindex["TIME_PERIOD"], format="%Y-%m"
    )
    df_bis_hkpropindex = df_bis_hkpropindex[["OBS_VALUE"]].copy()
    df_bis_hkpropindex.columns = ["INDEX"]

    df_hkma_hkaggbalance = pd.concat(
        [pd.DataFrame(hkma_results[i]["result"]["records"]) for i in range(9)],
        ignore_index=True,
    )
    df_hkma_hkaggbalance.index = pd.to_datetime(
        df_hkma_hkaggbalance["end_of_date"], format="%Y-%m-%d"
    )
    df_hkma_hkaggbalance.index.name = "TIME_PERIOD"
    df_hkma_hkaggbalance = df_hkma_hkaggbalance[["aggr_balance_bf_disc_win"]].copy()
    df_hkma_hkaggbalance.columns = ["BALANCE"]

    return df_bis_hkcreditgap, df_bis_hkpropindex, df_hkma_hkaggbalance
