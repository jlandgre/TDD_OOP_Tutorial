import os, sys
from pathlib import Path

class ProjectPaths():
  """
  __init__ sets locations for project folder structure. A typical structure is:

  projname
    projname_analysis         <== one-off analyses performed for the project
    projname_data              <== input and output data files operated on by scripts
    projname_scripts
      libs                     <== generic (non project-specific) code libraries
        libxxx.py
      tests                     <==pytest tests of project code
        test_xxx.py
      jupyter                   <== exploratory code snippets
        mockup_code_xxx.ipynb
      projscript_xxx.py
      projscript_yyy.py
    projname_zrawdata_bigfiles  <== optional if filesize makes desirable to segregate from other data
  """
  def __init__(self):
      
      #Start by setting the root directory
      self.root = ''
      self.PathRoot()

      #Set other sub-directories relative to root
      self.analysis = self.root + 'oop_example_analysis/'
      self.data = self.root + 'oop_example_data/'
      self.scripts = self.root + 'oop_example_scripts/'
      self.tests = self.scripts + 'tests/'
      self.lstpaths = []

  def PathRoot(self):
    """
    Return project's root directory path
    Example usage: iLevelSelf = 2 Structure: root/scripts/libs/dirpathutil.py
    JDL 4/20/22
    """
    # How many levels is dirpathutil.py from project root dir [root=0]?
    iLevelSelf = 2
    sPathHome = str(Path(__file__).parent)
    self.lstpaths = LstPaths(sPathHome, iLevelSelf+1)
    self.root =  self.lstpaths[iLevelSelf]

  def AddSysPath(self, sNewPath):
    """
    Add a single library path to sys.path
    """
    if not sNewPath in sys.path:
      sys.path.append(sNewPath)

  def AddLibPaths(self, lstLibs):
    """
    Add a list of library paths to sys.path
    """
    for libpath in lstLibs:
      self.AddSysPath(libpath)  

#Create OS-tailored path from underscore-delimited version
def MakePath(sPathString):
    lst = sPathString.split('/')
    sep = os.sep
    return sep.join(lst)

def LstPaths(sPath, idepth):
    """
    Build list of nested directory paths based on sPath argument 
    (usually str(Path(__file__)) of calling module) - JDL 4/16/22
    """
    # List paths to idepth levels - starting with home/top-level, lst[0]; 4/8/22
    lstdirs = sPath.split(os.sep)
    lstpaths = []
    for i in range(len(lstdirs), len(lstdirs) - idepth, -1):
        lstpaths.append(os.sep.join(lstdirs[0:i]) + os.sep)
    return lstpaths

"""
Usage:
* Place dirpathutil.py in a project's 'root' directory/scripts/libs folder
* Include following statements at the beginning of each library:

    import sys, os
    from pathlib import Path
    sys.path.append(sys.path[0][0:sys.path[0].rfind(os.sep)])
    import dirpathutil
    lstpaths = dirpathutil.LstPaths(str(Path(__file__).parent), 4)
    sys.path.append(lstpaths[1] + os.sep + 'pkg' + os.sep)
    sys.path.append(lstpaths[1] + os.sep + 'pkg2' + os.sep)
    etc.

* Next upgrade move lstpaths = and sys.path.append into LstPaths
  by including a list of needed libraries as an argument
* LstPaths can keep sys.path tidy by only adding a string if it
  is not already in sys.path
"""