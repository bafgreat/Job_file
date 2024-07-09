
import socket
import re 

def put_contents(filename, output):
    with open(filename, 'w') as f:
        f.writelines(output)
    return

def zih(qc_base):
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
    New_input.append('module add ams.2024\n')
    New_input.append('./'+qc_base+'.run  >  '+ qc_base+'.out \n' )
    new_file = 'submita.sh'
    put_contents(new_file, New_input)
    #os.system('mv '+ new_file+ '  '+ dir)
    return

def noctua_pc2(qc_base):
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
    New_input.append('module reset\n')
    New_input.append('export I_MPI_PMI=pmi2\n')
    New_input.append('export SCM_USE_IMPI_2021=1\n')
    New_input.append('source ~/.bash_profile\n')
    New_input.append('source $HOME/src/ams2024.102/adfbashrc.sh\n')
    New_input.append('$AMSBIN/setenv.sh\n')
    New_input.append('sleep 15\n')
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

def create_submit(filename):
    hostname = socket.gethostname()
    if re.match('n.*login\d*', hostname):
        noctua_pc2(filename)
    elif hostname == 'login02':
        young(filename)
    return