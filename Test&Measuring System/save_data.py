import os
import pandas as pd

prev_points = 3

def save_data(data, path):
    if os.path.exists(path):                    # If the file exists append to it
            df = pd.read_csv(path, sep = ';')   # Existing data
            new_values_df = pd.DataFrame(data)              # New data
            
            new_df = pd.concat((df, new_values_df))         # Append the new data
            
            if len(new_df) > 5 and path == 'data.csv':
                for i in range(1, prev_points + 1):
                    for col in ['N1', 'P1', 'P2', 'N3', 'P3']:
                        new_col_name = f'{col}_prev{i}'
                        new_df[new_col_name] = new_df[col].shift(i)

            new_df.to_csv(path, index = False, sep = ';')   # Save it

    else:
        pd.DataFrame(data).to_csv(path, index = False, sep = ';')