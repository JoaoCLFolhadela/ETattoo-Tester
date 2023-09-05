import pyvisa
import pandas as pd
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from save_data import save_data
from get_plots import update_plot
import csv 
import os


data_lock = threading.Lock()
heads = ['N1', 'P1', 'P2', 'N3', 'P3'] # Channels from e-tatto

# Get devices connected
rm = pyvisa.ResourceManager()
V1 = rm.open_resource('GPIB0::6::INSTR') # Agilent nanovoltmeter
V2 = rm.open_resource('GPIB0::7::INSTR') # Keithley multimeter 2700
V3 = rm.open_resource('GPIB0::8::INSTR') # Agilent nanovoltmeter

data = {'time':[],'N1': [], 'P1': [], 'P2': [], 'N3': [], 'P3': []} # Dictionary to save each channels data
predictions = {'time':[], 'binary': [], 'AP':[]}                  # Store results of gotten predictions
t0 = time.time()
new_data = False
curr_time = 0

def measure_nanovolt(device):
    
    CH1 = float(device.query("MEAS:VOLT:DC? (@FRONt1)")) # Measure channel 1 of Agilent nanovoltmeter

    CH2 = float(device.query("MEAS:VOLT:DC? (@FRONt2)")) # Measure channel 2 of Agilent nanovoltmeter

    return CH1, CH2

def measure_keithley(device):
    l = device.query(":FETCh?").split('VDC') # Keithley multimerter 2700 returns a string with 3 values, the 1st one is 
    return eval(l[0])                        # the voltage so we split till 'VDC' appears
            
def data_listener():
    global curr_time
    global new_data 

    new_meas = True
    last_meas_time = 0.0
    try:
        for V in (V1,V2,V3):
            print(V.query("*IDN?"))
    except Exception as e:
        print(f'Error in data_listener thread: {e}')
        
    while True:
        try:
            with open('taking_meas_flag.csv') as file: # Check if new meas is started
                reader = csv.reader(file)
                
                if eval(next(reader)[0]):
                    with ThreadPoolExecutor(max_workers= 3) as executor: # Read all instruments simultaneously
                    
                        print("Reading voltages...")
                        V1_reading, V3_reading = list(executor.map(measure_nanovolt, [V1, V3]))
                        V2_future = executor.submit(measure_keithley, V2)
                        V2_reading = V2_future.result()
                        
                        
                        with data_lock: # Save the data read
                            
                            if new_meas:
                                if os.path.exists('data.csv'):                    # If the file exists append to it
                                    df = pd.read_csv('data.csv', sep = ';') 
                                    last_meas_time = df['time'].values[-1]

                            curr_time = time.time()-t0 + last_meas_time
                            
                            data['time'] = [curr_time]
                            data['N1'] = [V1_reading[0]]
                            data['P1'] = [V1_reading[1]]
                            data['P2'] = [V2_reading]
                            data['N3'] = [V3_reading[0]]
                            data['P3'] = [V3_reading[1]]
                            
                            #save_data(data = data, path = 'data_without_filter.csv')
                            #
                            ## Saturate voltages
                            #for key, value in data.items():
                            #    if key != 'time':
                            #        if value > df[key].abs().max():
                            #            data[key] = df[key].abs().max()
                            #            print(f"Found a BIG voltage for channel {key}")

                            save_data(data = data, path = 'data.csv')
                            print('Voltages saved!')
                            
                            new_data = True
                            new_meas = False
                        file.close()
                            
                else:
                    file.close()
            
        except Exception as e:
            print(f'Error in data_listener thread: {e}')
            
    
thread = threading.Thread(target=data_listener)
thread.daemon = True
thread.start()

while True:
    
    if new_data:
        try:
            df = pd.read_csv('data.csv', sep = ';') 
            update_plot(df)
            new_data = False
        except Exception as e:
            print('Error in main loop:' , e)
    else:
        continue

        
    