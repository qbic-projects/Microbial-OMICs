#!/usr/bin/env python3
#
#   Author: Jannik Seidel
#   E-mail: jannik.seidel@qbic.uni-tuebingen.de
#   Date:   16.02.2024
#
#   To load the ontologies and extract controlled
#   vocabularies for the metadata schemes of the
#   DZIF microbial OMICs database from them use 
#   this script.
#
##################################################
from .ontoDownloader import main as ontoDownloader
import sys
import glob
import os
import pandas as pd
import rdflib
import networkx as nx
import re
import argparse as arg
import errno
import shutil


def handlePandasDfRor(dataFrame: pd.DataFrame, termsToKeep: list) -> list:
    DataFrameToKeep = dataFrame[termsToKeep].sort_values("name")
    pandasToYAMLList = []
    for ind,row in DataFrameToKeep.iterrows():
        if "\'" in row["name"] and "\"" in row["name"]:
            newKey = row["name"].replace("\"","")
            pandasToYAMLList.append("      \"" + newKey + ", " + row["id"] + "\" :\n")
            pandasToYAMLList.append("        text: \"" + newKey + ", " + row["id"] + "\"\n")
            pandasToYAMLList.append("        meaning: \"" + row["id"] + "\"\n")
        elif "\"" in row["name"]:

            pandasToYAMLList.append("      \'" + row["name"] + ", " + row["id"] + "\' :\n")
            pandasToYAMLList.append("        text: \'" + row["name"]  +  ", " + row["id"] + "\'\n")
            pandasToYAMLList.append("        meaning: \"" + row["id"] + "\"\n")
        elif "\'" in row["name"]:
            pandasToYAMLList.append("      \"" + row["name"] + ", " + row["id"] + "\" :\n")
            pandasToYAMLList.append("        text: \"" + row["name"]  + ", " + row["id"] + "\"\n")
            pandasToYAMLList.append("        meaning: \"" + row["id"] + "\"\n")
        else:
            newKey = row["name"].replace("\\","/")
            pandasToYAMLList.append("      \"" + newKey + ", " + row["id"] + "\" :\n")
            pandasToYAMLList.append("        text: \"" + newKey  + ", " + row["id"] + "\"\n")
            pandasToYAMLList.append("        meaning: \"" + row["id"] + "\"\n")

    return pandasToYAMLList

def handleOntologyDictToYAMLList(dictionary: dict) -> list:
    dictionaryToYAMLList = []
    for key in dictionary.keys():
        if "      \"" + dictionary[key]["label"] + "\" :\n" in dictionaryToYAMLList:
            continue
        dictionaryToYAMLList.append("      \"" + dictionary[key]["label"] + "\" :\n")
        dictionaryToYAMLList.append("        text: \"" + dictionary[key]["label"]  + "\"\n")
        dictionaryToYAMLList.append("        meaning: \"" + dictionary[key]["id"] + "\"\n")
    return dictionaryToYAMLList

def getPrefixesOwl(dictionary: dict) -> dict:
    prefixes = set()
    prefixDictionary = dict()
    for key in dictionary.keys():
        processedKey = key.split("/")[-1].split("_")[0]
        prefixes.update([processedKey])
    for key in dictionary.keys():
        processedKey = key.split("/")[-1].split("_")[0]
        if processedKey in prefixes:
            prefixDictionary[processedKey] = key.split("_")[0] +"_"
            prefixes.remove(processedKey)
        else:
            continue
    return prefixDictionary

def getNodeByName(graph,name):
    for node in graph.nodes():
        if name == str(node):
            return node
    return None

def insertYamlListByTerm(yamlList: list, termToReplace: str, pathToSchemes: str, pathToFinalSchemes: str, nameOfSchemesFile: str):
    if os.path.exists(pathToFinalSchemes) == False:
        os.mkdir(pathToFinalSchemes)
        
    pathOld = pathToSchemes + os.sep + nameOfSchemesFile
    pathNew = pathToFinalSchemes + os.sep + nameOfSchemesFile
    if os.path.isfile(pathNew) == False:
        file = open(pathOld, "r")
        fileRead = file.readlines()
        file.close()
        if termToReplace in fileRead:
            index = fileRead.index(termToReplace)
            listOut = fileRead[:index] + yamlList + fileRead[index+1:]
            with open(pathNew,"w") as outfile:
                for entry in listOut:
                    outfile.write(entry)
    else:
        file = open(pathNew, "r")
        fileRead = file.readlines()
        file.close()
        if termToReplace in fileRead:
            index = fileRead.index(termToReplace)
            listOut = fileRead[:index] + yamlList + fileRead[index+1:]
            with open(pathNew,"w") as outfile:
                for entry in listOut:
                    outfile.write(entry)

def prefixDictToYamlList(prefixDict: dict) -> list:
    yamlList = []
    for key in prefixDict.keys():
        newLine = "  " + key + ": " + prefixDict[key] + "\n"
        yamlList.append(newLine)
    yamlList.sort()
    return yamlList

def main(nameOfRepository: str):
    '''
    Provide the name of the parent folder of src/ to this function to run the 
    download of the ontologies used for the controlled vocabularies in the 
    metadata schemes and insert them into the schemes. 
    '''
    configYAML = ontoDownloader(nameOfRepository)
    pathToOntologies = configYAML["config"]["environment"]["path_for_ontologies"]
    getCurrentWorkingDirectory = os.getcwd()
    print("Started to enter the controlled vocabularies into metadata scheme.\n")
    if not nameOfRepository in getCurrentWorkingDirectory:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), nameOfRepository)
    else:
        pathToParent = getCurrentWorkingDirectory.split(nameOfRepository)[0]
        pathToWorkingDirectory = pathToParent + nameOfRepository + os.sep
    os.chdir(pathToWorkingDirectory + pathToOntologies)
    ontologies = configYAML["config"]["ontologies"]
    prefixDictionary = dict()

    # clean environment if script was already executed before
    pathToFinalSchemes = configYAML["config"]["environment"]["path_for_final_schemes"]
    if os.path.exists(pathToFinalSchemes):
        shutil.rmtree(pathToFinalSchemes)

    # run the insertion of controlled vocabularies into the schemes
    for key in ontologies.keys():
        lowerKey = key.lower()
        if ontologies[key]["format"]["file_suffix"] == "owl":
            # processing of the owl graph
            filePath = lowerKey + "." + ontologies[key]["format"]["file_suffix"]
            # parsing to networkx graph
            ontology = rdflib.Graph().parse(filePath, format="xml")
            G = nx.DiGraph()
            for subj, pred, obj in ontology:    
                if ('oboInOwl#id' in pred or 'rdf-schema#label' in pred or "rdf-schema#subClassOf" in pred) and ("http://purl.obolibrary.org/obo/" in subj or "http://purl.obolibrary.org/obo/" in obj):
                    G.add_edge(subj, obj, predicate=pred)
            # removing unnecessary nodes
            nodesToRemove = []
            for node in G.nodes():
                pattern = r"^N.{32}$"
                if bool(re.match(pattern,node)):
                    nodesToRemove.append(node)
            for node in nodesToRemove:
                G.remove_node(node)

            # extracting subgraphs for a specific controlled vocabulary and inserting it into the schemes
            for entry in ontologies[key]["enum"]:
                descendingFromNode = getNodeByName(G,ontologies[key]["enum"][entry]["descending_from"])
                graphNodesPointingTowardsDescendingFromNode = nx.ancestors(G,descendingFromNode)
                finalGraphNodes = set()
                for node in graphNodesPointingTowardsDescendingFromNode:
                    finalGraphNodes.update([node])
                    finalGraphNodes.update(G.predecessors(node))
                    finalGraphNodes.update(G.successors(node))
                insertionDictionary = {}
                for node in finalGraphNodes:
                    allConnectedNodesOfNode = nx.all_neighbors(G,node)
                    for connectedNode in allConnectedNodesOfNode:
                        edgeData = G.get_edge_data(node,connectedNode)
                        if edgeData != None:
                            if str(node) not in insertionDictionary.keys():
                                insertionDictionary[str(node)] = {}
                                insertionDictionary[str(node)].update({"id":str(node).split("/")[-1].replace("_",":")})
                            if "#label" in edgeData["predicate"]:
                                insertionDictionary[str(node)].update({"label":str(connectedNode)})
                sortedInsertionDictionary = dict(sorted(insertionDictionary.items(), key=lambda item: item[1]["label"]))
                del sortedInsertionDictionary[str(descendingFromNode)]
                yamlList = handleOntologyDictToYAMLList(sortedInsertionDictionary)

                # generation of prefix list for prefixes at the top of the linkML schemes
                prefixesLocal = getPrefixesOwl(sortedInsertionDictionary)
                for prefixKey in prefixesLocal.keys():
                    if prefixKey not in prefixDictionary.keys():
                        prefixDictionary[prefixKey] = prefixesLocal[prefixKey]
                os.chdir(pathToWorkingDirectory)
                insertYamlListByTerm(yamlList,ontologies[key]["enum"][entry]["term_to_replace"],configYAML["config"]["environment"]["path_for_schemes"],configYAML["config"]["environment"]["path_for_final_schemes"],configYAML["config"]["environment"]["name_of_schemes_file"])
                os.chdir(pathToWorkingDirectory + pathToOntologies)

        elif ontologies[key]["format"]["file_suffix"] == "csv":
            fileList = glob.glob("*.csv")
            for entry in fileList:
                if lowerKey in entry:
                    df = pd.read_csv(entry)
                    if "coll_by_enum" in ontologies[key]["enum"]:
                        filteringColumn = ontologies[key]["enum"]["coll_by_enum"]["filtering_column"]
                        filteringTerm = ontologies[key]["enum"]["coll_by_enum"]["filtering_term"]
                        termsToInclude = ontologies[key]["enum"]["coll_by_enum"]["terms_to_include"]
                    else:
                        raise KeyError(key + " is not yet covered by ontoHandler.py")
                    dfFiltered = df[ 
                        df[
                            filteringColumn
                        ] 
                        == 
                        filteringTerm
                    ]
                    yamlList = handlePandasDfRor(dfFiltered, termsToInclude)
                    os.chdir(pathToWorkingDirectory)
                    insertYamlListByTerm(yamlList,ontologies[key]["enum"]["coll_by_enum"]["term_to_replace"],configYAML["config"]["environment"]["path_for_schemes"],configYAML["config"]["environment"]["path_for_final_schemes"],configYAML["config"]["environment"]["name_of_schemes_file"])
                    os.chdir(pathToWorkingDirectory + pathToOntologies)
    yamlList = prefixDictToYamlList(prefixDictionary)
    os.chdir(pathToWorkingDirectory)
    insertYamlListByTerm(yamlList,configYAML["config"]["prefixes_controlled_vocabularies"]["term_to_replace"],configYAML["config"]["environment"]["path_for_schemes"],configYAML["config"]["environment"]["path_for_final_schemes"],configYAML["config"]["environment"]["name_of_schemes_file"])
    os.chdir(pathToWorkingDirectory + pathToOntologies)
    print("Finished to enter the controlled vocabularies into scheme.\n\n")
if __name__ == '__main__':
    parser = arg.ArgumentParser(
        prog='DZIF microbial OMICs Database Ontology Handler',
        description='This piece of software creates the final metadata scheme in LinkML which can be used by the DZIFDataHarmonizer to collect and validate Metadata.',
        epilog='Written by Jannik Seidel (jannik.seidel@qbic.uni-tuebingen.de) and released under MIT License.')
    parser.add_argument("--repo", required=True, help="name of the top-level folder of this software (in which the README.md is located)",type=str)
    args = parser.parse_args()
    sys.exit(main(nameOfRepository=args.repo))