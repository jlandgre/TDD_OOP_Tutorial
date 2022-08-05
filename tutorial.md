This shares a case study using the combination of test-driven design (TDD) and object-oriented programming (OOP) in Python coding projects. While both are individually great, in my opinion, there is insufficient discussion online and in tutorials about how to pragmatically use them together. There is tremendous synergy from this.

#### Introduction
It is one thing to know how to code classes aka objects in Python. It is another to know the TDD approach of writing a pytest test first and then writing the project code to pass the test. From experience though, there is magic in putting the two together –having each test validate a single-action class method and where simply calling the methods in order completes the procedural job-to-be-done of transforming some data or running a model. In consulting work, this has been wonderful for efficiently creating Python (and VBA) code that is easy to revisit and update later.

Using OOP gathers a topic’s methods and attributes together in a way that purely procedural code does not. Using TDD removes any future question about the program getting broken by changes. The TDD tests serve as part of the project's documentation and await being re-run at any time. Personally, I wish I had discovered this combo 20 years ago during my career as an R&D engineer. Certainly, I have always validated my models, but too often not in a way where it’s easy for myself or others to later extend the model or to re-ascertain that it is giving correct results. The TDD/OOP combo (Let’s call this “Tuhdoop” I guess?) has recently taken my working efficiency to a new level.

#### TDD/OOP Case Study
A simple data transformation makes a good case study. With TDD/OOP we simultaneously build tests and a Python class to do the job. Our case study is based on a real world client question requiring urgent turnaround. The business context was to search for malfunctioning internet-connected consumer devices in market. We recommended doing this by looking for outliers in measured consumption from a refillable reservoir in each device. The consumer uses an on-device **intensity** setting to control the rate. The picture shows mockup data, which is intentionally constructed to include edge cases and to resemble the project's AWS raw, event data from the device. The test data is 40 rows from 3 devices. The production data is a few million rows on thousands of in-market devices.

<p align="center">
  Raw Data Mockup for Testing</br>
  <img src=images/data.png "non-transformed raw data" width=400></br>
</p>

The **refill_percent** column logs level remaining in a reservoir that devices deplete as they run.  The data contain unrelated events represented by rows that are blank in columns 3 and 4. In production data, there are other populated columns associated with these rows.

The **intensity** variable reports changes in a user controlled setting. Intensity sets consumption rate for the device. In properly-functioning devices, the time per **refill_percent** decrement should strongly correlate to intensity, but the client asked to look for devices that might be malfunctioning in market. We guided looking for these by looking for outliers in this correlation.

The business question is a a reasonable one, right? Is everything ok in market? Not so fast though! The event-based raw data doesn’t align **intensity** reporting with the **refill_percent** reporting, so there’s work to do to answer. Once an intensity value is reported, it describes the device’s state until another event indicates a change. The data transform goal is to align **intensity** events with subsequent **refill_percent** events. Elemental steps for this are:

#### Data Transformation Steps
1.	Add a copy of the **intensity** column, **intensity_aligned**, to hold the transformed data
2.	If there doesn’t happen to be an initial **intensity** event for a device’s data, add a dummy value, ‘999’, as a marker at each device change in data sorted by device and timestamp. This makes it possible to just fill down without propagating one device’s **intensity** settings into the next device’s rows.
3.	Fill **intensity** down to populate it for all rows including the populated **refill_percent** rows
4.	Clear unneeded **intensity_aligned** rows where **refill_percent** is not populated
5.	Make a summary of consumption-weighted intensity by device

For completeness , here is the deeper analysis [not described in detail here] enabled by the transformed data:</br>
* To answer the client’s question about potentially-malfunctioning devices, we calculated time per **refill_percent** decrement and plotted this versus **intensity_aligned**. This let us look for outliers whose consumption didn’t make sense relative to intensity setting.
* For limiting case consumers who kept their devices always on, we fit a regression model to get a concise, quantitative description of consumption versus intensity. This also allowed us to characterize the fraction of time non limiting case devices are running.

<p align="center">
  Transformed Data With Intensity Aligned To refill_Percent</br>
  <img src=images/data_transformed5.png "transformed data" width=600></br>
</p>

#### Coding The Project - Intro
With that valuable pre-planning, we are ready to do the work. The working canvas is to initialize an **align_intensity.py** and **test_align_intensity.py** files side by side in an IDE such as VS Code shown here. Before describing the coding, it is worth mentioning a few, sanity-inducing conventions used for such projects.

<p align="center">
  VSCode *.py / test.py Canvas for Working</br>
  <img src=images/code_initial.png "*.py/test.py canvas"></br>
</p>

Both the align_intensity.py and test_align_intensity.py files have preamble code to orient to the project’s sub-directories and enable importing utility libraries and working with data files. I use a standard sub-directory structure in all projects and use the **scriptsfiles.py** utility to instance a 'files' class holding all file locations --essentially an inventory listing any project file and its path. This eliminates needing to embed these things into our class or its testing. The scriptsfiles **IsTest** argument makes it a breeze to toggle from testing to working with production files.

<p align="center">
  Project directory tree structure
</p>

```
OOP_TDD_Example                   << Overall Project folder
├── oop_example_data              << Production data (if local)
└── oop_example_scripts
    ├── align_intensity.py
    ├── libs                      << Generic utilities and file locations
    │   ├── dirpathutil.py
    │   ├── scriptsfiles.py       <<Project file names and directory paths
    │   └── util.py
    └── tests
        ├── data.csv                <<Test data
        └── test_align_intensity.py
```

As needed by pytest, the tests file imports the associated py file as a library. I use @pytest. fixtures to instance file locations and to create an instance of the **SummIntensityByDecr** class we need to code. For those new to using pytest, fixtures eliminate needing to repeat these steps in multiple tests.

A caveat worth mentioning is that, although the author has a successful consulting business based on decades of domain knowledge and modeling expertise, his Python knowledge is a work in progress. What's described here works well for helping clients, but the author is well aware that it is not the final answer!

#### TDD/OOP Cycles
The work from here is pretty executional and can be pleasantly boring. Namely, we write a test to check that a transformation or calculation step occurred. Write a class method to pass the test. Rinse and repeat. This makes it possible to walk away from a project and later return and keep going without a big re-start time. The GitHub project includes the intermediate files in its **demo files** folder.

As an example of the cycle, here is a first test for adding the needed intensity_aligned column —possibly overdoing the testing just a bit as an illustration. This test fails initially, but we then add the class method to copy the column and pass. TDD purists say that the bar is low on this method’s code. Just do the minimum to pass the test. We can refactor it later to our heart’s content and make it nice.

<p align="center">
  In test_align_intensity.py
</p>

```
    <<<other fixtures load data and instance align class>>

    @pytest.fixture
    def cols_input():
        return ['device_id', 'timestamp', 'refill_percent', 'intensity']

    def test_AddColumn(align, cols_input):
        """
        Copy intensity column to what will be the aligned column
        """
        align.AddIntensityAlignedCol()
        assert list(align._dfC.columns) == cols_input + ['intensity_aligned']
        lst_orig = list(align._dfC['intensity'].values)
        lst_new = list(align._dfC['intensity_aligned'].values)
        assert util.LstEquals(lst_orig, lst_new)

```
<p align="center">
  In align_intensity.py
</p>

```
    def __init__(self, dfC_input):
        self._dfC = dfC_input

    def AddIntensityAlignedCol(self):
        """
        Add a copy of intensity to be aligned with refill_percent
        """
        self._dfC['intensity_aligned'] = self._dfC['intensity']

```

This add-a-column example shows personal strategies for checking DataFrame structure and contents. A bit of judgement is justified. If the method is just a column copy, it’s sufficient to just verify that the new column is in df.columns (first assert statement). For something more complex, it is a good idea to verify number of rows, index and even individual data values with assert statements. SciPy2022 included an excellent tutorial on the [hypothesis](https://github.com/HypothesisWorks/hypothesis) Python library. It is designed to supplement **pytest** and creates a wide variety of “property-based” tests. Hypothesis is worth incorporating into future testing.

That’s it. Just repeat this cycle of writing tests and methods for the above list of steps until we have validated class methods for all procedural steps. Finally, I typically add and validate an @property function that runs all steps and returns the work product such as the transformed DataFrame or by-device summary in this example. As with many data transform examples, we don’t plan to “live” in this class doing extended work. Nor do we need to instance it for doing work elsewhere. We merely want to spit out the result and get on with statistical analysis.

<p align="center">
  Pytest Command Line Results For Finished Project
</p>

```
  $ pwd
  xxx/OOP_TDD_Example/oop_example_scripts/tests

  $ python -m pytest test_align_intensity.py -v -s
  ======== test session starts ========
  platform darwin -- Python 3.8.8, pytest-6.2.3, py-1.10.0, pluggy-0.13.1 -- xxx/opt/anaconda3/bin/python
  cachedir: .pytest_cache
  rootdir: xxx/OOP_TDD_Example/oop_example_scripts/tests
  plugins: anyio-2.2.0
  collected 10 items      

  test_align_intensity.py::test_ser_summ_intensity_property PASSED
  test_align_intensity.py::test_SummarizeIntensityByDevice PASSED
  test_align_intensity.py::test_ClearUnneededValues PASSED
  test_align_intensity.py::test_UpdateFilters_final PASSED
  test_align_intensity.py::test_FillDownDecrIntensity PASSED
  test_align_intensity.py::test_PopulateDeviceChangeRows PASSED
  test_align_intensity.py::test_UpdateFilters_initial PASSED
  test_align_intensity.py::test_AddColumn PASSED
  test_align_intensity.py::test_files_fixture PASSED
  test_align_intensity.py::test_TestData PASSED

  ======== 10 passed in 0.63s ========
  $
```

#### Side notes
There is one, Pandas elegance here worth highlighting. It is avoiding the temptation to loop through the rows with **df.iterrows** to find the device-change rows. Instead, our class uses the **.shift** function in a Pandas filter for device-change rows. Either approach performs ok in the 40-row test data, but iterrows is painfully slow with millions of rows. Our code is concise and scales well for good performance.

<p align="center">
  Loop-free Approach to Filter to Device-Change Rows
</p>

```
#Device change rows
self.fil_dev_change = self._dfC['device_id'] != self._dfC.shift(1)['device_id']
```

The second side note is that predictable code structure saves time and flailing around to find things. As you work, you may find it helpful to organize both test.py and class.py files in reverse “rolling scroll” order. This puts current work near the top of the files and saves a lot of searching and scrolling while debugging.

Once the work is done, you can re-order the class.py file such as intensity_aligned.py here to put property functions just below the \__init__ function You can order method functions in procedural order as much as possible. We find that it also helps clarity to initialize ALL attributes in \__init__ even if they are not used until later in the class methods. This leads to \__init__ being a transparent list of attributes and the @properties being a transparent, ordered listing of procedure(s) as run by class methods.


  J.D. Landgrebe
  Data Delve LLC
