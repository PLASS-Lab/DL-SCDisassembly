import shutil
import os, re
import sys

from .server.servicethread import OneShotServiceThread

from .config import (
    MODULE_PATH,
    ELMO_TOOL_REPOSITORY,
    ELMO_INPUT_FILE_NAME,
    DEFAULT_HOST,
    DEFAULT_PORT,
)
from .project_base import SimulationProject
from .manage import execute_simulation

from .utils import Color

class Executor(OneShotServiceThread):
    def execute(self):
        """ Answer a request of simulation """
        # Get simulation data
        data = self.protocol.get_data()
        self.protocol.please_assert(data)
        
        elmo_path = os.path.join(MODULE_PATH, ELMO_TOOL_REPOSITORY)
        
        # Set the input of ELMO
        self.protocol.please_assert('input' in data)
        with open(os.path.join(elmo_path, ELMO_INPUT_FILE_NAME), 'w') as _input_file:
            _input_file.write(data['input'])
        self.protocol.send_ack()
        
        # Get the binary
        binary_content = self.protocol.get_file()
        binary_path = os.path.join(elmo_path, 'project.bin')
        with open(binary_path, 'wb') as _binary_file:
            _binary_file.write(binary_content)
        self.protocol.send_ack()
        
        
        ### Generate the traces by launching ELMO
        print(Color.OKGREEN + ' - Simulation accepted...' + Color.ENDC)
        simulation = SimulationProject()
        simulation.get_binary_path = lambda: os.path.abspath(binary_path)
        data = execute_simulation(simulation)
        
        if data['error']:
            print(Color.FAIL + ' - Simulation failed.' + Color.ENDC)
            self.protocol.send_data(results)
            self.protocol.close()
            return
            
        print(Color.OKGREEN + ' - Simulation finished: {} traces, {} instructions'.format(
            data['nb_traces'],
            data['nb_instructions'],
        ) + Color.ENDC)

        output_path = os.path.join(elmo_path, 'output')
        
        ### Get the trace
        data['results'] = []
        for i in range(data['nb_traces']):
            filename = os.path.join(output_path, 'traces', 'trace%05d.trc' % (i+1))
            with open(filename, 'r') as _file:
                data['results'].append(
                    list(map(float,  _file.readlines()))
                )
                
        ### Get asmtrace and printed data
        asmtrace = None
        if ('asmtrace' not in data) or data['asmtrace']:
            with open(os.path.join(output_path, 'asmoutput', 'asmtrace00001.txt'), 'r') as _file:
                data['asmtrace'] = _file.read()

        printed_data = None
        if ('printdata' not in data) or data['printdata']:
            with open(os.path.join(output_path, 'printdata.txt'), 'r') as _file:
                data['printed_data'] = list(map(lambda x: int(x, 16), _file.readlines()))

        ### Send results
        print(Color.OKCYAN + ' - Sending results...' + Color.ENDC, end='')
        sys.stdout.flush()
        self.protocol.send_data(data)
        print(Color.OKGREEN + ' Sent!' + Color.ENDC)
        self.protocol.close()


def launch_executor(host=DEFAULT_HOST, port=DEFAULT_PORT, waiting_function=True):
    """ Launch ELMO server on 'host' listening to the 'port' """
    from .server.servicethread import ListeningThread
        
    def do_main_program():
        thread = ListeningThread(host, port, Executor, debug=True)
        thread.start()
        return thread

    def program_cleanup(signum, frame):
        thread.stop()

    # Launch the listening server
    thread = do_main_program()
    
    # Give a way to stop the server
    import signal
    signal.signal(signal.SIGINT, program_cleanup)
    signal.signal(signal.SIGTERM, program_cleanup)
    
    # Do somthing during the execution of the server
    if waiting_function is True:
        import time
        while thread.is_running():
            time.sleep(1)
        return
    
    return_value = None
    if waiting_function:
        return_value = waiting_function()

    if thread.is_running():
        program_cleanup(None, None)    
    return return_value
