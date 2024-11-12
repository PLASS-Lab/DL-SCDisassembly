import os, shutil
from subprocess import check_call

### Install ELMO
from elmo.config import ELMO_TOOL_REPOSITORY
ELMO_SOURCE = 'https://github.com/sca-research/ELMO.git'
elmo_complete_path = os.path.join('elmo', ELMO_TOOL_REPOSITORY)
if not os.path.isdir(elmo_complete_path):
    from setup import install_elmo_tool
    install_elmo_tool(elmo_complete_path)

def print_success(text):
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'
    print(OKGREEN+text+ENDC)

#########################################################
#           TEST 1 : MANAGE A FRESH SIMULATION          #
#########################################################

foldername = 'test-project'
classname = 'TestSimu'

### Create Simulation
from elmo.manage import create_simulation
shutil.rmtree('test-project', ignore_errors=True) # Clean before
create_simulation(foldername, classname)

assert os.path.isdir(foldername), 'Folder not created'

### List Available Simulations
from elmo.manage import search_simulations
simulations = search_simulations(foldername)

assert classname in simulations, 'Test Simulation not found'

### Use a Simulation
from elmo.manage import get_simulation
simu = get_simulation(classname, foldername)

shutil.rmtree(foldername)
print_success(' - Test 1 "Manage A Fresh Simulation": Success!')

#########################################################
#               TEST 2 : USE ELMO ENGINE                #
#########################################################

### Use the ELMO Engine
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

assert power.shape == (256, )

print_success(' - Test 2 "Use ELMO Engine": Success!')

#########################################################
#            TEST 3 : USE A REAL SIMULATION             #
#########################################################

from elmo import get_simulation
KyberNTTSimulation = get_simulation('KyberNTTSimulation')
simulation = KyberNTTSimulation()
simulation.set_challenges(simulation.get_random_challenges(10))
res = simulation.run()

assert not res['error']
assert res['nb_traces'] == 10
assert res['nb_instructions']

# Test the methods for analysis
multiplication_indexes = simulation.get_indexes_of(lambda instr: 'mul' in instr)
asmtrace = simulation.get_asmtrace()
for index, instr in enumerate(asmtrace):
    assert ('mul' in instr) == (index in multiplication_indexes)

traces = simulation.get_traces()
traces = simulation.get_traces(multiplication_indexes)
assert traces.shape == (10, len(multiplication_indexes))
print(traces)
printed_data = simulation.get_printed_data()

print_success(' - Test 3 "Use A Real Simulation": Success!')

#########################################################
#          TEST 4 : USE ELMO BY RUNNING ONLINE          #
#########################################################

def test_online_server():
    from elmo import get_simulation
    KyberNTTSimulation = get_simulation('KyberNTTSimulation')
    simulation = KyberNTTSimulation()
    simulation.set_challenges(simulation.get_random_challenges(10))
    return simulation.run_online()

from elmo.executor import launch_executor
# Launch the server and realize the test
res = launch_executor(waiting_function=test_online_server)

assert not res['error']
assert res['nb_traces'] == 10
assert res['nb_instructions']

print_success(' - Test 4 "Use ELMO By Running Online": Success!')

#########################################################

print_success('All seems fine!')