import matplotlib.pyplot as plt
import matplotlib as mpl

def update_plot(df):
    
    if len(df) > 0:
    
        plt.style.use("dark_background")
        mpl.rcParams['grid.color'] = '#42ffff'
        fig, axs = plt.subplots(2,3, figsize=(14, 7))


        ts = df['time'].iloc[-100:]
        fig.tight_layout(pad=2.0)
        axs[0,0].plot(ts, df['N1'].iloc[-100:] / df['N1'].abs().max(), '-o', label = 'N1', color = '#fafa64')
        axs[0,0].grid()
        axs[0,0].set_title('$V_{N1}$')
        axs[0,0].set_ylim([-1,1])

        axs[0,2].plot(ts, df['N3'].iloc[-100:] / df['N3'].abs().max(), '-o', label = 'N3' , color = "#fafa64")
        axs[0,2].grid()
        axs[0,2].set_title('$V_{N3}$')
        axs[0,2].set_ylim([-1,1])

        axs[1,0].plot(ts, df['P1'].iloc[-100:] / df['P1'].abs().max(), '-o', label = 'P1' , color = "#fafa64")
        axs[1,0].grid()
        axs[1,0].set_title('$V_{P1}$')
        axs[1,0].set_ylim([-1,1])

        axs[1,1].plot(ts, df['P2'].iloc[-100:] / df['P2'].abs().max(), '-o', label = 'P2' , color = "#fafa64")
        axs[1,1].grid()
        axs[1,1].set_title('$V_{P2}$')
        axs[1,1].set_ylim([-1,1])

        axs[1,2].plot(ts, df['P3'].iloc[-100:] / df['P3'].abs().max(), '-o', label = 'P3' , color = "#fafa64")
        axs[1,2].grid()
        axs[1,2].set_title('$V_{P3}$')
        axs[1,2].set_ylim([-1,1])
        saved_pic = False

        while not saved_pic:
            try:
                plt.savefig('images/plots.png')
                plt.close()

                saved_pic = True
            except Exception as e:
                print("Failed to save pic", e)


heads = ['N1', 'P1', 'P2', 'N3', 'P3'] 
import pandas as pd
import numpy as np

d = {}
for h in heads:
    d[h] = np.random.randint(1, 10, 30)* 1e-5
d['time'] = np.arange(0, 3 * 30,3)
update_plot(pd.DataFrame(d))

#while True:
#    try:
#        df = pd.read_csv("data.csv", sep = ';')
#        if len(df) > 0:
#            if len(df) < 100:
#                df = df
#            else: 
#                df = df.iloc[-100:]
#
#        update_plot(df)
#        print("Updating plot...")
#    except Exception as e:
#        print(f"Error {e}")
#        continue
#    time.sleep(0.01)