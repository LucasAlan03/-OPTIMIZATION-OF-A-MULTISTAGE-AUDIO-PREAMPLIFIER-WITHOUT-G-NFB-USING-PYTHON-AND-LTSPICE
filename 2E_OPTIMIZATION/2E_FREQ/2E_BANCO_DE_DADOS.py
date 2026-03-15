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







ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

runner = SimRunner(output_folder='./BANCO_DE_DADOS', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_path_freq  = "2E_JFET_FREQ.asc"

resultados_freq = []
RIN = 47E3


# Banco de dados da polarização
df_bias = pd.read_csv("THD_VS_AV_buffer_is_0_5_mA.csv")
df_bias["Is_mA"] = df_bias["Is_mA"].round(3)

resultados_csv = []    # Caso a simulação já tenha sido feita uma vez e apenas algumas curvas tenham que ser adicionadas


pares_escolhidos = [(6,0.5,1.0),   (8, 0.5,1.0), (10,0.5,1.0), (12,0.5,1.0)]  


for ganho, is_,irb in pares_escolhidos:

    filtro = (
        (df_bias["Ganho"] == ganho) &
        (df_bias["Is_mA"] == round(is_, 3)) &
        (df_bias["I_mA"] == irb)
    )

    df_filtrado = df_bias.loc[filtro]

    # CASO 1: ponto existe no banco
    if not df_filtrado.empty:
        for _, linha in df_filtrado.iterrows():
            RE = linha["RE"]
            RC = linha["RC"]
            RB = linha["RB"]
            

            resultados_freq.append((ganho, is_, RE, RC, RB,irb))

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
  
             # aproximação

            resultados_freq.append((ganho, is_, RE, RC, RB,irb))

        else:
            print(f"Sem solução para ({ganho}, {is_})")
#---------------------------------- Final da Seleção------------------------------------------------#

#-------------- TRECHO DO CÓDIGO PARA ESCOLHER AS CORRENTES DO SEGUNDO ESTÁGIO.

ic_menor = [0.1e-3,0.25e-3]     #Correntes menores para simulação
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3) #CORRENTES MAIORES PARA SIMULAÇÃO
ic = np.concatenate((ic_menor, ic_maior))
#ic = ic_maior
RIN = 47E3
#---------------------Print inicial de verificação.

for ganho, is_, RE, RC, RB, irb in resultados_freq:
    print(f"Simulando para Ganho: {ganho} | Is: {is_} | IRB: {irb} | RE: {RE} | RC: {RC} |RB :{RB}")



if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for i in ic:
        for ganho, is_, RE, RC, RB, irb in resultados_freq:

            # ---------- PARÂMETROS FIXOS DO CASO ----------
            rvbe_buffer = (4/irb)*1000

            RE_2E = (15 - 1.06)/i
            bre = 26e-3/i

            RC_GUESS_symbol = symbols('RC_guess', positive=True, real=True)

            gain_2 = 100.6/(ganho)

            av2 = Eq(RC_GUESS_symbol/(bre+RE_2E), gain_2)
            solutions = solve(av2, RC_GUESS_symbol)

            RC_teorico_2E = float(solutions[0])

            RC_ajuste = RC_teorico_2E

            # ---------- LOOP DE AJUSTE DO GANHO ----------
            melhor_erro = float("inf")
            melhor_RC = RC_ajuste
            melhor_ganho = None
            for tentativa in range(5):

                net_freq = SpiceEditor(netlist_path_freq)

                # ---------- ESTÁGIO 1 ----------
                net_freq.set_component_value("I1", f"{is_}m")
                net_freq.set_component_value("R1", str(RC))
                net_freq.set_component_value("R2", str(RC))
                net_freq.set_component_value("R3", str(RE))
                net_freq.set_component_value("R4", str(RE))
                
                net_freq.set_component_value("R5", str(RIN))
                net_freq.set_component_value("R6", str(RIN))

                net_freq.set_component_value("R7", str(RB))
                net_freq.set_component_value("R8", str(RB))
                net_freq.set_component_value("R9", str(RB))
                net_freq.set_component_value("R10", str(RB))

                #net_freq.set_component_value("RVBE_BUFFER_1", str(rvbe_buffer))
                #net_freq.set_component_value("RVBE_BUFFER_2", str(rvbe_buffer))

                # ---------- ESTÁGIO 2 ----------
                net_freq.set_component_value("RE_2E_1", str(RE_2E))
                net_freq.set_component_value("RE_2E_2", str(RE_2E))

                net_freq.set_component_value("RC_2E_1", str(RC_ajuste))
                net_freq.set_component_value("RC_2E_2", str(RC_ajuste))

                # ---------- SIMULAÇÃO ----------
                net_freq.add_instruction(".ac lin 1 1k 1k")
                net_freq.set_element_model("V3", "AC 1")
                net_freq.add_instruction(".save V(vout) time")
                net_freq.add_instruction(".option noopiter")

                raw_ac, log_ac = runner.run_now(net_freq)

                curvas = RawRead(raw_ac)

                vout = curvas.get_trace("V(vout)").get_wave(0)

                avtotal = abs(vout[0])
                if tentativa ==0:
                    print(f"ganho inicial: {avtotal}")
                erro = abs(avtotal - 100.6)

                if erro < melhor_erro:
                    melhor_erro = erro
                    melhor_RC = RC_ajuste
                    melhor_ganho = avtotal


                print(f"Tentativa {tentativa+1} | RC = {RC_ajuste:.2f} | ganho = {avtotal:.6f}")

                # ---------- CONDIÇÃO DE PARADA ----------
                if 100.5 <= avtotal <= 100.8:
                    melhor_RC = RC_ajuste
                    melhor_ganho = avtotal
                    print("GANHO OK")
                    break


                RC_ajuste = RC_ajuste * (100.7/avtotal)

            # ---------- RESULTADO FINAL ----------
            RC_final = melhor_RC
            avtotal = melhor_ganho

            resultados_csv.append({
                "Av1": ganho,
                "Is_mA": is_,
                "IRB_mA": irb,
                "Ic_2E_mA": i*1e3,
                "RE_1E": RE,
                "RC_1E": RC,
                "RBuffer": RB,
                "RVBE_BUFFER": rvbe_buffer,
                "RE_2E": RE_2E,
                "RC_2E": RC_final,
                "Av2": round(avtotal/ganho, 2),
                "Av_total": avtotal
            })
            df_resultados = pd.DataFrame(resultados_csv)

            df_resultados.to_csv(
                "RESULTADOS_FINAIS_2E_is05_ir1mA.csv",
                index=False
            )


print('------------Final do código, csv salvo com sucesso')



                        





