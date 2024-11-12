import setuptools
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from subprocess import check_call
import os, shutil
import re


### CONFIGURATION
PELMO_SOURCE = 'https://github.com/ThFeneuil/python-elmo'
ELMO_MODULE_NAME = 'elmo'
ELMO_SOURCE = 'https://github.com/sca-research/ELMO.git'

# Import configuration of ELMO_MODULE,
#  cannot use 'import elmo' because it can be ambiguous which module it will call
with open(os.path.join(ELMO_MODULE_NAME, 'confg.py')) as _file:
    globals = {'__file__': os.path.join(
        os.path.abspath(ELMO_MODULE_NAME),
        'config.py'
    )}
    exec(_file.read(), globals)
    ELMO_TOOL_REPOSITORY = globals['ELMO_TOOL_REPOSITORY']
    ELMO_INPUT_FILE_NAME = globals['ELMO_INPUT_FILE_NAME']


def install_elmo_tool(elmo_complete_path):
    ## Download the tool
    elmo_download_command = "git clone --depth=1 --branch=master {url} {elmo_path}".format(
        url=ELMO_SOURCE,
        elmo_path=elmo_complete_path,
    )
    check_call(elmo_download_command.split())
    shutil.rmtree(os.path.join(elmo_complete_path, '.git'))
    # 'test' contains a Python2 test, and it raises an error during byte-compiling
    shutil.rmtree(os.path.join(elmo_complete_path, 'test'))

    ## Setup the tool
    elmodefines_h = None
    elmodefines_h_path = os.path.join(elmo_complete_path, 'elmodefines.h')
    with open(elmodefines_h_path, 'r') as _file:
        elmodefines_lines = _file.readlines()
        for i, line in enumerate(elmodefines_lines):
            if re.match(r'\s*#define\s+DATAFILEPATH', line):
                elmodefines_lines[i] = '#define DATAFILEPATH "{}"'.format(ELMO_INPUT_FILE_NAME)
        elmodefines_h = ''.join(elmodefines_lines)
    with open(elmodefines_h_path, 'w') as _file:
        _file.write(elmodefines_h)

    # Compile the tool
    check_call("make clean".split(), cwd=elmo_complete_path)
    check_call("make".split(), cwd=elmo_complete_path)


class PostBuildCommand(build_py):
    """ Build Command to add the ELMO installation """
    def run(self):
        build_py.run(self)

        # ELMO Installation
        elmo_complete_path = os.path.join(
            self.build_lib,
            ELMO_MODULE_NAME,
            ELMO_TOOL_REPOSITORY,
        )
        shutil.rmtree(elmo_complete_path, ignore_errors=True)
        install_elmo_tool(elmo_complete_path)


if __name__ == '__main__':
    with open("README.md", "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="python-elmo",
        version="0.1.0",
        author="Thibauld Feneuil",
        author_email="thibauld.feneuil@cryptoexperts.com",
        description="A Python encapsulation of a statistical leakage simulator for the ARM M0 family",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url=PELMO_SOURCE,
        project_urls={
            "ELMO Source": ELMO_SOURCE,
        },
        packages=setuptools.find_packages(),
        keywords="python3 crypto",
        classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS",
            "Operating System :: POSIX :: Linux",
            "Topic :: Scientific/Engineering",
            "Topic :: Security :: Cryptography",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        python_requires=">=3.5",
        cmdclass={
            "build_py": PostBuildCommand,
        },
        install_requires=["numpy"],
        include_package_data=True,
    )
