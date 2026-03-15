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

# -------- CASO A SIMULAÇÃO JÁ TENHA SIDO FEITA EM ALGUM MOMENTO LER O CSV E PULAR ESSES PONTOS ------------------
csv_path = "THD_VS_IC_2E.csv"

if os.path.exists(csv_path):
    df_existente = pd.read_csv(csv_path)

    df_existente["Is_mA"] = df_existente["Is_mA"].round(3)
    df_existente["IRB_mA"] = df_existente["IRB_mA"].round(3)
    df_existente["IC_2E_mA"] = df_existente["IC_2E_mA"].round(3)

    resultados_csv = df_existente.to_dict("records")
else:
    df_existente = pd.DataFrame()

# ---------------------- CASO NÃO, A SIMULAÇÃO SEGUE NORMA --------------------------------------------------------







ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"

runner = SimRunner(output_folder='./THD_2E_J201_CORRETO', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_path_slew  = "2E_JFET_THD.asc"


RIN = 47E3
df_bias = pd.read_csv("RESULTADOS_FINAIS_2E_is05_ir1mA.csv")

#  Parâmetros para simulação de THD.
Freq = 1e3
numcyc= 350
FFT= 655360*2
dlycyc = 50
simtime = (dlycyc+numcyc)/Freq
dlytime = dlycyc/Freq
numsampl = simtime / Freq / ((simtime / numcyc) * FFT)


df_bias["Is_mA"] = df_bias["Is_mA"].round(3)
df_bias["IRB_mA"] = df_bias["IRB_mA"].round(3)
df_bias["Ic_2E_mA"] = df_bias["Ic_2E_mA"].round(3)



pares_escolhidos = [(6,0.5,1.0),   (8, 0.5,1.0), (10,0.5,1.0), (12,0.5,1.0)]  


ic_menor = [0.1e-3,0.25e-3]
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3)
ic = np.concatenate((ic_menor, ic_maior))*1e3                      #esse é o ic_Ma do banco

#ic = ic_maior*1e3
if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for i in ic:



        ic_ma = round(i,3)
        for ganho, is_, irb in pares_escolhidos:
            thd = None
            filtro = (
                (df_bias["Av1"] == ganho) &
                np.isclose(df_bias["Is_mA"], is_) &
                np.isclose(df_bias["IRB_mA"], irb) &
                np.isclose(df_bias["Ic_2E_mA"], ic_ma)
            )
            df_filtrado = df_bias.loc[filtro]

            if df_filtrado.empty:
                print(f"Ponto não encontrado: Av1={ganho} Is={is_} IRB={irb} Ic={ic_ma}")
                continue

            '''           # -------------------------- VERIFICAÇÃO DOS PONTOS CALCULADOS -------------------------------------#
            if not df_existente.empty:
                filtro_existente = (
                    (df_existente["Av"] == ganho) &
                    np.isclose(df_existente["Is_mA"], is_) &
                    np.isclose(df_existente["IRB_mA"], irb) &
                    np.isclose(df_existente["IC_2E_mA"], ic_ma)
                )

                if filtro_existente.any():
                    #print(f"Ponto já calculado -> Av={ganho} Is={is_} IRB={irb} Ic={ic_ma}")
                    print("Pontos carregados:", len(df_existente))
                    continue
            # -----------------------  SEQUÊNCIA DA SIMULAÇÃO --------------------------------------------------#
            '''
            print('----------------------------Simulando--------------------------')
            linha = df_filtrado.iloc[0]
            RE = linha["RE_1E"]
            RC = linha["RC_1E"]

            RB = linha["RBuffer"]
            #rvbe_buffer = linha["RVBE_BUFFER"]
             
            RE_2E = linha["RE_2E"]
            RC_2E = linha["RC_2E"]

            print(f'para os pontos de Av = {ganho},Corrente de cauda {is_}, corrente de buffer {irb} e corrente de coletor {ic_ma}\n')
            #print(f'RE1 {RE}, RC1 {RC}, RUBBER {RB},RE_2E {RE_2E},RC {RC_2E}')



            net_thd = SpiceEditor(netlist_path_slew)

            net_thd.add_instruction(".options plotwinsize=0")
            net_thd.add_instruction(".options numdgt=99")
            net_thd.add_instruction(".option noopiter")
            
            
            net_thd.add_instruction(f".four {Freq} V(vout)")
            net_thd.add_instruction(f".tran 0 {simtime} {dlytime} {numsampl}")

            net_thd.set_component_value("I1", f"{is_}m")

            net_thd.set_component_value("R1", str(RC))
            net_thd.set_component_value("R2", str(RC))

            net_thd.set_component_value("R3", str(RE))
            net_thd.set_component_value("R4", str(RE))

            net_thd.set_component_value("R5", str(RIN))
            net_thd.set_component_value("R6", str(RIN))

            net_thd.set_component_value("R7", str(RB))
            net_thd.set_component_value("R8", str(RB))
            net_thd.set_component_value("R9", str(RB))
            net_thd.set_component_value("R10", str(RB))

            #net_thd.set_component_value("RVBE_BUFFER_1", str(rvbe_buffer))
            #net_thd.set_component_value("RVBE_BUFFER_2", str(rvbe_buffer))

            net_thd.set_component_value("RE_2E_1", str(RE_2E))
            net_thd.set_component_value("RE_2E_2", str(RE_2E))

            net_thd.set_component_value("RC_2E_1", str(RC_2E))
            net_thd.set_component_value("RC_2E_2", str(RC_2E))

            net_thd.add_instruction(".save V(vout) time")   
            net_thd.set_element_model("V3",f"SINE(0 28.2m {Freq})")

            raw_ac, log_ac = runner.run_now(net_thd,timeout= 600)   
            time.sleep(2)  # esperar 2 seg para garantir que os arquivos_foram_gerados

            if not os.path.exists(log_ac):
                print("Log não foi gerado")
                continue

            with open(log_ac, "r", encoding="utf-8", errors="ignore") as f:
                for linha in f:
                    if "Total Harmonic Distortion" in linha:
                        thd = float(linha.split(":")[1].split("%")[0])
                        break
            #print('-----------final da busca-----------------------')
            av2 = round(100/ganho,2)
            if thd is None:
                print("THD não encontrado no log")
                continue
            else :
                print(f'para os pontos de Av = {ganho},Corrente de cauda {is_}, corrente de buffer {irb} e corrente de coletor {ic_ma}')
                print(f' THD : {thd}\n')

            resultados_csv.append({
                    'thd':thd,
                    'IRB_mA': irb,
                    'Av2' : av2,
                    'Av': ganho,
                    'Is_mA':is_,
                    'IC_2E_mA':ic_ma
                }) 

            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv("THD_VS_IC_2E_is_0.5_irb_1mA.csv", index=False)

print ('----------- FINAL DO CÓDIGO-----------------')           