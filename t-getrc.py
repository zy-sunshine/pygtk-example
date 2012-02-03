#!/usr/bin/python
import os
import glob

if __name__ == '__main__':
    gtkrcs = glob.glob('/usr/share/themes/*/*/gtkrc')
    print gtkrcs[0].split(os.path.sep)[4]

