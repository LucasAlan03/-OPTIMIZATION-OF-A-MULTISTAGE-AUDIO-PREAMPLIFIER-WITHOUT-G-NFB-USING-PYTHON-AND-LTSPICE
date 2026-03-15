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


r1vbe = np.arange(1.5E3,14E3+200,500)

if __name__ == "__main__":

    print("-----------Codigo começou------------")

    for r in r1vbe:
        
        net_thd = SpiceEditor(netlist_thd)
        net_thd.set_component_value('R1_VBE',str(r))

        # análise DC (ponto de operação)
        net_thd.add_instruction(".op")

        raw_file, log_file = runner.run_now(net_thd)
        
        time.sleep(2)  # esperar 2 seg para garantir que os arquivos_foram_gerados
        raw = RawRead(raw_file)

        ir13 = raw.get_trace("I(R13)").get_wave()[0]
        
        resultados_csv.append({
            'IOUT': round(ir13*1e3,4)
        })
        print(f' R1_VBE = {r} e {round(ir13*1e3,4)}mA')
        dados_df= pd.DataFrame(resultados_csv)
        dados_df.to_csv('CORRENTE_AJUSTE_20m_IR13.csv',index= False)
