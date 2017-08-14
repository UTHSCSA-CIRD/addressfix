#!/usr/bin/env python
'''
Takes a CSV file with a particular column specified by an argument (by default, last column), converts the 
addresses in that column into one or more standardized formats and outputs a file with those columns added
on.

Usage:
   addressfix.py [options] -f FILE

Options:
    -h --help           Show this screen
    -a --address=<num>  Which column is the address column? (last column by default)
    -k --keep=<nums>    Comma-separated list of columns to keep. (all by default)
    -v --verbose        Verbose/debug output (show all SQL)
    -c --config=FILE    Configuration file [default: config.ini]
    -f --infile=FILE      Input data. A CSV file with a column of addresses to standardize
'''
import sys
from sys import argv
from docopt import docopt
from ConfigParser import SafeConfigParser
from contextlib import contextmanager
from operator import itemgetter
from streetaddress import StreetAddressParser
import logging
import csv
import re # maybe not needed


log = logging.getLogger(__name__)
config_default = './config.ini'
sp = StreetAddressParser()

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
        opt['address'] = int(arguments['--address']) or None
        opt['keep'] = [int(ii) for ii in arguments['--keep'].split(',')] or None
        opt['infile'] = arguments['--infile'] or None
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
	# create file-handle for infile
	self.outfile = 'out_'+self.infile
	with open(self.infile,'rb') as incsv:
	    # sniff to check dialect
	    dialect = csv.Sniffer().sniff(incsv.read(1024))
	    incsv.seek(0)
	    # create file-handle for outfile
	    csvout = csv.writer(sys.stdout,dialect=dialect)
	    # sniff for a header
	    hashead = csv.Sniffer().has_header(incsv.read(1024))
	    incsv.seek(0)
	    inrows = csv.reader(incsv,dialect)
	    line1 = inrows.next()
	    # use address to identify column to standardize
	    if not self.address: self.address = len(line1) - 1
	    # use keep to identify what to keep in outheader and append result column header
	    if not self.keep: self.keep = range(0,len(line1))
	    import pdb ; pdb.set_trace()
	    # if hashead, write a header out, otherwise just do to first line what will be done to all
	    if(hashead): csvout.writerow(itemgetter(*self.keep)(line1)+('AddrFix',))
	    # the FOO is a placeholder, to be replaced with normalized value from streetaddress
	    else: 
		oo1 = sp.parse(line1[self.address])
		oo1.update((kk,'') for kk,vv in oo1.items() if vv is None)
		oo1 = ' '.join(itemgetter('house','street_name','street_type')(oo1))
		csvout.writerow(itemgetter(*self.keep)(line1) + (oo1,))
	    for linen in inrows:
		oo1 = sp.parse(linen[self.address])
		oo1.update((kk,'') for kk,vv in oo1.items() if vv is None)
		oo1 = ' '.join(itemgetter('house','street_name','street_type')(oo1))
		csvout.writerow(itemgetter(*self.keep)(linen) + (oo1,))
		#csvout.writerow(itemgetter(*self.keep)(linen) + (linen[self.address]+' FOO',))
		# cycle through rows, write keep columns and standardized column


if __name__=='__main__':
    userargs = docopt(__doc__, argv=argv[1:])
    if userargs['--infile']:
        log.info(Addfix(args=userargs).doFix())
    else:
	log.error('The -f argument must specify the name of a CSV file')
