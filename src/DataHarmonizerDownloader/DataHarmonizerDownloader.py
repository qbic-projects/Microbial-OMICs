#!/usr/bin/env python3
#
#   Author: Jannik Seidel
#   E-mail: jannik.seidel@qbic.uni-tuebingen.de
#   Date:   26.02.2024
#
#   This script can be used to download the DZIF
#   DataHarmonizer for the DZIF microbial OMICs 
#   database from github
#
##################################################
import yaml
import sys
import os
import requests
import argparse as arg
import errno
import zipfile
import re

def downloadDataHarmonizer(pathToDataHarmonizerFolder: str, dataHarmonizerURL: str) -> str:
    fileName = dataHarmonizerURL.split("/")[-1]
    filePath = pathToDataHarmonizerFolder + os.sep + fileName
    if not os.path.isfile(filePath):
        with requests.get(dataHarmonizerURL,stream=True) as streamOfOntology:
            streamOfOntology.raise_for_status()
            with open(filePath, "wb") as file:
                for chunk in streamOfOntology.iter_content():
                    if chunk:
                        file.write(chunk)

    return filePath

def loadConfigYAML(pathToYAML: str) -> dict:
    with open(pathToYAML, "r") as file:
        yamlDict = yaml.safe_load(file)
    return yamlDict

def main(nameOfRepository: str) -> dict:
    getCurrentWorkingDirectory = os.getcwd()
    if not nameOfRepository in getCurrentWorkingDirectory:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), nameOfRepository)
    else:
        pathToParent = getCurrentWorkingDirectory.split(nameOfRepository)[0]
        pathToWorkingDirectory = pathToParent + nameOfRepository + os.sep
        os.chdir(pathToWorkingDirectory)
        pathToConfig = "config" + os.sep + "config.yaml"
    configYAML = loadConfigYAML(pathToConfig)
    
    pathToDataHarmonizer = configYAML["config"]["environment"]["path_for_DataHarmonizer"]
    if os.path.exists(pathToWorkingDirectory + pathToDataHarmonizer) == False:
        os.mkdir(pathToWorkingDirectory + pathToDataHarmonizer)
    os.chdir(pathToWorkingDirectory + pathToDataHarmonizer)
    filePath = downloadDataHarmonizer(pathToWorkingDirectory + pathToDataHarmonizer, configYAML["config"]["DataHarmonizerBuild"]["url_of_DataHarmonizer"])
    with zipfile.ZipFile(filePath, "r") as zippedDataHarmonizer:
        for file in zippedDataHarmonizer.infolist():
            pattern = ".+" + os.sep +".+"
            if bool(re.match(pattern, file.filename)):
                source = zippedDataHarmonizer.open(file.filename)
                target = os.path.join(os.getcwd(),file.filename.replace(patternToRemove, ""))
                if target.endswith(os.sep):
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as outfile:
                    outfile.write(source.read())
            else:
                patternToRemove = file.filename
    return configYAML

if __name__ == "__main__":
    parser = arg.ArgumentParser(
        prog='DZIF microbial OMICs Database DataHarmonizer Downloader',
        description='This piece of software downloads the DataHarmonizer from the internet to be further used to build it with the schemes for the DZIF microbial OMICs Database.',
        epilog='Written by Jannik Seidel (jannik.seidel@qbic.uni-tuebingen.de) and released under MIT License.')
    parser.add_argument("--repo", required=True, help="name of the top-level folder of this software (in which the README.md is located)",type=str)
    args = parser.parse_args()
    sys.exit(main(nameOfRepository=args.repo))