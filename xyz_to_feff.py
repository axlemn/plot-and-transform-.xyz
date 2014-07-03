# Alexander Mun
# 07/02/2014

import periodic as pt
import sys
import re

# Note: have not yet enforced anything to do with central atom, nor 
# with having an atom at (0,0,0).
central_elt = "Ta"

def title(f_name):
#   Gets the title of the .xyz file to make into the title of feff.inp
    if f_name[-4:] != ".xyz":
        raise Exception("`Not a .xyz file!")
    return "Test " + f_name[0:-4]

def scrape_xyz(f_name):
#   Gets data from a file of format .xyz
    atom_lines = []
    f = open(f_name, 'r+')
    for line in f:
#   if line fits regex:
        if re.match("[A-Z]", line):
            atom_lines.append(line)

#   Gets data from each of the lines
    atoms = []
    for l in atom_lines:
        atoms.append(l.split())
    return atoms

def elements(atoms):
#   Lists the elements in a list of atoms
    elements = []
    for a in atoms:
        if a[0] not in elements:
            elements.append(a[0])
    return elements

def dictionary_from_elts(elts):
#   Dictionary giving potential-index given an element
    d = {}
    for (i,e) in enumerate(elts):
        d.update({e:i})
    return d

def central_atom_check(atoms):
#   Checks that some atom is the central element, and checks 
#   that the central atom is of the type central_elt
#   OR that the central atom is placed first!!!
    atom_list = []

    for (i,a) in enumerate(atom_list):
        if (float(a[1]), float(a[2]), float(a[3])) == (0,0,0):
            if i == 0 or a[0] == central_elt:
                return True
            return False
    return False

def shift_atoms(atoms):
    atom_list = []
    to_subtract = []
    for (i,a) in enumerate(atoms):
        atom_list.append([a[0], float(a[1]), float(a[2]), float(a[3])])

#       Gets shift from first element listed of type central_elt
        if to_subtract == [] and a[0] == central_elt:
            to_subtract = [float(a[1]), float(a[2]), float(a[3])]

    if to_subtract == []:
        raise Exception("No " + central_elt + " atom found to shift to center.")

#   Will cause rounding issue if .xyz changes the standard to be more 
#   than 5 decimal places.  
    for atom in atom_list: 
        atom[1] -= to_subtract[0]
        atom[2] -= to_subtract[1]
        atom[3] -= to_subtract[2]
        for i in range(1,4):
            atom[i] = format(atom[i], '.5f') 

    return atom_list

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        print 'Usage error.'
    f_name = args[1]

#   Should modify so that the central atom type can be set.

    atom_list = scrape_xyz(f_name)

#   If central atom is not of fixed type, then shifts atoms so such is the case
    if not central_atom_check(atom_list):
        atom_list = shift_atoms(atom_list)

    print "TITLE %s\n" % title(f_name)
    print "CONTROL 1 1 1 1 1 1\n" \
          "PRINT   0 0 0 0 0 0\n"
    print "POTENTIALS\n" \
          "* potential-index   z   tag"

    elts = elements(atom_list)
    d = dictionary_from_elts(elts)

    for (i,e) in enumerate(elts): 
# Using an alternate printing method to get around python spacing issues
        sys.stdout.write(' '*9)
        sys.stdout.write(str(i))
        sys.stdout.write(' '*(11-len(str(i))))
        atomic_num = pt.element(e).atomic
        sys.stdout.write(str(atomic_num))
        sys.stdout.write(' '*(4-len(str(atomic_num))))
        sys.stdout.write(e)
        sys.stdout.write('\n')

    sys.stdout.write('\n')

    print "ATOMS\n" \
          "* x        y        z       ipot"
    for atom in atom_list:
        for i in range(1,4):
            sys.stdout.write(' '*(9-len(atom[i])))
            sys.stdout.write(atom[i])
        sys.stdout.write(' '*3)
        print d[atom[0]]

    sys.stdout.write('\n')

    print('END')
            
    

