#!/usr/bin/env python
'''
Chinotype back-end script, RC v1.1.0
Create counts and prevalences for ranking patient cohorts
   by relative prevalence of concepts.

Usage:
   chinotype.py [options][-f PATTERN]... -m QMID
   chinotype.py [options][-f PATTERN]... -p PSID
   chinotype.py [options][-f PATTERN]... -t PSID -r PSID

Options:
    -h --help           Show this screen
    -m QMID             Query master ID to test, TOTAL population as reference
    -p PSID             Patient set ID to test, TOTAL population as reference
    -t PSID             Patient set ID to test
    -r PSID             Patient set ID for reference
    -v --verbose        Verbose/debug output (show all SQL)
    -c --config=FILE    Configuration file [default: config.ini]
    -o --output         Save chi2 csv output file
    -j --json           Return JSON output
    -e --exists         Return extant data only; do not create new data columns
    -n LIMIT            Output only LIMIT rows of over/under represented facts
    -f PATTERN          Filter output concept codes by PATTERN (e.g. i2b2metadata.SCHEMES.C_KEY)
    -x CUTOFF           Filter output where reference population patient/fact count >= CUTOFF

QMID is the query master ID (from i2b2 QT tables). The latest query 
instance/result for a given QMID will be used.

PSID is the result instance ID (from i2b2 QT tables). 
'''
from sys import argv
from docopt import docopt
from ConfigParser import SafeConfigParser
from contextlib import contextmanager
import logging
import csv
import re # maybe not needed
