#version 7/13/22
import numpy as np

class SummIntensityByDecr():
    """
    Training example with mocked up data
    
    This class populates intensity values aligned onto populated refill
    percent rows (except for initial device rows where the device's 
    intensity is unknown).  Previously-reported  intensity applies to a
    subsequent refill percent row
    
    JDL 7/13/22
    """
    def __init__(self, dfC_input):
        self._dfC = dfC_input
        
        #Initialize filters (Use self.UpdateFilters() to refresh after changes):
        self.fil_null_alignedintensity = None   #Null perfume_intensity rows
        self.fil_null_refperc = None     #Null Refill percent rows
        self.fil_dev_change = None       #Device change rows
        self._serSummIntensity = None   #By-device intensity summary (Pandas Series)

    @property
    def ser_summ_intensity(self):
        """
        Summarize intensity by device (weighted by consumption/decrements)
        """
        self.TransformProcedure()
        self.SummarizeIntensityByDevice()
        return self._serSummIntensity
    
    @property
    def dfC(self):
        """
        Construct transformed dfC
        """
        self.TransformProcedure()
        return self._dfC

    def TransformProcedure(self):
        """
        Run all data transform methods as procedure
        """
        self.AddIntensityAlignedCol()
        self.UpdateFilters()
        self.PopulateDeviceChangeRows()
        self.FillDownDecrIntensity()
        self.UpdateFilters()
        self.ClearUnneededValues()

    def AddIntensityAlignedCol(self):
        """
        Add a copy of intensity to be aligned with refill_percent
        """
        self._dfC['intensity_aligned'] = self._dfC['intensity']

    def UpdateFilters(self):
        """        
        Filters used in sub-functions
        """        
        #Null Refill percent rows
        self.fil_null_refperc = self._dfC['refill_percent'].isnull()        
        
        #Null intensity rows         
        self.fil_null_intensity = self._dfC['intensity_aligned'].isnull()
        self.fil_null_alignedintensity = self._dfC['intensity_aligned'].isnull()

        #Device change rows
        self.fil_dev_change = self._dfC['device_id'] != self._dfC.shift(1)['device_id']

        #Intensity rows with 999 marker
        self.fil_999 = self._dfC['intensity_aligned'] == 999.
                
    def PopulateDeviceChangeRows(self):
        """
        Set 999 value to mark intensity_aligned for non-null device change rows
        """
        fil = self.fil_null_alignedintensity & self.fil_dev_change
        self._dfC.loc[fil, 'intensity_aligned'] = 999.

    def FillDownDecrIntensity(self):
        self._dfC['intensity_aligned'] = self._dfC['intensity_aligned'].ffill()

    def ClearUnneededValues(self):
        self.UpdateFilters()
                
        #Clear values from rows that are not populated refill percents
        self._dfC.loc[self.fil_null_refperc, 'intensity_aligned'] = np.nan

        #Clear 999 markers
        self._dfC.loc[self.fil_999, 'intensity_aligned'] = np.nan
    
    def SummarizeIntensityByDevice(self):
        self.summ = self._dfC[~self.fil_null_refperc].groupby('device_id')
        self._serSummIntensity = self.summ['intensity_aligned'].mean().round(2)