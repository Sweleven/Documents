#!/usr/bin/env python3

from os import listdir, getcwd, mkdir, remove
from os.path import isdir, isfile, join, splitext
import subprocess
from subprocess import check_output
from shutil import move
from PyPDF2 import PdfFileMerger
import re
import argparse

_excluded_dirs = [
    "Utils",
    "venv",
    ".git",
    ".github",
    "output"
    ]

def getDirs(path='.', excluded_dirs=_excluded_dirs):
    '''
        Returns all directories (even nested ones) existing in `path` excluding `excluded_dirs`
    '''
    
    dirs = []
    for dir in listdir(path):
        if dir in excluded_dirs:
            continue

        dir = join(path, dir)
        if isdir(dir):
            dirs.append(dir)
            # Recursive call for nested folders
            dirs = dirs + getDirs(dir, excluded_dirs)

    return dirs


def buildDirs(dirs):
    '''
        Builds all dirs from `dirs`
    '''

    for dir in dirs:
        buildDir(dir)


def buildDir(dir):
    '''
        Builds `*.tex` files in `dir` which are not recognized by the regex `/\.\w+/gm`
    '''

    files = [f for f in listdir(dir) if isfile(join(dir, f))]
    for file in files:
        filename, file_extension = splitext(file)
        
        if file_extension == '.tex' and not re.search("\.\w+", filename):
            buildFile(filename, dir)


def buildFile(file, dir):
    '''
        Builds `file`.tex file generating `file`.pdf output
    '''

    jobname = "-jobname=" + file
    file = file + '.tex'
    buildCmd = ["docker", "run", "-i", "-v", getcwd() + dir[1:] + ":/data", "blang/latex", "latexmk", "-pdf", jobname, file]
    subprocess.run(buildCmd)


def groupPdfs(dirs, outputDir):
    '''
        Groups all `.pdf` files found in all `dirs` elements into `outputDir`
    '''

    mkdir(outputDir)

    for dir in dirs:
        _outputDir = join(outputDir, dir)
        mkdir(_outputDir)
        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        for file in files:
            filename, file_extension = splitext(file)
            if file_extension == '.pdf':
                move(join(dir, file), join(_outputDir, file))
    

def getArgs():
    # Parsing arguments (i.e. output folder)
    parser = argparse.ArgumentParser()
    parser.add_argument("outDir", help="directory where the output will be stored")
    return parser.parse_args()


def main():
    args = getArgs()
    dirs = getDirs()

    buildDirs(dirs)
    
    groupPdfs(dirs, join('.', args.outDir))


if __name__ == '__main__':
    main()
