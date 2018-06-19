import os
import sys
import re
from shutil import copyfile

g_log = "Routines "
g_IDglossentries=[]
g_DITAcontent  = ""
g_DITAlist = []
g_all_glossgroup = []


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
    
    
    g_current_Dir=os.getcwd()
    print "directory in process: " + g_current_Dir
    
    for dirpath, dirnames, filenames in os.walk(g_current_Dir):
        for filename in [f for f in filenames if f.endswith(".dita")]:
            DITAfile = os.path.join(g_current_Dir, dirpath, filename)
            g_DITAlist.append(DITAfile)
 
    return


def R10BbackupDITAfiles():
    routine = 'R10B '
    R99writeLog(routine)
    #
    """
    Make a backup of all .dita files because the program changes the files.
    """

    #
    backup_Dir = g_current_Dir + '/DITAbackup/'
    
    if os.path.exists(backup_Dir):
        print """
        Tags <indexterm> already present.
        User actions:
        Verify DITA code for tags <indexterm>
        If you want to generate <indexterm> tags, delete " + backup_Dir 
        Run this program again
        """
        sys.exit()
    else:    
        try:
            os.makedirs(backup_Dir)
        except IOError:
            print ("ERROR: Cannot make directory " + routine + g_current_Dir + backup_Dir)
            sys.exit()
        
    for dirpath, dirnames, filenames in os.walk(g_current_Dir):
        for filename in [f for f in filenames if f.endswith(".dita")]:
            DITAfile = os.path.join(g_current_Dir, dirpath, filename)
            backup_File = backup_Dir + filename
            if not os.path.isfile(backup_File):
                try:
                    copyfile(DITAfile, backup_File)
                except IOError:
                    ioError(routine, backup_File)
                    print("ERROR: Cannot copy " + routine + backup_File)
                    sys.exit()
                    
    return


def R10CgetGlossaryFiles():
    routine = 'R10C '
    R99writeLog(routine)
    #
    
    global g_all_glossgroup
    
    headerString = "<!DOCTYPE glossgroup" 
    
    for Glossfile in g_DITAlist:
        try:
            GLOSSFILE = open(Glossfile)
            filecontent = GLOSSFILE.read()
        except IOError:
            ioError(routine, Glossfile)
            
        if headerString in filecontent:
            g_all_glossgroup.append(Glossfile)
            
    return


def R10InitPrg():
    routine = 'R10 '
    R99writeLog(routine)
    #
    R10AgetDITAfiles()
    R10BbackupDITAfiles()
    R10CgetGlossaryFiles()
    
    return


def R19FinPrg():
    routine = 'R19 '
    R99writeLog(routine)
    #
    LOG = open("log.log", "w")
    LOG.write(g_log)
    LOG.close()
    #
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
    
    DITA.close()
    
    return


def R29FinDITA(DITAfile, g_DITAcontent):
    routine = 'R29 '
    R99writeLog(routine)
    #
    try:
        DITA = open(DITAfile, "w" )
    except IOError:    
        ioError(routine, DITAfile)
        
    DITA.write(g_DITAcontent)
    DITA.close() 
    
    return


def R30Init_glossgroup(DITAfile, glossFile):
    routine = 'R30 '
    R99writeLog(routine)
    #
    global g_IDglossentries
    try:
        GLOSS = open(glossFile)
    except IOError:
        ioError(routine, glossFile)  
     
    text = GLOSS.read()
    relativePath = R30ArelPath(glossFile, DITAfile)
    print "Glossary: " + glossFile
    # print text
    regex = r"""
    <glossentry\s*id=\"(\w*)\">.*?<glossterm>(.*?)<\/glossterm>
    """
    g_IDglossentries = re.findall(regex, text, re.M|re.S|re.X)
            
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


def R40AcheckTerm(string, term):
    routine = 'R40A '
    R99writeLog(routine)
    #
    # Put all content in a single line
    # Then, count the substring occurrences in both single-line and multi-line string
    OneLineStr = string.replace("\n", "")
    nLC1 = OneLineStr.count(term)
    nUC1 = OneLineStr.count(term.capitalize())

    nLC = string.count(term)
    nUC = string.count(term.capitalize())
    
    occur  = nLC  + nUC                     
    occur1 = nLC1 + nUC1
    
    difference = occur1 - occur

    return difference


def R40Proc_glossdef(g_DITAcontent, DITAfile ):
    routine = 'R40 '
    R99writeLog(routine)
    #
    glossentryID=""
    xrefStr   = " "
    xrefStrUC = " "
    strPre = '<xref href="'
    strSuf = '</xref>'
    
    for index in range(len(g_IDglossentries)):
        # In the glossary, the term can be all lower case
        # In the DITA file. The glossaryterm can start with an upper-case letter on the DITA file
        # Terms cannot span more than 1 line
        glossterm   = g_IDglossentries[index][1]
        glosstermUC = glossterm.capitalize()
    
        glossentryID   = g_IDglossentries[index][0]
 
        xrefStr   = strPre + g_relativePath + '#' +  glossentryID + '">' + glossterm   + strSuf
        xrefStrUC = strPre + g_relativePath + '#' +  glossentryID + '">' + glosstermUC + strSuf
    
        print "BEFORE: " + g_DITAcontent
        print glossterm + ":::" + xrefStr
        resultStr  = g_DITAcontent.replace(glossterm, xrefStr)
        print "AFTER: " + resultStr
        resultStr = resultStr.replace(glosstermUC, xrefStrUC)
        g_DITAcontent = resultStr
        
        # Check for term that are spread in two or more lines
        difference = R40AcheckTerm(g_DITAcontent, glossterm)
    
        if difference <> 0:
            print routine + '001ERROR'
            print '''
            xref incomplete:  
            The term cannot include a new line
            user action: check for new lines within terms in your DITA code.
            '''
            print "differences " + str(difference) + "\nterm: " + glossterm    
            exit()
        else:   
            try:
                DITA = open(DITAfile, "w" )
            except IOError:
                ioError(routine, DITAfile)    
            
            DITA.write(g_DITAcontent)
            DITA.close() 
    
    return


# ===== MAIN =====
def R00Main():
    routine = 'R00 '
    R99writeLog(routine)
    #
    DITAfile = ""
    glossary = ""
        
    R10InitPrg()
    for DITAfile in g_DITAlist:
        R20InitDITA(DITAfile)
        if g_DITAcontent <> '':
            for glossary in g_all_glossgroup:
                R30Init_glossgroup(DITAfile, glossary)
                R40Proc_glossdef(g_DITAcontent, DITAfile)
                R39Fin_glossgroup()    
    R19FinPrg()
    
    return
 

R00Main()