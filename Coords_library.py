#!/bin/python
import numpy as np
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

def ASE_coordinate(filename):
    from  ase.io import read, write
    from ase import Atom, Atoms
    molecule = read(filename)
    atoms = Atoms(molecule)
    Cell= atoms.get_cell(complete=True)
    elements = atoms.get_chemical_symbols()
    positions = atoms.get_positions()
    Coords = []
    for ele, xyz in zip(elements, positions):
        cods = '\t'.join([ele]+[str(i) for i in xyz])
        Coords.append(cods)
    lattice =[]
    for i in range(3):
        a = [' '] + [str(i) for i in Cell[i]]
        b = '\t'.join(a)
        lattice.append(b)
    return Coords, lattice
    

def GJF(File):
    qc_input = get_contents(File)
    Lines=[]
    for line in qc_input:
        Lines.append(line.split())
    coords=[]
    lattice =[]
    ASE_line = Lines[2]
    if not 'ASE' in ASE_line:
        for row in  Lines[6:]:
            if len(row)>0:
                if not 'Tv' in row:
                    b = '\t'.join(row)
                    coords.append(b)
                else:
                    b = '\t'.join(row[1:])
                    lattice.append(b)
            else:
                break
    else:
        for row in  Lines[5:]:
            if len(row)>0:
                if not 'TV' in row:
                    b = '\t'.join(row)
                    coords.append(b)
                else:
                    b = '\t'.join(row[1:])
                    lattice.append(b)
            else:
                break
        
    return coords, lattice
    
def XYZ(File):
    lattice =[]
    qc_input = get_contents(File)
    coords=[]
    Lines=[]
    for line in qc_input:
        Lines.append(line.split())
    for row in  Lines[2:]:
        a = [' '] + row
        b = '\t'.join(a)
        coords.append(b)
    return coords
    
def Verdict(qcin):
    qc_input = get_contents(qcin)
    verdict = ''
    for line in qc_input:
        if 'Lattice vectors (angstrom)' in line:
            verdict = 'True'
            break
    return verdict

def ADFOUT(qcin):
    qc_input = get_contents(qcin)
    verdict = Verdict(qcin)
    coords=[]
    Lattice =[]
    lattice=[]
    Len = []
    new_input = []

    if verdict == 'True':
    
        cods = get_section(qc_input, 'Index Symbol   x (angstrom)   y (angstrom)   z (angstrom)', 'Lattice vectors (angstrom)', 1, -2)

        for  lines in cods:
            data = lines.split()
            Len.append(data[0])
            b = '\t'.join(data[1:])
            coords.append(b)
        length = str(len(Len))
        
        #TV = ['Tv', 'Tv', 'Tv']
        lat_index = 0
        for i, line in enumerate(qc_input):
            data = line.split()
            lattice.append(data)
            if 'Lattice vectors (angstrom)' in line:
                lat_index = i

        Parameters = [lattice[lat_index+1], lattice[lat_index+2], lattice[lat_index+3]]

        for  line in Parameters:
            a = line[1:]
            if len(a) > 2:
                b = '\t'.join(a)
                Lattice.append(b)
                
    else:
        cods = get_section(qc_input, 'Index Symbol   x (angstrom)   y (angstrom)   z (angstrom)', 'Total System Charge', 1, -2)
        for  lines in cods:
            data = lines.split()
            Len.append(data[0])
            b = '\t'.join(data[1:])
            coords.append(b)
        length = str(len(Len))
        Lattice =['']
    return coords, Lattice


def Qchemcout(qcin):
    qc_input = get_contents(qcin)
    cods = get_section(qc_input, 'OPTIMIZATION CONVERGED', 'Z-matrix Print:', 5, -2)
    #cods = get_section(qc_input, '$molecule', '$end', 2, -1)
    coords=[]
    for row in cods:
        data = row.split()
        b = '\t'.join(data[1:])
        coords.append(b)
    return coords

def Qchemin(qcin):
    qc_input = get_contents(qcin)
    coords = get_section(qc_input, '$molecule', '$end', 2, -1)
    return coords

def Format_coords(coords, atom_types):
    coordinates =[]
    #file_obj.write('%d\n\n' %len(atom_types))
    for labels,row in zip(atom_types,coords):
        b = [labels] + [str(atom)+' ' for atom in row]
        printable_row = '\t'.join(b)
        coordinates.append(printable_row + '\n')
    return coordinates



def Coords(filename):
    print (filename)
    #Robust algorithm for finding file extention (check)
    import re
    iter = re.finditer('\.', filename)
    check = [filename[i.span()[0]+1:] for i in iter ][-1]
    coords, lattice = [],[]
    #check = filename.split('.')[1]
    if check == 'gjf':
        coords, lattice = GJF(filename)
    elif check =='xyz':
        coords =XYZ(filename)
    elif check =='out':
         coords, lattice = ADFOUT(filename)
    elif check =='cout':
         coords= Qchemcout(filename)
    elif check =='cin':
         coords= Qchemin(filename)
    else:
        coords, lattice = ASE_coordinate(filename)
         
    return coords, lattice

def Collect_coords(File):
    coords, lattice = Coords(File)
    elements = []
    positions =[]
    cell = []
    for lines in coords:
        data = lines.split()
        elements.append(data[0])
        positions.append([float(i) for i in data[1:]])
        
    positions = np.array(positions)
    
    if len(lattice)!=0:
        cell = np.array([[float(i) for i in j.split()] for j in lattice])
    
    return elements, positions,cell

def New_coords(coords, atom_types):
    coordinates =[]
    #file_obj.write('%d\n\n' %len(atom_types))
    for labels,row in zip(atom_types,coords):
        b = [labels] + [str(atom)+' ' for atom in row]
        printable_row = '\t'.join(b)
        coordinates.append(printable_row + '\n')
    return coordinates
