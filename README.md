
# Neoden4-Altium
Tested using Altium Version: 23.4.1
Used on Neoden 4

## Usage

- Export your Pick and Place file from Altium Designer with metric (mm) units as a .csv file

- Run this script with Python 3 or newer.

- Import the newly created ```Example.csv``` file using the UI on the machine, and proceed with the machine programming.
- Exported file/s will be placed in the `Output` folder

## Settings for Altium Pick and Place file export

Outputted Columns:

Designator,Comment,Layer,Footprint,Center-X(mm),Center-Y(mm),Rotation, Description\n\n" + \

Output Settings:

 - Unit = Metric
 - Show Units = False
 - Separator= .

Format Setting:
 - Format = CSV

Misc Setting:

 - Exclude Filter Parameters = Unticked
 - Include Variation Component = Unticked
 - Distinguish different footprint with the same name = Unticked 
 - Include Standard (No BOM) Items = Ticked 
 - Y-flip Bottom Side Components = Unticked


  

## Examples

### Help information
Get useful information on the program
```py neodenAltium.py -h"```
or
```py neodenAltium.py -help"```

  

### Import and apply Machine coordinates

1- Import File "Example.csv"

2- make all components relative to first component in list

3- apply machine positions


Command:

```py neodenAltium.py "Example.csv" -r -o 100 140```

  

### Import, Rotate components, Apply Machine coordinates

1- Import File "Example.csv"

2- Make all components relative to first component in list

4- Rotate components about a point 0,0 (X,Y) with an angle of 90 (Degrees)

3- Apply machine positions of 100, 140 (X,Y)


```py neodenAltium.py "Example.csv" -r -a 0 0 90 -o 100 140 ```

### Import, Rotate components, Apply Machine coordinates, Apply a component Move

1- Import File "Example.csv"

2- Make all components relative to first component in list

4- Rotate components about a point 0,0 (X,Y) with an angle of 90 (Degrees)

3- Apply machine positions of 100, 140 (X,Y)

4- Apply component move, skipping N number of components. move -10.043,5.3 (X,Y) skipping 1 component in list (Handy for shifting components within a panel, for example when the panel has been defined by the PCB fabrication house)


```py neodenAltium.py "Example.csv" -r -a 0 0 90 -o 100 140 -m -10.043 5.3 1```


## Program order of event

It's handy to know the order the parameter's are applied so you can get best use from the tool:

1- Apply relative component positions `-r` (Optional)

2- Apply board rotation about a rotation point `-a` (Optional)

3- Offset components - IE add machine positions `-o` (Optional)

4- Move components - skipping N number of component `-m` (Optional)

5- Plot resulted transformation in window `-p` (Optional)

6- Export file - layer can be defined `-s` (Optional layer argument)


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=michaelmoskie/Neoden4-Altium&type=Timeline)](https://star-history.com/#michaelmoskie/Neoden4-Altium&Timeline)
