#!/bin/python
import os
import sys
import shutil
import itertools
path = os.getenv("HOME") + '/src/Job_file'
sys.path.append(path)#Add this directory to the path
import Coords_library

if len(sys.argv) == 3:
    qcin = sys.argv[1]
    job_type = sys.argv[2]
    qc_base = qcin.split('.')[0]
else:
    print ('try: Jobname, HSE06/HSE03/PBE/SCAN')
    sys.exit()

def get_contents(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()
    return contents

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return


def Submit(qc_base):
    New_input =[]
    New_input.append('#!/bin/bash\n')
    New_input.append('#SBATCH --nodes=1\n')
    New_input.append('#SBATCH --cpus-per-task=1\n')
    New_input.append('#SBATCH  -t 4-48:10:00\n')
    New_input.append('#SBATCH --ntasks=64\n')
    New_input.append('#SBATCH --mem-per-cpu=2GB\n')
    New_input.append(f'#SBATCH -o {qc_base}_slurm.out\n')
    New_input.append(f'#SBATCH -e {qc_base}_slurm.err\n')
    New_input.append('#SBATCH -J  '+ qc_base +'\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('sleep 10\n')
    New_input.append('module purge\n')
    New_input.append('module use -a  /projects/m_chemie/privatemodules/\n')
    New_input.append('module add ams/2021.impi\n')
    New_input.append('./'+qc_base+'.run  >  '+ qc_base+'.out \n' )
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    #os.system('mv '+ new_file+ '  '+ dir)
    return

def Make_dir(qc_base):
    if not os.path.exists(qc_base):
        os.makedirs(qc_base)
    #shutil.move(qc_base+'*', qc_base)
    os.system('mv ' + qc_base +'.*   ' + qc_base)
    os.system('mv ' + 'submita.sh' + qc_base)
    return

def InitialHessian(file_name):
    New_input =[]
    #if file_name !=None:
    path = os.path.abspath(file_name)
    #file = path+'/ams.results/ams.rkf'
    file = path+'/ams.results/dftb.rkf'
    New_input.append(' GeometryOptimization \n')
    New_input.append('     InitialHessian \n')
    New_input.append('        Type FromFile \n')
    New_input.append('        File '+ file +' \n')
    New_input.append('     End\n')
    New_input.append(' End\n')
    return New_input

def Make_dir(qc_base):
    if not os.path.exists(qc_base):
        os.makedirs(qc_base)
    #shutil.move(qc_base+'*', qc_base)
    os.system('mv ' + qc_base +'.*   ' + qc_base)
    return

def HSEO6(name):
     coords, lattice = Coords_library.Coords(name)
     New_input=[]
     New_input.append("#!/bin/sh\n")
     New_input.append('\n')
     New_input.append('$ADFBIN/ams << eor\n\n')
     New_input.append(' Task SinglePoint \n')
     New_input.append(' System \n')
     New_input.append('  Atoms\n')
     New_input.append('\n'.join(coords))
     New_input.append(' \n')
     New_input.append('    End\n')
     New_input.append('     Lattice\n')
     New_input.append('\n'.join( lattice))
     New_input.append(' \n')
     New_input.append('   \n End\n')
     New_input.append('    End\n\n')

     New_input.append(' Engine BAND\n')
     New_input.append('     AIMCriticalPoints\n')
     New_input.append('         AIMCriticalPoints\n')
     New_input.append('     End\n')
     New_input.append('     Basis\n')
     New_input.append('         Type TZP\n')
     New_input.append('     End\n')
     New_input.append('     BandStructure\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     EffectiveMass\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     GridBasedAIM\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     DOS\n')
     New_input.append('         CalcPDOS Yes\n')
     New_input.append('         StoreCoopPerBasPair Yes\n')
     New_input.append('     End\n')
     New_input.append('     NumericalQuality Good\n')
     New_input.append('     XC\n')
     New_input.append('         libxc hse06\n')
     New_input.append('     End\n')
     New_input.append('    EndEngine\n')


     new_file = qc_base + ".run"
     put_contents(new_file, New_input)
     os.system("chmod +x " + new_file)
     Submit(qc_base)
     Make_dir(qc_base)
     return new_file

def HSEO3(name):
     coords, lattice = Coords_library.Coords(name)
     New_input=[]
     New_input.append("#!/bin/sh\n")
     New_input.append('\n')
     New_input.append('$ADFBIN/ams << eor\n\n')
     New_input.append(' Task SinglePoint \n')
     New_input.append(' System \n')
     New_input.append('  Atoms\n')
     New_input.append('\n'.join(coords))
     New_input.append(' \n')
     New_input.append('    End\n')
     New_input.append('     Lattice\n')
     New_input.append('\n'.join( lattice))
     New_input.append(' \n')
     New_input.append('   \n End\n')
     New_input.append('    End\n\n')

     New_input.append(' Engine BAND\n')
     New_input.append('     AIMCriticalPoints\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     Basis\n')
     New_input.append('         Type TZP\n')
     New_input.append('     End\n')
     New_input.append('     BandStructure\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     EffectiveMass\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     GridBasedAIM\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     DOS\n')
     New_input.append('         CalcPDOS Yes\n')
     New_input.append('         StoreCoopPerBasPair Yes\n')
     New_input.append('     End\n')
     New_input.append('     NumericalQuality Good\n')
     New_input.append('     XC\n')
     New_input.append('         libxc hse03\n')
     New_input.append('     End\n')
     New_input.append('    EndEngine\n')


     new_file = qc_base + ".run"
     put_contents(new_file, New_input)
     os.system("chmod +x " + new_file)
     Submit(qc_base)
     Make_dir(qc_base)
     return new_file


def PBE(name):
     coords, lattice = Coords_library.Coords(name)
     New_input=[]
     New_input.append("#!/bin/sh\n")
     New_input.append('\n')
     New_input.append('$ADFBIN/ams << eor\n\n')
     New_input.append(' Task SinglePoint \n')
     New_input.append(' System \n')
     New_input.append('  Atoms\n')
     New_input.append('\n'.join(coords))
     New_input.append(' \n')
     New_input.append('    End\n')
     New_input.append('     Lattice\n')
     New_input.append('\n'.join( lattice))
     New_input.append(' \n')
     New_input.append('   \n End\n')
     New_input.append('    End\n\n')

     New_input.append(' Engine BAND\n')
     New_input.append(' BZPath\n')
     New_input.append('     Path\n')
     New_input.append('     0.00 0.00 0.00 G\n')
     New_input.append('     0.50 0.00 0.00 X\n')
     New_input.append('     0.50 0.50 0.00 M\n')
     New_input.append('     0.50 0.50 0.50 R\n')
     New_input.append('     0.00 0.00 0.00 G\n')
     New_input.append('     End\n')
     New_input.append(' End\n')
     New_input.append('     Basis\n')
     New_input.append('         Type TZP\n')
     New_input.append('     End\n')
     New_input.append('     BandStructure\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     DOS\n')
     New_input.append('         CalcPDOS Yes\n')
     New_input.append('         StoreCoopPerBasPair Yes\n')
     New_input.append('     End\n')
     New_input.append('     NumericalQuality Good\n')
     New_input.append('     XC\n')
     New_input.append('     GGA PBE\n')
     New_input.append('         DISPERSION GRIMME3 BJDAMP\n')
     New_input.append('     End\n')
     New_input.append('    EndEngine\n')


     new_file = qc_base + ".run"
     put_contents(new_file, New_input)
     os.system("chmod +x " + new_file)
     Submit(qc_base)
     Make_dir(qc_base)
     return new_file

def SCAN(name):
     coords, lattice = Coords_library.Coords(name)
     New_input=[]
     New_input.append("#!/bin/sh\n")
     New_input.append('\n')
     New_input.append('$ADFBIN/ams << eor\n\n')
     New_input.append(' Task SinglePoint \n')
     New_input.append(' System \n')
     New_input.append('  Atoms\n')
     New_input.append('\n'.join(coords))
     New_input.append(' \n')
     New_input.append('    End\n')
     New_input.append('     Lattice\n')
     New_input.append('\n'.join( lattice))
     New_input.append(' \n')
     New_input.append('   \n End\n')
     New_input.append('    End\n\n')

     New_input.append(' Engine BAND\n')
     New_input.append('     AIMCriticalPoints\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     Basis\n')
     New_input.append('         Type TZP\n')
     New_input.append('     End\n')
     New_input.append('     BandStructure\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     EffectiveMass\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     GridBasedAIM\n')
     New_input.append('         Enabled Yes\n')
     New_input.append('     End\n')
     New_input.append('     DOS\n')
     New_input.append('         CalcPDOS Yes\n')
     New_input.append('         StoreCoopPerBasPair Yes\n')
     New_input.append('     End\n')
     New_input.append('     NumericalQuality Good\n')
     New_input.append('     XC\n')
     New_input.append('         MetaGGA SCAN\n')
     New_input.append('         DISPERSION GRIMME3 BJDAMP\n')
     New_input.append('     End\n')
     New_input.append('    EndEngine\n')


     new_file = qc_base + ".run"
     put_contents(new_file, New_input)
     os.system("chmod +x " + new_file)
     Submit(qc_base)
     Make_dir(qc_base)
     return new_file



if job_type == 'SCAN':
    SCAN(qcin)
elif job_type == 'HSE06':
    HSEO6(qcin)
elif job_type == 'HSE03':
    HSE03(qcin)
elif job_type == 'PBE':
    PBE(qcin)


