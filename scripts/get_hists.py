#!/usr/bin/env python
u"""
get_hist.py

Download user-requested histograms and save as numpy array.
All strong beams are extracted and saved.

History
    06/16/2020  Written (Yara Mohajerani)
"""
import os
import sys
import h5py
import getopt
import shutil
import numpy as np
from icepyx import icesat2data as ipd

#-- help function
def run_help():
    print("Commandline options:")
    print("Type '--HELP' or '-H' flag for help.")
    print("Type '--DIR=' or '-D:' flag to specify data directory.")
    print("Type '--EXTENT=' or '-E:' flag to specify data spatial extent.")
    print("Type '--DATE=' or '-T:' to specify data date range.")
    print("Type '--USER=' or '-U:' flag to specify EarthData username.")
    print("Type '--EMAIL=' or '-E:' flag to specify EarthData email.")
    print("Type '--FILENAME=' or '-F:' flag to specify file name to read.")
    print("Type '--noDownload' or '-N' flag to skip downloading data if it's already there.")
    
#-- main function
def main():
    #-- Read the system arguments listed after the program
    long_options=['HELP','DIR=','EXTENT=','DATE=','USER=','EMAIL=','FILENAME=','noDownload']
    optlist,arglist = getopt.getopt(sys.argv[1:],'HD:E:T:U:E:F:N',long_options)

    #-- Set default settings
    filename = 'processed_ATL06_20200330121520_00600712_003_01.h5'
    ddir = '/home/jovyan/data'
    short_name = 'ATL06'
    spatial_extent = [31.5, -70.56, 33.73, -69.29]
    date_range = ['2020-03-30','2020-04-1']
    user = ''
    email = ''
    download = True
    #-- read commandline inputs
    for opt, arg in optlist:
        if opt in ("-H","--HELP"):
            run_help()
            sys.exit('Done.')
        elif opt in ("-D","--DIR"):
            ddir = os.path.expanduser(arg)
        elif opt in ("-E","--EXTENT"):
            spatial_extent = [float(i) for i in arg.split(',')]
        elif opt in ("-T","--DATE"):
            date_range = arg.split(',')
        elif opt in ("-U","--USER"):
            user = arg
        elif opt in ("-E","--EMAIL"):
            email = arg
        elif opt in ("-F","--FILENAME"):
            filename = arg
        elif opt in ("N","--noDownload"):
            download = False
    
    if download:
        #-- login to earth data and get data
        region_a = ipd.Icesat2Data(short_name, spatial_extent, date_range)
        region_a.earthdata_login(user,email)
        
        #-- put data order
        region_a.order_vars.append(var_list=['count'])
        #-- download data
        region_a.download_granules(ddir)

    #-- read specified file
    FILE_NAME = os.path.join(ddir,filename)
    f = h5py.File(FILE_NAME, mode='r')

    #-- determine which beam is the strong beam (left or right)
    if f['gt1l'].attrs['atlas_beam_type'] == 'strong':
        strong_id = 'l'
    else:
        strong_id = 'r'
        
    #-- loop all three beam pairs and save all three
    for i in range(1,4):
        #-- read count
        count = np.array(f['gt%i%s/residual_histogram/count'%(i,strong_id)])
    
        #-- save numpy array
        np.save(os.path.join(ddir,filename.replace('.h5','_hist_gt%i%s.npy'%(i,strong_id))),count)

#-- run main program
if __name__ == '__main__':
    main()
