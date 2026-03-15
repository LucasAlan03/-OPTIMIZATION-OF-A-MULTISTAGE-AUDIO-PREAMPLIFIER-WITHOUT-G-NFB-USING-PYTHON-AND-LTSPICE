import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.ticker import AutoMinorLocator
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

df = pd.read_csv("FREQ_VS_IRB.csv")



plt.figure(figsize=(8,5))
ax = plt.gca()

curvas ={}
if __name__ == "__main__":
    print ("-----------Codigo começou------------")

    for _, row in df.iterrows():
        Freq_corte = complex(row["Freq_corte(Khz)"]).real
        ganho = row["Av"]
        is_ma = row["Is_mA"]
        irb = row["IRB_mA"]

        chave = (ganho,is_ma)

        curvas.setdefault(chave,{"corrente":[],"freq":[]})

        curvas[chave]["corrente"].append(irb)
        curvas[chave]["freq"].append(Freq_corte)

    # cores
    cores = {
        6.0: "black",
        8.0: "red",
        10.0: "purple",
        12.0: "brown",
    }


    # ---------------- PLOT ----------------
    def virgula(x, pos):
        return f"{x:.2f}".replace('.', ',')


    for (ganho,is_ma) in curvas:

        x = curvas[(ganho,is_ma)]["corrente"]
        y = curvas[(ganho,is_ma)]["freq"]

        dados = sorted(zip(x,y))

        x,y = zip(*dados)
        plt.plot(
            x,
            y,
            linewidth=2,
            color=cores.get(ganho, "blue"),
            label=f"Av={ganho} | Is= {is_ma:.2f}".replace('.',',')
        )


    # Labels
    plt.xlabel("Corrente IRB (mA)")
    plt.ylabel("Frequência de Corte (kHz)")
    plt.xlim(0.1,10)
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    plt.ylim(400,510)

    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(10))

    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    plt.legend(loc="best", fontsize=8)

    plt.tight_layout()

    plt.savefig("Freq_corteVsCorrente.png", dpi=600, bbox_inches="tight")

    plt.close()

print('----------------FIM DO CÓDIGO--------------------')