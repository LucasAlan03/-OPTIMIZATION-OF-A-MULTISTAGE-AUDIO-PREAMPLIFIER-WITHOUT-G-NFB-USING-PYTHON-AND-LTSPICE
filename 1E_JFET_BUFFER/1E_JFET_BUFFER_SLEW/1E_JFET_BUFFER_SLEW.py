from PyLTSpice import SimRunner, SpiceEditor, RawRead,LTSpiceLogReader
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import pandas as pd
import os
import time
from sympy import symbols, Eq,solve

# ensure script runs from its own directory so relative paths resolve correctly
_script_dir = Path(__file__).parent.resolve()
os.chdir(_script_dir)



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


# -------- Leitura do CSV do slew rate para plotagem do gráfico----------------
'''
csv_slew = "SLEW_RATE.csv"
if os.path.exists(csv_slew):
    df_slew_existente = pd.read_csv(csv_slew)
    pares_existentes = set(zip(df_slew_existente["Av"], df_slew_existente["Is_ma"]))
else:
    df_slew_existente = pd.DataFrame()
    pares_existentes = set()
'''

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

runner = SimRunner(output_folder='./SLEW_RATE_', simulator=ltspice_exe_path)
runner.cleanup_files()   


# Banco de dados da polarização
df_bias = pd.read_csv("Banco_de_Dados_J201.csv")
df_bias["Is"] = df_bias["Is"].round(8)


netlist_path_slew  = "1E_JFET_BUFFER_SLEW.asc"

dados_resultados = []


resultados_csv = []    # Caso a simulação já tenha sido feita uma vez e apenas algumas curvas tenham que ser adicionadas

resultados_slew = []
pares_escolhidos = [(6,0.5E-3),   (8, 0.5e-3), (10,0.5E-3), (12,0.5E-3)]                       #ESCOLHER AQUI OS PARES DESEJADOS PARA SIMULAR O SLEW RATE



#---------------- Resistor de base
RIN= 47E3
#-------------------------------

resultados_slew = []


# Selecionando o ponto de operação para os valores escolhidos
for ganho, is_ in pares_escolhidos:

    filtro = (
        (df_bias["Av_target"] == ganho) &
        (df_bias["Is"] == round(is_, 4))
    )

    df_filtrado = df_bias.loc[filtro]

    # CASO 1: ponto existe no banco
    if not df_filtrado.empty:
        for _, linha in df_filtrado.iterrows():
            RE = linha["RE"]
            RC = linha["RC"]
            AV_REAL = linha["Av_Real"]

            resultados_slew.append((ganho, is_, RE, RC, AV_REAL))

    # CASO 2: ponto não existe → calcular
    else:
        print(f"Ponto ({ganho}, {is_}) não encontrado no banco → calculando")


        id = is_/2
        RC = 15/id

        beta = 1.07e-3   # do modelo SPICE
        gm = 2*np.sqrt(beta*id)

        RE_guess_symbol = symbols('RE_guess', positive=True, real=True)

        equation = Eq(RC/(2*((1/gm)+RE_guess_symbol)), ganho)

        solutions = solve(equation, RE_guess_symbol)

        if solutions:
            RE = float(solutions[0])
            AV_REAL = ganho  # aproximação

            resultados_slew.append((ganho, is_, RE, RC, AV_REAL))

        else:
            print(f"Sem solução para ({ganho}, {is_})")
#---------------------------------- Final da Seleção------------------------------------------------#

#---------------------Print inicial de verificação.

for ganho, is_, RE, RC, AV_REAL in resultados_slew:
    print(f"Simulando para Ganho: {ganho}, Is: {is_}, RE: {RE}, RC: {RC}, Av_real: {AV_REAL}")

#-------------- TRECHO DO CÓDIGO PARA ESCOLHER AS CORRENTES DO SEGUNDO ESTÁGIO.

ic_menor = [0.1e-3,0.25e-3]     #Correntes menores para simulação
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3) #CORRENTES MAIORES PARA SIMULAÇÃO
ic = np.concatenate((ic_menor, ic_maior))
#ic = ic_maior


#---------------------------------------VER SE O PONTO JA TEM NO CSV SALVO ABAIXO , SE SIM, PULAR.
csv_file = "SLEW_RATE.csv"

# conjunto com pontos já calculados
pontos_calculados = set()

if os.path.exists(csv_file):
    df_existente = pd.read_csv(csv_file)

    for _, row in df_existente.iterrows():
        chave = (row["IRB_ma"], row["Av"], row["Is_ma"])
        pontos_calculados.add(chave)










if __name__ == "__main__":
    print ("-----------Codigo Atualizado começou------------")
    for i in ic:
            for ganho, is_, RE, RC, Av_real in resultados_slew:  
              


                chave = (i*1e3, ganho, is_*1e3)
                if chave in pontos_calculados:
                    print("ponto já calculado, pulando:", chave)
                    continue

                ir1 = is_/2      #corrente de coletor primeiro estágio
               
                net_slew = SpiceEditor(netlist_path_slew)
                net_slew.set_component_value("I1",f"{is_}")
                net_slew.set_component_value("R1", str(RC))
                net_slew.set_component_value("R2", str(RC))
                net_slew.set_component_value("R3",str(RE))
                net_slew.set_component_value("R4", str(RE))
                net_slew.set_component_value("R5", str(RIN))
                net_slew.set_component_value("R6", str(RIN))

                #Calculo dos resisotores do buffer
                RB = (ir1*RC - 0.530)/i
                net_slew.set_component_value("R7", str(RB))
                net_slew.set_component_value("R8", str(RB))
                net_slew.set_component_value("R9", str(RB))
                net_slew.set_component_value("R10", str(RB))

                net_slew.set_element_model("V3","PULSE( -0.0282 0.0282 0 1n 1n 50u 100u)")

                net_slew.add_instruction(".tran 0 1m 0 0.1n")   
                net_slew.add_instruction(".save V(vout) time")                 
                raw_slew, log_slew = runner.run_now(net_slew,timeout=1200)

                time.sleep(2) # Pausa para evitar sobrecarga do LTspice e garantir que os arquivos sejam escritos corretamente

                if raw_slew is None:
                    print(f"Pulei o ponto Is={i*1e3:.1f}mA pois a simulação demorou mais de 20 min ou falhou.")
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
                    print(f'nao foi possível determinar o slew rate pra corrente de {i*1e3:.1f} mA')
                    continue
                else:
                    print (f'--------Resultado para Av: {ganho} | IS: {is_*1e3:.2f}mA-----------')
                    print(f'--------- Irb: {i*1e3:.1f} mA ---------')
                    print(f'Slew rate={slew_rate1}\n')
                    pontos_calculados.add(chave)

                    dados = {
                        "IRB_ma": i*1e3,
                        "Av": ganho,
                        "Is_ma": is_*1e3,
                        "Slew_Rate_Metodo1_V_per_us": slew_rate1
                    }
                    
                    resultados_csv.append(dados)

                    arquivo = "SLEW_RATE_is_0.csv"

                    dados_df = pd.DataFrame([dados])

                    dados_df.to_csv(
                        arquivo,
                        mode="a",
                        header=not os.path.exists(arquivo),
                        index=False
                    )

                if os.path.exists(raw_slew):
                    
                    os.remove(raw_slew)

