# Alexander Mun
# 06/17/14

# Calls some terminal command on all files which need to be 
# updated

import subprocess
import shutil
import os
import time
import matplotlib_script as mpl
import threading
from helper import *

METADATA_FILE = "temp.txt"
this_file_dir = os.path.dirname(os.path.realpath(__file__))

def update_file(f, *args):
    '''The main function.  This directs what is to be done to input 
    file f on update.  Should work on relative paths, but if that's not working,
    passing the absolute path won't hurt.'''

    def read_num_center_atoms(f):
        '''Looks in f's directory for a temp.txt file, and from it reads
        and returns the number of center atoms.'''
        file_path = get_dirname(f, METADATA_FILE)
        temp = open(file_path, 'r')
        for l in temp:
            # Checks if the part of a string appearing 
            # before an = on a line is 'num_center_atoms'
            if l.split('=')[0].split()[0] == 'num_center_atoms':
                 num = int(l.split('=')[1].split()[0])
        return num

    def calc_chik(f, run_index):
        '''Runs ifeffit_script.ps on dir with data from feff that has 
           the run_index atom in the center.  Zero indexed.'''
        print ['perl', 'ifeffit_script.ps', get_dirname(f, run_index)]
        subprocess.call(['perl', this_file_dir + '/' + 'ifeffit_script.ps', \
            get_dirname(f, run_index)])

    if '-n' not in args:
        ##############
        # Main loop:
        ##############
        # Tracks how many times feff has been run:
        run_index = 0
        # num_center_atoms is set within the loop, initializing 
        # arbitrarily so preconditions are met
        num_center_atoms = 1

        # To pay for speed in computing power, one could thread the following 
        # loop instead of doing each iteration consecutively
        while run_index < num_center_atoms:
    
            # Making subdirectory to hold files for a fixed run index
            new_dir = get_dirname(f, run_index)
            make_sure_path_exists(new_dir)
    
            # xyz_to_feff.py called
            # Note1: .xyz file is assumed to use atomic symbols, and angstroms 
            # as coordinates 
            # Note2: when run_index == 0, xyz_to_feff records num_center_atoms 
            # in temp.txt file.  
            # Note3: xyz_to_feff is called every time.  It may seem redundant, 
            # but this allows slightly easier and more sensibly modular
            # pruning of the data to be done within xyz_to_feff.py
            convert_xyz(f, run_index)
    
            # feff called
            run_feff(f, run_index)
    
            # If not done already, gets num_center_atoms via the temp.txt file
            if run_index == 0:
                num_center_atoms = read_num_center_atoms(f)
    
            calc_chik(f, run_index)
            run_index += 1
        ##################
    else: 
        num_center_atoms = read_num_center_atoms(f)

    unaveraged_chik = get_dirname(f, "paths")
    make_sure_path_exists(unaveraged_chik)

    ## Gathering chi(k) to push to matplotlib_script.py ##
    f_list = []
    for i in range(0, num_center_atoms):
        f_list.append( get_dirname(f, i) + "/ifeffit_out" )

    ### Graphing and plotting in matplotlib: ###

    # Averaging must occur before graphs can open
    subprocess.call(['python', 
         this_file_dir + '/' + 'matplotlib_script.py',
         get_dirname(f), str(len(f_list))] + f_list + ['-a'])

    # Plotting averaged chi(k) and chi(r)
    # Opens subprocess via Popen to prevent matplotlib graphs from 
    # blocking loops in super-processes.  
    p = subprocess.Popen(['python', 
                        this_file_dir + '/' + 'matplotlib_script.py',
                        get_dirname(f), str(0), 
                        '-k', '-r'])

    # Should only wait for the LAST updated file, if update_file is called 
    # on some short list (note there's some danger in parallelizing update_file
    # since feff is called on the current directory, which can cause issues)
    p.wait()
    ############################################

    ### Cleanup ###
    clean(f, num_center_atoms)

def clean(f, num_center_atoms):
    ' Removes directories referring to Ta atoms which no longer exist. '
    for x in os.walk(get_dirname(f)):
        x_base = os.path.basename(x[0])
        if x_base.isdigit() and int(x_base) >= num_center_atoms:
            shutil.rmtree(x[0])

def convert_xyz(f, run_index):
    '''Creates a directory based on the run index (name determined via 
    get_dirname(f, run_index)), passes the run_index to xyz_to_feff.py, 
    and pipes the output into said directory.  '''

    new_dir = get_dirname(f, run_index)

    # Piping output of xyz_to_feff into subdirectory with the name 'feff.inp'
    f_name = new_dir + '/feff.inp'
    output_f = open(f_name, 'w')
    # 'Hi user, this is what I'm doing!'
    print "Converting xyz file...\n Writing output of "
    to_call = ['python', 
                this_file_dir + '/' + 'xyz_to_feff.py', 
                f, 
                str(run_index)]
    print ' '.join(to_call)
    print " to file " + f_name
    subprocess.call(to_call, stdout=output_f, stderr=subprocess.PIPE)
    output_f.close()

def run_feff(f, run_index):
    '''Calls feff after changing to the subdirectory obtained from 
    get_dirname(f, run_index).  Then changes directory back.  Assumes that 
    the directory exists, and that f_name is the correct feff input file.'''

    new_dir = get_dirname(f, run_index)
    f_name = new_dir + '/feff.inp'
    print "Calling feff, run index " + str(run_index) + "..."
    working_dir = os.getcwd()
    os.chdir(new_dir)
    subprocess.call(['feff6', f_name])
    os.chdir(working_dir)

if __name__ == '__main__':
    pass
