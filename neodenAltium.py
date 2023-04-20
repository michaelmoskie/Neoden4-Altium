# It is important to note that this script will include your PTH components as well as your SMT components.
# You will need to later select which parts are skipped or not.
# Copyright 2018 Michael Moskie
import sys
from decimal import Decimal
import argparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Convert Altium Pick and Place file to Neoden 4 Format')


class component:
    ##just a structure to represent a physical component
    def __init__(self, line):
        #Designator,Footprint,Mid X,Mid Y,Layer,Rotation,Comment
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

    def ApplyMachinePositionsToComponents(self):
        for comp in self.components:
            comp.X += self.firstChipPhysicalX
            comp.Y += self.firstChipPhysicalY

    def createOutputFile(self,_side):
        Filename_suffix = "-NEODEN-" + _side + ".csv"
        outputFile = open(self.AltiumOutputFile.name.replace(".csv",Filename_suffix), "w")
        if self.IncHeader == True:
            outputFile.write("#Feeder,Feeder ID,Type,Nozzle,X,Y,Angle,Footprint,Value,Pick height,Pick delay,Place Height,Place Delay,Vacuum detection,Threshold,Vision Alignment,Speed,,,,,,,,,,,,,\n")
            outputFile.write("stack,1,0,1,409.54,89.6,90,,,0.5,20,0,50,No,-40,1,70,4,50,80,No,No,-40,-40,-40,-40,0,0,0,0\n")
            outputFile.write(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("pcb,Manual,Trace,100,100,304.58,333.94,Front,10,10,0,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("mark,Whole,Auto,20.00,20.00,,,,,,,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("markext,0,0.8,2,1,0,,,,,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("test,No,,,,,,,,,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("mirror_create,1,1,100.00,130.00,0,0,110.0,150.00,0.0,,,,,,,,,,,,,,,,,,,,\n")
            outputFile.write("mirror,266.88,138.81,0,No,,,,,,,,,,,,,,,,,,,,,,,,,\n")
        outputFile.write("#SMD,Feeder ID,Nozzle,Name,Value,Footprint,X,Y,Rotation,Skip,,,,,,,,,,,,,,,,,,,,\n")
        #outputFile.write(",,,,,,\n")
        for comp in self.components:
            if comp.Layer == _side:
                #SMD,Feeder ID,Nozzle,
                outLine = "comp,,," + \
                    str(comp.Designator).replace("\"","") + "," + \
                    str(comp.Comment.replace("\"","")) + "," + \
                    str(comp.Footprint).replace("\"","") + "," + \
                    str(round(Decimal(comp.X),3)) + "," + \
                    str(round(Decimal(comp.Y),3)) + "," + \
                    str(comp.Rotation).replace("\"","") + \
                    ",,"
                #outLine = str(comp.Designator).replace("\"","") + "," + str(comp.Footprint).replace("\"","") + "," + str(round(Decimal(comp.X),2))+"mm" + "," + str(round(Decimal(comp.Y),2))+"mm" + "," + "T," + str(comp.Rotation).replace("\"","") + "," + comp.Comment.replace("\"","")
                outputFile.write(outLine + "\n")

    def __init__(self, fileName,_Side,_IncHeader,_Offset,_Relative):
        self.AltiumOutputFile = open(fileName, "r")
        self.Side = _Side
        self.IncHeader = _IncHeader
        self.Offset = _Offset
        self.Relative = _Relative
        self.components = list()
        self.MakeComponentList()
        if self.Relative:
            self.getDistancesFromFirstChip();
        if self.Offset:
            self.firstChipPhysicalX = float(input("Enter the machine X coordinate of component " ))
            self.firstChipPhysicalY = float(input("Enter the machine Y coordinate of component " ))
            self.ApplyMachinePositionsToComponents()
        if self.Side == None:
            self.createOutputFile("TopLayer")
            self.createOutputFile("BottomLayer")
        elif self.Side == "TopLayer":
            self.createOutputFile("TopLayer") 
        elif self.Side == "BottomLayer":
            self.createOutputFile("BottomLayer") 

#if(sys.argv[1]):
#    Converter = NeoDenConverter(sys.argv[1])

# Required positional argument
parser.add_argument('File', type=str,
                    help='Input Pick and Place File (Output file from Altium)')
# Required positional argument
parser.add_argument('--Side', type=str,
                    help='Select which side of the Pick and Place file is needed (TopLayer/BottomLayer) \n If excluded both Top and Bottom Files will be generated')
# Add header information
parser.add_argument('--IncHeader', action='store_true',
                    help='Include the blank Feeder header outline at the start of the CSV File')
# Ask whether to offsets should be appied or not
parser.add_argument('--Offset', action='store_true',
                    help='Ask if the tool should inquire whehter to apply component offsets or not')

# Ask whether all component posistions are relavtive to the first component
parser.add_argument('--Relative', action='store_true',
                    help='if set, all component are relative to the first component in list')

args = parser.parse_args()
print("Argument values:")
print(args.File)
print(args.Side)
print(args.IncHeader)
print(args.Offset)
print(args.Relative)
Converter = NeoDenConverter(args.File,args.Side,args.IncHeader,args.Offset,args.Relative)

#if __name__ == "__main__":
#    print("Running From Main - DO NOTHING")
#    Converter = NeoDenConverter("Pick Place for BS4K_AARDVARKINTERFACE.csv",None,True,True,False)
