<h1 align="center"><strong>DL-SCDisassembly</strong></h1>

<p align="left">
  🪪&nbsp;<a href="#about">About</a>
  | 🪄&nbsp;<a href="#Installation">Installation</a>
  | 🗃️&nbsp;<a href="#Usage">Usage</a>
  | 🏷️&nbsp;<a href="#Features">Features</a>
  | 🔗&nbsp;<a href="#citation">Citation</a>
  | 📝&nbsp;<a href="https://doi.org/10.1016/j.eswa.2024.126079" target="_blank">Paper</a>
</p>

This repository contains the code for the paper:
<a href="https://doi.org/10.1016/j.eswa.2024.126079" target="_blank">Enhancing deep learning-based side-channel analysis using feature engineering in a fully simulated IoT system</a>

## About
The main objective is to create a refined dataset for side channel-based disassembly tasks using DL models. The dataset is enhanced using statistical and temporal log transformation features.

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


## Citation
If you use this code for your research, please cite the following paper.
```bibtex
@article{alabdulwahab2025dlscd,
  journal = {Expert Systems with Applications},
  title = {Enhancing deep learning-based side-channel analysis using feature engineering in a fully simulated IoT system},
  doi = {https://doi.org/10.1016/j.eswa.2024.126079},
  author = {Alabdulwahab, Saleh and Cheong, Muyoung and Seo, Aria and Kim, Young-Tak and Son, Yunsik},
  year = {2025}
}
```

<p align="center">
  <a href="https://plass.dongguk.edu" target="_blank">
    <img src="https://github.com/sucystem/PLASS/blob/main/logo.png" width="400" alt="PLASS Lab, Dongguk University">
  </a>
</p>

