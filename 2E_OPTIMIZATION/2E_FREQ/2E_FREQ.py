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

runner = SimRunner(output_folder='./SLEW_RATE', simulator=ltspice_exe_path)
runner.cleanup_files()   

netlist_path_freq  = "2E_JFET_FREQ.asc"
resultados_csv = []
resultados_slew = []
RIN = 47E3


df_bias = pd.read_csv("RESULTADOS_FINAIS_2E_is05_ir1mA.csv")

df_bias["Is_mA"] = df_bias["Is_mA"].round(3)
df_bias["IRB_mA"] = df_bias["IRB_mA"].round(3)
df_bias["Ic_2E_mA"] = df_bias["Ic_2E_mA"].round(3)



pares_escolhidos = [(6,0.5,1.0),   (8, 0.5,1.0), (10,0.5,1.0), (12,0.5,1.0)]  


ic_menor = [0.1e-3,0.25e-3]
ic_maior = np.arange(0.5e-3,10e-3+0.5e-3,0.5e-3)

ic = np.concatenate((ic_menor, ic_maior))*1e3         #esse é o ic_Ma do banco

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for i in ic:

        
        ic_ma = round(i,3)
        for ganho, is_, irb in pares_escolhidos:

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

            linha = df_filtrado.iloc[0]
            RE = linha["RE_1E"]
            RC = linha["RC_1E"]

            RB = linha["RBuffer"]
            rvbe_buffer = linha["RVBE_BUFFER"]
             
            RE_2E = linha["RE_2E"]
            RC_2E = linha["RC_2E"]

            #print(f'para os pontos de Av = {ganho},Corrente de cauda {is_}, corrente de buffer {irb} e corrente de coletor {ic_ma}')
            #print(RE, RC, RB, RE_2E, RC_2E)

            net_freq = SpiceEditor(netlist_path_freq)

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

            net_freq.set_component_value("RE_2E_1", str(RE_2E))
            net_freq.set_component_value("RE_2E_2", str(RE_2E))

            net_freq.set_component_value("RC_2E_1", str(RC_2E))
            net_freq.set_component_value("RC_2E_2", str(RC_2E))


            net_freq.add_instruction(".save V(vout) time")    
            net_freq.set_component_value("V3", "AC 1")
            net_freq.add_instruction(".ac dec 800 10 10Meg")

            raw_ac, log_ac = runner.run_now(net_freq)
            time.sleep(2) 

            f_corte, max_gain = encontrar_freq_corte(raw_ac)


            if f_corte is  None:
                print(f"Frequência de corte não  encontrada para {i*1e3} mA")
                continue
            av2 = round(100/ganho,2)
            resultados_csv.append({
                'Freq_corte(Khz)':f_corte / 1e3,
                'IRB_mA': irb,
                'Av2' : av2,
                'Av': ganho,
                'Is_mA':is_,
                'IC_2E_mA':ic_ma
            }) 
            dados_df = pd.DataFrame(resultados_csv)
            dados_df.to_csv("FREQ_VS_IC_2E.csv", index=False)

print("--------------------------Final do código-----------------------------------")        




