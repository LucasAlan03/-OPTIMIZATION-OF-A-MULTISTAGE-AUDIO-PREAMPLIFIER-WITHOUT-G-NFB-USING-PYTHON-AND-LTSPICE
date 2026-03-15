import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os
from pathlib import Path

# garantir que rode na pasta do script
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ==============================
# Ler CSV
# ==============================

df = pd.read_csv("FREQ_VS_IS.csv")
df["Freq_corte (Khz)"] = df["Freq_corte (Khz)"].apply(lambda x: complex(x).real)

plt.figure(figsize=(8,5))
ax = plt.gca()

# ==============================
# cores das curvas
# ==============================

cores = {
    4.0: "green",
    6.0: "black",
    8.0: "red",
    10.0: "purple",
    12.0: "brown",
    14.0: "blue",
    16.0: "orange"
}

# ==============================
# organizar curvas
# ==============================

curvas = {}

for _, linha in df.iterrows():

    Is_mA = linha["Is_ma"]
    freq_kHz = linha["Freq_corte (Khz)"]
    Av = linha["Ganho"]

    curvas.setdefault(Av, {"Is": [], "freq": []})

    curvas[Av]["Is"].append(Is_mA)
    curvas[Av]["freq"].append(freq_kHz)

# ==============================
# plotar curvas
# ==============================

for Av in curvas:

    plt.plot(
        curvas[Av]["Is"],
        curvas[Av]["freq"],
        linewidth=2,
        color=cores.get(Av, "cyan"),
        label=f"Av={float(Av):.1f}".replace('.',',')
    )

# ==============================
# labels e limites
# ==============================

plt.xlabel("Is (mA)")
plt.ylabel("Frequência de Corte superior (kHz)")

plt.xlim(0.1, 2)
plt.ylim(500, 6100)

# ==============================
# divisões dos eixos
# ==============================

ax.xaxis.set_major_locator(MultipleLocator(0.5))
ax.xaxis.set_minor_locator(MultipleLocator(0.25))

ax.yaxis.set_major_locator(MultipleLocator(1000))
ax.yaxis.set_minor_locator(MultipleLocator(200))

# ==============================
# grid
# ==============================

ax.grid(True, which='major', linestyle='-', linewidth=1.0, alpha=1)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)

# ==============================
# legenda
# ==============================

plt.legend(loc="best", fontsize=8)

plt.tight_layout()

plt.savefig("FREQUENCIA_CORTE_VS_IS.png", dpi=600, bbox_inches="tight")

plt.close()

print("-----------Código terminou------------")