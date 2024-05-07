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
import matplotlib.pyplot as plt
from kftools import KFFile

    
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

    return symbol, coords, cell_vector #ase_atom
    
def Normal_mode_displacement(file_data, index, add_index):
    displacement =[]
    for i in add_index:
        data = file_data[i+index]
        displacement.append([float(j) for j in data[2:]])
    return displacement
        
def Normal_mode_displacement2(file_data, index, atom_index):
    displacement = [float(i) for i in file_data[atom_index +index][2:]]

    return displacement
        
    
    
def Grab_Displacement_coord(qcin):
    qc_input = get_contents(qcin)
    Freq_index = []
    Freqencies =[]
    file_data = []
    Hessians = []
    try:
        cods = get_section(qc_input, 'Index Symbol   x (angstrom)   y (angstrom)   z (angstrom)', 'Lattice vectors (angstrom)', 1, -2)
    except:
        cods =  get_section(qc_input, 'Index Symbol   x (angstrom)   y (angstrom)   z (angstrom)', 'Total System Charge', 1, -2)
    
    add_index = range(1, len(cods)+1)
    
    #Find Index of frequency lines
    for i, lines in enumerate(qc_input):
        data = lines.split()
        file_data.append(data)
        if ' Index  Atom      ---- Displacements (x/y/z) ----' in lines:
            Freq_index.append(i)
  
    Freqencies = [float(file_data[i-1][4]) for i in Freq_index]

    for index in Freq_index:
        mode  = Normal_mode_displacement(file_data, index, add_index)
        Hessians.append(mode)
  
    Hessians = np.array(Hessians)

    
    return Hessians, Freqencies

def RKF_Hessian (rkf_file):
    content = KFFile(rkf_file+'/dftb.rkf')
    AMSRESULT =content.read_section('AMSResults')
    number_atoms = content.read_section('Molecule')['nAtoms']
    nxn = 3*number_atoms
    hessian = np.array(AMSRESULT['Hessian']).reshape(nxn,nxn)
    Hess_to_file = ['\t'.join([str(i) for i in cod]+['\n']) for cod in hessian]
    
    return hessian.tolist() #, Hess_to_file


def Bandstructure(rkf_file):
    Band ={}
    content = KFFile(rkf_file+'/dftb.rkf')
    BandStructure =content.read_section('BandStructure')
    Band['BandGap'] = BandStructure['BandGap']
    Band['HasGap'] = BandStructure['HasGap']
    Band['nBand'] = BandStructure['nBand']
    Band['bandsEnergyRange'] = BandStructure['bandsEnergyRange']
    Band['FermiEnergy'] = BandStructure['FermiEnergy']
    Band['FermiEnergy'] = BandStructure['FermiEnergy']
    return Band

    
