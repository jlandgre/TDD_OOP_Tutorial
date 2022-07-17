#Version 7/13/22
#python -m pytest test_align_intensity.py -v -s

#Set home (projname_scripts) Path and import needed libraries
import pandas as pd
import numpy as np
import pytest
import sys, os
from pathlib import Path
sPathHome = str(Path(__file__).parent)
sPathHome = sPathHome[0:sPathHome.rfind(os.sep)]
if not sPathHome in sys.path: sys.path.append(sPathHome)
sPathLibs = sPathHome + os.sep + 'libs'
if not sPathLibs in sys.path: sys.path.append(sPathLibs)
import scriptsfiles
import util
import align_intensity

#Toggle for outputting align._dfC intermediate demo files
IsOutputDemoFiles = False

@pytest.fixture
def files():
    """
    Instance the project files class
    """
    return scriptsfiles.ScriptsFiles_New(IsTest=True)

@pytest.fixture
def dfC_input(files):
    """
    Open the input DataFrame
    """
    return pd.read_csv(files.sPF_data)

@pytest.fixture
def align(dfC_input):
    """
    Instance the class from the library being tested
    """
    return align_intensity.SummIntensityByDecr(dfC_input)

@pytest.fixture
def cols_input():
    return ['device_id', 'timestamp', 'refill_percent', 'intensity']

@pytest.fixture
def lst_test_devices():
    return ['DSN_001', 'DSN_002', 'DSN_003']

#print('\n\n')
#print(align._dfC)
#def test_dfC_property(dfC_input, lst_test_devices):

def test_ser_summ_intensity_property(dfC_input, lst_test_devices):
    ser = align_intensity.SummIntensityByDecr(dfC_input).ser_summ_intensity
    CheckIntensitySummary(ser, lst_test_devices)

def test_SummarizeIntensityByDevice(align, lst_test_devices):
    """
    Check the final summary of average intensity by device
    """
    ProcedureThroughFillDown(align)
    align.UpdateFilters()
    align.ClearUnneededValues()
    align.SummarizeIntensityByDevice()
    ser_summary = align._serSummIntensity

    #Check summary values (average intensity by device)
    CheckIntensitySummary(ser_summary, lst_test_devices)

    if IsOutputDemoFiles: 
        df = align._serSummIntensity.to_frame()
        OutputDfC(df, 'summary.xlsx', True)

def CheckIntensitySummary(ser, lst_devs):
    """Helper function for intensity summary check"""
    lst_expected = [7.5, 5.25, 9.5]
    for dev, val in zip(lst_devs, lst_expected):
        assert ser[dev] == val

def test_ClearUnneededValues(align):
    ProcedureThroughFillDown(align)
    align.UpdateFilters()
    align.ClearUnneededValues()
    
    #Filter to non-blank rows and check what's included
    fil = ~align._dfC['intensity_aligned'].isnull()
    assert list(align._dfC[fil].index) == [6,7,13,14,21,27,28,29,31,36,38,39]

    if IsOutputDemoFiles: OutputDfC(align._dfC, 'data_transformed5.xlsx')


def test_UpdateFilters_final(align):
    ProcedureThroughFillDown(align)
    align.UpdateFilters()

    fil  = align.fil_999
    assert list(align._dfC[fil].index) == [0,1,2,3,4,15,16,17,18,19,20]

def ProcedureThroughFillDown(align):
    align.AddIntensityAlignedCol()
    align.UpdateFilters()
    align.PopulateDeviceChangeRows()
    align.FillDownDecrIntensity()


def test_FillDownDecrIntensity(align, lst_test_devices):
    align.AddIntensityAlignedCol()
    align.UpdateFilters()
    align.PopulateDeviceChangeRows()
    align.FillDownDecrIntensity()

    #Lists of expected values for each device section of data
    #Device change row for DSN_003 already populated so no 999 there
    lst_expected = [5 * [999.] + 7 * [8.] + 3 * [7.], 
                    6 * [999.] + 4 * [6.] + 5 * [5.],
                    7 * [9.] + 3 * [10.]]
    col = 'intensity_aligned'
    for lstvals, dev in zip(lst_expected, lst_test_devices):
        fil = align._dfC['device_id'] == dev
        assert list(align._dfC.loc[fil, col]) == lstvals
    
    if IsOutputDemoFiles: OutputDfC(align._dfC, 'data_transformed4.xlsx')

def test_PopulateDeviceChangeRows(align):
    """
    Add 999 values in device change rows as anchor for fill down
    """
    align.AddIntensityAlignedCol()
    align.UpdateFilters()
    align.PopulateDeviceChangeRows()

    lst = list(align._dfC.loc[align.fil_dev_change, 'intensity_aligned'])
    assert lst == [999, 999, 9]

    if IsOutputDemoFiles: OutputDfC(align._dfC, 'data_transformed3.xlsx')


def test_UpdateFilters_initial(align):
    """
    Check of filters initially --before transform to intensity_aligned
    """
    align.AddIntensityAlignedCol()
    align.UpdateFilters()

    #Null Refill Percent filter
    assert align._dfC[~align.fil_null_refperc].index.size == 14

    #Intensity filters - in initial check, aligned same as orig
    for fil in [align.fil_null_intensity, align.fil_null_alignedintensity]:
        assert align._dfC[~fil].index.size == 6

    #Device change rows
    assert align._dfC[align.fil_dev_change].index.size == 3
    assert list(align._dfC[align.fil_dev_change].index) == [0, 15, 30]

def test_AddColumn(align, cols_input):
    """
    Copy intensity column to what will be the aligned column
    """
    if IsOutputDemoFiles: OutputDfC(align._dfC, 'data_transformed1.xlsx')

    align.AddIntensityAlignedCol()
    assert list(align._dfC.columns) == cols_input + ['intensity_aligned']
    lst_orig = list(align._dfC['intensity'].values)
    lst_new = list(align._dfC['intensity_aligned'].values)
    assert util.LstEquals(lst_orig, lst_new)

    if IsOutputDemoFiles: OutputDfC(align._dfC, 'data_transformed2.xlsx')

def test_files_fixture(files):
    """
    Check files fixture. It should point to data in tests/ for IsTest=True
    """
    assert files.sF_data == 'data.csv'
    assert files.sPF_data == sPathHome + os.sep + 'tests' + os.sep + 'data.csv'

def test_TestData(dfC_input, cols_input):
    """
    Check columns and dimensions of test input data
    """
    assert list(dfC_input.columns) == cols_input
    assert list(dfC_input['device_id'].unique()) == ['DSN_001', 'DSN_002', 'DSN_003']
    assert dfC_input.index.size == 40

#Output a demo file
def OutputDfC(df, fname, IsWithIdx=False):
    df.to_excel(fname, index=IsWithIdx, merge_cells=False)


