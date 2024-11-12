# DL-SCDisassembly

This project is part of "Enhancing Deep Learning-based Side-channel Analysis Using Feature Engineering in
a Fully Simulated IoT System" paper.

The main objective is to create a refined dataset for side channel-based disassembly tasks using DL models. The dataset is enhanced using statistical and temporal log transformation features.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Features](#features)
---

## Installation

```bash
# Clone the repository
git clone https://github.com/PLASS-Lab/DL-SCDisassembly.git

# Navigate to the project directory
cd DL-SCDisassembly

# Install dependencies
python setup.py install
```

## Usage

After uploading the assembly logs, collected from GDB, to the selected folder, it can be converted to a structured CSV file using `assembleyTocsv.py`

```bash
python assembleyTocsv.py
```

The generated CSV file can be passed to [python-elmo](https://github.com/ThFeneuil/python-elmo) engine for power simulation.

Then, the `FeatureEngineering.py` file can be used to generate the features using a user-specified window size.

```bash
python FeatureEngineering.py
```

The refined dataset can then be used for the detection of countermeasures or disassembly using predefined feature sets and window sizes

```bash
python inference.py
python classification
```

## Features

The main features.

- **Assembly to CSV Conversion**: Convert raw assembly logs from GDB into structured CSV files, making them easier to manipulate and analyze.
- **Feature Engineering for Side-Channel Analysis**: Use `FeatureEngineering.py` to apply statistical and temporal log transformation features on the dataset, allowing for customizable feature sets and window sizes.
- **Countermeasure Detection and Disassembly Analysis**: Perform classification and disassembly tasks with the refined dataset. Experiment with different window sizes and feature sets.

