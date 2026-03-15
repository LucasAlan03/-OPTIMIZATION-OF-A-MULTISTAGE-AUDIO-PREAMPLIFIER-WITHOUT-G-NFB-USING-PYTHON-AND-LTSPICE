import pandas as pd
import os
from pathlib import Path
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

df = pd.read_csv("THD_VS_IC_2E_is_0.5_irb_1mA.csv")

# manter apenas Is = 0.5 e IRB = 1.0
df_filtrado = df[(df["Is_mA"] == 0.5) & (df["IRB_mA"] == 1.0)]

df_filtrado.to_csv("THD_VS_IC_2E_filtrado.csv", index=False)

print("Linhas originais:", len(df))
print("Linhas após filtro:", len(df_filtrado))