import pandas as pd
import os 
from pathlib import Path


_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)
# arquivos
csv_antigo = "SLEW_RATE.csv"
csv_novo = "SLEW_RATE_is_0.csv"
csv_saida = "SLEW_RATE_FINAL.csv"

# ler arquivos
df_antigo = pd.read_csv(csv_antigo)
df_novo = pd.read_csv(csv_novo)

# limpar precisão numérica
for df in [df_antigo, df_novo]:
    df["IRB_ma"] = df["IRB_ma"].round(3)
    df["Is_ma"] = df["Is_ma"].round(3)

# concatenar
df_total = pd.concat([df_antigo, df_novo], ignore_index=True)

# remover duplicatas (mantém o primeiro encontrado)
df_total = df_total.drop_duplicates(subset=["IRB_ma", "Av", "Is_ma"])

# ordenar
df_total = df_total.sort_values(by=["IRB_ma", "Av", "Is_ma"])

# salvar resultado
df_total.to_csv(csv_saida, index=False)

print("Arquivo final criado:", csv_saida)
print("Total de pontos:", len(df_total))