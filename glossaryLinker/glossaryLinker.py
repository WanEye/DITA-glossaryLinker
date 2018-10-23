import errno
import os
import re
import shutil
import sys
import time


g_log = "Routines "
g_IDglossentries = []
g_DITAcontent = ""
g_DITAlist = []
g_all_glossgroup = []

# globals
# g_all_glossgroup    list of glossary files
# g_allowedTags       list of tags where you can put <xref>
# g_DITAlist          list of DITA files
# g_DITAcontent       String that contains the entire DITA file content
# g_IDglossentries    list of glossentry, glossterm with ID


def R99writeLog(content):
    global g_log
    g_log = g_log + "\n" + content
    print g_log
    
    return


def ioError(routine, iofile):
    
    ErrMess = 'ERROR ' + routine + "open file " + iofile
    print ErrMess
    R99writeLog(ErrMess)
    sys.exit()    
    
    return 


def R10AgetDITAfiles():
    """
    Determine the current directory.
    Get all .dita files with full path in the current directory and subdirectories.
    Put all these .dita files in global list    
    """
    routine = 'R10A '
    R99writeLog(routine)
    #
    global g_current_Dir
    global g_DITAlist
    global g_resultContent
    
    g_current_Dir = os.getcwd()
    print "directory in process: " + g_current_Dir
    
    for dirpath, dirnames, filenames in os.walk(g_current_Dir):
        for filename in [f for f in filenames if f.endswith(".dita")]:
            DITAfile = os.path.join(g_current_Dir, dirpath, filename)
            g_DITAlist.append(DITAfile)
 
    return


def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the source is not a folder
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print(src + ' Folder not copied. Error: %s' % e)
            
    return
            

def R10BbackupDITAfiles():
    routine = 'R10B '
    R99writeLog(routine)
    #
    # Make a backup of all .dita files because the program changes the files.
    #
    backup_Dir = g_current_Dir + '/DITAbackup/'
    
    if os.path.exists(backup_Dir):
        errorR10 = """
        Glossary links already present.
        User actions:
        Verify DITA code for glossary links
        If you want to generate links to glossary terms again, delete """
        print errorR10
        print "        " + backup_Dir 
        print "        Then, run this program again."
        
        sys.exit()
    
    copy(g_current_Dir, backup_Dir)
                  
    return


def R10CgetGlossaryFiles():
    routine = 'R10C '
    R99writeLog(routine)
    #
    global g_all_glossgroup
    g_all_glossgroup = []
    
    headerString = "<!DOCTYPE glossgroup" 
    
    for Glossfile in g_DITAlist:
        try:
            GLOSSFILE = open(Glossfile)
            filecontent = GLOSSFILE.read()
        except IOError:
            ioError(routine, Glossfile)
        # test if DITA file is a glossary file    
        if headerString in filecontent:
            g_all_glossgroup.append(Glossfile)
           
    return


def R10EgetAllowedTags():
    routine = "R10 "
    R99writeLog(routine)
    #
    global g_allowedTags
    g_allowedTags = []
    TAGS = open("containedBy.txt", "r")
    g_allowedTags = TAGS.readlines()
    
    # remove newline from tags
    for index in range(len(g_allowedTags)):
        g_allowedTags[index] = g_allowedTags[index].rstrip('\n')
      
    return


def R10InitPrg():
    routine = 'R10 '
    localtime = time.asctime(time.localtime(time.time()))
    R99writeLog(routine + ": " + localtime)
    #
    R10AgetDITAfiles()
    R10BbackupDITAfiles()
    R10CgetGlossaryFiles()
    R10EgetAllowedTags()
    
    return


def R19FinPrg():
    routine = 'R19 '
    localtime = time.asctime(time.localtime(time.time()))
    R99writeLog(routine + ": " + localtime)
    #
    LOG = open("log.log", "w")
    LOG.write(g_log)
    LOG.close()
    
    print "The End"
    
    return


def R20InitDITA(DITAfile):
    routine = 'R20 '
    R99writeLog(routine)
    #
    global g_DITAcontent
    
    try:
        DITA = open(DITAfile, "r+")
    except IOError:
        ioError(routine, DITAfile)
    
    DITAcontent = DITA.read()
    if '<glossgroup id' in DITAcontent:
        g_DITAcontent = ''
    else:
        g_DITAcontent = DITAcontent
        # remove all new lines
        # to format and indent again, use Oxygen Tools > Format and Indent files ... 
        g_DITAcontent = g_DITAcontent.replace('\n', " ")
        # replace multi spaces with single spaces
        while ("  " in g_DITAcontent):
            g_DITAcontent = g_DITAcontent.replace("  ", " ")   
    
    DITA.close()
    
    return


def R30Init_glossgroup(DITAfile, glossFile):
    routine = 'R30 '
    R99writeLog(routine)
    #
    # determine relative path DITA file and glossary file
    # fill list with glossentry and glossterm
    global g_IDglossentries
    try:
        GLOSS = open(glossFile)
    except IOError:
        ioError(routine, glossFile)  
     
    text = GLOSS.read()
    relativePath = R30ArelPath(glossFile, DITAfile)

    regex = r"""
    <glossentry\s*id=\"(\w*)\">.*?<glossterm>(.*?)<\/glossterm>
    """
    g_IDglossentries = re.findall(regex, text, re.M | re.S | re.X)
            
    return relativePath, g_IDglossentries


def R30ArelPath(file1, file2):
    routine = 'R30A '
    R99writeLog(routine)
    #
    global g_relativePath
    from os.path import relpath
    
    g_relativePath = relpath (file1, file2)
    # cut ../ or ..\ from path because input are files rather than dirs
    g_relativePath = g_relativePath[3:] 
    
    return g_relativePath


def R39Fin_glossgroup():

    return


def R40Proc_glossdef(DITAfile, tag, glossentry):
    routine = 'R40 '
    R99writeLog(routine)
    #
    # glossentry is a tuple 
    # glossentry[1] contains the glossary term
    #
    global g_DITAcontent
    #
    strPre = '<xref href="'
    strSuf = '</xref>'
    
    tagEnd = tag.replace("<", "</")
    # add newline after closing tag to facilitate regex
    g_DITAcontent = g_DITAcontent.replace(tagEnd, tagEnd + '\n')
    
    glossentryID = glossentry[0]
    glossterm = glossentry[1]
    
    # build xref tag        
    xrefStr = strPre + g_relativePath + '#' + glossentryID + '">' + glossterm + strSuf
    regex = glossterm + '[^<]*' + tagEnd
    
    # find all occurences case-insensitive and put in a tuple
    occurencesALL = re.findall(regex, g_DITAcontent, re.IGNORECASE)
    for occurence in occurencesALL:
        occurenceNew = occurence.replace(glossterm, xrefStr)
        # if term starts with upper case in the DITA file
        if occurence == occurence:
            occurence = occurence.capitalize()
            glosstermUC = glossterm.capitalize()
            xrefStrUC = strPre + g_relativePath + '#' + glossentryID + '">' + glosstermUC + strSuf
            occurenceNew = occurence.replace(glosstermUC, xrefStrUC)
        
        # replace content with content that contains xref link   
        g_DITAcontent = g_DITAcontent.replace(occurence, occurenceNew)
        # remove all new lines again
        g_DITAcontent = g_DITAcontent.replace('\n', " ")
        
    return g_DITAcontent


def R29WriteDITA(content, DITAfile):
    routine = 'R49 '
    R99writeLog(routine)
    # write replaced content to file
    
    try:
        DITA = open(DITAfile, "w")
    except IOError:
        ioError(routine, DITAfile)    
            
    DITA.write(content)
    DITA.close() 
    return


# ===== MAIN =====
def R00Main():
    start = time.time()
    routine = 'R00 '
    R99writeLog(routine)
    #
    DITAfile = ""
    glossary = ""
    # global g_DITAcontent    
    R10InitPrg()
    for DITAfile in g_DITAlist:
        R20InitDITA(DITAfile)
        if g_DITAcontent <> '':
            for glossary in g_all_glossgroup:
                R30Init_glossgroup(DITAfile, glossary)
                for tag in g_allowedTags:                     
                    if tag.rstrip() in g_DITAcontent:
                        for glossentry in g_IDglossentries:
                            R40Proc_glossdef(DITAfile, tag, glossentry)
                R39Fin_glossgroup()            
            R29WriteDITA(g_DITAcontent, DITAfile)
    R19FinPrg()
    #
    end = time.time()
    R99writeLog("elapsed time: " + str(end - start) + "sec")
    
    return
 

R00Main()
