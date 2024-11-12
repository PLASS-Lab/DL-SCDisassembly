import sys
from .utils import Color

if len(sys.argv) <= 1:
    print(Color.FAIL + 'Please enter an instruction.' + Color.ENDC)
    exit()

command = sys.argv[1]

if command == 'create-simulation':
    import os, shutil
    import re

    print('Creation of a new simulation project...')

    ### Create the repository of the projects
    global_path = 'projects'
    os.makedirs(global_path, exist_ok=True)

    ### Get the project classname
    project_classname = ''
    search = re.compile(r'[^a-zA-Z0-9_]').search
    while not project_classname:
        classname = input(' - What is the project classname? ')
        if search(classname):
            print('   > Illegal characters detected! Please enter a name with only the following characters : a-z, A-Z, 0-9, and "_".')
        else:
            project_classname = classname.strip()

    ### Get and create the project repository
    search = re.compile(r'[^a-zA-Z0-9.-_/]').search
    project_repository = ''
    while not project_repository:
        repository = input(' - What is the project repository? ')
        if search(repository):
            print('Illegal characters detected! Please enter a name with only the following characters : a-z, A-Z, 0-9, ".", "-", "_" and "/".')
        else:
            project_repository = repository
    project_path = global_path+'/'+repository

    from .manage import create_simulation
    project_path = create_simulation(project_path, classname)

    print('')
    print('Creation complete !')
    print(' - Project repository: {}'.format(project_path))
    print(' - Project class "{}" in {}'.format(project_classname, project_path+'/projectclass.py'))
    print(' - Linker script: {}'.format(project_path+'/project.ld'))
    print('')
    print('Please don\'t to compile the project with the present Makefile before using it!')
    exit()

if command == 'run-server':
    from .executor import launch_executor
    from .config import DEFAULT_HOST, DEFAULT_PORT
    
    host = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_HOST
    port = int(sys.argv[3]) if len(sys.argv) >= 4 else DEFAULT_PORT

    launch_executor(host, port)
    exit()
    
print(Color.FAIL + 'Unknown Command.' + Color.ENDC)
exit()
