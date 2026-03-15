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



#  Configurações iniciais para a simulação

#-------------------------- COLOCAR O CAMINHO DO LTSPICE NO SEU PC AQUI --------------------------

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

#caminho nesse PC C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe

runner = SimRunner(output_folder='./THD', simulator=ltspice_exe_path)
runner.cleanup_files()                  #limpa arquivos antigos da pasta de resultados
netlist_path_thd = "1E_JFET_BUFFER_THD.asc"

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

# Simulação TRANSIENTE
resultados_THD = []
pares_escolhidos = [(6,0.5E-3),   (8, 0.5e-3), (10,0.5E-3), (12,0.5E-3)]   

#--------------------------RIN
RIN = 47E3

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

            resultados_THD.append((ganho, is_, RE, RC, AV_REAL))

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

            resultados_THD.append((ganho, is_, RE, RC, AV_REAL))

        else:
            print(f"Sem solução para ({ganho}, {is_})")
#---------------------------------- Final da Seleção------------------------------------------------#


ponto_bias = []
# Simulação de THD
ic_menor = [0.1e-3,0.25e-3]     #Correntes menores para simulação
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3) #CORRENTES MAIORES PARA SIMULAÇÃO
ic = np.concatenate((ic_menor, ic_maior))
# Correntes menores + 5mA
RG = 47000


# COLOCAR OUTROS VALORES DE I1, RC,RE PARA TESTE
# .param RC=10k RE=232 RG=47k   IS =1MA 
#resultados_THD = [(15, 1e-3, 232, 10000, 14)]  # Ganho, Is, RE, RC, Av_real
for ganho, is_, RE, RC, AV_REAL in resultados_THD:
    print(f"Simulando para Ganho: {ganho}, Is: {is_}, RE: {RE}, RC: {RC}, Av_real: {AV_REAL}")


if __name__ == "__main__":
    print ("-----------Codigo ATUALIZADO começou------------")
    for i in ic:
        for ganho, is_, RE, RC, Av_real in resultados_THD:
            thd = None
            
            
            # Definindo valores dos componentes para a simulação de THD
             
            ir1 = is_/2
            # PARAMETRO PARA SIMULAÇÃO DE THD, CORRENTE DE POLARIZAÇÃO DO BUFFER
            net_thd = SpiceEditor(netlist_path_thd)
            net_thd.add_instruction(".options plotwinsize=0")
            net_thd.add_instruction(".options numdgt=99")
            net_thd.add_instruction(f".four {Freq} V(vout)")
            net_thd.add_instruction(".option noopiter")
            net_thd.add_instruction(f".tran 0 {simtime} {dlytime} {numsampl}")
            # SETANDO VALORES DOS COMPONENTES PARA SIMULAÇÃO DE THD

            net_thd.set_component_value("I1",f"{is_}")
            net_thd.set_component_value("R1", str(RC))
            net_thd.set_component_value("R2", str(RC))
            net_thd.set_component_value("R3",str(RE))
            net_thd.set_component_value("R4", str(RE))
            net_thd.set_component_value("R5", str(RG))
            net_thd.set_component_value("R6", str(RG))
            #Calculo dos resisotores do buffer
            RB = (ir1*RC - 0.530)/i
            net_thd.set_component_value("R7", str(RB))
            net_thd.set_component_value("R8", str(RB))
            net_thd.set_component_value("R9", str(RB))
            net_thd.set_component_value("R10", str(RB))

            #CONFIGURAÇÕES PARA SIMULAÇÃO DE THD
            net_thd.add_instruction(".save V(vout) time")   
            net_thd.set_element_model("V3",f"SINE(0 28.2m {Freq})")   #A AMPLITUDE DA FONTE PODE SER MUDADA AQUI
            #print("-------Passei por esssa parte--------------------")

            raw_ac, log_ac = runner.run_now(net_thd,timeout=300)   
            time.sleep(2)  # esperar 2 seg para garantir que os arquivos_foram_gerados

            if not os.path.exists(log_ac):
                print("Log não foi gerado")
                continue
            #print(log_ac) 

            #print('--------------------------começando ler o raw----------')
            #curvas = RawRead(raw_ac)
            #log = LTSpiceLogReader(log_ac)
            #print('------------lendo raw--------------')
            #vout = curvas.get_trace('V(vout)').get_wave(0)
            #print('-----------peguei a curva-------------')

            #ic_real = vout / RB
            
            # Lendo os resultados da simulação
            #print('---------------procurando thd------------------')
            with open(log_ac, "r", encoding="utf-8", errors="ignore") as f:
                for linha in f:
                    if "Total Harmonic Distortion" in linha:
                        thd = float(linha.split(":")[1].split("%")[0])
                        break
            #print('-----------final da busca-----------------------')
            if thd is None:
                print("THD não encontrado no log")
                continue
            #print (f'thd : {thd} | corrente projetada : {i}  | RB : {RB}')
            ponto_bias.append((ganho, i, thd))   # Armazenando os resultados em um dicionário para posterior análise

            resultados_csv.append({
                'Ganho': ganho,
                'I_mA': i*1e3,
                'RE': RE,
                'RC': RC,
                'Av_real': Av_real,
                'RB': RB,
                'Is_mA': is_*1e3,
                'THD': thd})
            
            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv("THD_VS_AV_buffer_is_0_5_mA.csv", index=False)
            if os.path.exists(raw_ac):
                os.remove(raw_ac)


print('------------------------Fim do código-----------------------')