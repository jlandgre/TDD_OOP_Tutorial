import sys, os
import dirpathutil

class ScriptsFiles_New():
    """
    Class holding file locations for a project; 
    locations assume os.getcwd() is  projname_scripts sub-folder
    Specify relative paths using '/' separator; dirpathutil.MakePath converts to '\\' for Windows
    """
    def __init__(self, IsTest=False, sTestsSubdir=''):
        """
        Inputs:
        IsTest [Boolean] toggle to point paths to tests sub-directory
        sTestsSubdir [Boolean] optional tests sub-directory for segregating issue-specific files
                               related to a particular issue
        """
        #Include paths class instance as attribute of ScriptsFiles
        paths = dirpathutil.ProjectPaths()

        self.spathroot = paths.root
        self.spathdata = paths.data
        self.spathscripts = paths.scripts
        if IsTest:
            self.spathroot = paths.tests
            self.spathdata = paths.tests + sTestsSubdir

        #input file - align_intensity raw data
        self.sPF_data = dirpathutil.MakePath(self.spathdata + 'data.csv')
        self.sF_data = 'data.csv'

        #output file - align_intensity transformed data
        self.sPF_data_out = dirpathutil.MakePath(self.spathdata + 'data_out.csv')
        self.sF_data_out = 'data_out.csv'