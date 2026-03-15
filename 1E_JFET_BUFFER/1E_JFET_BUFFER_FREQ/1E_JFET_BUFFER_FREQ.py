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



# =======================================================
# Função para encontrar a frequência de corte (-3dB)
# =======================================================
def encontrar_freq_corte(raw_ac):
    raw = RawRead(raw_ac)

    v = raw.get_trace("V(vout)").data
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


ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

runner = SimRunner(output_folder='./FREQ', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_path_freq  = "1E_JFET_BUFFER_FREQ.asc"

resultados_freq = []
RIN = 47E3

# Banco de dados da polarização
df_bias = pd.read_csv("Banco_de_Dados_J201.csv")
df_bias["Is"] = df_bias["Is"].round(4)

resultados_csv = []    # Caso a simulação já tenha sido feita uma vez e apenas algumas curvas tenham que ser adicionadas


pares_escolhidos = [(6,0.5E-3),   (8, 0.5e-3), (10,0.5E-3), (12,0.5E-3)]   

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

            resultados_freq.append((ganho, is_, RE, RC, AV_REAL))

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

            resultados_freq.append((ganho, is_, RE, RC, AV_REAL))

        else:
            print(f"Sem solução para ({ganho}, {is_})")
#---------------------------------- Final da Seleção------------------------------------------------#


#-------------- TRECHO DO CÓDIGO PARA ESCOLHER AS CORRENTES DO SEGUNDO ESTÁGIO.

ic_menor = [0.1e-3,0.25e-3]     #Correntes menores para simulação
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3) #CORRENTES MAIORES PARA SIMULAÇÃO
ic = np.concatenate((ic_menor, ic_maior))
#ic = ic_maior

#---------------------Print inicial de verificação.

for ganho, is_, RE, RC, AV_REAL in resultados_freq:
    print(f"Simulando para Ganho: {ganho}, Is: {is_}, RE: {RE}, RC: {RC}, Av_real: {AV_REAL}")

if __name__ == "__main__":
    print ("-----------Codigo começou------------")
    for i in ic:
        for ganho, is_, RE, RC, Av_real in resultados_freq:

            f_corte = None

            ir1 = is_/2      #corrente de coletor primeiro estágio

            net_freq = SpiceEditor(netlist_path_freq)
            net_freq.set_component_value("I1",f"{is_}")
            net_freq.set_component_value("R1", str(RC))
            net_freq.set_component_value("R2", str(RC))
            net_freq.set_component_value("R3",str(RE))
            net_freq.set_component_value("R4", str(RE))
            net_freq.set_component_value("R5", str(RIN))
            net_freq.set_component_value("R6", str(RIN))

            #Calculo dos resisotores do buffer
            RB = (ir1*RC - 0.530)/i
            net_freq.set_component_value("R7", str(RB))
            net_freq.set_component_value("R8", str(RB))
            net_freq.set_component_value("R9", str(RB))
            net_freq.set_component_value("R10", str(RB))

            #parametros para simulação de frequência
            net_freq.add_instruction(".save V(vout) time")    
            net_freq.set_component_value("V3", "AC 1")
            net_freq.add_instruction(".ac dec 800 10 10Meg")

            raw_ac, log_ac = runner.run_now(net_freq)
            time.sleep(2)  # esperar 2 seg para garantir que os arquivos_foram_gerados

            f_corte, max_gain = encontrar_freq_corte(raw_ac)

            if f_corte is  None:
                print(f"Frequência de corte não  encontrada para {i*1e3} mA")
                continue

            resultados_csv.append({
                'Freq_corte(Khz)':f_corte / 1e3,
                'IRB_mA': i*1e3,
                'Av': ganho,
                'Is_mA':is_*1e3
            }) 
            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv("FREQ_VS_IRB.csv", index=False)

            if os.path.exists(raw_ac):
                os.remove(raw_ac)


print('---------Fim do código---------------------')
