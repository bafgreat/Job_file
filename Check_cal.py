#!/usr/bin/python
import sys
import subprocess
import os
import glob
import csv
#import matplotlib.pyplot as plt
#from matplotlib.offsetbox import AnchoredText


'''if len(sys.argv) == 2:
    qcin = sys.argv[1]
    qc_base = qcin.split('.')[0]
else:
    print 'Incorrect filetype'
    sys.exit()'''

def get_contents(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()
    return contents

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return


def get_section(contents, start_key, stop_key, start_offset=0, stop_offset=0):
    for i, line in enumerate(contents):
        if  start_key in line:
            start_index = i + start_offset
            break
    for i in range(start_index, len(contents)):
        line = contents[i]
        if stop_key in line:
            stop_index = i + 1 + stop_offset
            break
    data = contents[start_index:stop_index]
    return  data

def Energetic_parameter(output):
    parameters = get_contents(output)
    for  line in parameters:
        if "Total Energy (hartree)" in line:
            Total = float(line.split()[3])
        elif "Total Mermin free energy:" in line:
            Total = float(line.split()[4])
    return Total



def Write(folder):
    f = open('Calculations_To_Complete' + '.csv', 'wb')
    w = csv.writer(f)
    for  files in folder:
        w.writerow([files])
    return

def  Collect(folder):
    List =[]
    base= os.getcwd()
    os.chdir(folder)
    All_folders = sorted(glob.glob('*/'))
    #print All_folders
    for folders in All_folders:
        base2= os.getcwd()
        os.chdir(folders)
        
        #Akward checking mechanism
        try:
            energy = Energetic_parameter('All.out')
            print folders, energy
        except:
            List.append(folders)

        os.chdir(base2)
    Write(List)
    
    return


Folder = raw_input("Please Enter Name of Folder:  ")
Collect(Folder)



