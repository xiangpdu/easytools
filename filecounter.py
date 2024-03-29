#! /usr/local/bin/python
#This tiny tool is used to count the number of specified type file.
import sys
import os
import re

class Config(object):

    def __init__(self):
        # options config, (key, needparam, desc)
        self.OPTION_APPOINTTYPE = ("-a", True,  "appoint the type of files")
        self.OPTION_EXCLUDEFILE = ("-e", True,  "exclude directorys, regular expression is avliable")
        self.OPTION_LEVELS      = ("-l", True,  "the levels when scan directory recursively")
        self.OPTION_HELP        = ("-h", False, "for help")
        self.OPTION_SEARCH      = ("-s", True,  "search pattern within found files")

    def getKey(self, option):
        key, _, _ = option
        return key

    def needParam(self, option):
        _, needParam, _ = option
        return needParam

    def getDesc(self, option):
        _, _, desc = option
        return desc

    def hasKey(self, key):
        for pkey, _, _ in self.getOptions():
            if pkey == key:
                return True
        return False

    def getOptions(self):
        options = []
        for name, value in vars(self).items():
            if str(name).startswith("OPTION"):
                options.append(value)
        return options

config = Config()

#Exclude file, return True if need exclude this file
def exclude(path, options):
    if not options.has_key(config.getKey(config.OPTION_EXCLUDEFILE)):
        return False
    excludedirs = options[config.getKey(config.OPTION_EXCLUDEFILE)].split('|')
    slice = path.split('/')
    shortdir = slice[len(slice)-1]
    for dir in excludedirs:
        if shortdir == dir:
            return True
    return False

#Scan specified directory recursively, and return files in this directory.
def scanfiles(path, level, maxLevel, options):
    if not os.path.isdir(path):
        print path + " is not a directory!"
        return
    if level == 1:
        print "scanning path: " + path
    if level == 2 and exclude(path, options):
        return []
    if level > maxLevel:
        return []
    files = []
    curfiles = os.listdir(path)
    for file in curfiles:
        fullpath = path + "/" + file
        if os.path.isfile(fullpath):
            if filter(file, options):
                files.append(fullpath)
        else:
            subfiles = scanfiles(fullpath, level+1, maxLevel, options)
            if len(subfiles) > 0:
                files.extend(subfiles)
    return files

#filter the files that is specified format, return true if pass through
def filter(file, options):
    if not options.has_key(config.getKey(config.OPTION_APPOINTTYPE)):
        return True
    value = options[config.getKey(config.OPTION_APPOINTTYPE)]
    filters = value.split("|")
    for f in filters:
        if file.endswith(f):
            return True
    return False

#search pattern in found files
def search(files, options):
    if not options.has_key(config.getKey(config.OPTION_SEARCH)):
        return
    pstr = options[config.getKey(config.OPTION_SEARCH)]
    pattern = re.compile(pstr)
    for filename in files:
        results = []
        file = open(filename, mode="r+")
        linenumber = 1
        line = file.readline(1024*512)
        while line != "":
            match = pattern.finditer(line)
            matchpos = []
            for m in match:
                matchpos.append((m.start(), m.group()))
            if len(matchpos) > 0:
                results.append((linenumber, line, matchpos))
            line = file.readline(1024*512)
            linenumber += 1

        # finish search this file, print result if have any
        if len(results) == 0:
            continue
        print filename
        for linenumber, line, positions in results:
            writedend = 0
            outline = ""
            for start, group in positions:
                if writedend < start:
                    outline += line[writedend:start]
                outline += ("\033[0;31m" + group + "\033[0m")
                writedend = start + len(group)
            if writedend < len(line):
                outline += line[writedend:]
            print str(linenumber) + "   " + outline,
        file.close()

#handle count task
def handle(path, options):
    files = []
    if path == None:
        print "invalid path, please double check"
        return
    if options.has_key(config.getKey(config.OPTION_HELP)):
        helper()
        exit(1)
    if options.has_key(config.getKey(config.OPTION_LEVELS)):
        files = scanfiles(path, 1, int(options[config.getKey(config.OPTION_LEVELS)]), options)
    else:
        files = scanfiles(path, 1, sys.maxint, options)
    
    #if there is no search option, print result
    if not options.has_key(config.getKey(config.OPTION_SEARCH)):
        for item in files:
            print item
        print "found " + str(len(files)) + " results"
        return
    else:
        search(files, options)

#Parse argv
def parse(argv):
    options = {} #Store options ("-a": ".cpp")
    if len(argv) <= 1:
        print "Please input the directory path"
        exit(1)
    pendingdel = []

    #Find valid options
    for index in range(len(argv)):
        ret, needparam = isOption(argv[index])
        if ret:
            pendingdel.append(index)
            if needparam:
                if index+1 >= len(argv):
                    print "need value for " + argv[index]
                    exit(1)
                options[argv[index]] = argv[index+1]
                pendingdel.append(index+1)
                index+=1
            else:
                options[argv[index]] = None

    #Delete options in origin argv
    for idx, it in enumerate(pendingdel):
        argv.pop(it-idx)

    #if contains -h, return
    if options.has_key("-h"):
        helper()
        exit(1)

    if len(argv) > 2 or len(argv) < 2:
        print "Please check the number of parameters: " + str(len(argv))
        exit(1)

    return argv[-1], options

def isOption(str):
    for option, needparam, _ in config.getOptions():
        if option == str:
            return True, needparam
    return False, needparam

def helper():
    print "usage: fct $path [options]"
    for key, _, desc in config.getOptions():
        print "    " + key + "  " + desc

if __name__ == "__main__":
    path, options = parse(sys.argv)
    handle(path, options)
