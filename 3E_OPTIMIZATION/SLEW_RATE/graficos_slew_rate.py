import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FuncFormatter
from pathlib import Path
import os

# ir para a pasta do script
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# ler CSV
df = pd.read_csv("SLEW_3E_FINAL.csv")

plt.figure(figsize=(8,5))
ax = plt.gca()

# Formatação eixo X/Y
def virgula_x(x, pos):
    return f"{x:.1f}".replace('.', ',')

def virgula_y(y, pos):
    return f"{y:.2f}".replace('.', ',')

ax.xaxis.set_major_formatter(FuncFormatter(virgula_x))
ax.yaxis.set_major_formatter(FuncFormatter(virgula_y))

# Divisões eixo X
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.xaxis.set_minor_locator(MultipleLocator(1))

# Divisões eixo Y
ax.yaxis.set_major_locator(MultipleLocator(0.01))
ax.yaxis.set_minor_locator(MultipleLocator())

# Grid
ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)

# Labels
plt.xlabel("Iout (mA)")
plt.ylabel("Slew Rate (V/μs)")

# Limites
plt.xlim(2,20)
plt.ylim(3.44,3.53)
# Plot
plt.plot(df['IOUT'], df['Slew Rate (V/us)'], linestyle='-')

plt.tight_layout()
#plt.show()

plt.savefig('SLEW_RATE_X_IOUT.png', dpi=600,bbox_inches='tight',pad_inches=0.1)

plt.close()