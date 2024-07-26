#!/usr/bin/env python3
#
#   Author: Jannik Seidel
#   E-mail: jannik.seidel@qbic.uni-tuebingen.de
#   Date:   27.02.2024
#
#   This script can be used to build the DZIF
#   DataHarmonizer
#
##################################################

import argparse as arg
import DataHarmonizerDownloader.DataHarmonizerDownloader as DataHarmonizerDownloader
import errno
import os
import ontoHandler.ontoHandler as ontoHandler
import sys
import shutil
import subprocess

def main(nameOfRepository):
    print("Building of the DZIF DataHarmonizer has started.\n\n")
    getCurrentWorkingDirectory = os.getcwd()
    if not nameOfRepository in getCurrentWorkingDirectory:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), nameOfRepository)
    else:
        pathToParent = getCurrentWorkingDirectory.split(nameOfRepository)[0]
        pathToWorkingDirectory = pathToParent + nameOfRepository + os.sep
        os.chdir(pathToWorkingDirectory)
    print("Started to download and unpack the DataHarmonizer from github.\n")
    configYAML = DataHarmonizerDownloader.main(nameOfRepository)
    print("Finished.\n\n")
    ontoHandler.main(nameOfRepository)
    shutil.rmtree(pathToWorkingDirectory + os.sep + configYAML["config"]["environment"]["path_for_ontologies"])
    print("Started to build DZIF DataHarmonizer.\n")
    pathToScheme = pathToWorkingDirectory + os.sep + configYAML["config"]["environment"]["path_for_final_schemes"] + os.sep + "metaDZIF.yaml"
    pathToTemplate = pathToWorkingDirectory + os.sep + configYAML["config"]["environment"]["path_for_DataHarmonizer"] + os.sep + "web" + os.sep + "templates" + os.sep + "metaDZIF"
    if os.path.exists(pathToTemplate) == False:
        os.mkdir(pathToTemplate)
    pathToTemplateFile = pathToTemplate + os.sep + "metaDZIF.yaml"
    shutil.copy(pathToScheme,pathToTemplateFile)
    os.chdir(pathToTemplate)
    with open("export.js", "w") as outfile:
        outfile.write("// A dictionary of possible export formats\nexport default {};\n")
    runPath = ".." + os.sep + ".." + os.sep + ".." + os.sep + "script" + os.sep + "linkml.py"
    flags = ["-i", "metaDZIF.yaml"]
    command = ["python3", runPath] + flags
    subprocess.run(command)
    command = ["corepack","enable"]
    subprocess.run(command)
    command = "yarn"
    subprocess.run(command)
    command = ["yarn","build:web"]
    subprocess.run(command)
    pathToBuiltDataHarmonizerOld = pathToWorkingDirectory + os.sep + configYAML["config"]["environment"]["path_for_DataHarmonizer"] + os.sep + "web" + os.sep + "dist"
    pathToBuiltDataHarmonizerNew = pathToWorkingDirectory + os.sep + "DZIFDataHarmonizer"
    if os.path.exists(pathToBuiltDataHarmonizerNew):
        shutil.rmtree(pathToBuiltDataHarmonizerNew)
    shutil.move(pathToBuiltDataHarmonizerOld,pathToBuiltDataHarmonizerNew)
    pathToDataHarmonizer = pathToWorkingDirectory + os.sep + configYAML["config"]["environment"]["path_for_DataHarmonizer"]
    shutil.rmtree(pathToDataHarmonizer)
    print("\nFinished to build DZIF DataHarmonizer.\n\n  It is located in the 'DZIFDataHarmonizer' folder\n\n  Goodbye!\n")

if __name__ == "__main__":
    parser = arg.ArgumentParser(
        prog='DZIF microbial OMICs Database DataHarmonizer Downloader',
        description='This piece of software downloads the DataHarmonizer from the internet to be further used to build it with the schemes for the DZIF microbial OMICs Database.',
        epilog='Written by Jannik Seidel (jannik.seidel@qbic.uni-tuebingen.de) and released under MIT License.')
    parser.add_argument("--repo", required=True, help="name of the top-level folder of this software (in which the README.md is located)",type=str)
    args = parser.parse_args()
    sys.exit(main(nameOfRepository=args.repo))