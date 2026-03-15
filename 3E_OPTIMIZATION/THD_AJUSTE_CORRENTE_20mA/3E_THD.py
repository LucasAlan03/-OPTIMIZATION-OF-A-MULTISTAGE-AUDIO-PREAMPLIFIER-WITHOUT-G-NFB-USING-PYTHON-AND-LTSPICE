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

ltspice_exe_path = r"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe"
resultados_csv = []

runner = SimRunner(output_folder='./THD_3E', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_thd  = "3E_THD_OFFSET_CORRENTE_20mA.asc"


#  Parâmetros para simulação de THD.
Freq = 1e3
numcyc= 350
FFT= 655360*2
dlycyc = 50
simtime = (dlycyc+numcyc)/Freq
dlytime = dlycyc/Freq
numsampl = simtime / Freq / ((simtime / numcyc) * FFT)


# ----------- Variação do Resistor do Resistor R1 do multiplicador de VBE
# -- R1 = 1.5K I = 2.05mA  ; R1 = 7.5K I= 20.5mA ; R1 = 14K I = 40.8mA

r1vbe = np.arange(1.5E3,14E3+200,500)

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for r in r1vbe:
        
        net_thd = SpiceEditor(netlist_thd)
        net_thd.set_component_value('R1_VBE',str(r))

        #--------- Parametros THD.
        
        net_thd.add_instruction(".options plotwinsize=0")
        net_thd.add_instruction(".options numdgt=99")
        net_thd.add_instruction(".option noopiter")
            
            
        net_thd.add_instruction(f".four {Freq} V(vout)")
        net_thd.add_instruction(f".tran 0 {simtime} {dlytime} {numsampl}")
        

        net_thd.add_instruction(".save V(vout) time")   
        net_thd.set_element_model("V3",f"SINE(0 28.2m {Freq})")

        raw_ac, log_ac = runner.run_now(net_thd,timeout= 1200)   
        time.sleep(2)  # esperar 2 seg para garantir que os arquivos_foram_gerados

        if not os.path.exists(log_ac):
            print("Log não foi gerado")
            continue

        with open(log_ac, "r", encoding="utf-8", errors="ignore") as f:
            for linha in f:
                if "Total Harmonic Distortion" in linha:
                    thd = float(linha.split(":")[1].split("%")[0])
                    break

            if thd is None:
                print("THD não encontrado no log")
                continue
            else :
                print(f' THD : {thd}\n')

            resultados_csv.append({
                'thd':thd,
                'R1_VBE':r

            })
            
            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv('THD_3E.csv',index = False)

print('------------------ Final do código-------------------')




