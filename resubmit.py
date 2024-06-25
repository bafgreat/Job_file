#!/usr/bin/python
import re
import sys
import subprocess
import os
import glob
import csv

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
    New_input.append('      Gradients 0.0001\n')
    New_input.append('    End\n')
    New_input.append('End\n')
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
    New_input.append('#SBATCH --partition=single\n')
    New_input.append('#SBATCH --nodes=1\n')
    New_input.append('#SBATCH --cpus-per-task=16\n')
    New_input.append('#SBATCH --mem-per-cpu=3GB\n')
    #New_input.append('#SBATCH --ntasks=8\n')
    New_input.append('#SBATCH --time=00-72:00:00\n')
    New_input.append('#SBATCH --mem=64gb\n')
    New_input.append('#SBATCH -J  '+ qc_base+'\n')
    New_input.append('#SBATCH --error='+qc_base+'.log\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('# Set the environment\n')
    New_input.append('module load devel/python/3.8.6_intel_19.1\n')
    New_input.append('./' + qc_base+'.run  > '+qc_base+'.out\n\n' )
    new_file = 'submita.sh'
    put_contents(new_file,New_input)
    #os.system('mv '+ new_file+ '  '+ qc_base)
    return

def Submit_Barnard(qc_base):
    New_input =[]
    New_input.append('#!/bin/bash\n')
    New_input.append('#SBATCH --nodes=1\n')
    New_input.append('#SBATCH --cpus-per-task=1\n')
    New_input.append('#SBATCH  -t 4-48:10:00\n')
    New_input.append('#SBATCH --ntasks=64\n')
    New_input.append('#SBATCH --mem-per-cpu=3GB\n')
    #New_input.append('#SBATCH --mem=200gb\n')
    New_input.append(f'#SBATCH -o {qc_base}_slurm.out\n')
    New_input.append(f'#SBATCH -e {qc_base}_slurm.err\n')
    New_input.append('#SBATCH -J  '+ qc_base +'\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('sleep 10\n')
    New_input.append('module purge\n')
    New_input.append('module use -a  /projects/m_chemie/privatemodules/\n')
    New_input.append('module add module add ams.2024\n')
    New_input.append('./'+qc_base+'.run  >  '+ qc_base+'.out \n' )
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    #os.system('mv '+ new_file+ '  '+ dir)
    return


def Submit_pc2(qc_base):
    New_input =[]
    New_input.append('#!/bin/bash\n')
    New_input.append('#SBATCH --nodes=1\n')
    New_input.append('#SBATCH --cpus-per-task=1\n')
    New_input.append('#SBATCH  -t 20-12:10:00\n')
    New_input.append('#SBATCH --ntasks=64\n')
    New_input.append('#SBATCH --mem-per-cpu=3GB\n')
    New_input.append('#SBATCH -p normal\n')
    New_input.append(f'#SBATCH -o {qc_base}_slurm.out\n')
    New_input.append(f'#SBATCH -e {qc_base}_slurm.err\n')
    New_input.append('#SBATCH -J  '+ qc_base +'\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('source $HOME/src/ams2024.102/adfbashrc.sh\n')
    New_input.append('sleep 10\n')
    New_input.append('./'+qc_base+'.run  >  '+ qc_base+'.out \n' )
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    #os.system('mv '+ new_file+ '  '+ dir)
    return

def young(qc_base):
    name = remove_digits_at_start(qc_base)
    job_name = os.path.abspath('.').split('work/')[1]
    New_input = []
    New_input.append('#!/bin/bash\n')
    New_input.append(
        '# Batch script to run an OpenMP threaded job on Legion with the upgraded\n\n')
    New_input.append('# software stack under SGE.\n')
    New_input.append('#$ -P Gold\n')
    New_input.append('#$ -A MCC_discov_add\n')
    New_input.append('# 1. Force bash as the executing shell.\n')
    New_input.append('#$ -S /bin/bash\n\n')
    New_input.append(
        '# 2. Request ten minutes of wallclock time (format hours:minutes:seconds).\n')
    New_input.append('#$ -l h_rt=48:00:00\n\n')
    New_input.append('# 3. Request 1 gigabyte of RAM for each core/thread\n')
    New_input.append('#$ -l mem=1G\n\n')
    New_input.append("# 5. Set the name of the job.\n")
    New_input.append("#$ -N "+name + "\n\n")
    New_input.append("# 6. Select 24 threads\n")
    New_input.append("#$ -pe smp 24\n\n")
    New_input.append(
        '# 7. Set the working directory to somewhere in your scratch space.  This is\n')
    New_input.append(
        '# a necessary step with the upgraded software stack as compute nodes cannot \n')
    New_input.append('# write to $HOME.\n')
    New_input.append('# Replace "<your_UCL_id>" with your UCL user ID :)\n')
    New_input.append('#$ -wd /home/mmm0555/Scratch/work/'+job_name+'  \n\n')
    New_input.append('# 8. Run the application. \n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('module unload default-modules/2018\n')
    New_input.append('module unload rcps-core/1.0.0\n')
    New_input.append(
        'module unload cmake/3.13.3 flex/2.5.39 git/2.19.1 apr/1.5.2 apr-util/1.5.4  \n')
    New_input.append(
        'module unload subversion/1.8.13 screen/4.2.1 nano/2.4.2 nedit/5.6-aug15\n')
    New_input.append(
        'module unload dos2unix/7.3 giflib/5.1.1 tmux/2.2 mrxvt/0.5.4\n')
    New_input.append(
        'module unload compilers/intel/2018/update3 apr-util/1.6.1 apr/1.7.0\n\n')
    New_input.append('module load beta-modules \n')
    New_input.append('module unload gcc-libs \n')
    New_input.append("module load gcc-libs/9.2.0\n\n")
    New_input.append("source ~/src/ams2020.103/amsbashrc.sh\n")
    New_input.append("sleep 10\n\n")
    New_input.append('./' + qc_base+'.run  > '+qc_base+'.out \n\n')
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    # os.system('mv '+ new_file+ '  '+ qc_base)
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
                os.system('rm slurm*')
                Check_coords(qc_base+'.out')
                Submit_Barnard(qc_base)
                os.system('qsub submita.sh')
                os.chdir(base)

        else:
            os.chdir(folders)
            if   os.path.exists('ams.results'):
                os.system(' rm -r ams.results')
            Submit_Barnard(qc_base)
            os.system('qsub submita.sh')
            os.chdir(base)
    return


All_folders = sorted(glob.glob('cif/*'))
index = All_folders.index('cif/TFPA-TGCl-iCOF-3')
Unfinished(All_folders[index+1:])

