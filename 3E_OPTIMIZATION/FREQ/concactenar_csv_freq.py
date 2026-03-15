import pandas as pd
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)


# ler os dois csv
df_freq = pd.read_csv("FREQ_VS_Iout_3E.csv", sep=',')
df_iout = pd.read_csv("CORRENTE_AJUSTE_20m_IR13.csv")

# adicionar coluna
df_freq["IOUT"] = df_iout["IOUT"]

# salvar novo csv
df_freq.to_csv("FREQ_3E_FINAL.csv", sep=',', index=False)

print("CSV final criado!")