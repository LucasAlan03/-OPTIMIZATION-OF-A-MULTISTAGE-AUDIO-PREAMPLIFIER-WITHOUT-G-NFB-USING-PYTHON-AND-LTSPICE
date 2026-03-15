from PyLTSpice import SimRunner, SpiceEditor, RawRead
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator,  MultipleLocator
import matplotlib.patches as patches
import pandas as pd
import os
from pathlib import Path
from matplotlib.ticker import FuncFormatter

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

# =======================================================
# Função para encontrar a frequência de corte (-3dB)
# =======================================================
def encontrar_freq_corte(raw_ac,name_vout):
    raw = RawRead(raw_ac)

    v = raw.get_trace(f"V({name_vout})").data
    freq = raw.get_trace("frequency").data

    # magnitude em dB
    vout = 20 * np.log10(np.abs(v))

    # ganho máximo (ignorando DC)
    indice_vmax = np.argmax(vout[1:]) + 1
    max_gain_db = vout[indice_vmax]

    # nível de corte
    vcorte = max_gain_db - 3

    # busca somente na região após o máximo
    indices_corte = np.where(vout[indice_vmax:] < vcorte)[0]
    if len(indices_corte) == 0:
        raise ValueError("Frequência de corte não encontrada. Aumente o sweep.")

    indice_corte = indices_corte[0] + indice_vmax
    f_corte = freq[indice_corte]

    return f_corte, max_gain_db


#  Configurações iniciais para a simulação

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
runner = SimRunner(output_folder='./THD', simulator=ltspice_exe_path)
netlist_path_freq = "1E_J201_FREQ.asc"
RIN = 47E3

# Banco de dados da polarização
df_bias = pd.read_csv("Banco_de_Dados_J201.csv")
df_bias["Is"] = df_bias["Is"].round(8)

resultados = []
resultados_csv = []    # Caso a simulação já tenha sido feita uma vez e apenas algumas curvas tenham que ser adicionadas
name_vout = 'Vout'
if __name__ == "__main__":
    print ("-----------Codigo começou------------")

    # 1. Simular Para todos os pontos
    for _, linha in df_bias.iterrows():

    #2. Simular somente para os pontos filtrados
    #for _,linha in df_filtrado.iterrows():

        Av_target = linha["Av_target"]
        Is = linha["Is"]
        R_calc = linha["RC"]
        RE_calc = linha["RE"]

        net = SpiceEditor(netlist_path_freq)
        net.set_component_value("I1", f"{Is}")
        net.set_component_value("R1", str(R_calc))
        net.set_component_value("R2", str(R_calc))
        net.set_component_value("R3", str(RE_calc))
        net.set_component_value("R4", str(RE_calc))
        net.set_component_value("R5", str(RIN))
        net.set_component_value("R6", str(RIN))
        net.set_component_value("V3", "AC 1")

        net.add_instruction(".ac dec 800 10 10Meg")

        raw_ac, log_ac = runner.run_now(net)

        f_corte, max_gain = encontrar_freq_corte(raw_ac,name_vout)

        resultados.append((Is * 1e3, f_corte / 1e3, Av_target))
        resultados_csv.append({
            "Is_ma":Is*1e3,
            "Freq_corte (Khz)":f_corte / 1e3,
            "Ganho": Av_target
        })
        dados_df = pd.DataFrame(resultados_csv)
        dados_df.to_csv("FREQ_VS_IS.csv", index=False)

        if os.path.exists(raw_ac):
            os.remove(raw_ac)
        '''
        print(
            f"Av={Av_target} | Is={Is*1e3:.2f}mA | "
            f"RC={R_calc:.1f}Ω | RE={RE_calc:.1f}Ω -> "
            f"Fh={f_corte/1e3:.2f}kHz | Gain={max_gain:.2f}dB"
        )
        '''
# =======================================================
# Plotagem
# =======================================================
plt.figure(figsize=(8, 5))
cores = {
    4.0: "green",
    6.0: "black",
    8.0: "red",
    10.0: "purple",
    12.0: "brown",
    14.0:  "blue",
    16.0:  "orange"
}

curvas = {}
for Is_mA, freq_kHz, Av in resultados:
    curvas.setdefault(Av, {"Is": [], "freq": []})
    curvas[Av]["Is"].append(Is_mA)
    curvas[Av]["freq"].append(freq_kHz)

for Av in curvas:
    plt.plot(curvas[Av]["Is"],
             curvas[Av]["freq"],
             linewidth=2,
             color=cores.get(Av, "cyan"),  # preto se não estiver mapeado
             label=f"Av={Av}")



plt.xlabel("Is (mA)")
plt.xlim (0.1,2)
plt.ylabel("Frequência de Corte superior (kHz)")
plt.ylim(80,2000)
#subdivsões
ax = plt.gca()

ax.xaxis.set_major_locator(MultipleLocator(0.5))   # números grandes eixo x
ax.xaxis.set_minor_locator(MultipleLocator(0.025))   # tracinhos pequenos  eixo x

ax.yaxis.set_major_locator(MultipleLocator(100))   # números grandes eixo y
ax.yaxis.set_minor_locator(MultipleLocator(20))    # tracinhos pequenos

#---------------Grades centrais e secundárias----------------#
ax.grid(True, which='major', linestyle='-', linewidth=1.0, alpha=1)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)


plt.legend(loc = 'best', fontsize=8)
plt.tight_layout()
plt.savefig(f"FREQUENCIA_CORTE_VS_IS.png", dpi=600, bbox_inches="tight")

plt.close()

print('-----------Código terminou------------')
