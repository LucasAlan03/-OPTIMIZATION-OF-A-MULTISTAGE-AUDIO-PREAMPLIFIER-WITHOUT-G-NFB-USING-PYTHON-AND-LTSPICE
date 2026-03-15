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
    print("-----------Codigo começou------------")

    df = pd.read_csv("FREQ_3E_FINAL.csv")
    Freq_corte = df["Freq_corte(Khz)"].apply(lambda x: complex(x).real)

    plt.figure(figsize=(8,5))
    ax = plt.gca()
    

    # Substituindo ponto por virgula
    def virgula_x(x, pos):
        return f"{x:.1f}".replace('.', ',')
    
    def virgula_y(y, pos):
        return f"{y:.1f}".replace('.', ',')
    
    ax.xaxis.set_major_formatter(FuncFormatter(virgula_x))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula_y))

            # divisões eixo X
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))

    # grid
    ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)

    # divisões eixo Y
    ax.yaxis.set_major_locator(MultipleLocator())
    ax.yaxis.set_minor_locator(MultipleLocator())


    plt.xlabel("Iout (mA)")
    plt.ylabel("Frequência de Corte superior (KHz)")

    plt.xlim(2,20)
    plt.ylim(267,270)
    plt.plot(df['IOUT'],Freq_corte)
    
    plt.tight_layout()

    plt.savefig("FREQ_vs_IOUT_20mA.png", dpi=600, bbox_inches="tight")

    plt.close()