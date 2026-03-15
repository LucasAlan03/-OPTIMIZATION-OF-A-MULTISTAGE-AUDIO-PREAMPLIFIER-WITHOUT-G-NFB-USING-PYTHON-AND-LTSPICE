import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator, FuncFormatter
import os
from pathlib import Path
# ensure script runs from its own directory so relative paths resolve correctly
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)


# -------- ler csv --------
df_plot = pd.read_csv("SLEW_RATE.csv")

plt.figure(figsize=(8,5))
ax = plt.gca()


# Plotar só para alguns ganhos.

gain_target = [2,4,6,8,10,12,14,16]


cores = {
    2.0: "crimson",
    4.0: "green",
    6.0: "black",
    8.0: "red",
    10.0: "purple",
    12.0: "brown",
    14.0: "blue",
    16.0: "orange"
}

curvas_plt = {}

if __name__ == "__main__":
    print ("-----------Codigo começou------------")
# -------- organizar curvas --------
    for _, linha in df_plot.iterrows():

        av = linha["Av"]
        if av not in gain_target:
            continue
        Is_ma = linha["Is_ma"]
        slew = linha["Slew_Rate "]
       
        curvas_plt.setdefault(av, {"Is_ma":[], "slew_rate":[]})

        curvas_plt[av]["Is_ma"].append(Is_ma)
        curvas_plt[av]["slew_rate"].append(slew)

    # ---------------REGIAO DE INTERESSE:

    '''
    rect = patches.Rectangle(
        (0.37, 1.41),        # canto inferior esquerdo (x,y)
        2.0 - 0.37,          # largura
        1.75 - 1.41,         # altura
        linewidth=1.3,
        edgecolor='black',
        facecolor='none',
        linestyle='--',
        alpha=1,
        label = 'Slew Rate ponto ótimo (1,41 V/μs)'
    )

    ax.add_patch(rect)
    '''
    # -------- plot --------
    for av in curvas_plt:

        plt.plot(
            curvas_plt[av]["Is_ma"],
            curvas_plt[av]["slew_rate"],
            linewidth=1.5,
            color=cores.get(av,'cyan'),
            label=f"Av={av}".replace('.',',')
        )

    plt.xlabel("Corrente Is (mA)")
    plt.ylabel("Slew Rate (V/μs)")

    # -------- linhas de referência --------
    
    plt.axhline(
        1.41,
        linestyle='--',
        color='black',
        linewidth=1.5,
        label='Slew Rate ponto ótimo'
    )



    
    # -------- escalas --------
    plt.xlim(0.1,2)
    plt.ylim(0.5,1.75)

    ax.xaxis.set_major_locator(MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    # -------- grid --------
    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    # -------- trocar ponto por vírgula --------
    def virgula(x, pos):
        return f"{x:.2f}".replace('.', ',')

    ax.xaxis.set_major_formatter(FuncFormatter(virgula))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula))

    plt.legend(loc="best", fontsize=8)

    plt.tight_layout()

    plt.savefig("SlewRateVsCorrente.png", dpi=600, bbox_inches="tight")

    plt.close()

print('--------------------Fim do código------------------------')