 

# It is important to note that this script will include your PTH components as well as your SMT components.
# You will need to later select which parts are skipped or not.
# Copyright 2018 Michael Moskie
from decimal import Decimal
import argparse
from argparse import RawTextHelpFormatter

# Instantiate the parser
description_str = "--------Convert Altium Pick and Place file to Neoden 4 Format ---------\n\n\n" + \
"Settings for Altium Pick and Place file export:\n" + \
"Outputted Comlumns:\n" +\
    "\tDesignator,Comment,Layer,Footprint,Center-X(mm),Center-Y(mm),Rotation,Description\n\n" + \
"Output Settings:\n" +\
    "\tUnit = Metric\n" +\
    "\tShow Units = False\n" +\
    "\tSeparator= .\n\n" +\
"Format Setting:\n" +\
    "\tFormat = CSV\n\n" +\
"Misc Setting:\n" +\
    "\tExclude Filter Parameters = Unticked\n" +\
    "\tInclude Variation Component = Unticked\n" +\
    "\tDistinguish different footprint with the same name = Unticked\n" +\
    "\tInclude Standard (No BOM) Items = Ticked\n" +\
    "\tY-flip Bottom Side Components = Unticked\n\n"

parser = argparse.ArgumentParser(description=description_str,formatter_class=RawTextHelpFormatter)


class component:
    ##just a structure to represent a physical component
    def __init__(self, line):
        #"Designator","Comment","Layer","Footprint","Center-X(mm)","Center-Y(mm)","Rotation","Description"    
        temp = line.split(',')
        self.Designator = line.split(',')[0]
        self.Comment = line.split(',')[1]
        self.Layer = line.split(',')[2].replace("\"", "")
        self.Footprint = line.split(',')[3]
        self.X = float(line.split(',')[4].replace("\"", ""))
        self.Y = float(line.split(',')[5].replace("\"", ""))
        self.Rotation = line.split(',')[6]
        self.Description = line.split(',')[7]

class NeoDenConverter:
    def MakeComponentList(self):
        counter = 0
        for line in self.AltiumOutputFile:
            if(counter < 13):
                #throw away the header.
                pass
            else:
                self.components.append(component(line))
            counter += 1

    def getDistancesFromFirstChip(self):
        FirstChipX = 0
        FirstChipY = 0
        counter = 0
        for comp in self.components:
                if(counter == 0):
                    #this is the first component
                    FirstChipX = comp.X
                    FirstChipY = comp.Y
                    comp.X = 0
                    comp.Y = 0
                else:
                    comp.X = float(comp.X) - float(FirstChipX)
                    comp.Y = float(comp.Y) - float(FirstChipY)
                counter += 1

    def ApplyMachinePositionsToComponents(self,_x,_y):
        for comp in self.components:
            comp.X += _x
            comp.Y += _y

    def createOutputFile(self,_side):
        Filename_suffix = "-NEODEN-" + _side + ".csv"
        outputFile = open(self.AltiumOutputFile.name.replace(".csv",Filename_suffix), "w")
        outputFile.write("Designator,Footprint,Mid X,Mid Y,Layer,Rotation,Comment\n")
        outputFile.write(",,,,,,\n")
        for comp in self.components:
            if comp.Layer == _side:
                outLine = str(comp.Designator).replace("\"","") + "," + str(comp.Footprint).replace("\"","") + "," + str(round(Decimal(comp.X),2))+"mm" + "," + str(round(Decimal(comp.Y),2))+"mm" + "," + "T," + str(comp.Rotation).replace("\"","") + "," + comp.Comment.replace("\"","")
                outputFile.write(outLine + "\n")

    def __init__(self, fileName,_Side,_Offset,_Relative):
        self.AltiumOutputFile = open(fileName, "r")
        self.components = list()
        self.MakeComponentList()
        if _Relative:
            self.getDistancesFromFirstChip()
        if _Offset:
            self.ApplyMachinePositionsToComponents(_Offset[0],_Offset[1])
        if _Side == None:
            self.createOutputFile("TopLayer")
            self.createOutputFile("BottomLayer")
        elif _Side == "TopLayer":
            self.createOutputFile("TopLayer") 
        elif _Side == "BottomLayer":
            self.createOutputFile("BottomLayer") 

# Required positional argument
parser.add_argument('File', type=str,
                    help='Input Pick and Place File (Output file from Altium)')
# Required positional argument
parser.add_argument('-s','--side', type=str,
                    help="Select which side of the Pick and Place file is needed\n" + \
                        "*If argument is ommitted then two files will be generated for both Top and Bottom Sides*\n"
                        "Options:\n" + \
                        "\t\"TopLayer\" = Top Layer \n" + \
                        "\t\"BottomLayer\" = Bottom Layer\n"+\
                        "Example: \" -s \"TopLayer\" \" - This will export file for all components on the Top Layer" )
# Ask whether to offsets should be appied or not
parser.add_argument('-o','--offset',nargs=2, type=float,
                    help="Apply a Offset to all components in list - this is a fixed offset\n" + \
                        "If argument is ommitted then no Offset is appiled\n"+ \
                        "Example: \"-o 100 140\" - This will apply a Offset in X of 100 and Offset in Y of 140")

# Ask whether all component posistions are relavtive to the first component
parser.add_argument('-r','--relative', action='store_true',
                    help='Set posisition of all components relative to the first component in list')

args = parser.parse_args()
#print("Argument values:")
#print(args.File)
#print(args.side)
#print(args.offset)
#print(args.relative)
if args.side != "TopLayer" and args.side != "BottomLayer" and args.side != None:
    print("Invalid Side input - please ensure the value is \"TopLayer\" or \"BottomLayer\"")

exitConverter = NeoDenConverter(args.File,args.side,args.offset,args.relative)
