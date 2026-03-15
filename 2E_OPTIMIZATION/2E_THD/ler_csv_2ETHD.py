import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os
from pathlib import Path
import numpy as np
from matplotlib.ticker import FuncFormatter
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

df = pd.read_csv("THD_VS_IC_2E_filtrado.csv")
df.columns = df.columns.str.strip()
df = df.drop_duplicates(subset=["Av","IC_2E_mA"], keep="last")
thd = df["thd"].values
min = np.argmin(thd)


plt.figure(figsize=(8,5))
ax = plt.gca()

curvas = {}

if __name__ == "__main__":
    print("-----------Codigo começou------------")

    for _, row in df.iterrows():

        ganho = row["Av"]
        is_ma = row["Is_mA"]
        irb = row["IRB_mA"]
        av2 = row["Av2"]
        ic2e = row["IC_2E_mA"]
        thd = row["thd"]

        chave = (ganho, is_ma, irb, av2)

        curvas.setdefault(chave, {"corrente":[], "thd":[]})

        curvas[chave]["corrente"].append(ic2e)
        curvas[chave]["thd"].append(thd)


    # cores por ganho (opcional)
    cores = {
        6.0: "black",
        8.0: "red",
        10.0: "purple",
        12.0: "brown",
    }

    # ---------------- PLOT ----------------


    def virgula(x, pos):
        return f"{x:.3f}".replace('.', ',')
    
 
    ax.yaxis.set_major_formatter(FuncFormatter(virgula))

    for (ganho, is_ma, irb, av2) in sorted(curvas):

        x = curvas[(ganho,is_ma,irb,av2)]["corrente"]
        y = curvas[(ganho,is_ma,irb,av2)]["thd"]

        dados = sorted(zip(x,y))
        x,y = zip(*dados)

        plt.plot(
            x,
            y,
            linewidth=2,
            color=cores.get(ganho,'blue'),
            label=f"Av1={ganho} | Av2={av2}".replace('.',',')
        )

    # Labels
    plt.xlabel("Corrente IC segundo estágio (mA)")
    plt.ylabel("THD (%)")

    plt.xlim(0,6)
    plt.ylim(0.007,0.03)
    # ---------- TICKS ----------

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    ax.yaxis.set_major_locator(MultipleLocator(0.005))
    ax.yaxis.set_minor_locator(MultipleLocator(0.001))

    # linha referência THD
    '''
    plt.axhline(
        0.001,
        linestyle='--',
        linewidth=1,
        color='black',
        label='THD alvo (0.1%)'
    )
    '''
    # ---------- GRID ----------

    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    plt.legend(loc="best", fontsize=7)

    plt.tight_layout()

    plt.savefig("THD_vs_IC2E_FFT_MAIS_PONTOS.png", dpi=600, bbox_inches="tight")

    plt.close()

print('----------------FIM DO CÓDIGO--------------------')
