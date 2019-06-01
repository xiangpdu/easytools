#This tiny tool is used to count the number of specified type file.
import sys
import os

#Scan specified directory recursively, and return files in this directory.
def scanfiles(path, level, maxLevel):
    if level == 1:
        print "scanning path: " + path
    if level > maxLevel:
        return []
    files = []
    curfiles = os.listdir(path)
    for file in curfiles:
        fullpath = path + "/" + file
        if os.path.isfile(fullpath):
            files.append(fullpath)
        else:
            subfiles = scanfiles(fullpath, level+1, maxLevel)
            if len(subfiles) > 0:
                files.extend(subfiles)
    return files

#filter the files that is specified format
def filter(files, options):
    if not options.has_key('-a'):
        return files
    result = []
    value = options["-a"]
    filters = value.split("|")
    for file in files:
       for f in filters:
           if file.endswith(f):
               result.append(file)
    return result

#handle count task
def handle(path, options):
    files = []
    if path == None:
        print "invalid path, please double check"
        return
    if options.has_key("-h"):
        helper()
        exit(1)
    if options.has_key("-l"):
        files = scanfiles(path, 1, int(options["-l"]))
    else:
        files = scanfiles(path, 1, sys.maxint)
    results = filter(files, options)
    
    #print results
    for item in results:
        print item
    print "found " + str(len(results)) + " results"

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
    #Store option configs, the second show if this option need a parameter
    options = [("-a", True), ("-e", True), ("-l", True), ("-h", False)]
    for option, needparam in options:
        if option == str:
            return True, needparam
    return False, needparam

def helper():
    print \
          "usage: fct $path [options] \n"\
          "     -a appoint the type of files\n"\
          "     -e exclude directorys, regular expression is avliable\n"\
          "     -l the levels when scan directory recursively\n"\
          "     -h for help"

if __name__ == "__main__":
    path, options = parse(sys.argv)
    handle(path, options)