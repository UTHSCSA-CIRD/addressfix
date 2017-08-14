# addressfix
Wrapper for a couple of address parsing/standardizing libraries for the purpose of cleaning up addresses in CSV files.

## Instructions:

Setup:

    pip install -r requirements.txt

Run with default settings (won't work right for this input file):

    python addressfix.py -f test_address_input.csv

Run keeping columns 0,2,3,4 in the output and using column 4 as the address:
    
    python addressfix.py -a 4 -k 0,2,3,4 -f test_address_input.csv

Get help

    python addressfix.py -h

