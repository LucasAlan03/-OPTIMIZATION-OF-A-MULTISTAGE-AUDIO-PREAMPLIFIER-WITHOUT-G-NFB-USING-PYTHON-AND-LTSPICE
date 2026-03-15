from PyLTSpice import SimRunner, SpiceEditor, RawRead,LTSpiceLogReader
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import pandas as pd
import os
import time
from sympy import symbols, Eq,solve

_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)


#---------------------- AJUSTE PARA CORRENTE DE 2mA ------------------------------#



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
resultados_csv = []

runner = SimRunner(output_folder='./SLEW_RATE_3E', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_slew  = "3E_SLEW_OFFSET_CORRENTE_20mA.asc"




# ----------- Variação do Resistor do Resistor R1 do multiplicador de VBE
# -- R1 = 1.5K I = 2.05mA  ; R1 = 7.5K I= 20.5mA ; R1 = 14K I = 40.8mA

r1vbe = np.arange(1.5E3,14E3+200,500)

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for r in r1vbe:
        
        net_slew = SpiceEditor(netlist_slew)
        net_slew.set_component_value('R1_VBE',str(r))
        net_slew.add_instruction(".option noopiter")
        net_slew.set_element_model("V3","PULSE( -0.0282 0.0282 0 1n 1n 50u 100u)")


        net_slew.add_instruction(".tran 0 1m 0 0.1n")   
        net_slew.add_instruction(".save V(vout) time")                 
        raw_slew, log_slew = runner.run_now(net_slew,timeout=600)

        time.sleep(2) # Pausa para evitar sobrecarga do LTspice e garantir que os arquivos sejam escritos corretamente
        print('Raw carregado\n')

        if raw_slew is None:
            print(f"Pulei o ponto Is={r} pois a simulação demorou mais de 20 min ou falhou.")
            continue


        log_slew_rate = LTSpiceLogReader(log_slew)
        slew_rate_raw = RawRead(raw_slew)

        vout = slew_rate_raw.get_trace("V(vout)").get_wave(0)
        #vin = slew_rate_raw.get_trace("V(vin)").get_wave(0)

        #__________ Pegar as curvas para plot______________#
        vout_avg_slew = np.mean(vout)
        #vout_rms_slew = log_slew_rate.get_measure_value(meas_rms)
        tempo = slew_rate_raw.get_axis()
            #_____________ Tirando "offset" da saída________#
        vout_slew_rate = vout - vout_avg_slew

        vout_max1, vout_min1, slew_rate1 = Encontrar_V_max_Vmin(vout_slew_rate,tempo)

        if slew_rate1 is None:
            print(f'nao foi possível determinar o slew rate pra corrente de {r} ohms')
            continue

        else :
            print(f' {r},  Slew Rate{slew_rate1}(V/us)')
            resultados_csv.append({
                'Slew Rate (V/us)': slew_rate1,
                'R1_VBE':r
            })
            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv('3E_SLEW_RATE.csv',index = False)

print('------------------ Final do código-------------------')

