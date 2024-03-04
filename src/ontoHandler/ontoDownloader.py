#!/usr/bin/env python3
#
#   Author: Jannik Seidel
#   E-mail: jannik.seidel@qbic.uni-tuebingen.de
#   Date:   15.02.2024
#
#   To download the necessary ontologies to build
#   the metadata schemas for the DZIF microbial 
#   OMICs database run this script
#
##################################################
import yaml
import requests
import os
import errno
import zipfile
import sys
import argparse as arg


def createFolder(pathToOntologiesFolder: str):
    if not os.path.exists(pathToOntologiesFolder):
        os.makedirs(pathToOntologiesFolder)

def downloadOntology(pathToOntologiesFolder: str, ontologyURL: str) -> str:
    fileName = ontologyURL.split("/")[-1]
    filePath = pathToOntologiesFolder + os.sep + fileName
    createFolder(pathToOntologiesFolder)
    if not os.path.isfile(filePath):
        with requests.get(ontologyURL,stream=True) as streamOfOntology:
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

def main(nameOfRepository: str):
    getCurrentWorkingDirectory = os.getcwd()
    if not nameOfRepository in getCurrentWorkingDirectory:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), nameOfRepository)
    else:
        pathToParent = getCurrentWorkingDirectory.split(nameOfRepository)[0]
        pathToWorkingDirectory = pathToParent + nameOfRepository + os.sep
        pathToConfig = "config" + os.sep + "config.yaml"

    os.chdir(pathToWorkingDirectory)
    configYAML = loadConfigYAML(pathToConfig)
    pathToOntologies = configYAML["config"]["environment"]["path_for_ontologies"]
    ontologies = configYAML["config"]["ontologies"]
    print("Started to download ontologies.\n\n")
    for key in ontologies.keys():
        print(f"Started to download {key} ontology.\n")
        ontologyPath = downloadOntology(pathToOntologies,ontologies[key]["URL"])
        if ontologies[key]["format"]["zipped"]:
            with zipfile.ZipFile(ontologyPath, "r") as zippedOntology:
                zippedOntology.extractall(pathToOntologies)
        print(f"Finished to download {key} ontology.\n\n")
    print("Finished to download ontologies.\n\n")
    return configYAML

if __name__ == '__main__':
    parser = arg.ArgumentParser(
        prog='DZIF microbial OMICs Database Ontology Downloader',
        description='This piece of software downloads the ontologies used by the DZIF microbial OMICs database metadata schemes.',
        epilog='Written by Jannik Seidel (jannik.seidel@qbic.uni-tuebingen.de) and released under MIT License.')
    parser.add_argument("--repo", required=True, help="name of the top-level folder of this software (in which the README.md is located)",type=str)
    args = parser.parse_args()
    sys.exit(main(nameOfRepository=args.repo))