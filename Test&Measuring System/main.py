from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
import pandas as pd
import numpy as np
from time import sleep
from save_data import save_data
import csv
import torch
from nn import Deep

model = torch.load('TPSM1.pth')

Window.clearcolor = (1, 1, 1, 1) # Background
Builder.load_file('main.kv') # Load .kb file

class CustomLayout(FloatLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        # Points variables
        self.preds = []
        self.true_pred = 0

        #Other Variables
        self.taking_meas_flag = False
        self.countdown_clock = None
        self.meas_data = None
        self.meas_t0 = 0.0        
        
        Clock.schedule_interval(self.update_plot, 1) # update plots every second
        
    
    def build(self): # Build Kivy layout
        return FloatLayout()
    

    def START(self, instance):

        self.taking_meas_flag = False
        with open('taking_meas_flag.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.taking_meas_flag])
            f.close()
        
        # Hide and disable Start button
        instance.opacity = 0
        instance.disabled = True
        
        # Start Countdown, every one second update it
        self.ids.countdown_number.text = '3'
        self.countdown_clock = Clock.schedule_interval(self.update_countdown, 1)



    def reset(self, instance):
        # Reset to init states
        if not self.taking_meas_flag or instance.text[0] == 'N': # If not taking measurement or button is New Meas Button
            self.taking_meas_flag = False
            self.ids.countdown_number.text = '-'
            self.ids.countdown_text.text = 'COUNTDOWN'
            self.ids.prediction.text = "Model Prediction: \n      [- , - , - , - , -]"
            self.ids.start_button.opacity = 1
            self.ids.start_button.disabled = False
            self.ids.reset_button.opacity = 0
            self.ids.reset_button.disabled = True
            self.ids.true_pred.text = 'Please insert the \nposition you put \nyour finger on \nand press ENTER.'
                
    def update_plot(self, a):
        # Update_plots every 1 sec
        try:
            self.ids.plot.reload()
        except Exception as e:
            print('Failed to get plot, trying again')
            sleep(0.1)
            self.update_plot(a = '')
    
    def update_countdown(self, a):
        
        if self.ids.countdown_number.text.isdigit(): # If the countdown is a number decrease it
            
            c = int(self.ids.countdown_number.text)
            
            # Update countdown every second
            if c > 0 and self.ids.countdown_text.text[0] != 'H': # countdown to 3
                
                self.ids.countdown_number.text = str(c - 1)
                
                if c == 2:
                    self.taking_meas_flag = True
                    with open('taking_meas_flag.csv', 'w') as f:
                       writer = csv.writer(f)
                       writer.writerow([self.taking_meas_flag])
                       f.close()
                       
            elif c == 0 and self.ids.countdown_text.text[0] != 'H':

                self.ids.countdown_number.text = '15'
                self.ids.countdown_text.text = "Hold your finger on the spot..." # From here comes the ...text[0] != H
                sleep(1)
                self.read_data()
                self.meas_t0 = self.data['time'].iloc[-1]
                
            elif c > 0 and self.ids.countdown_text.text[0] == 'H':
                self.ids.countdown_number.text = str(c - 1)
                
            elif c == 0 and self.ids.countdown_text.text[0] == 'H':
                self.ids.true_pred.disabled = False
                self.ids.countdown_text.text = ""
                self.ids.countdown_number.text = ''
                
        else:
            self.read_data()       
            # If countdown is over stop calling this function every second
            self.meas_data = self.data.loc[self.data['time'] > self.meas_t0].copy()
            self.countdown_clock.cancel()
            self.get_pred()
            
            
    def get_pred(self):
        # Normalize and convert the data to tensors
        X = self.meas_data.drop(columns = ['time'])
        for c in X.columns:
            X[c] = X[c] / self.data[c].abs().max() # Normalize to highest values yet
                        
        X = torch.tensor(X.values, dtype=torch.float32)
        
        # Get predictions
        y_pred = model(X)
        _, predicted = torch.max(y_pred, 1)
        self.preds = predicted.numpy()

        # Show predictions
        self.ids.prediction.text = f" Model Prediction: \n     {list(self.preds)}"
        
        
    def read_data(self): # Tries reading the data.csv file
        try:
            self.data = pd.read_csv('data.csv', sep = ';')
        except Exception as e:  # Use a more specific exception
            print('Error getting file, retrying in 0.1 seconds')
            sleep(0.1)  # Wait before retrying
            self.read_data()
        
    def save_true_AP(self, text):
        
        # Get the AP that was chosen by user
        self.true_pred = int(text.text)
        
        # Remove user input box
        self.ids.true_pred.disabled = True
        self.ids.countdown_text.text = "\n\n\n\n\n\nThanks for your time!"
        
        # Activate reset button
        self.ids.reset_button.opacity = 1
        self.ids.reset_button.disabled = False
        
        # Save the true and predicted APs
        self.meas_data['AP'] = list(np.zeros(len(self.meas_data), dtype = int) + int(self.true_pred))
        self.meas_data['Predicted AP'] = list(self.preds)
        save_data(data = self.meas_data, path = f'data_with_label\\Data_w_label{self.true_pred}.csv')
        
        
                
    
class TestETattooApp(App):
    def build(self):
        return CustomLayout()
    
    
if __name__ == '__main__':
    TestETattooApp().run()
