#!/usr/bin/python
"""
Function for extracting data from SCM rkf files
"""
__name__ ="MOF.structure"
__author__ = "Dinga Wonanke"
#!/bin/python
from email import contentmanager
import os
import sys
import numpy as np
from ase import Atoms
import glob


    
def get_contents(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()
    return contents

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return


def get_section(contents, start_key, stop_key, start_offset=0, stop_offset=0):
    all_start_indices = []
    for i, line in enumerate(contents):
        if  start_key in line:
            all_start_indices.append(i + start_offset)
    start_index = all_start_indices[-1]
    for i in range(start_index, len(contents)):
        line = contents[i]
        if stop_key in line:
            stop_index = i + 1 + stop_offset
            break
    data = contents[start_index:stop_index]
    return  data
    
    
    
def ADFOUT(qcin):
    qc_input = get_contents(qcin)
    coords=[]
    lattice=[]
    symbol =[]
   
    
    cods = get_section(qc_input, 'Index Symbol   x (angstrom)   y (angstrom)   z (angstrom)', 'Lattice vectors (angstrom)', 1, -2)

    for  lines in cods:
        data = lines.split()
        symbol.append(data[1])
        coords.append([float(i) for i in data[2:]])
    
    #TV = ['Tv', 'Tv', 'Tv']
    lat_index = 0
    for i, line in enumerate(qc_input):
        data = line.split()
        lattice.append(data)
        if 'Lattice vectors (angstrom)' in line:
            lat_index = i

    Parameters = [lattice[lat_index+1], lattice[lat_index+2], lattice[lat_index+3]]
    cell_vector = [[float(i) for i in data[1:]] for data in Parameters]
   
    ase_atom = Atoms(symbols=symbol, positions=coords,cell=cell_vector,  pbc=True)

    return ase_atom
    

def convert_to_cif(src_folder, dst_folder):
    seen = [ i.split("/")[-1].split('.')[0] for i in  glob.glob('dst_folder/*cif')]
    for folder in src_folder:
        base_name = folder.split("/")[-1]
        if not base_name in seen:
            
            print (base_name)
            ase_atom =ADFOUT(folder+'/'+base_name+'.out')
            ase_atom.write(f"{dst_folder}/{base_name}.cif")

#dst_folder = '/data/horse/ws/diwo093e-MOFs/GFN_CIFs'
#
#src_folder = glob.glob("/data/walrus/ws/diwo093e-MOFDATA/diwo093e-MOFdata/100_250/*")
##src_folder = glob.glob("/data/walrus/ws/diwo093e-MOFDATA/diwo093e-MOFdata/200_more/AB*")

dst_folder = 'GFN_CIFs'
src_folder = glob.glob("MOFData/*")
convert_to_cif(src_folder, dst_folder)


