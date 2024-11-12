# Python-ELMO

_Python-ELMO_ is a Python library which proposes an encapsulation of the project _ELMO_, a statistical leakage simulator for the ARM M0 family.

[MOW17] **Towards Practical Tools for Side
Channel Aware Software Engineering : ’Grey Box’ Modelling for Instruction Leakages**
by _David McCann, Elisabeth Oswald et Carolyn Whitnall_.
https://www.usenix.org/conference/usenixsecurity17/technical-sessions/presentation/mccann

**ELMO GitHub**: https://github.com/sca-research/ELMO

## Requirements

To use _Python-ELMO_, you need at least Python3.5 and ```numpy```.

The library will install and compile ELMO. So, you need the GCC compiler collection and the command/utility ```make``` (for more details, see the documentation of ELMO). On Ubuntu/Debian,

```bash
sudo apt install build-essential
```

To use ELMO on a leaking binary program, you need to compile the C implementations to binary programs (a ".bin" file). "ELMO is not linked to any ARM specific tools, so users should be fine to utilise whatever they want for this purpose. A minimal working platform for compiling your code into an ARM Thumb binary would be to use the GNU ARM Embedded Toolchain (tested version: arm-none-eabi-gcc version 7.3.1 20180622, it can be downloaded from https://developer.arm.com/open-source/gnu-toolchain/gnu-rm).", see the [documentation of ELMO](https://github.com/sca-research/ELMO) for more details.

## Installation

First, download _Python-ELMO_.

```bash
git clone https://github.com/ThFeneuil/python-elmo
```

And then, install ELMO thanks to the installation script. It will use Internet to download the [ELMO project](https://github.com/sca-research/ELMO).

```bash
python setup.py install
```

## Usage

### Create a new simulation project

What is a _simulation project_ ? It is a project to simulate the power traces of _one_ binary program. It includes
 - A Python class to manage the project;
 - The C program which will be compile to have the binary program for the analysis;
 - A linker script where the configuration of the simulated device are defined.

To start a new project, you can use the following function.

```python
from elmo import create_simulation
create_simulation(
   'dilithium', # The (relative) path of the project
   'DilithiumSimulation' # The classname of the simulation
)
```

This function will create a repository ```dilithium``` with all the complete squeleton of the project. In this repository, you can find:
 - The file ```project.c``` where you must put the leaking code;
 - The file ```projectclass.py``` where there is the class of the simulation which will enable you to generate traces of the project in Python scripts;
 - A ```Makefile``` ready to be used with a compiler _arm-none-eabi-gcc_.

Usually a leaking code runs challenges, one challenge giving a power trace. A challenge is the execution of a code with a specific set of data. This set of data is given in the input of the leakage simulation. For example, one can imagine that the leaking code is a symmetric encryption and one wants to study its power leakage according to the message and the secret key. Then, a challenge is the simulation of the leakage for a specific message and for a specific secret key.

So, the classical form of ```project.c``` is the following one:
 - It gets a number of challenges with ```readbyte```.
 - Then, it loops for each challenge.
   - For the challenge, load the specific set of data with ```readbyte```.
   - Start the record of the power leakage (start a power trace) with ```starttrigger```.
   - Realise the leaking operations with the loaded set of data.
   - Stop the record of the power leakage (end a power trace) with ```endtrigger```.
   - Eventually output some data with ```printbyte```.
 - Indicate to ELMO tool that the simulation is finished with ```endprogram```.

The file ```projectclass.py``` contains a subclass of ```SimulationProject```. It is the description of the ```project.c``` file for the ELMO tool, in order to correctly realise the simulation. It also provides methods to manage the simulation (see following sections).
 - The classmethod ```get_binary_path(cl)``` must return the relative path of the leakage binary (```project.c``` correctly compiled).
 - The method ```set_input_for_each_challenge(self, input, challenge)``` must write a ```challenge``` in ```input``` using the function ```write```.

Many methods of ```SimulationProject``` can be rewritten in the subclass if necessary. For example, in the case where your ```project.c``` doesn't run challenges, you can rewrite the method ```set_input(self, input)```.

Important! Don't forget that _ELMO_ (and so _Python-ELMO_) needs a **compiled** version of ```project.c``` (see the "Requirements" section for more details). The provided ```Makefile``` is here to help you to compile.

### List all the available simulation

```python
from elmo import search_simulations
search_simulations('.')
```

```text
{'DilithiumSimulation': <class 'DilithiumSimulation'>,
 'KyberNTTSimulation': <class 'KyberNTTSimulation'>}
```

_Python-ELMO_ offers a example project to you in the repository ```projects/Examples``` of the module. This example is a project to generate traces of the execution of the NTT implemented in the cryptosystem [Kyber](https://pq-crystals.org/kyber/).

### Use a simulation project

Warning! Before using it, you have to compile your project thanks to the provided Makefile.

```python
from elmo import get_simulation
KyberNTTSimulation = get_simulation('KyberNTTSimulation')

simulation = KyberNTTSimulation()
challenges = simulation.get_random_challenges(10)
simulation.set_challenges(challenges)

simulation.run() # Launch the simulation
traces = simulation.get_traces()
# And now, I can draw and analyse the traces
```

### Use a simulation project thanks to a server

Sometimes, it is impossible to run the simulation thanks the simple method ```run``` of the project class. Indeed, sometimes the Python script is executed in the environment where _Python-ELMO_ cannot launch the ELMO tool. For example, it is the case where _Python-ELMO_ is used in SageMath on Windows. On Windows, SageMath installation relies on the Cygwin POSIX emulation system and it can be a problem.

To offer a solution, _Python-ELMO_ can be used thanks to a client-server link. The idea is you must launch the following script which will listen (by default) at port 5000 in localhost.

```bash
python -m elmo run-server
```

And after, you can manipulate the projects as described in the previous section by replacing ```run``` to ```run_online```.

```python
from elmo.manage import get_simulation
KyberNTTSimulation = get_simulation('KyberNTTSimulation')

simulation = KyberNTTSimulation()
challenges = simulation.get_random_challenges(10)
simulation.set_challenges(challenges)

simulation.run_online() # Launch the simulation THANKS TO A SERVER
traces = simulation.get_traces()
# And now, I can draw and analyse the traces
```

Warning! Using the ```run_online``` method doesn't exempt you from compiling the project with the provided Makefile.

### Use the ELMO Engine

The engine exploits the model of ELMO to directly give the power consumption of an assembler instruction. In the model, to have the power consumption of an assembler instruction, it needs
 - the type and the operands of the previous assembler instruction
 - the type and the operands of the current assembler instruction
 - the type of the next assembler instruction

The type of the instructions are:
 - ```EOR``` for ADD(1-4), AND, CMP, CPY, EOR, MOV, ORR, ROR, SUB;
 - ```LSL``` for LSL(2), LSR(2);
 - ```STR``` for STR, STRB, STRH;
 - ```LDR``` for LDR, LDRB, LDRH;
 - ```MUL``` for MUL;
 - ```OTHER``` for the other instructions.

```python
from elmo.engine import ELMOEngine, Instr
engine = ELMOEngine()
for i in range(0, 256):
    engine.add_point(
        (Instr.LDR, Instr.MUL, Instr.OTHER), # Types of the previous, current and next instructions
        (0x0000, i), # Operands of the previous instructions
        (0x2BAC, i)  # Operands of the current instructions
    )
engine.run() # Compute the power consumption of all these points
power = engine.power # Numpy 1D array with an entry for each previous point
engine.reset_points() # Reset the engine to study other points
```

## Limitations

Since the [ELMO project](https://github.com/sca-research/ELMO) takes its inputs and outputs from files, _Python-ELMO_ **can not** manage simultaneous runs.

## Licences

[MIT](LICENCE.txt)
