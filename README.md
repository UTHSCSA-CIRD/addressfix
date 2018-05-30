# addressfix
Wrapper for a couple of address parsing/standardizing libraries for the purpose of cleaning up addresses in CSV files.

## Instructions:

Setup:

    pip install -r requirements.txt

Run with default settings (won't work right for this input file):

    python addressfix.py -f test_address_input.csv

Run keeping columns 0,2,3,4 in the output and using column 4 as the address:
    
    python addressfix.py -a 4 -k 0,2,3,4 -f test_address_input.csv
    
    NOTE: Python counts everything from 0!! So -a 4 means the FIFTH column 
    the way most non-programmers would count them in a spreadsheet, and the
    0,2,3,4 would likewise be first and the third through fifth columns!

Get help

    python addressfix.py -h

