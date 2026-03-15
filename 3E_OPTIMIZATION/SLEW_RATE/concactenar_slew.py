import pandas as pd
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ler os dois csv
df_slew = pd.read_csv("3E_SLEW_RATE.csv", sep=',')
df_iout = pd.read_csv("CORRENTE_AJUSTE_20m_IR13.csv")

# adicionar coluna
df_slew["IOUT"] = df_iout["IOUT"]

# salvar novo csv
df_slew.to_csv("SLEW_3E_FINAL.csv", sep=',', index=False)

print("CSV final criado!")