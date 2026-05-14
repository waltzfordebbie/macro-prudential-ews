import io
import pandas as pd


def data_to_df(bis_results, hkma_results):
    df_bis_hkcreditgap = pd.read_csv(io.StringIO(bis_results[0]))
    df_bis_hkpropindex = pd.read_csv(io.StringIO(bis_results[1]))
    df_hkma_hkaggbalance = pd.DataFrame(hkma_results[0]["result"]["records"])
    df_hkma_hkaggbalance["end_of_date"] = pd.to_datetime(
        df_hkma_hkaggbalance["end_of_date"]
    )
    return df_bis_hkcreditgap, df_bis_hkpropindex, df_hkma_hkaggbalance
