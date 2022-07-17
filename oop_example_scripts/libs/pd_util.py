#Version 8/30/21 - Added JSON parse functions
import pandas as pd
import numpy as np

#Import JDL utility modules
import colinfo
import util

def SubsetToFilter(df, fil):
    return df[fil]

#Add a row order column to fingerprint rows (move this to tbltools library)
def AddRowOrderCol(df, col_name):
    df.reset_index(inplace=True,drop=True)
    df.index.name = col_name
    df.reset_index(drop=False, inplace=True)
    return df

def ImportDataFrame2(tbl_cls, file, dir_colinfo):
    """
    Import a DataFrame from csv.
    Rename columns to ColInfo Names.
    Filter to keepcols
    Set data types on import
    JDL 9/28/20
    """
    df = pd.read_csv(file)
    ColInfo = colinfo.ReadColInfoFromFile(dir_colinfo)
    colinfo.CI_RenameColsFromImport(ColInfo, df)
    if len(tbl_cls.keepcols) > 0: df = df[tbl_cls.keepcols]
    return df

def ImportDataFrame(tbl_cls, file):
    """
    Import a DataFrame from csv. Rename columns to ColInfo Names. Filter to keepcols
    JDL 7/21/20
    """
    df = pd.read_csv(file)
    ColInfo = colinfo.ReadColInfoFromFile('libs/colinfo.csv')
    colinfo.CI_RenameColsFromImport(ColInfo, df)
    if len(tbl_cls.keepcols) > 0: df = df[tbl_cls.keepcols]
    return df

def TopItemCtAndDesc(df, lst_by):
    """
    Group a Dataframe by a list of "by" columns and return top item's lst_by value(s) and count

    Returns:
    desc:   lst_by value(s) for top-ranked row.  data type will be value or tuple depending
            on whether lst_by is single item or multi-item list
    ct:     count of top-ranked row in groupby

    JDL 7/27/20
    """
    ser = df.groupby(lst_by).size()
    ser.sort_values(ascending=False, inplace=True)
    if ser.index.size > 0:
        return ser.index.values[0], ser[0]
    else:
        return 'None', 0

def MapSerToAltVals(ser_data, lst_data_keys, lst_data_vals):
    """Map a list of values to an alternate list for plotting

    Useful for "rescaling" or mapping text categories to numerical values for plotting

    Args:
    ser_data (Pandas Series) - data series with values for remapping
    lst_data_keys (list) - list of keys (current series values) for mapping
    lst_data_vals (list) - list of values to map to

    Raises:
    No error trapping currently

    Returns:
    Pandas series with keys remapped to values

    """

    ser_mapped = ser_data.copy()
    di = dict(zip(lst_data_keys, lst_data_vals))
    return ser_mapped.replace(di)

def RescaleSerValues(ser_data, tup_lims_data, tup_lims_rescaled):
    """
    Rescale numeric data

    Useful for "rescaling" data for plotting.  Example:
    tup_lims_data = (0, 100)
    tup_lims_rescaled = (-10, 0)
    Series will be rescaled such that 0 --> -10 and 100 --> 0

    Args:
    ser_data (Pandas Series) - data series with numeric values for remapping
    tup_lims_data (tuple; numeric values)
    tup_lims_data (tuple; numeric values)

    Raises:
    No error trapping currently

    Returns:
    Pandas series with rescaled values
    """
    ser_plot = ser_data.copy()

    x1_new = tup_lims_rescaled[1]
    x0_new = tup_lims_rescaled[0]
    x1_prev = tup_lims_data[1]
    x0_prev = tup_lims_data[0]
    return (ser_data - x0_prev)*((x1_new - x0_new)/(x1_prev - x0_prev)) + x0_new

def RescaleValue(val, tup_lims_data, tup_lims_rescaled):
    """
    Rescale numeric data value

    Useful for "rescaling" data for plotting.  Example:
    tup_lims_data = (0, 100)
    tup_lims_rescaled = (-10, 0)
    value will be rescaled such that 0 --> -10 and 100 --> 0

    Args:
    val (Float) - value to be rescaled
    tup_lims_data (tuple; numeric values)
    tup_lims_data (tuple; numeric values)

    Raises:
    No error trapping currently

    Returns:
    rescaled value
    """

    x1_new = tup_lims_rescaled[1]
    x0_new = tup_lims_rescaled[0]
    x1_prev = tup_lims_data[1]
    x0_prev = tup_lims_data[0]
    return (val - x0_prev)*((x1_new - x0_new)/(x1_prev - x0_prev)) + x0_new

def SeriesFromDFCols(df, valcol, indexcol, dtype=None):
    """
    Convert two DataFrame columns into a Series as index and values; drop nulls from valcol

    args:
    df (Pandas DataFrame) - DataFrame containing valcol and indexcol
    valcol (String) - name of DataFrame column to return as Series values (and name of Series)
    indexcol (String) - name of DataFrame column to return as Series index
    dtype (Python dtype - typically int) - optional returned dtype of Series

    JDL 8/6/20
    """
    ser = pd.Series(df[valcol].values, index=df[indexcol]).dropna()
    ser.name = valcol
    if not dtype is None: ser = ser.astype(dtype)
    return ser

def CreateTopEventTable(lst_grp, dfdata):
    """
    Create a table of top-occurring items from a two-key table where lst_grp = [key, item]

    JDL 11/13/20
    """
    key = lst_grp[0]

    #Create groupby DataFrame summarizing occurrences of all items (item is lst_grp[1])
    df_grp = dfdata.groupby(lst_grp).size().to_frame().reset_index(drop=False)
    #print(df_grp.head(10))
    #Sort so that top event is first for each key value; filter for first key row
    df_grp = df_grp.sort_values([key, 0], ascending=False).reset_index(drop=True)
    #print(df_grp.head(10))
    return df_grp[df_grp[key].shift(1) != df_grp[key]].sort_values(0,ascending=False).set_index(key)

def SplitAndStack(df, lst_keys, splitcol, sDelim, sIDCol):
    """
    Compound parsing of delimited Pandas column
    Split a DataFrame column and stack based on one or more key columns and a specified delimiter

    Inputs:
        df [Pandas DataFrame] DataFrame containing keycols, splitcol and possibly extraneous columns
            not involved with reshaping
        lst_keys [List of Strings] key column names
        splitcol [String] name of column to be parsed
        sDelim [String] delimiter character string for splitting splitcol values

    Return: Reshaped DataFrame with keycols, a new ID col and splitcol as columns
            (Combo of keycols and new ID col uniquely identify each row)

    JDL 8/2/21
    """    
    #Make a copy that has only the key columns and split column
    dftemp = df.copy().loc[:, lst_keys + [splitcol]]
    
    #Set the key columns as index; split and stack
    dftemp = dftemp.set_index(lst_keys)
    dftemp = dftemp[splitcol].str.split(sDelim, expand=True)
    ser = dftemp.stack()
    ser.index.names = lst_keys + [sIDCol]
    
    #Turn the stacked series back into DataFrame by converting Series index to columns
    dftemp = ser.reset_index()
    dftemp = dftemp.rename(columns={0:splitcol})
    
    #Return without stack order integer column
    #return dftemp.loc[:, lst_keys + [splitcol]]
    return dftemp


def SubSplitColumnAndJoin(df, lst_keys, sSplitCol, sDelim1, sDelim2):
    """
    Compound parsing of delimited Pandas column
    Split a DataFrame column into multiple columns and sub-split those strings to get variable name + values

    Inputs:
        df [Pandas DataFrame] DataFrame containing keycols, splitcol and possibly extraneous columns
            not involved with reshaping
        lst_keys [List of Strings] key column names uniquely identifying the original rows
        splitcol [String] name of column to be parsed
        sDelim1 [String] delimiter character string for initially splitting splitcol values
        sDelim2 [String] delimiter used for sub-splitting splitcol values

    Return: Reshaped DataFrame with keycols, a new ID col and splitcol as columns
            (Combo of keycols and new ID col uniquely identify each row)

    JDL 8/2/21
    """    
    #Set keys as index; split specified column into multiple columns having integer names
    df2 = df.set_index(lst_keys).copy()
    df2 = df2[sSplitCol].str.split(sDelim1, expand=True)
    
    #Iteratively sub-split integer-named columns; merge into combined DataFrame
    dfFinal = pd.DataFrame()
    for col in df2.columns:

        #Sub-split on the specified delimiter
        dftemp = df2[col].str.split(sDelim2, expand=True)

        #Use the first row's value as column name (Note: assumes same name for all rows)
        dftemp = dftemp.rename(columns={1:dftemp[0].iloc[0]})
        dftemp = dftemp.drop(0, axis=1)

        #Create a new DataFrame with expanded columns
        if dfFinal.index.size < 1:
            dfFinal = dftemp
        else:
            dfFinal = dfFinal.merge(dftemp,left_index=True, right_index=True)
    
    return dfFinal.reset_index(drop=False)


def JoinNonSplitStackCols(df_reshaped, df, lst_keys, splitcol):
    """
    Compound parsing of delimited Pandas column
    re-Join columns not invovled with Split/Stack reshaping

    Inputs:
        df_reshaped [Pandas DataFrame] DataFrame that has been Split/Stacked by parsing a column
        df [Pandas DataFrame] original non-reshaped version of data
        lst_keys [List of Strings] key columns in df and df_reshaped
        splitcol [String] name of parsed column in both df and df_reshaped

    Return: Reshaped DataFrame with original (non key and split) columns rejoined

    JDL 8/2/21
    """
    #Set the key columns as index; split and stack
    dftemp = df.copy().set_index(lst_keys)
    
    #drop the splitcol that was dealt with separately to make df_reshaped
    dftemp = dftemp.drop(splitcol, axis=1)
    
    #merge into df_reshaped
    df_out = df_reshaped
    if len(dftemp.columns) > 0:
        dfout = df_reshaped.merge(dftemp, how='left', left_on=lst_keys, right_index=True)
    return dfout

def SplitAndSubsplitDelimitedColumn(df, lstKeys, splitcol, lstDelim, sIDPrefix):
    """
    Compound parsing of delimited Pandas column
    Split a specified column on multiple delimiters and stack elements in single rows with ID columns

    JDL 8/10/21
    """
    dfShaped = df.copy()
    i = 1
    for delim in lstDelim:
        sID = sIDPrefix + str(i)
        dfShaped = SplitAndStack(dfShaped, lstKeys, splitcol, delim, sID)
        lstKeys.append(sID)
        i += 1
    return dfShaped, lstKeys

def PivotOnLastID(dfShaped, lstKeys, splitcol):
    """
    Compound parsing of delimited Pandas column
    Pivot split column data by the last (lowest level) ID to get params and values in separate columns


    JDL 8/10/21
    """    
    #Pivot on keys without last ID; creates separate param/value columns
    dfShaped = dfShaped.pivot(index=lstKeys[0:-1], columns=lstKeys[-1], values=splitcol)
    
    #Name the columns
    dfShaped.columns.name = None
    dfShaped.to_csv('temp2.csv')
    dfShaped.columns = ['param', 'value']

    #Drop the Param/Value ID from the index (param name and other keys fully identifies rows)
    return dfShaped.reset_index(level=dfShaped.index.names[-1], drop=True)

def UnstackLastSplit(dfShaped):
    """
    Compound parsing of delimited Pandas column
    Reshape a table with Key cols, ID cols from column split and param/value columns to 
    pivot the param names into columns containing the values

    Adds new ID column(s) to the list of Keys, which is also returned along with the reshaped DataFrame

    JDL 8/10/21
    """      
    #Move param column into the index
    dfShaped = dfShaped.set_index('param', append=True)

    #Unstack and clean up the resulting DataFrame
    dfShaped = dfShaped.unstack(level=-1)
    dfShaped = dfShaped.droplevel(0, axis=1)
    dfShaped.columns.name=None
    return dfShaped

def AddRowIncidence(df, lst_keys):
    """
    Add a column with incidence of specified key column values

    Inputs:
        df [Pandas DataFrame] DataFrame containing keycols
        lst_keys [List of Strings] key column names

    Return: DataFrame with row incidence column

    JDL 8/2/21
    """
    ser = df.groupby(lst_keys).size()
    ser.name = 'Row Incidence'
    dfcounts = ser.reset_index()
    return df.merge(dfcounts, how='left', left_on=lst_keys, right_on=lst_keys)

def DeleteNestedVariableBrackets(df, col):
    """
    Convert nested cells to dictionary (leaves empty list if no dict items)

    JDL 8/25/21
    """
    for sReplace, sWith in zip(['[{', '}]', '}]'], ['{', '}']):
        df[col] = df[col].astype(str).str.replace(sReplace, sWith, regex=False)
    return df

def EvalCol(df, col):
    """
    eval(x) converts string values to dict or list based on [] or {} delimiters/formatting

    JDL 8/25/21
    """
    df[col]=df[col].apply(lambda x:util.EvalAll(x))
    return df

def RenameDfFromKeepColDict(dict_names, df):
    """
    Subset DataFrame based on dictionary of keep names (keys) and new names (values)
    (Keeps variable with original name if dictionary value is empty string)

    JDL 8/30/21
    """
    
    #Return if no names dictionary
    if not isinstance(dict_names, dict): return df

    #Keep original variable name if dictionary value is empty string
    dnames = dict_names.copy()
    for key in dnames:
        if len(dnames[key]) < 1: dnames[key] = key
    
    #Drop any variables not in dictionary
    df = df[list(dnames.keys())]

    #Rename
    df = df.rename(dnames, axis=1)
    return df

def StackAndReindex(df_in, lstIndex, sNameStacked='Stacked Col', sNameCtIdx='Count Index'):
    """
    Stack DataFrame columns and reindex with a count column

    Inputs:
        df [Pandas DataFrame] DataFrame containing keycols and stack cols
        lst_keys [List of Strings] key column names
        sNameStacked [String] name of stacked column
        sNameCtIdx [String] Name of count index col post-stacking

    Return: Reshaped DataFrame with keycols + count index col as index

    JDL 10/2/21
    """
    df = df_in.reset_index(drop=True).copy()

    #Convert stack column names to integers
    lst = list(df.columns[0:len(lstIndex)]) + list(range(1, len(df.columns)-1))
    df.columns = lst

    #Set lst_index as index and stack
    dfs = df.set_index(lstIndex).stack().to_frame()
    dfs.columns = [sNameStacked]

    #Add the count name to the index
    dfs.index = dfs.index.rename(lstIndex + [sNameCtIdx])
    return dfs

def RecodeFlagColToBoolean(df, sCol):
    """
    Map  data 1/blank flag column to boolean type
    JDL 10/26/21 
    """
    #Map to True if original value is non-null
    if sCol not in df.columns: return df
    df[sCol] = df[sCol].map(lambda x: False if util.IsNullVal(x) else True)
    return df

def RecodeFlagColToOnes(df, sCol):
    """
    Map Boolean flag column to 1/blank (e.g. for writing efficiently in Excel)
    JDL 10/26/21
    """
    #Map True to 1; False to blank
    if sCol not in df.columns: return df
    df[sCol] = df[sCol].map(lambda x: 1 if x else np.nan)
    return df

def RecodeFlagColToOnesZeroes(df, sCol):
    """
    Map Boolean flag column to 1/0 (e.g. for selection in graphics software)
    JDL 4/26/21
    """
    #Map True to 1; False to blank
    if sCol not in df.columns: return df
    df[sCol] = df[sCol].map(lambda x: 1 if x else 0)
    return df


def BuildLstIntersect(df, lst_master):
    """
    Build a keep_cols list of just columns that are in a DataFrame
    JDL 3/29/22
    """
    lst_cols = list(df.columns)
    lst_iter = lst_master.copy() #Avoid disrupt iter with remove
    for col in lst_iter:
        if not col in lst_cols: lst_master.remove(col)
    return lst_master

def printdf(df):
    print('\n\n')
    print('\n\nsize:', df.index.size)
    print('\n\n', df, '\n\n')
