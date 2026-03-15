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

    df = pd.read_csv("THD_3E_FINAL.csv")

    plt.figure(figsize=(8,5))
    ax = plt.gca()
    

    # Substituindo ponto por virgula
    def virgula_x(x, pos):
        return f"{x:.1f}".replace('.', ',')
    
    def virgula_y(y, pos):
        return f"{y:.3f}".replace('.', ',')
    
    ax.xaxis.set_major_formatter(FuncFormatter(virgula_x))
    ax.yaxis.set_major_formatter(FuncFormatter(virgula_y))

        # divisões eixo X
    ax.xaxis.set_major_locator(MultipleLocator(2))
    ax.xaxis.set_minor_locator(MultipleLocator(1))

    # grid
    ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
    ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)

    # divisões eixo Y
    ax.yaxis.set_major_locator(MultipleLocator(0.002))
    ax.yaxis.set_minor_locator(MultipleLocator(0.0005))


    plt.xlabel("Iout (mA)")
    plt.ylabel("THD (%)")

    plt.xlim(2,20)
    plt.ylim(0.003,0.01)
    plt.plot(df['IOUT'],df['thd'])
    
    plt.tight_layout()

    plt.savefig("THD_vs_IOUT_20mA.png", dpi=600, bbox_inches="tight")

    plt.close()
