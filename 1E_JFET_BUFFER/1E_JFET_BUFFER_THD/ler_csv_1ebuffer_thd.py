import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.lines import Line2D
import os
import matplotlib.patches as patches
from pathlib import Path
from matplotlib.ticker import FuncFormatter

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

plt.figure(figsize=(8,5))


# -------- ler csv --------
df = pd.read_csv("THD_VS_AV_buffer_is_0_5_mA.csv")
df.columns = df.columns.str.strip()
plt.figure(figsize=(8,5))
ax = plt.gca()

curvas = {}

if __name__ == "__main__":
    print ("-----------Codigo começou------------")
# -------- organizar curvas --------
    for _, row in df.iterrows():

        ganho = row["Ganho"]
        i_mA = row["I_mA"]
        is_ma = row["Is_mA"]
        thd = row["THD"]

        chave = (ganho, is_ma)

        curvas.setdefault(chave, {"corrente":[], "thd":[]})

        curvas[chave]["corrente"].append(i_mA)
        curvas[chave]["thd"].append(thd)

# cores (opcional)
    cores = {
        6.0: "black",
        8.0: "red",
        10.0: "purple",
        12.0: "brown",
        14.0: "blue"
    }
    #LEGENDA THD
    linha_legenda = Line2D(
    [0], [0],
    color='black',
    linewidth=1.5,
    linestyle=(0,(5,3)),
    label='THD = 0,0012%'
)

    # -------- plot --------
    def virgula_x(x, pos):
        return f"{x:.2f}".replace('.', ',')
    
    def virgula_y(x, pos):
        return f"{x:.3f}".replace('.', ',')
    
    ax.xaxis.set_major_formatter(FuncFormatter(virgula_x))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula_y))

    rect = patches.Rectangle(
        (0, 0.00),        # canto inferior esquerdo (x,y)
        1.0 - 0,          # largura
        0.001 - 0,         # altura
        linewidth=1.5,
        edgecolor='black',
        facecolor='none',
        linestyle=(0,(5,3)),
        alpha=1,
        #label = 'THD = 0,0012'
    )

    ax.add_patch(rect)

    for (ganho, is_ma) in curvas:
        x = curvas[(ganho,is_ma)]["corrente"]
        y = curvas[(ganho,is_ma)]["thd"]

        dados = sorted(zip(x,y))

        x,y = zip(*dados)

        plt.plot(
            x,
            y,
            linewidth=2,
            color=cores.get(ganho,'green'),
            label=f"Av={ganho} "
        )

    # Labels
    plt.xlabel("Corrente IRB (mA)")
    plt.ylabel("THD (%)")

    # Limites eixo X
    plt.xlim(0.1,5)
    plt.ylim(0,0.004)

    # ---------- TICKS ----------

    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))

    ax.yaxis.set_major_locator(MultipleLocator(0.002))
    ax.yaxis.set_minor_locator(MultipleLocator(0.0005))

    '''
    plt.axhline(
        0.001,
        linestyle='--',
        linewidth=1,
        color='black'
    )
    '''

    # ---------- GRID ----------

    ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(linha_legenda)

    plt.legend(handles=handles, fontsize=8, loc="best")



    plt.tight_layout()

    plt.savefig("THD_vs_CORRENTE_IRB_BUFFER_J201_IRB.png", dpi=600, bbox_inches="tight")

    plt.close()


print("---------FIM DO CÓDIGO---------")