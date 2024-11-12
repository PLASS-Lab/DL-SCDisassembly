import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Prompt the user for a window size input
window_size = int(input("Enter window size: "))

# the paths for the input and output files
input_dir = r'input_dir'
output_dir = r'output_dir'

# Read the CSV files
dfs = []  # A list to store the processed DataFrames
for filename in os.listdir(input_dir):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_dir, filename)
        df = pd.read_csv(file_path)

        # Rolling Window Approach for mean, standard deviation, max
        df[f'mean_{window_size}'] = df['Power'].rolling(window=window_size, min_periods=1).mean()
        df[f'std_dev_{window_size}'] = df['Power'].rolling(window=window_size, min_periods=1).std()
        df[f'max_{window_size}'] = df['Power'].rolling(window=window_size, min_periods=1).max()

        # Exponential Moving Average Approach
        alpha = 2 / (window_size + 1)
        df[f'ewma_{window_size}'] = df['Power'].ewm(alpha=alpha, min_periods=1, adjust=False).mean()

        # Calculate autocorrelation
        df[f'autocorrelation_{window_size}'] = df['Power'].rolling(window=window_size, min_periods=1).apply(lambda x: pd.Series(x).autocorr(lag=1), raw=True)

        dfs.append(df)

# Combine the DataFrames
combined_df = pd.concat(dfs)

# Resetting the index will create a new index column
combined_df.reset_index(inplace=True)
# moving log-transformed temporal interaction (MLTI) features.
combined_df[f'MLTI_autocor_{window_size}'] = np.log(combined_df['Sequence'] + 1) * combined_df[f'autocorrelation_{window_size}']  # added 1 to avoid log(0) as it equals infinity
combined_df[f'MLTI_EWMA_{window_size}'] = np.log(combined_df['Sequence'] + 1) * combined_df[f'ewma_{window_size}']  # added 1 to avoid log(0) as it equals infinity

# Fill NA with 0, for some features that can start with 1 or 2 window sizes
# combined_df.fillna(0, inplace=True)

feature_cols = [col for col in combined_df.columns if col not in ['power', 'type' , 'instruction', 'label', 'context']]

# Save the combined DataFrame to a CSV file
output_filename = f'output_filename'
output_path = os.path.join(output_dir, output_filename)
combined_df.to_csv(output_path, index=False)
