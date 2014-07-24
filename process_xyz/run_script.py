# Alexander Mun
# 06/17/14

# Calls some terminal command on all files which need to be 
# updated, as specified

from subprocess import call, PIPE
import os
import errno

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def update_files(to_update):
    for f in to_update:
        update_file(f)


def update_file(f):
    an_int = 0
    sentinel = True
    while sentinel:
        run_feff(f, an_int)
        file_path = get_new_dir_name(f, an_int)
        if os.path.isfile(file_path + '/feff.err'):
            sentinel = False
        an_int += 1
    # Remove the dud directory created, with the invalid feff.inp file
    print('Updated ' + f)

def get_new_dir_name(f, an_int):
    base = os.path.basename(f)

    if base == "":
        raise Exception("Tried to update an invalid path name!")

    d = os.path.dirname(os.path.abspath(f))
    return d +  "/" + base[:-4] + "/" + str(an_int)

def run_feff(f, an_int):
    '''Creates directory, runs chain of commands on file and puts 
    output files in said directory'''

    # Making directory
    new_dir = get_new_dir_name(f, an_int)
    make_sure_path_exists(new_dir)

    # Piping output of xyz_to_feff
    f_name = new_dir + '/feff.inp'
    output_f = open(f_name, 'w')
    call(['python', 'xyz_to_feff.py', f, str(an_int)],\
        stdout=output_f, stderr = PIPE)
    output_f.close()

    working_dir = os.getcwd()
    os.chdir(new_dir)
    call(['feff6', f_name])
    os.chdir(working_dir)

if __name__ == '__main__':
    dirname = sys.argv[1]
    if len(sys.argv) == 3:
        ts_file = sys.argv[2]
    else: 
        ts_file = default_ts_file

    curr_stamps = get_stamps(dirname)
    old_stamps  = open_records(ts_file)
    to_update = stamps_to_files(curr_stamps - old_stamps)

    update_files(to_update)
    store_stamps(curr_stamps, ts_file)
