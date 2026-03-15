import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from matplotlib.ticker import AutoMinorLocator
import os
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ---------------- LER CSV ----------------
df = pd.read_csv("SLEW_RATE_FINAL.csv")

plt.figure(figsize=(8,5))
ax = plt.gca()

curvas = {}

if __name__ == "__main__":
    print ("-----------Codigo começou------------")
# reconstruir as curvas
    for _, row in df.iterrows():

        i_mA = row["IRB_ma"]
        ganho = row["Av"]
        is_ma = row["Is_ma"]
        if is_ma != 0.5:
            continue

        slew = row["Slew_Rate_Metodo1_V_per_us"]

        chave = (ganho,is_ma)
        curvas.setdefault(chave, {"corrente":[], "slew":[]})

        curvas[chave]["corrente"].append(i_mA)
        curvas[chave]["slew"].append(slew)

    # cores
    cores = {
        6.0: "black",
        8.0: "red",
        10.0: "purple",
        12.0: "brown",
    }

    # ---------------- PLOT ----------------
    for (ganho,is_ma) in curvas:
        x = curvas[(ganho,is_ma)]["corrente"]
        y = curvas[(ganho,is_ma)]["slew"]

        dados = sorted(zip(x,y))

        x,y = zip(*dados)

        plt.plot(
            x,
            y,
            linewidth=2,
            color=cores.get(ganho, "blue"),
            label=f"Av={ganho}"
        )

    # ---------------- FORMATACAO ----------------

    plt.xlabel("Corrente IRB (mA)")
    plt.ylabel("Slew Rate (V/μs)")
    plt.ylim(0.15,0.65)
    plt.xlim(0.1,5)

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    ax.yaxis.set_major_locator(MultipleLocator(0.15))
    ax.yaxis.set_minor_locator(MultipleLocator(0.10))

    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    # linha limite
    plt.axhline(
        0.35,
        linestyle='--',
        linewidth=1.5,
        color='black',
        label="Slew Rate minímo (0,35 V/μs)"
    )

    # -------- trocar ponto por virgula --------

    def virgula(x, pos):
        return f"{x:.2f}".replace('.', ',')

    ax.xaxis.set_major_formatter(FuncFormatter(virgula))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula))

    # legenda
    plt.legend(loc="lower right", fontsize=8)

    plt.tight_layout()

    plt.savefig("SlewRateVsCorrente_IRB.png", dpi=600, bbox_inches="tight")

    plt.close()


print('---------------------------FIM DO CÓDIGO----------------------')