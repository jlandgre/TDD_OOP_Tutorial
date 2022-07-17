#Version 4/25/22

import pandas as pd
import math
import os, sys
import glob
import shutil
import numpy as np
import datetime as dt
import random 
import string
import re
from datetime import datetime, date, timedelta

class BlockIteration():
    """
    Class for block iteration -  params track overall and interim reporting
    See iter_test.py for example
    JDL 6/16/22
    """
    def __init__(self, lstItems, iBlkMaxIter=0, idxMaxIter=0, IsPrint=True):
        self.idxMax = len(lstItems) - 1 #Number of items

        #Optional limit on number of iterations; n lst items if not specified
        self.idxMaxIter = idxMaxIter
        if idxMaxIter == 0: self.idxMaxIter = self.idxMax

        #Optional block size; n lst items if not specified
        self.iBlkMaxIter = iBlkMaxIter
        if iBlkMaxIter == 0: self.iBlkMaxIter = self.idxMax

        #Internal variables managed by calling function
        self.idxCurItem = 0
        self.idxCurBlock = 0
        self.idxPrevBlock = 0

        self.iError = 0
        self.IsContinue = True
        self.IsPrint = IsPrint
        self.sMsgs = ''

    def PrintAppendMsg(self, s):
        if self.IsPrint: print(s)
        self.sMsgs += s
        
def IsNullVal(val):

    """Return TRUE if val is null (nan)"""

    if (isinstance(val,float) and math.isnan(val)) or (val is np.nan): return True
    return False

#Set the environment for code - can convert to return a class
def OSDefaults():

    """Set OS-specific values"""

    IsWindows, IsMacOS = False, False
    if os.name == 'nt':
        IsWindows = True
        sep = '\\'
    elif os.name == 'posix':
        IsMacOS = True
        sep = '/'
    return sep

#Returns the filename portion of a directory path
def FileNameFromPath(pathplusfile, sep):

    """Return the filename string from a directory path"""

    return pathplusfile.split(sep)[-1]

def ResetInitialAndFinalFolders(sPath_i, sPath_f, IsRemove, sFileType):

    """Reset files in an initial/final sub-folder structure by either moving files back to initial
       from final or, optionally, deleting all files from both subfolders

    Args:
        path_i (String): directory path of 'initial' sub-folder including final path separator
        path_f (String): directory path of 'final' sub-folder  including final path separator
        IsRemove (Boolean): toggle to either (TRUE) delete all files or (FALSE) move files in final
                            sub-folder to initial without any deletions
        sFileType (String): file specifier such as '*.csv' or '*.*' recognizable to glob.glob()

    Returns:
        i, j, k (Integers): numbers of files relocated, removed from initial and removed from
                            final subfolders, respectively
    """

    i, j, k = 0, 0, 0
    for f in glob.glob(sPath_f + sFileType):
        if not IsRemove:
            shutil.move(f, sPath_i)
            i += 1
        else:
            os.remove(f)
            j += 1
    if IsRemove:
        for f in glob.glob(sPath_i + sFileType):
            os.remove(f)
            k += 1
    return i, j, k


def FractionalDays(tdelta):
    sec_day = 86400
    return round(tdelta.total_seconds()/sec_day,1)

def DatetimeDurationMin(dt_end, dt_begin):
    return round((dt_end - dt_begin).total_seconds()/60,1)

def DatetimeDurationHrs(dt_end, dt_begin):
    return round((dt_end - dt_begin).total_seconds()/3600,1)

def PrintClass(cls):
    """Print all attribute values for a class instance"""
    for var in vars(cls).items():
        if isinstance(var[1], pd.DataFrame) | isinstance(var[1], pd.Series):
            print('\n',var[0], '\n', var[1], '\n\n')
        else:
            print(var[0], ': ', var[1])

def PrintPkgFunctions(pkg):
    """ Print contents of imported package as diagnostic (move to util) """
    from inspect import getmembers, isfunction
    funcs = getmembers(pkg, isfunction)
    print('functions in :', str(pkg))
    for func in funcs:
        print(func[0])
    print('\n')

def PrintDuration(tstart):
    """Duration from a start time"""
    print('Duration: ', round((dt.datetime.now() - tstart).total_seconds(),1), ' seconds')

def EvalAll(st):
    """
    Use Python eval() to attempt to evaluate any object
    JDL 8/25/21 (Call DemoEvalAll() to test/demo)
    """
    try:
        return eval(str(st))
    except:
        return st
def DemoEvalAll():
    """ Demo the EvalAll() function """
    for w in ['[1,2]', 1, 'xxx', {'a':1, 'b':2}]:
        result = EvalAll(w)
        print(type(result), result)

def AddEnclosingBrackets(s):
    """ Add enclosing square brackets to a string"""
    if s[0] == '[': return s
    return '[' + s + ']'

def JSONHasEnclosingBrackets(sJSON):
    """ 
    Determine whether JSON string has leading and trailing square brackets
    """
    s = str(sJSON)
    IsBrackets = True
    if s[0] != '[': IsBrackets = False
    if s[-1] != ']': IsBrackets = False
    return IsBrackets

def JSONHasInternalBrackets(sJSON, sVarName):
    """ 
    Determine whether JSON string has internal square brackets (sub-nested variables)
    """
    s = str(sJSON)
    IsBrackets = True
    s1 = sVarName + '":['
    if s.find(s1) < 1: IsBrackets = False
    return IsBrackets

def MultiReplace(lstReplace, lstWith, s):
    for sReplace, sWith in zip(lstReplace, lstWith):
        s = re.sub(sReplace, sWith, s)    
    return s

def ListDifference(lstParent, lstChild):
    """
    Return a sub-list of items not in a second, "child" list
    JDL 9/22/21
    """
    if not isinstance(lstParent, list) or not isinstance(lstChild, list):
        return lstParent
    return [item for item in lstParent if item not in lstChild]

def SingleToDoubleQuotes(s):
    """
    Convert strings with single quotes to double quotes 
    (for JSON compatibility. Single and double quotes are interchangeable in Python
    but JSON requires double quotes)

    JDL 9/24/21
    """
    s_double = s.replace('\'', '"')
    return s_double

def RanStrGen(size, chars=string.ascii_uppercase + string.digits): 
    """
    Return a random string of length, size, either based on chars seed argument
    or on Python constants for uppercase letters + digits if no seed is supplied

    JDL 9/27/21
    """
    return ''.join(random.choice(chars) for x in range(size)) 

def ClsAttsAndMethods(cls):
    return [s for s in dir(cls) if not s.startswith('__')]

def PrintClsAttsAndMethods(cls):
    for s in ClsAttsAndMethods(cls):
        print(f"{s: <20}", getattr(cls, s))

def ClsMethods(cls):
    return [s for s in dir(cls) if callable(getattr(cls, s)) and not s.startswith("__")]

def PrintClsMethods(cls):
    for s in ClsMethods(cls):
        print(f"{s: <20}", getattr(cls, s))

def ClsAttributes(cls):
    return [s for s in dir(cls) if not callable(getattr(cls, s)) and not s.startswith("__")]

def PrintClsAtts(cls):
    for s in ClsAttributes(cls):
        print(f"{s: <20}", getattr(cls, s))

def PrintDuration(tstart):
    """Duration from a start time"""
    print('Duration: ', round((dt.datetime.now() - tstart).total_seconds(),1), ' seconds')

def DirFileCount(sdir):
    return len([s for s in os.listdir(sdir) if os.path.isfile(sdir + s)])

def LstEquals(l1, l2):
    """
    Test whether lists are equal (accounts for nan != nan)
    7/14/22
    """
    for v1, v2 in zip(l1, l2):

        #First if clause False for nan/non-nan comparison
        if not (np.isnan(v1) and np.isnan(v2)) and v1 != v2: return False
    return True