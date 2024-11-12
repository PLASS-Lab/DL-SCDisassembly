import os

### Configuration of the module

TEMPLATE_REPOSITORY = 'templates'
PROJECTS_REPOSITORY = 'projects'
ELMO_TOOL_REPOSITORY = 'elmo-tool'
ELMO_EXECUTABLE_NAME = 'elmo'
ELMO_OUTPUT_ENCODING = 'latin-1'
ELMO_INPUT_FILE_NAME = 'input.txt'

MODULE_PATH = os.path.dirname(os.path.abspath(__file__))

SEARCH_EXCLUSION_TAG = 'EXCLUDE-FROM-SIMULATION-SEARCH'

# ELMO Server
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 5000 