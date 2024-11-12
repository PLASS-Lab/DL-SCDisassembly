import os
import pandas as pd
import numpy as np
from elmo.engine import ELMOEngine, Instr
import matplotlib.pyplot as plt

def generate_power(filename, parent_folder_path, savepath):
    csv_file_path = os.path.join(parent_folder_path, filename)
    df = pd.read_csv(csv_file_path)

    # get the instances of the instruction, operands as hex and value form the dataset
    hex_list = df['address'].tolist()
    operands_list_hex = [int(x, 16) for x in hex_list]
    value_list = df['value'].tolist()
    instr = df['type'].tolist()

    # convert instruction strings to their corresponding enum values
    instr = [eval(instruction) for instruction in instr]
    power = []
    engine = ELMOEngine()

    # retrieve instances for the previous, current, and next instructions
    for i in range(1, len(instr) - 1):
        previous_type = instr[i-1]
        current_type = instr[i]
        next_type = instr[i+1]

        previous_operands_hex = operands_list_hex[i-1]
        previous_value = value_list[i-1]

        current_operands_hex = operands_list_hex[i]
        current_value = value_list[i]
        # add the point to the ELMO engine
        engine.add_point(
            (previous_type, current_type, next_type),
            (previous_operands_hex, previous_value),
            (current_operands_hex, current_value)
        )

    # compute the power consumption of all these points
    engine.run()
    power = engine.power
    # reset the engine to study other points
    engine.reset_points()

    # saving the generated power as a CSV file along with corresponding instruction
    power_df = pd.DataFrame(power, columns=['Power'])
    power_df['type'] = df['type']
    power_df['instruction'] = df['instruction']
    power_df['label'] = df['label'] 
    power_df['context'] = df['context']


    #power_df['context'] = df['context']
    power_file_path = os.path.join(savepath, f'{os.path.splitext(filename)[0]}_power_trace.csv')
    power_df.to_csv(power_file_path, index=False)

parent_folder_path = r'parent_folder_path'
savepath = r'savepath'

for filename in os.listdir(parent_folder_path):
    if filename.endswith(".csv"):
        generate_power(filename, parent_folder_path, savepath)

for filename in os.listdir(savepath):
    if filename.endswith("_power_trace.csv"):
        power_df = pd.read_csv(os.path.join(savepath, filename))

