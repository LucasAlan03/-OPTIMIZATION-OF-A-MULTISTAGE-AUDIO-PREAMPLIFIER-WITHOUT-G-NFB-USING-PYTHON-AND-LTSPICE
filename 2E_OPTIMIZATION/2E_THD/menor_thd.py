import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os
from pathlib import Path
import numpy as np
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

df = pd.read_csv("THD_VS_IC_2E_filtrado.csv")
df.columns = df.columns.str.strip()
df = df.drop_duplicates(subset=["Av","IC_2E_mA"], keep="last")
thd = df["thd"].values
min = np.argmin(thd)
thdmin = thd[min]

print(f'menor valor de thd: {thdmin}')

