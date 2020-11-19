from jinja2 import Environment, FileSystemLoader
from os import listdir, getcwd, mkdir, remove
from os.path import isdir, join
import json
import argparse
import hashlib

templatesDir = 'Utils/templates'
outFolder = './output'

fileLoader = FileSystemLoader(templatesDir)
env = Environment(loader=fileLoader)
repoName = 'Documents'


def loadFilesList():
    with open('./Utils/filesList.json') as file:
        filesList = file.read()

    filesList = json.loads(filesList) 

    for file in filesList:
        file['path'] = file['name']
    
    return filesList


def getBranchesList():
    return [{"name": dir, "path": join('/', repoName, dir)} for dir in listdir(outFolder) if isdir(join(getcwd(), outFolder, dir))]


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


def buildBranchesListPage(branchesList):
    page = {
        "title": "Branches list",
        "description": "Questa pagina contiene tutti i branch. Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
    }

    template = buildTemplate('template.j2',
                        {
                            "basename": repoName,
                            "page": page,
                            "branches": branchesList,
                            "elements": branchesList
                        })
    outPath = join(outFolder, 'index.html')
    writeToFile(outPath, template)


def buildDirList(branches, currentBranch, branchColor):
    page = {
        "title": "Branches list",
        "description": "Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
    }

    elements = [
        {
            "name": "Documenti Interni",
            "path": join('/', repoName, currentBranch, "DocumentiInterni")
        },
        {
            "name": "Documenti Esterni",
            "path": join('/', repoName, currentBranch, "DocumentiEsterni")
        }
    ]

    template = buildTemplate('template.j2',
                        {
                            "basename": repoName,
                            "page": page,
                            "color": branchColor,
                            "branches": branches,
                            "elements": elements
                        })
    outPath = join(outFolder, currentBranch, 'index.html')
    writeToFile(outPath, template)


def buildDocumentsList(type, dirName, branches, currentBranch, files, branchColor):
    page = {
        "title": type + " Documents List",
        "description": "Something short and leading about the collection below—its contents, the creator, etc. Make it short and sweet, but not too short so folks don't simply skip over it entirely."
    }

    for file in files:
        file['path'] = join('/', repoName, currentBranch, dirName, file['path'])

    template = buildTemplate('template.j2',
                        {
                            "basename": repoName,
                            "page": page,
                            "color": branchColor,
                            "branches": branches,
                            "elements": files
                        })
    outPath = join(outFolder, currentBranch, dirName, 'index.html')
    writeToFile(outPath, template)


def getArgs():
    # Parsing arguments (i.e. output folder)
    parser = argparse.ArgumentParser()
    parser.add_argument("currentBranch", help="name of the current branch")
    return parser.parse_args()


def generateRandColor(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()[:6]


def main():
    # TODO: clean branches

    args = getArgs()

    branchColor = generateRandColor(args.currentBranch)


    branches = getBranchesList()

    buildBranchesListPage(branches)

    buildDirList(branches, args.currentBranch, branchColor)

    files = loadFilesList()

    buildDocumentsList('Internal', 'DocumentiInterni', branches, args.currentBranch, files['DocumentiInterni'], branchColor)

    buildDocumentsList('External', 'DocumentiEsterni', branches, args.currentBranch, files['DocumentiEsterni'], branchColor)

    buildDocumentsList('Internal', 'DocumentiInterni/Verbali', branches, args.currentBranch, files['VerbaliInterni'], branchColor)

    buildDocumentsList('External', 'DocumentiEsterni/Verbali', branches, args.currentBranch, files['VerbaliEsterni'], branchColor)


if __name__ == '__main__':
    main()