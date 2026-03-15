from PyLTSpice import SimRunner, SpiceEditor, RawRead,LTSpiceLogReader
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import pandas as pd
import os


# ensure script runs from its own directory so relative paths resolve correctly
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)

#_____________Função Para Cálculo Slew Rate__________________#
def Encontrar_V_max_Vmin(vout_slew_rate,time,Is,Av_target): #Função Inicial sem interpolação 
    
    Indice = max(1,int(len(vout_slew_rate)*0.92)) # Índice para pegar os últimos 8% da simulação
    cut_index = int(len(time) * 0.92)
    t_final = time[cut_index:]
    v_final = vout_slew_rate[cut_index:]

    # 2. Histograma no último ciclo para achar níveis reais de regime
    hist, bin_edges = np.histogram(v_final, bins=300)
    centros = (bin_edges[:-1] + bin_edges[1:]) / 2
    indices_picos = np.argsort(hist)[-2:]
    niveis = sorted([centros[i] for i in indices_picos])
    vout_min1, vout_max1 = niveis[0], niveis[1]

    #### Excursão para encontrar os pontos de 10% e 90% do regime para o cálculo do slew rate
    vtotal = vout_max1 - vout_min1
    v_slew_min = 0.1*vtotal + vout_min1
    v_slew_max = 0.9*vtotal + vout_min1


    indice_max = np.argmin(np.abs(v_final -v_slew_max))
    indice_min = np.argmin(np.abs(v_final - v_slew_min))


    vmax = v_final[indice_max]
    vmin = v_final[indice_min]


    delta_t = time[cut_index + indice_max] - time[cut_index + indice_min]
    if abs(delta_t) > 0 :
        slew_rate1 = abs((vmax - vmin) / delta_t) * 1e-6
    else:
        slew_rate1 = None
    
    '''
    print(f'-----------------------Av={Av_target} | Is={Is*1e3:.1f}mA-----------------------')
    print(f"Níveis encontrados: Vmin = {vout_min1:.2f} V, Vmax = {vout_max1:.2f} V")
    print(f'10% do regime: {vmin:.4f} V | 90% do regime: {vmax:.4f} V')
    print(f' tempo = t_final[indice_max]{t_final[indice_max]*1e6:.4f}us - t_final[indice_min]{t_final[indice_min]*1e6:.4f}us = {delta_t*1e6:.2f} us | Slew Rate Método 1: {slew_rate1:.2f} V/us\n')
    
    
    plt.plot(t_final, v_final, label="Sinal de saída")
    plt.axhline(y=vout_max1, color='r', linestyle='--', label="Topo")
    plt.axhline(y=vout_min1, color='b', linestyle='--', label="Base")
    plt.scatter(t_final[indice_max],vmax,color = 'green', label="Valor para cálculo do slew rate (90% do máximo)")
    plt.scatter(t_final[indice_min],vmin,color = 'orange', label="Valor para cálculo do slew rate (10% do mínimo)")
    plt.legend(loc="best", fontsize = 7)
    plt.show()
    '''

    return vout_max1, vout_min1, slew_rate1


csv_slew = "SLEW_RATE.csv"

if os.path.exists(csv_slew):
    df_slew_existente = pd.read_csv(csv_slew)
    pares_existentes = set(zip(df_slew_existente["Av"], df_slew_existente["Is_ma"]))
else:
    df_slew_existente = pd.DataFrame()
    pares_existentes = set()

resultados=[]
resultados_csv = []






#  Configurações iniciais para a simulação
ltspice_exe = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
runner_2 = SimRunner(output_folder='./SLEW_RATE_J201',simulator=ltspice_exe)
net_slew_2= "1E_J201_SLEW.asc"

# Dados com a polarização  DC do circuito
df_bias = pd.read_csv("Banco_de_Dados_J201.csv")
df_bias["Is"] = df_bias["Is"].round(8)

RIN = 47E3
name_vout = 'Vout'

gain_target = [2,6,10]
# Duas opções: Simular para todos os pontos, ou usar somente pontos desejados.

df_gain_filtrado = df_bias[df_bias["Av_target"].isin(gain_target)]





if __name__ == "__main__":
    print ("-----------Codigo começou------------")

  
    # Opção 1: Simular Para todos os pontos
    for _, linha in df_bias.iterrows():
    

    # Opcão 2: Simular somente para os pontos filtrados
    #for _,linha in df_gain_filtrado.iterrows():

        Av_target = linha["Av_target"]
        Is = linha["Is"]
        R_calc = linha["RC"]
        RE_calc = linha["RE"]
        Av_Real = linha["Av_Real"]
        
        #if (Av_target, Is*1e3) in pares_existentes:     # 3° ---------- Pular dados já existentes no CSV
            #print(f"Pulei o ponto Av={Av_target} e Is={Is*1e3}mA pois já existe no CSV.")
        #   continue
        #_____________SLEW RATE________________#
        net_slew_rate = SpiceEditor(net_slew_2)
        net_slew_rate.set_component_value("I1",f"{Is}")
        net_slew_rate.set_component_value("R1", str(R_calc))
        net_slew_rate.set_component_value("R2", str(R_calc))
        net_slew_rate.set_component_value("R3",str(RE_calc))
        net_slew_rate.set_component_value("R4", str(RE_calc))
        net_slew_rate.set_component_value("R5", str(RIN))
        net_slew_rate.set_component_value("R6", str(RIN))
        net_slew_rate.set_element_model("V3",f"PULSE( -0.0282 0.0282 0 1n 1n 50u 100u)")

        net_slew_rate.add_instruction(".save V(Vout)")

        net_slew_rate.add_instruction(".tran 0 1m 0 0.1n")               
        raw_slew, log_slew = runner_2.run_now(net_slew_rate,timeout=1200)

        if raw_slew is None:
            print(f"Pulei o ponto Is={Is} | av= { Av_target} pois a simulação demorou mais de 20 min ou falhou.")
            continue
        
        log_slew_rate = LTSpiceLogReader(log_slew)
        slew_rate_raw = RawRead(raw_slew)

        vout = slew_rate_raw.get_trace(f"V({name_vout})").get_wave(0)
        #vin = slew_rate_raw.get_trace("V(vin)").get_wave(0)
                    #__________ Pegar as curvas para plot______________#
        vout_avg_slew = np.mean(vout)
        #vout_rms_slew = log_slew_rate.get_measure_value(meas_rms)
        time = slew_rate_raw.get_axis()
            #_____________ Tirando "offset" da saída________#
        vout_slew_rate = vout - vout_avg_slew

        vout_max1, vout_min1, slew_rate1 = Encontrar_V_max_Vmin(vout_slew_rate,time,Is,Av_target)


        if slew_rate1 is None:
            print(f"Não foi possível determinar o slew rate para Av={Av_target} e Is={Is*1e3}mA")
            continue
        resultados.append((Is*1e3, Av_target, slew_rate1))
        resultados_csv.append({
            "Is_ma": Is*1e3,
            "Av": Av_target,
            "Slew_Rate ": slew_rate1
        })
        dados_df = pd.DataFrame(resultados_csv)
        dados_df.to_csv("SLEW_RATE.csv", index=False)
        if os.path.exists(raw_slew):
            os.remove(raw_slew)


# Concatenando o CSV antigo com o novo -------------------------------#
if resultados_csv:
    df_novo = pd.DataFrame(resultados_csv)
    df_final = pd.concat([df_slew_existente, df_novo], ignore_index=True)
else:
    df_final = df_slew_existente

df_final.to_csv(csv_slew, index=False)

# ----------- Plotagem do gráfico Slew Rate x Is para os ganhos selecionados -------------------------------#


plt.figure(figsize=(8, 5))
ax = plt.gca()

cores = {
    4.0: "green",
    6.0: "black",
    8.0: "red",
    10.0: "purple",
    12.0: "brown",
    14.0:  "blue",
    16.0:  "orange"
}



df_plot = pd.read_csv(csv_slew)

curvas_plt = {}

for _, linha in df_plot.iterrows():
    av = linha["Av"]
    Is_ma = linha["Is_ma"]
    slew = linha["Slew_Rate"]

    curvas_plt.setdefault(av, {"Is_ma":[], "slew_rate":[]})
    curvas_plt[av]["Is_ma"].append(Is_ma)
    curvas_plt[av]["slew_rate"].append(slew)

for av in curvas_plt:
    plt.plot(curvas_plt[av]["Is_ma"],
             curvas_plt[av]["slew_rate"],
             linewidth=2,
             color =cores.get(av,'cyan'),
             label=f"Av={av}")


plt.xlabel("Corrente Is (mA)")
plt.ylabel("Slew Rate (V/us)")




plt.axhline(1.41, linestyle='--', color = 'green',linewidth=1,label ='Slew Rate ponto ótimo')  

ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(MultipleLocator(0.25))

ax.yaxis.set_major_locator(AutoMinorLocator(0.2))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))


ax.grid(True, which='major', linestyle='-', linewidth=0.7, alpha=0.6)
ax.grid(True, which='minor', linestyle='--', linewidth=0.4, alpha=0.5)

plt.axhline(0.35, linestyle='--', linewidth=0.8, color='black', label="Slew Rate mínimo recomendado (0.35 V/μs)") 
plt.xlim(0.1,2)

plt.legend(loc="best", fontsize=8)

plt.tight_layout()

plt.savefig("SlewRateVsCorrente.png", dpi=600, bbox_inches="tight")

plt.close()
