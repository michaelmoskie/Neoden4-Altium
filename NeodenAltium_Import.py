 

# It is important to note that this script will include your PTH components as well as your SMT components.
# You will need to later select which parts are skipped or not.
# Copyright 2018 Michael Moskie
from decimal import Decimal
import argparse
from argparse import RawTextHelpFormatter
import math
import matplotlib.pyplot as plt
import numpy as np
import copy

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
    def PlotData(self,_name ="Figure_1"):
        in_x = np.empty(0)
        in_y = np.empty(0)
        for comp in self.InputComps:
            in_x = np.append(in_x,comp.X)
            in_y = np.append(in_y,comp.Y)
        
        out_x = np.empty(0)
        out_y = np.empty(0)
        for comp in self.components:
            out_x = np.append(out_x,comp.X)
            out_y = np.append(out_y,comp.Y)

        fig, axs = plt.subplots(2)
        fig.suptitle('Vertically stacked subplots')
        axs[0].scatter(in_x, in_y)
        axs[1].scatter(out_x, out_y)
        plt.show()
        
    def rotate(self, ox, oy , px, py, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in degrees.
        """
        angle = math.radians(angle)

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy
    
    def MakeComponentList(self):
        counter = 0
        for line in self.AltiumOutputFile:
            if counter < 13:
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

    def MoveComponents(self,_x,_y):
        for comp in self.components:
            comp.X += _x
            comp.Y += _y

            
    def MoveComponents_SkipFirstComp(self,_move):
        counter = 0
        for comp in self.components:
            if(counter > _move[2]):
                comp.X += _move[0]
                comp.Y += _move[1]
            counter += 1

    def ApplyRotationToComponents(self,_rotation):
        for comp in self.components:
            RotatedCompPos = self.rotate(_rotation[0],_rotation[1],comp.X, comp.Y,_rotation[2])
            comp.X = RotatedCompPos[0]
            comp.Y = RotatedCompPos[1]

    def createOutputFile(self,_side):
        Filename_suffix = "-NEODEN-" + _side + ".csv"
        outputFile = open(self.AltiumOutputFile.name.replace(".csv",Filename_suffix), "w")
        outputFile.write("Designator,Footprint,Mid X,Mid Y,Layer,Rotation,Comment\n")
        outputFile.write(",,,,,,\n")
        for comp in self.components:
            if comp.Layer == _side:
                outLine = str(comp.Designator).replace("\"","") + "," + str(comp.Footprint).replace("\"","") + "," + str(round(Decimal(comp.X),2))+"mm" + "," + str(round(Decimal(comp.Y),2))+"mm" + "," + "T," + str(comp.Rotation).replace("\"","") + "," + comp.Comment.replace("\"","")
                outputFile.write(outLine + "\n")

    def __init__(self, fileName,_Side,_Offset,_Relative,_rotation,_plot,_move):
        self.AltiumOutputFile = open(fileName, "r")
        self.components :component = list()
        self.MakeComponentList()
        self.InputComps = copy.deepcopy(self.components)
        if _Relative:
            self.getDistancesFromFirstChip()
        if _rotation != None:
            self.ApplyRotationToComponents(_rotation)
        if _Offset:
            self.MoveComponents(_Offset[0],_Offset[1])
        if _move != None:
            self.MoveComponents_SkipFirstComp(_move)
        if _plot:
            self.PlotData()
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
# Ask whether all component posistions are relavtive to the first component
parser.add_argument('-p','--plot', action='store_true',
                    help='plot posisitions of component centers')
# Ask whether all component posistions are Rotate about a point
parser.add_argument('-a','--angle',nargs=3, type=float,
                    help="Rotate all components in list - this is a fixed Rotation\n" + \
                        "If argument is ommitted then no Rotation is appiled\n"+ \
                        "Example: \"-a 0 0 180\" - This will apply a rotation about point 0,0 with a rotation counterclockwise of 180")

parser.add_argument('-m','--move',nargs=3, type=float,
                    help="Move all components after N components\n" + \
                        "If argument is ommitted then no Rotation is appiled\n"+ \
                        "Example: \"-m 20 10 1\" - This will apply a move of X = 20 and Y=10 after the 1st component")

args = parser.parse_args()
#print("Argument values:")
#print(args.File)
#print(args.side)
#print(args.offset)
#print(args.relative)
if args.side != "TopLayer" and args.side != "BottomLayer" and args.side != None:
    print("Invalid Side input - please ensure the value is \"TopLayer\" or \"BottomLayer\"")

exitConverter = NeoDenConverter(args.File,args.side,args.offset,args.relative,args.angle,args.plot,args.move)

#if __name__ == "__main__":
#    print("Running From Main - DO NOTHING")
#    Converter = NeoDenConverter("Pick Place for 0-0091-03_BS4k_camera.csv",None,[0,0],False,[0,0,90],True)

