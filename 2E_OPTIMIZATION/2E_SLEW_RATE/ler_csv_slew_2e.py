import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ---------------- LER CSV ----------------
df = pd.read_csv("Slew_Rate_VS_IC_2E_is05_IRB1mA.csv")
df.columns = df.columns.str.strip()

plt.figure(figsize=(8,5))
ax = plt.gca()

curvas = {}

if __name__ == "__main__":
    print("-----------Codigo começou------------")

    # reconstruir curvas
    for _, row in df.iterrows():

        ganho = row["Av"]
        is_ma = row["Is_mA"]
        irb = row["IRB_mA"]
        av2 = row["Av2"]

        ic2e = row["IC_2E_mA"]
        slew = row["Slew_rate(V/us)"]

        chave = (ganho, is_ma, irb, av2)

        curvas.setdefault(chave, {"corrente":[], "slew":[]})

        curvas[chave]["corrente"].append(ic2e)
        curvas[chave]["slew"].append(slew)

    # cores por ganho
    cores = {
        6.0: "black",
        8.0: "red",
        10.0: "purple",
        12.0: "brown",
    }

    # ---------------- PLOT ----------------

    for (ganho, is_ma, irb, av2) in curvas:

        x = curvas[(ganho,is_ma,irb,av2)]["corrente"]
        y = curvas[(ganho,is_ma,irb,av2)]["slew"]

        dados = sorted(zip(x,y))
        x,y = zip(*dados)

        plt.plot(
            x,
            y,
            linewidth=2,
            color=cores.get(ganho,"blue"),
            label=f"Av1={ganho} | Av2={av2}".replace('.',',')
        )

    # ---------------- FORMATACAO ----------------

    plt.xlabel("Corrente IC segundo estágio (mA)")
    plt.ylabel("Slew Rate (V/μs)")

    plt.xlim(0.5,10)
    plt.ylim(1.1,4.7)
  

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    # linha limite
    plt.axhline(
        1.41,
        linestyle='--',
        linewidth=1.5,
        color='black',
        label="Slew Rate ponto ótimo (1,41 V/μs)"
    )

    # -------- trocar ponto por vírgula --------

    def virgula(x, pos):
        return f"{x:.2f}".replace('.', ',')

    ax.xaxis.set_major_formatter(FuncFormatter(virgula))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula))

    plt.legend(loc="best", fontsize=7)

    plt.tight_layout()

    plt.savefig("SlewRateVsIC_2E.png", dpi=600, bbox_inches="tight")

    plt.close()

print('---------------------------FIM DO CÓDIGO----------------------')