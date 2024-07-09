#!/bin/python
import os
import sys
import re
import socket
import shutil
import itertools
#source = os.path('~/src/Job_file/')
# path =  os.getenv("HOME")+ '/src/Job_file'
# sys.path.append(path)#Add this directory to the path
import Coords_library
import submit_files


if len(sys.argv) == 3:
    qcin = sys.argv[1]
    Hessian = sys.argv[2]
    qc_base = qcin.split('.')[0]


elif len(sys.argv) == 2:
    qcin = sys.argv[1]
    qc_base = qcin.split('.')[0]
    Hessian = None

else:
    sys.exit()

def get_contents(filename):
    with open(filename, 'r') as f:
        contents = f.readlines()
    return contents

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return

def make_dir(qc_base):
    if not os.path.exists(qc_base):
        os.makedirs(qc_base)
    #shutil.move(qc_base+'*', qc_base)
    os.system('mv ' + qc_base +'.*   ' + qc_base)
    os.system('mv  '+ ' submita.sh  ' + qc_base)
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

def Gas_OPt_Freq(name, Hessian):
    coords, lattice = Coords_library.Coords(name)
    New_input=[]
    New_input.append("#!/bin/sh\n")
    New_input.append('CM_AMSEXTERNAL=$NSCM\n')
    New_input.append('export NSCM_AMSEXTERNAL\n')
    New_input.append(' NSCM=64\n')
    New_input.append(' export NSCM\n')
    New_input.append('\n')
    New_input.append('$AMSBIN/ams << eor\n\n')
    New_input.append(' Task GeometryOptimization \n')
    New_input.append(' Properties \n')
    New_input.append('    NormalModes Yes \n')
    New_input.append('    StressTensor Yes\n')
    New_input.append('    ElasticTensor Yes\n')
    New_input.append('  End\n')
    New_input.append('GeometryOptimization\n')
    New_input.append('    Convergence\n')
    New_input.append('      Energy 1e-06\n')
    New_input.append('      Gradients 0.001\n')
    New_input.append('    End\n')
    New_input.append('End\n')

    if Hessian != None:
        hess = InitialHessian(Hessian)
        New_input.extend (hess)


    New_input.append(' System \n')
    New_input.append('  Atoms\n')
    New_input.append('\n'.join(coords))
    New_input.append(' \n')
    New_input.append('    End\n')
    New_input.append('     Lattice\n')
    New_input.append('\n'.join( lattice))
    New_input.append('   \n End\n')
    New_input.append('    End\n\n')
    New_input.append(' Engine BAND\n')
    New_input.append('   Basis\n')
    New_input.append('      Type TZ2P\n')
    New_input.append('   End\n')
    New_input.append('   XC\n')
    New_input.append('      MetaGGA SCAN\n')
    New_input.append('      DISPERSION GRIMME3 BJDAMP\n')
    New_input.append('   End\n')
    New_input.append('   BandStructure\n')
    New_input.append('   Enabled No\n')
    New_input.append('   End\n')

    New_input.append('    EndEngine\n')
    #New_input.append('    eor\n')

    new_file = qc_base + ".run"
    put_contents(new_file, New_input)
    os.system("chmod +x " + new_file)
    submit_files.create_submit(qc_base)

    make_dir(qc_base)
    return new_file

Gas_OPt_Freq(qcin, Hessian)
