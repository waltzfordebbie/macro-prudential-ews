import os
from fetch_data import fetch_data
from database import data_to_df
from risk_engine import risk_analysis

bis_results, hkma_results = fetch_data()

df_bis_hkcreditgap, df_bis_hkpropindex, df_hkma_hkaggbalance = data_to_df(
    bis_results, hkma_results
)

df_ews = risk_analysis(df_bis_hkcreditgap, df_bis_hkpropindex, df_hkma_hkaggbalance)

os.makedirs("output", exist_ok=True)
df_ews.to_csv("output/ews_scores.csv")
