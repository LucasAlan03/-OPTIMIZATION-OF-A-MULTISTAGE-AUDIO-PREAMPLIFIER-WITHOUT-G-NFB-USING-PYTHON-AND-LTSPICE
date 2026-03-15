from PyLTSpice import SimRunner, SpiceEditor, RawRead,LTSpiceLogReader
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import pandas as pd
import os
import time
from sympy import symbols, Eq,solve



N_CPU = max(1, os.cpu_count() - 2)  # deixa 2 livres para o sistema
print("Usando", N_CPU, "núcleos")

#_____________Função Para Cálculo Slew Rate__________________#
def Encontrar_V_max_Vmin(vout_slew_rate,tempo): #Função Inicial sem interpolação 
    
    #Indice = max(1,int(len(vout_slew_rate)*0.80)) # Índice para pegar os últimos XX% da simulação (PEGAR UM PERÍODO SÓ)
    cut_index = int(len(tempo) * 0.92)
    t_final = tempo[cut_index:]
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


    delta_t = tempo[cut_index + indice_max] - tempo[cut_index + indice_min]
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

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"



netlist_path_slew  = "2E_JFET_SLEW.asc"

resultados_csv = []
RIN = 47E3
df_bias = pd.read_csv("RESULTADOS_FINAIS_2E.csv")

df_bias["Is_mA"] = df_bias["Is_mA"].round(4)
df_bias["IRB_mA"] = df_bias["IRB_mA"].round(4)
df_bias["Ic_2E_mA"] = df_bias["Ic_2E_mA"].round(4)



pares_escolhidos = [(6,1.0,2.0), (8,1.0,2.0), (10,0.5,1.0), (12,0.5,1.0)]


#ic_menor = [0.1e-3,0.25e-3]
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3)*1e3
ic = ic_maior




def rodar_simulacao(args):

    i, ganho, is_, irb = args

    ic_ma = round(i,3)

    filtro = (
        (df_bias["Av1"] == ganho) &
        np.isclose(df_bias["Is_mA"], is_) &
        np.isclose(df_bias["IRB_mA"], irb) &
        np.isclose(df_bias["Ic_2E_mA"], ic_ma)
    )

    df_filtrado = df_bias.loc[filtro]

    if df_filtrado.empty:
        print(f"Ponto não encontrado: Av1={ganho} Is={is_} IRB={irb} Ic={ic_ma}")
        return None

    linha = df_filtrado.iloc[0]

    RE = linha["RE_1E"]
    RC = linha["RC_1E"]
    RB = linha["RBuffer"]
    rvbe_buffer = linha["RVBE_BUFFER"]
    RE_2E = linha["RE_2E"]
    RC_2E = linha["RC_2E"]

    runner = SimRunner(output_folder=f'./SLEW_RATE_2E_{int(i*1000)}_{ganho}', simulator=ltspice_exe_path)

    net_slew = SpiceEditor(netlist_path_slew)

    net_slew.set_component_value("I1", f"{is_}m")
    net_slew.add_instruction(".option noopiter")

    net_slew.set_component_value("R1", str(RC))
    net_slew.set_component_value("R2", str(RC))

    net_slew.set_component_value("R3", str(RE))
    net_slew.set_component_value("R4", str(RE))

    net_slew.set_component_value("R5", str(RIN))
    net_slew.set_component_value("R6", str(RIN))

    net_slew.set_component_value("R7", str(RB))
    net_slew.set_component_value("R8", str(RB))
    net_slew.set_component_value("R9", str(RB))
    net_slew.set_component_value("R10", str(RB))

    net_slew.set_component_value("RVBE_BUFFER_1", str(rvbe_buffer))
    net_slew.set_component_value("RVBE_BUFFER_2", str(rvbe_buffer))

    net_slew.set_component_value("RE_2E_1", str(RE_2E))
    net_slew.set_component_value("RE_2E_2", str(RE_2E))

    net_slew.set_component_value("RC_2E_1", str(RC_2E))
    net_slew.set_component_value("RC_2E_2", str(RC_2E))

    net_slew.set_element_model("V3","PULSE( -0.0282 0.0282 0 1n 1n 50u 100u)")

    net_slew.add_instruction(".tran 0 1m 0 0.1n")
    net_slew.add_instruction(".save V(vout) time")

    raw_slew, log_slew = runner.run_now(net_slew,timeout=1800)

    if raw_slew is None:
        return None

    slew_rate_raw = RawRead(raw_slew)

    vout = slew_rate_raw.get_trace("V(vout)").get_wave(0)
    tempo = slew_rate_raw.get_axis()

    vout_avg_slew = np.mean(vout)
    vout_slew_rate = vout - vout_avg_slew

    vout_max1, vout_min1, slew_rate1 = Encontrar_V_max_Vmin(vout_slew_rate,tempo)

    if slew_rate1 is None:
        return None

    av2 = round(100/ganho,2)

    return {
        'Slew_rate(V/us)':slew_rate1,
        'IRB_mA': irb,
        'Av2' : av2,
        'Av': ganho,
        'Is_mA':is_,
        'IC_2E_mA':ic_ma
    }

simulacoes = []

for i in ic:
    for ganho, is_, irb in pares_escolhidos:
        simulacoes.append((i, ganho, is_, irb))


from multiprocessing import Pool

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    with Pool(N_CPU) as p:
        resultados = p.map(rodar_simulacao, simulacoes)

    resultados = [r for r in resultados if r is not None]

    df = pd.DataFrame(resultados)
    df.to_csv("Slew_Rate_VS_IC_2E.csv", index=False)