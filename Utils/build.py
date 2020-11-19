import argparse
from os import getcwd, mkdir
from os.path import join
import subprocess
import json


def loadFilesList():
    with open('./Utils/filesList.json') as file:
        filesList = file.read()

    return json.loads(filesList) 


def buildFiles(prefix, files, outDir):
    for file in files:
        buildFile(prefix, file, outDir)


def buildFile(prefix, file, outDir):
    jobname = "-jobname=" + file['name']
    sourceFile = "main.tex"

    buildCmd = ["docker", "run", "-i", "-v", getcwd() + ":/data", "-w", join('/data', prefix, file['path']), 
                "blang/latex", "latexmk", "-pdf", jobname, sourceFile]
    
    moveCmd = ["mv", join(getcwd(), prefix, file['path'], file['name'] + ".pdf"),
                join(getcwd(), outDir, file['name'] + ".pdf")]

    subprocess.run(buildCmd)
    subprocess.run(moveCmd)


def getArgs():
    # Parsing arguments (i.e. output folder)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "outDir", help="directory where the output will be stored")
    return parser.parse_args()


def main():
    args = getArgs()
    files = loadFilesList()

    # Create output dir
    mkdir(args.outDir)

    # Create output dir for internal documents
    prefix = "DocumentiInterni"
    internalOutDir = join(args.outDir, prefix)
    mkdir(internalOutDir)

    # Build internal documents
    buildFiles(prefix, files[prefix], internalOutDir)


    # Create output dir for external documents
    prefix = "DocumentiEsterni"
    externalOutDir = join(args.outDir, prefix)
    mkdir(externalOutDir)

    # Build external documents
    buildFiles(prefix, files[prefix], externalOutDir)


    # Create output dir for internal minutes
    prefix = "DocumentiInterni/Verbali"
    internalMinutesOutDir = join(args.outDir, prefix)
    mkdir(internalMinutesOutDir)

    # Build internal minutes
    buildFiles(prefix, files["VerbaliInterni"], internalMinutesOutDir)

    # Create output dir for external minutes
    prefix = "DocumentiEsterni/Verbali"
    externalMinutesOutDir = join(args.outDir, prefix)
    mkdir(externalMinutesOutDir)

    # Build internal minutes
    buildFiles(prefix, files["VerbaliEsterni"], externalMinutesOutDir)

if __name__ == '__main__':
    main()
