#!/usr/bin/python
import re
import sys
import subprocess
import os
import glob
import csv


if len(sys.argv) == 2:
    qcin = sys.argv[1]
    qc_base = qcin.split('.')[0]
else:
    print ('Incorrect filetype')
    sys.exit()

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

def CSV_reader(file):
    f = open(file, 'r')
    data = csv.reader(f)
    return data

def Verdict(qcin):
    qc_input = get_contents(qcin)
    verdict = ''
    for line in qc_input:
        if 'Lattice vectors (angstrom)' in line:
            verdict = 'True'
            break
    return verdict

def remove_digits_at_start(input_string):
    pattern = re.compile(r'\b\d+([a-zA-Z])')
    result = pattern.sub(r'\1', input_string)
    return result



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

def OPt(name):
    qc_base = name.split('.')[0]
    coords, lattice = ADFOUT(name)
    New_input = []
    New_input.append("#!/bin/sh\n")
    New_input.append('\n')
    New_input.append('$AMSBIN/ams << eor\n\n')
    New_input.append(' Task GeometryOptimization \n')
    New_input.append(' Properties \n')
    New_input.append('     NormalModes No \n')
    New_input.append('  End\n')
    New_input.append(' System \n')
    New_input.append('  Atoms\n')
    New_input.append('\n'.join(coords))
    New_input.append(' \n')
    New_input.append('    End\n')
    New_input.append('     Lattice\n')
    New_input.append('\n'.join(lattice))
    New_input.append('   \n End\n')
    New_input.append('    End\n\n')
    New_input.append(' Engine BAND\n')
    New_input.append('   Basis\n')
    New_input.append('      Type TZP\n')
    New_input.append('   Core small\n')
    New_input.append('   End\n')
    New_input.append('   XC\n')
    New_input.append('      GGA PBE\n')
    New_input.append('      DISPERSION GRIMME3 BJDAMP\n')
    New_input.append('   End\n')
    New_input.append('   BandStructure\n')
    New_input.append('   Enabled No\n')
    New_input.append('   End\n')
    New_input.append('    EndEngine\n')
    new_file = qc_base + ".run"
    put_contents(new_file, New_input)
    os.system("chmod +x " + new_file)
    #Make_dir(qc_base)
    return new_file

def Check_coords(name):
    is_coord = False
    parameters = get_contents(name)
    for line in parameters:
        if 'Index Symbol' in line:
            is_coord =True
            break
    if is_coord:
        OPt(name)
    return


def Energetic_parameter(output):
    parameters = get_contents(output)
    for  line in parameters:
        if "NORMAL TERMINATION"  in line:
            return True
    return False


def Submit(qc_base):
    New_input =[]
    New_input.append('#!/bin/bash\n')
    New_input.append('#SBATCH --nodes=1\n')
    New_input.append('#SBATCH --cpus-per-task=1\n')
    New_input.append('#SBATCH  -t 4-48:10:00\n')
    New_input.append('#SBATCH --ntasks=64\n')
    New_input.append('#SBATCH --mem-per-cpu=3GB\n')
    #New_input.append('#SBATCH --mem=200GB\n')
    New_input.append(f'#SBATCH -o {qc_base}_slurm.out\n')
    New_input.append(f'#SBATCH -e {qc_base}_slurm.err\n')
    New_input.append('#SBATCH -J  '+ qc_base +'\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('sleep 10\n')
    New_input.append('module purge\n')
    New_input.append('module use -a  /projects/m_chemie/privatemodules/\n')
    New_input.append('module add ams\n')
    New_input.append('./'+qc_base+'.run  >  '+ qc_base+'.out \n' )
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    #os.system('mv '+ new_file+ '  '+ dir)
    return


def  Unfinished(All_folders):
    base= os.getcwd()
    for folders in All_folders:
        foldername= glob.glob(folders+'/*run')
        qc_base = foldername[0].split('/')[-1].split('.')[0]
        print (qc_base)
        #
        if   os.path.exists(folders+'/'+qc_base+'.out'):
        #Akward checking mechanis
            energy = Energetic_parameter(folders+'/'+qc_base+'.out')

            if energy is False:
                os.chdir(folders)
                if   os.path.exists('ams.results'):
                    os.system(' rm -r ams.results')
                os.system('cp  '+ qc_base+'.out   '+ 'Store.out')
                os.system('rm *slurm*')
                Check_coords(qc_base+'.out')
                Submit(qc_base)
                os.system('sbatch submita.sh')
                os.chdir(base)

        else:
            os.chdir(folders)
            if   os.path.exists('ams.results'):
                os.system(' rm -r ams.results')
            Submit(qc_base)
            os.system('sbatch submita.sh')
            os.chdir(base)
    return


Unfinished(qcin)