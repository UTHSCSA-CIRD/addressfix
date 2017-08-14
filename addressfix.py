#!/usr/bin/env python
'''
Takes a CSV file with a particular column specified by an argument (by default, last column), converts the 
addresses in that column into one or more standardized formats and outputs a file with those columns added
on.

Usage:
   addressfix.py [options] -f FILE

Options:
    -h --help           Show this screen
    -a --address        Which column is the address column? (last column by default)
    -k --keep           Which columns to keep? (all by default)
    -v --verbose        Verbose/debug output (show all SQL)
    -c --config=FILE    Configuration file [default: config.ini]
    -f --infile=FILE      Input data. A CSV file with a column of addresses to standardize
'''
from sys import argv
from docopt import docopt
from ConfigParser import SafeConfigParser
from contextlib import contextmanager
import logging
import csv
import re # maybe not needed
import streetaddress as sa

log = logging.getLogger(__name__)
config_default = './config.ini'

'''
Note: none of this stuff works yet. I'm just using the old chinotype code as a template for this one.
Most of it will be replaced with corresponding code for this project.
'''

def config(arguments={}):
    logging.basicConfig(format='%(asctime)s: %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S', level=logging.INFO)
    if arguments == {}:
        config_fn = config_default
    else:
        if arguments['--verbose']:
            log.setLevel(logging.DEBUG)
        config_fn = arguments['--config']
    cp = SafeConfigParser()
    cp.readfp(open(config_fn, 'r'), filename=config_fn)
    opt = cp._sections
    if arguments == {}:
        opt['address'] = None
        opt['keep'] = None
    else:
        opt['address'] = arguments['-a'] or None
        opt['keep'] = arguments['-k'] or None
        opt['infile'] = arguments['-f'] or None
    return opt

class Addfix:
    def __init__(self, listargs=[], args={}):
        if args == {}:
            args = docopt(__doc__, listargs)
        opt = config(args)
        self.address = opt['address']
        self.keep = opt['keep']
        self.infile = opt['infile']
        self.status = ''
    def doFix(self):
	# create file-handle for outfile
	# create file-handle for infile
	with open(self.infile,'rb') as incsv:
	    # sniff to check dialect
	    dialect = csv.Sniffer().sniff(incsv.read(1024))
	    incsv.seek(0)
	    import pdb ; pdb.set_trace
	    # sniff for a header
	    inhead = csv.Sniffer().sniff(incsv.read(1024))
	    # if inhead, write a header out also
	    # use keep to identify what to keep in outheader and append result column header
	    # use address to identify column to standardize
	    incsv.seek(0)
	    inrows = csv.reader(dialect)
	    # cycle through rows, write keep columns and standardized column


if __name__=='__main__':
    args = docopt(__doc__, argv=argv[1:])
    import pdb; pdb.set_trace()
    if args['-f']:
        log.info(Addfix(args=args).doFix())
    else:
	log.error('The -f argument must specify the name of a CSV file')
