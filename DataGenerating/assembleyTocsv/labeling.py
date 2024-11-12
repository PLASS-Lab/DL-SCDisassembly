import pandas as pd
import os

# Define the directory where the CSV files are located
source_dir = r'source_dir'

# Define the directory where the labeled files will be saved
destination_dir = r'destination_dir'

# Loop through each file in the source directory
for filename in os.listdir(source_dir):
    if filename.endswith('.csv'):
        
        # Full path to the current file
        full_path = os.path.join(source_dir, filename)
        
        # Read the file into a Pandas DataFrame
        df = pd.read_csv(full_path)
        
        # If the file has 'password_with_dummy' in its name
        if 'password_with_dummy' in filename:
            # Divide DataFrame into 4 equal sections
            n = len(df) // 4
            
            # Label the sections
            df['label'] = 0
            df.loc[n:2*n-1, 'label'] = 1
            df.loc[3*n:, 'label'] = 1
        
        # If the file has 'plaintext_with_dummy' in its name
        elif 'plaintext_with_dummy' in filename:
            # Divide DataFrame into 2 equal sections
            n = len(df) // 2
            
            # Label the sections
            df['label'] = 0
            df.loc[n:, 'label'] = 1
        
        # Full path to save the modified file
        save_path = os.path.join(destination_dir, filename)
        
        # Save the DataFrame back to CSV
        df.to_csv(save_path, index=False)
