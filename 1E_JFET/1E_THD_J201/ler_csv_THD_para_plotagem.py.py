import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.patches as patches
from matplotlib.ticker import FuncFormatter
import os
from matplotlib.lines import Line2D
from pathlib import Path

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

if __name__ == "__main__":

    print('------------------Codigo começou-------------------')

    # Ler CSV
    dados_df = pd.read_csv("THD_VS_AV.csv")

    plt.figure(figsize=(8,5))
    ax = plt.gca()

    curvas = {}

    current_target = [0.5,0.8,1,1.5]

    cores = {
        0.5: "black",
        0.8: "red",
        1.0: "purple",
        1.5: "brown",

    }

    # reconstruir dicionário de curvas
    for _, row in dados_df.iterrows():

        Av = row["Ganho"]
        Is_ma = row["Is_mA"]
        thd = row["THD"]

        if Is_ma not in current_target:
            continue

        curvas.setdefault(Is_ma, {"Av":[], "thd":[]})
        curvas[Is_ma]["Av"].append(Av)
        curvas[Is_ma]["thd"].append(thd)

    # plot

    # Substituindo ponto por virgula
    def virgula(x, pos):
        return f"{x:.4f}".replace('.', ',')
    
# ----------------Regiao de interesse-----------------------#
    rect = patches.Rectangle(
        (6,0.0005 ),        # canto inferior esquerdo (Av=6, THD=0)
        12 - 6,        # largura (até Av=15)
        0.00119-0.0005,         # altura (até THD=0.001)
        linewidth=1.3,
        edgecolor='black',
        facecolor='none',
        linestyle='--',
        alpha=1
    )

    ax.add_patch(rect)

    linha_legenda = Line2D(
    [0], [0],
    color='black',
    linewidth=1.5,
    linestyle=(0,(5,3)),
    label='THD = 0,0012')


    ax.xaxis.set_major_formatter(FuncFormatter(virgula))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula))
    for Is_ma in curvas:
        plt.plot(
            curvas[Is_ma]["Av"],
            curvas[Is_ma]["thd"],
            linewidth=1.5,
            color=cores.get(Is_ma, "blue"),
            label=f"Is={Is_ma:.1f}mA".replace('.',',')
        )

    plt.xlabel("AV (Ganho)")
    plt.ylabel("THD (%)")

    # divisões eixo X
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))

    # grid
    ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)

    # divisões eixo Y
    ax.yaxis.set_major_locator(MultipleLocator(0.0005))
    ax.yaxis.set_minor_locator(MultipleLocator(0.0005))

    plt.xlim(6,16)
    plt.ylim(0.0005,0.0025)


    handles, labels = ax.get_legend_handles_labels()
    handles.append(linha_legenda)
    plt.legend(handles=handles, fontsize=8, loc="best")

    plt.tight_layout()
    plt.savefig("THD_VS_AV.png", dpi=600, bbox_inches="tight")
    plt.close()

print('----------Fim do código--------------------')