# -*- coding: utf-8 -*-

from jinja2 import Environment, FileSystemLoader
from os import listdir, getcwd, mkdir, remove, environ
from os.path import isdir, isfile, join, splitext
import argparse
import re
import sys
import hashlib


################# 
# Config values #
#################

templatesDir = 'Utils/templates'
_excluded_dirs = []
outFolder = './output'
file_loader = FileSystemLoader(templatesDir)
env = Environment(loader=file_loader)
repoName = 'testAtions'


def getDirs(path='.', excluded_dirs=_excluded_dirs, recursive=False):
    '''
        Returns all directories (even nested ones) existing in `path` excluding `excluded_dirs`
    '''
    
    dirs = []
    for dir in listdir(path):
        if dir in excluded_dirs:
            continue

        dirPath = join(path, dir)
        if isdir(dirPath):
            dirs.append({
                    "path": dirPath,
                    "name": dir
                })
            if recursive:
                # Recursive call for nested folders
                dirs = dirs + getDirs(dirPath, excluded_dirs)

    return dirs


def getAllDocuments(dir):
    '''
        Returns all `.pdf` files inside `dir` and it's nested folders
    '''

    allDirs = getDirs(dir, recursive=True)
    allDocuments = []
    for dir in allDirs:
        files = [f for f in listdir(dir['path']) if isfile(join(dir['path'], f))]
        for file in files:
            filename, file_extension = splitext(file)
            if file_extension == '.pdf':
                allDocuments.append({
                        "path": join(dir['path'], file),
                        "name": file
                    })
    
    return allDocuments


def buildTemplate(template, _options):
    '''
        Builds jinja2 template `template` using options `options`
    '''

    template = env.get_template(template)
    return template.render(options=_options)
    

def writeToFile(outPath, content):
    '''
        Writes `content` to `outPath`
    '''

    with open(outPath, 'w') as file_object:
        file_object.write(content)


def getArgs():
    # Parsing arguments (i.e. output folder)
    parser = argparse.ArgumentParser()
    parser.add_argument("currentBranch", help="name of the current branch")
    return parser.parse_args()


def buildAbsolutePaths(elements):
    return [ { "path": re.sub(outFolder, '/'+repoName, element['path']), "name": element['name'] } for element in elements]


def generateRandColor(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()[:6]


def main():
    args = getArgs()

    branchColor = generateRandColor(args.currentBranch)

    revisions = getDirs(join(outFolder, args.currentBranch))
    # making path absolute starting from ./output
    revisions_absolute = buildAbsolutePaths(revisions)


    branches = getDirs(outFolder)
    # making path absolute starting from ./output
    branches_absolute = buildAbsolutePaths(branches)

    # Generate branches list page for first page
    page = {
        "title": "Branches list",
        "description": "Questa pagina contiene tutte le revisioni. Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
    }
    template = buildTemplate('branchesList.j2',
                            {
                                "basename": repoName,
                                "page": page,
                                "branches": branches_absolute,
                                "elements": branches_absolute
                            })
    outPath = join(outFolder, 'index.html')
    writeToFile(outPath, template)


    # Generate revisions list page for current branch
    page = {
        "title": args.currentBranch + " - Revisions list",
        "description": "Questa pagina contiene tutte le revisioni di " + args.currentBranch + ". Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
    }
    template = buildTemplate('branchesList.j2', 
                            {
                                "basename": repoName,
                                "page": page,
                                "color": branchColor,
                                "elements": revisions_absolute,
                                "branches": branches_absolute
                            })
    outPath = join(outFolder, args.currentBranch, 'index.html')
    writeToFile(outPath, template)
    

    # Generate documents list page for every revision of current branch
    for revision in revisions:
        documents = getAllDocuments(revision['path'])
        # making path absolute starting from ./output
        documents_absolute = buildAbsolutePaths(documents)

        page = {
            "title": revision['name'] + " - Documents list",
            "description": "Questa pagina contiene tutti i documenti della revisione " + revision['name'] + ". Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
        }
        template = buildTemplate('branchesList.j2', 
                                {
                                    "basename": repoName,
                                    "page": page,
                                    "color": branchColor,
                                    "elements": documents_absolute,
                                    "branches": branches_absolute
                                })
        outPath = join(revision['path'], 'index.html')
        writeToFile(outPath, template)


if __name__ == '__main__':
    main()