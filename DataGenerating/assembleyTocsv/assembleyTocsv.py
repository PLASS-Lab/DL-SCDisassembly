import os
import re
import csv

def extract_info(line, folder_name):
    address = re.search(r'0x\w+', line)
    if address:
        address_value = address.group(0)
    else:
        address_value = ''

    assembly = re.search(r':\s+(\S+)', line)
    if assembly:
        assembly_value = assembly.group(1)
    else:
        assembly_value = ''

    values = re.findall(r'#(\d+)', line)
    value1 = values[0] if len(values) > 0 else '0'

    instruction_type = get_instruction_type(assembly_value)

    return address_value, assembly_value, value1, instruction_type, folder_name

# categories each instruciton with its type
def get_instruction_type(instruction):
    instruction = instruction.upper()
    if instruction in ["ADDS", "ANDS", "CMPS", "EORS", "MOVS", "ORRS", "SUBS"]:
        return "Instr.EOR"
    elif instruction in ["LSLS", "LSRS", "RORS"]:
        return "Instr.LSL"
    elif instruction in ["STR", "STRB", "STRH"]:
        return "Instr.STR"
    elif instruction in ["LDR", "LDRB", "LDRH"]:
        return "Instr.LDR"
    elif instruction in ["MULS"]:
        return "Instr.MUL"
    else:
        return "OTHER"



# parent_folder_path where we will have the logs folders for each context
parent_folder_path = r'parent_folder_path'

# iterating over the context folders to get the logs
for folder_name in os.listdir(parent_folder_path):
    folder_path = os.path.join(parent_folder_path, folder_name)
    
    if os.path.isdir(folder_path):
        data_list = []
        
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r', errors='ignore') as f:
                    for line in f:
                        if line.startswith("=>"):
                            data = extract_info(line, folder_name)
                            print(data) 
                            if data[-2] != "OTHER":
                                data_list.append(data)
        
        # creating a separate CSV file for each context
        csv_file_path = os.path.join(parent_folder_path, f'{folder_name}.csv')
        
        with open(csv_file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['address', 'instruction', 'value', 'type', 'context']) # column headers
            for data in data_list:
                writer.writerow(data)