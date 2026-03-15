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


#  Configurações iniciais para a simulação

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
runner = SimRunner(output_folder='./THD', simulator=ltspice_exe_path)
netlist_path_thd = "1E_J201_THD.asc"

# Banco de dados da polarização
df_bias = pd.read_csv("Banco_de_Dados_J201.csv")
df_bias["Is"] = df_bias["Is"].round(8)


resultados_csv = []    # Caso a simulação já tenha sido feita uma vez e apenas algumas curvas tenham que ser adicionadas


#  Parâmetros para simulação de THD.
Freq = 1e3
numcyc= 250
FFT= 655360*2
dlycyc = 50
simtime = (dlycyc+numcyc)/Freq
dlytime = dlycyc/Freq
numsampl = simtime / Freq / ((simtime / numcyc) * FFT)

# Simulação AC
resultados_THD = []

gain_target = [3,6,8,10,12,14,20,25]

# Duas opções: Simular para todos os pontos, ou usar somente pontos desejados.

df_filtrado = df_bias[df_bias["Av_target"].isin(gain_target)]

# Opção 1: Simular somente para os pontos filtrados
#for _, linha in df_bias.iterrows():

RIN = 47E3
name_vout = 'Vout'
# Opcão 2: Simular somente para os pontos filtrados
if __name__ == "__main__":
    print ("-----------Codigo começou------------")
    #for _,linha in df_filtrado.iterrows():
        
    for _, linha in df_bias.iterrows():
        #if linha["Is"] not in current_target:
            #continue
        Av_target = linha["Av_target"]
        Is = linha["Is"]
        R_calc = linha["RC"]
        RE_calc = linha["RE"]
        net_thd = SpiceEditor(netlist_path_thd)
        net_thd.set_component_value("I1",f"{Is}")
        net_thd.set_component_value("R1", str(R_calc))
        net_thd.set_component_value("R2", str(R_calc))
        net_thd.set_component_value("R3",str(RE_calc))
        net_thd.set_component_value("R4", str(RE_calc))
        net_thd.set_component_value("R5", str(RIN))
        net_thd.set_component_value("R6", str(RIN))
        net_thd.set_element_model("V3",f"SINE(0 28.2m {Freq})")
        net_thd.add_instruction(".options plotwinsize=0")   
        net_thd.add_instruction(".options numdgt=99")
        net_thd.add_instruction(f".four {Freq} V({name_vout})")
        net_thd.add_instruction(f".tran 0 {simtime} {dlytime} {numsampl}")
        raw_ac, log_ac = runner.run_now(net_thd)       

        with open(log_ac, "r", encoding="utf-8", errors="ignore") as f:     #Leitura do THD NO ARQUIVO LOG
                log = f.read()
                for linha in log.splitlines():
                    if "Total Harmonic Distortion" in linha:
                        thd_string = linha.split(":")[1].strip()
                        thd = float(thd_string.split("%")[0]) 

        resultados_THD.append((Av_target,Is*1e3,thd))  

        resultados_csv.append({
            'Ganho': Av_target,
            'Is_mA': Is*1e3,
            'THD': thd

        })
        dados_df = pd.DataFrame(resultados_csv)
        dados_df.to_csv("THD_VS_AV.csv", index=False)

        if os.path.exists(raw_ac):
            print(f'APAGANDO O RAW PARA : {Av_target} | {Is*1e3:.1f}mA')
            os.remove(raw_ac)
        if os.path.exists(net_thd.netlist_file):
            os.remove(net_thd.netlist_file)


# Plotagem DEIXAR PARA O CSV
'''
plt.figure(figsize=(8, 5))

ax = plt.gca()


curvas = {}

current_target = [0.1, 0.2 ,0.3, 0.5,1.0,2.0]
cores = {
    0.1: "green",
    0.2: "black",
    0.3: "red",
    0.5: "purple",
    1.0: "brown"
    
}


for Av, Is_ma, thd in resultados_THD:
    if Is_ma not in current_target:
        continue
    curvas.setdefault(Is_ma,{"Av":[], "thd":[]})
    curvas[Is_ma]["Av"].append(Av)
    curvas[Is_ma]["thd"].append(thd)

def virgula(x, pos):
    return f"{x:.2f}".replace('.', ',')

ax.xaxis.set_major_formatter(FuncFormatter(virgula))
ax.yaxis.set_major_formatter(FuncFormatter(virgula))



for Is_ma in curvas:
    plt.plot(curvas[Is_ma]["Av"], curvas[Is_ma]["thd"],
             linewidth= 1.5,
             color = cores.get(Is_ma, "blue")
             ,label=f"Is={Is_ma:.1f}")



plt.xlabel("AV (Ganho)")
plt.ylabel("THD (%)")

# subdivsões
ax.xaxis.set_major_locator(MultipleLocator(2))   # números grandes eixo x
ax.xaxis.set_minor_locator(MultipleLocator(1))   # tracinhos pequenos  eixo x


#---------------Grades centrais e secundárias----------------#
ax.grid(True, which='major', linestyle='-', linewidth=0.5, alpha=0.5)
ax.grid(True, which='minor', linestyle='--', linewidth=0.5, alpha=0.5)
# 🔹 Escala fácil para conta

ax.yaxis.set_major_locator(MultipleLocator(0.001)) # números grandes eixo y
ax.yaxis.set_minor_locator(MultipleLocator(0.0005)) # tracinhos pequenos  eixo y


plt.xlim(2,16)
plt.ylim(0,0.008)


plt.legend(loc='best', fontsize=8)
plt.tight_layout()
plt.savefig(f"THD_VS_AV.png", dpi=600, bbox_inches="tight")
plt.close()
'''
print('---------FIM DO CÓDIGO---------')


