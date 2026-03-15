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



runner = SimRunner(output_folder='./3E_FREQ', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_path_freq  = "3E_FREQ_OFFSET_CORRENTE_20mA.asc"
resultados_csv = []

r1vbe = np.arange(1.5E3,14E3+200,500)

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for r in r1vbe:
        
        net_freq = SpiceEditor(netlist_path_freq)
        net_freq.set_component_value('R1_VBE',str(r))
        net_freq.add_instruction(".save V(vout) time")    
        net_freq.set_component_value("V3", "AC 1")
        net_freq.add_instruction(".ac dec 800 10 10Meg")


        raw_ac, log_ac = runner.run_now(net_freq)
        time.sleep(2) 

        f_corte, max_gain = encontrar_freq_corte(raw_ac)


        if f_corte is  None:
            print(f"Frequência de corte não  encontrada para {r} ohms")
            continue

        resultados_csv.append({
            'Freq_corte(Khz)':f_corte / 1e3,
            'R1_VBE':r
        })
        dados_df = pd.DataFrame(resultados_csv)
        dados_df.to_csv("FREQ_VS_Iout_3E.csv", index=False)









