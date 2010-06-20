# takes a normal 4 column wessel-lab formatted text file and makes it 
#  a tetrode file by repeating the data column 3 more times (data column=0)
import sys

filename = sys.argv[1]

with open(filename, 'r') as infile: 
    with open(filename+'.tet', 'w') as outfile:
        for line in infile.readlines():
            tokens = line.split()
            # repeat first column 3 more times.
            for i in [0, 0, 0]:
                tokens.insert(i, tokens[0])
            for token in tokens:
                outfile.write( token + '    ')
            outfile.write('\n')
    

