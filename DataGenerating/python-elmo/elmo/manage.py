import os, shutil
import re
import inspect
import subprocess
import sys
from os.path import join as pjoin

from .config import (
    TEMPLATE_REPOSITORY,
    PROJECTS_REPOSITORY,
    ELMO_TOOL_REPOSITORY,
    ELMO_EXECUTABLE_NAME,
    MODULE_PATH,
    ELMO_OUTPUT_ENCODING,
    SEARCH_EXCLUSION_TAG,
)
from .project_base import SimulationProject
from .utils import Color

############   GETTERS   ############

def search_simulations_in_repository(repository, criteria=lambda x:True):
    """ Search simulation classes in the 'repository' verifying the 'criteria'
    Return a list of 'SimulationProject' subclasses
    :repository: Repository of the searched simulation classes (string)
    :criteria: Boolean function with 'SimulationProject' subclasses for input
    """

    projects = {}
    
    from .utils import write
    for root, repositories, files in os.walk(repository):
        for filename in files:
            if re.fullmatch(r'.*project.*\.py', filename):
                complete_filename = pjoin(root, filename)

                # Encapsulate the project
                globals = {
                    #'__builtins__': {'__build_class__': __build_class__},
                    'SimulationProject': SimulationProject,
                    'write': write,
                }
                locals = {}
                
                # Read the project code
                with open(complete_filename, 'r') as _file:
                    project = ''.join(_file.read())
                    if ('SimulationProject' not in project) or (SEARCH_EXCLUSION_TAG in project):
                        continue # Exclude this file
                    exec(project, globals, locals)
                
                # Extract the simulations
                for key, obj in locals.items():
                    if inspect.isclass(obj) and issubclass(obj, SimulationProject):
                        if criteria(obj):
                            if key in projects:
                                print(Color.WARNING + \
                                    'Warning! Many simulations with the same name. ' + \
                                    'Simulation ignored: {} in {}'.format(
                                        key, complete_filename[len(repository)+1:]) + \
                                    Color.ENDC
                                )
                            else:
                                obj.set_project_directory(os.path.abspath(root))
                                projects[key] = obj
    
    return projects

def search_simulations_in_module(criteria=lambda x:True):
    """ Search simulation classes among the module projects verifying the 'criteria'
    Return a list of 'SimulationProject' subclasses
    :criteria: Boolean function with 'SimulationProject' subclasses for input
    """
    projects_path = pjoin(MODULE_PATH, PROJECTS_REPOSITORY)
    return search_simulations_in_repository(projects_path, criteria)

def search_simulations(repository='.', criteria=lambda x:True):
    """ Search simulation classes in the 'repository' and among
    the module projects verifying the 'criteria'
    Return a list of 'SimulationProject' subclasses
    :repository: Repository of the searched simulation classes (string)
    :criteria: Boolean function with 'SimulationProject' subclasses for input
    """
    projects = search_simulations_in_repository(repository, criteria)

    module_projects = search_simulations_in_module(criteria)
    for key, project in module_projects.items():
        if key not in projects:
            projects[key] = project

    return projects

class SimulationNotFoundError(Exception):
    pass
    
class TooManySimulationsError(Exception):
    pass
    
def get_simulation(classname=None, repository='.'):
    """ Get a simulation class in the 'repository' with the specific 'classname'
    Return a subclass of 'SimulationProject' class
    :classname: Name of the searched simulation class (string, optional)
    :repository: Repository of the searched simulation class (string, optional)
    """
    criteria = lambda x: True
    if classname is not None:
        criteria = lambda x: x.__name__ == classname.strip()    
    projects = search_simulations(repository, criteria)
    
    if len(projects) == 1:
        return list(projects.values())[0]
    elif len(projects) < 1:
        raise SimulationNotFoundError()
    else:
        raise TooManySimulationsError()


############   SETTERS   ############

def create_simulation(repository, classname, is_a_module_project=False):
    """ Create a Simulation Project.
    It builds a repository with the standard content for the project.
    Return the absolute path of the created repository
    :repository: Name of repository which will be created (string)
    :classname: Name of the Python class to manage the project (string)
    :is_a_module_project: If True and :repository: is a relative path,
        create the project among the module projects.
    """
    
    # Update the repository, if necessary
    if is_a_module_project and (not os.path.isabs(repository)):
        repository = pjoin(
            MODULE_PATH,
            PROJECTS_REPOSITORY,
            repository,
        )
    
    # Build the project repository
    try:
        os.makedirs(repository, exist_ok=False)
    except FileExistsError as err:
        raise FileExistsError('Error, a project with this repository already exists!') from err
    
    elmo_path = pjoin(MODULE_PATH, ELMO_TOOL_REPOSITORY)
    template_path = pjoin(MODULE_PATH, TEMPLATE_REPOSITORY)
    project_path = repository

    # Add standard content in the project
    files_from_ELMO = [
        pjoin('Examples', 'elmoasmfunctions.o'),
        pjoin('Examples', 'elmoasmfunctions.s'),
        pjoin('Examples', 'elmoasmfunctionsdef.h'),
        pjoin('Examples', 'DPATraces', 'MBedAES', 'vector.o'),
    ]
    files_from_templates = [
        'elmoasmfunctionsdef-extension.h',
        'Makefile',
        'project.c'
    ]

    for filename in files_from_ELMO:
        shutil.copy(pjoin(elmo_path, filename), project_path)
    for filename in files_from_templates:
        shutil.copy(pjoin(template_path, filename), project_path)
    shutil.copy(
        pjoin(elmo_path, 'Examples', 'DPATraces', 'MBedAES', 'MBedAES.ld'),
        pjoin(project_path, 'project.ld')
    )

    # Create the project class
    with open(pjoin(template_path, 'projectclass.txt')) as _source:
        code = ''.join(_source.readlines())
        code = code.replace('{{PROJECTCLASSNAME}}', classname)
        with open(pjoin(project_path, 'projectclass.py'), 'w') as _dest:
            _dest.write(code)
    
    # Return the path of the created repository
    return os.path.abspath(project_path)


############   USAGE FUNCTIONS   ############

class DontFindBinaryError(Exception):
    pass

def execute_simulation(project):
    """ Execute a simulation of the power leakage using ELMO tool
    Return the output and the errors of the execution of ELMO tool
    :project: Subclass of 'SimulationProject' defining all the parameters of the simulation
    """
    elmo_path = pjoin(MODULE_PATH, ELMO_TOOL_REPOSITORY)
    
    # Some checking before executing
    if not isinstance(project, SimulationProject):
        raise TypeError('The project is not an instance of \'SimulationProject\' class.')
    
    leaking_binary_path = project.get_binary_path()
    if not os.path.isabs(leaking_binary_path):
        leaking_binary_path = pjoin(project.get_project_directory(), project.get_binary_path())
    if not os.path.isfile(leaking_binary_path):
        raise BinaryNotFoundError('Binary not found. Did you compile your project?')
    
    if not os.path.isfile(pjoin(elmo_path, ELMO_EXECUTABLE_NAME)):
        raise Exception('Installation Error: the executable of the ELMO tool is not found.')
    
    # Launch generation of the traces by launching ELMO
    command = '{} "{}"'.format(
        pjoin('.', ELMO_EXECUTABLE_NAME),
        leaking_binary_path,
    )
    process = subprocess.Popen(command, shell=True,
        cwd=elmo_path, executable='/bin/bash',
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    
    # Follow the generation
    output, error = b'', b''
    num_trace = 0
    while True:
        output_line = process.stdout.readline()
        error_line = process.stderr.readline()
        if (not output_line) and (not error_line) and (process.poll() is not None):
            break
        if  error_line:
            error += error_line
        if output_line:
            output += output_line
            if 'TRACE NO' in output_line.decode(ELMO_OUTPUT_ENCODING):
                num_trace += 1
    return_code = process.poll()
    
    # Treat data
    output = output.decode(ELMO_OUTPUT_ENCODING) if output else None
    error = error.decode(ELMO_OUTPUT_ENCODING) if error else None
    
    nb_traces = None
    nb_instructions = None

    if output:
        nb_traces = output.count('TRACE NO')
        nb_instructions_pattern = re.compile(r'\s*instructions/cy..es\s+(\d+)\s*')
        for line in output.split('\n'):
            res = nb_instructions_pattern.fullmatch(line)
            if res:
                nb_instructions = res.group(1)

    # Return results
    return {
        'nb_traces': nb_traces,
        'nb_instructions': nb_instructions,
        'output': output,
        'error': error,
    }
    