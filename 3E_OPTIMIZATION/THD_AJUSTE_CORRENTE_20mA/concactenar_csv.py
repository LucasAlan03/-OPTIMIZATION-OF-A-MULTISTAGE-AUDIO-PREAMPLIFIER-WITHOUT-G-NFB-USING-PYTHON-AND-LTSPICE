import pandas as pd
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ler os dois csv
df_thd = pd.read_csv("THD_3E.csv", sep=';')
df_iout = pd.read_csv("CORRENTE_AJUSTE_20m_IR13.csv")

# adicionar coluna
df_thd["IOUT"] = df_iout["IOUT"]

# salvar novo csv
df_thd.to_csv("THD_3E_FINAL.csv", sep=';', index=False)

print("CSV final criado!")