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
#from streetaddress import StreetAddressParser
import usaddress as ua
import logging
import csv
import re
import json
import string


log = logging.getLogger(__name__)
config_default = './config.ini'
#sp = StreetAddressParser()

'''
Now it works. Let's see how well.
'''

def nrsfx(inputValue,case='u'):
        '''
        From... https://stackoverflow.com/questions/44725712/replace-function-with-dictionary/44725831#44725831
        who modified it from...
        http://bcdcspatial.blogspot.com/2012/09/normalize-to-usps-street-abbreviations.html	
	
        if case=='l', returns lowercase
        if case=='u', returns uppercase
        else returns proper case
        '''
        case = case[0].lower()
        abbv = suffixDict()
        words = inputValue.split()
        for i,word in enumerate(words):
            w = word.lower()
            rep = abbv[w] if w in abbv.keys() else words[i]
            words[i] = rep.upper() if case == 'u' else rep.lower() if case == 'l' else (rep[0].upper() + rep[1:])
        return ' '.join(words)

def suffixDict():
    """
    Use common abbreviations -> USPS standardized abbreviation to replace common street suffixes

    Obtains list from https://www.usps.com/send/official-abbreviations.htm
    TODO: We might not actually want all these. Maybe just the main ones-- DR, ST, AVE, LN, PL
        
    """
    return {'north': 'n', 'west': 'w','south': 's', 'east': 'e',
	    'northwest': 'nw', 'northeast': 'ne',
	    'southwest': 'sw', 'southeast': 'se',
	    # above are directionals, below are street types
	    'trpk': 'tpke', 'forges': 'frgs', 'bypas': 'byp', 'mnr': 'mnr', 
	    'viaduct': 'via', 'mnt': 'mt', 'lndng': 'lndg', 'vill': 'vlg', 
	    'aly': 'aly', 'mill': 'ml', 'pts':  'pts', 'centers': 'ctrs', 
	    'row': 'row', 'cnter': 'ctr', 'hrbor': 'hbr', 'tr': 'trl', 
	    'lndg': 'lndg', 'passage': 'psge', 'walks': 'walk', 'frks': 'frks', 
	    'crest': 'crst', 'meadows': 'mdws', 'freewy': 'fwy', 
	    'garden': 'gdn', 'bluffs': 'blfs', 'vlg': 'vlg', 'vly': 'vly', 
	    'fall': 'fall', 'trk': 'trak', 'squares': 'sqs', 'trl': 'trl', 
	    'harbor': 'hbr', 'frry': 'fry', 'div': 'dv', 'straven': 'stra', 
	    'cmp': 'cp', 'grdns': 'gdns', 'villg': 'vlg', 'meadow': 'mdw', 
	    'trails': 'trl', 'streets': 'sts', 'prairie': 'pr', 'hts': 'hts', 
	    'crescent': 'cres', 'pass': 'pass', 'ter': 'ter', 'port': 'prt', 
	    'bluf': 'blf', 'avnue': 'ave', 'lights': 'lgts', 'rpds': 'rpds', 
	    'harbors': 'hbrs', 'mews': 'mews', 'lodg': 'ldg', 'plz': 'plz', 
	    'tracks': 'trak',  'path': 'path', 'pkway': 'pkwy', 'gln': 'gln',
	    'bot': 'btm', 'drv': 'dr', 'rdg': 'rdg', 'fwy': 'fwy', 'hbr': 'hbr', 
	    'via': 'via', 'divide': 'dv', 'inlt': 'inlt', 'fords': 'frds', 
	    'avenu': 'ave', 'vis': 'vis', 'brk': 'brk',  'rivr': 'riv', 
	    'oval': 'oval', 'gateway': 'gtwy', 'stream': 'strm', 'bayoo': 'byu', 
	    'msn': 'msn', 'knoll': 'knl', 'expressway': 'expy', 'sprng': 'spg',
	    'flat': 'flt', 'holw': 'holw', 'grden': 'gdn', 'trail': 'trl', 
	    'jctns': 'jcts', 'rdgs': 'rdgs', 'tunnel': 'tunl', 'ml': 'ml', 
	    'fls': 'fls', 'flt': 'flt', 'lks': 'lks', 'mt': 'mt', 
	    'groves': 'grvs', 'vally': 'vly', 'ferry': 'fry', 'parkway': 'pkwy', 
	    'radiel': 'radl', 'strvnue': 'stra', 'fld': 'fld', 
	    'overpass': 'opas', 'plaza': 'plz', 'estate': 'est', 'mntn': 'mtn', 
	    'lock': 'lck', 'orchrd': 'orch',
			'strvn': 'stra', 'locks': 'lcks', 'bend': 'bnd', 'kys': 'kys', 
	    'junctions': 'jcts', 'mountin': 'mtn',
			'burgs': 'bgs', 'pine': 'pne', 'ldge': 'ldg', 'causway': 'cswy', 
	    'spg': 'spg', 'beach': 'bch', 'ft': 'ft',
			'crse': 'crse', 'motorway': 'mtwy', 'bluff': 'blf', 'court': 'ct', 
	    'grov': 'grv', 'sprngs': 'spgs',
			'ovl': 'oval', 'villag': 'vlg', 'vdct': 'via', 'neck': 'nck', 
	    'orchard': 'orch', 'light': 'lgt',
			'sq': 'sq', 'pkwy': 'pkwy', 'shore': 'shr', 'green': 'grn', 'strm': 
	    'strm', 'islnd': 'is',
			'turnpike': 'tpke', 'stra': 'stra', 'mission': 'msn', 'spngs': 
	    'spgs', 'course': 'crse',
			'trafficway': 'trfy', 'terrace': 'ter', 'hway': 'hwy', 'avenue': 
	    'ave', 'glen': 'gln',
			'boul': 'blvd', 'inlet': 'inlt', 'la': 'ln', 'ln': 'ln', 'frst': 
	    'frst', 'clf': 'clf',
			'cres': 'cres', 'brook': 'brk', 'lk': 'lk', 'byp': 'byp', 'shoar': 
	    'shr', 'bypass': 'byp',
			'mtin': 'mtn', 'ally': 'aly', 'forest': 'frst', 'junction': 'jct', 
	    'views': 'vws', 'wells': 'wls', 'cen': 'ctr',
			'exts': 'exts', 'crt': 'ct', 'corners': 'cors', 'trak': 'trak', 
	    'frway': 'fwy', 'prarie': 'pr', 'crossing': 'xing',
			'extn': 'ext', 'cliffs': 'clfs', 'manors': 'mnrs', 'ports': 'prts', 
	    'gatewy': 'gtwy', 'square': 'sq', 'hls': 'hls',
			'harb': 'hbr', 'loops': 'loop', 'mdw': 'mdw', 'smt': 'smt', 'rd': 
	    'rd', 'hill': 'hl', 'blf': 'blf',
			'highway': 'hwy', 'walk': 'walk', 'clfs': 'clfs', 'brooks': 'brks', 
	    'brnch': 'br', 'aven': 'ave',
			'shores': 'shrs', 'iss': 'iss', 'route': 'rte', 'wls': 'wls', 
	    'place': 'pl', 'sumit': 'smt', 'pines': 'pnes',
			'trks': 'trak', 'shoal': 'shl', 'strt': 'st', 'frwy': 'fwy', 
	    'heights': 'hts', 'ranches': 'rnch',
			'boulevard': 'blvd', 'extnsn': 'ext', 'mdws': 'mdws', 'hollows': 
	    'holw', 'vsta': 'vis', 'plains': 'plns',
			'station': 'sta', 'circl': 'cir', 'mntns': 'mtns', 'prts': 'prts', 
	    'shls': 'shls', 'villages': 'vlgs',
			'park': 'park', 'nck': 'nck', 'rst': 'rst', 'haven': 'hvn', 
	    'turnpk': 'tpke', 'expy': 'expy', 'sta': 'sta',
			'expr': 'expy', 'stn': 'sta', 'expw': 'expy', 'street': 'st', 
	    'str': 'st', 'spurs': 'spur', 'crecent': 'cres',
			'rad': 'radl', 'ranch': 'rnch', 'well': 'wl', 'shoals': 'shls', 
	    'alley': 'aly', 'plza': 'plz', 'medows': 'mdws',
			'allee': 'aly', 'knls': 'knls', 'ests': 'ests', 'st': 'st', 'anx': 
	    'anx', 'havn': 'hvn', 'paths': 'path', 'bypa': 'byp',
			'spgs': 'spgs', 'mills': 'mls', 'parks': 'park', 'byps': 'byp', 
	    'flts': 'flts', 'tunnels': 'tunl', 'club': 'clb', 'sqrs': 'sqs',
			'hllw': 'holw', 'manor': 'mnr', 'centre': 'ctr', 'track': 'trak', 
	    'hgts': 'hts', 'rnch': 'rnch', 'crcle': 'cir', 'falls': 'fls',
			'landing': 'lndg', 'plaines': 'plns', 'viadct': 'via', 'gdns': 
	    'gdns', 'gtwy': 'gtwy', 'grove': 'grv', 'camp': 'cp', 'tpk': 'tpke',
			'drive': 'dr', 'freeway': 'fwy', 'ext': 'ext', 'points': 'pts', 
	    'exp': 'expy', 'ky': 'ky', 'courts': 'cts', 'pky': 'pkwy', 'corner': 'cor',
			'crssing': 'xing', 'mnrs': 'mnrs', 'unions': 'uns', 'cyn': 'cyn', 
	    'lodge': 'ldg', 'trfy': 'trfy', 'circle': 'cir', 'bridge': 'brg',
			'dl': 'dl', 'dm': 'dm', 'express': 'expy', 'tunls': 'tunl', 'dv': 
	    'dv', 'dr': 'dr', 'shr': 'shr', 'knolls': 'knls', 'greens': 'grns',
			'tunel': 'tunl', 'fields': 'flds', 'common': 'cmn', 'orch': 'orch', 
	    'crk': 'crk', 'river': 'riv', 'shl': 'shl', 'view': 'vw',
			'crsent': 'cres', 'rnchs': 'rnch', 'crscnt': 'cres', 'arc': 'arc', 
	    'btm': 'btm', 'blvd': 'blvd', 'ways': 'ways', 'radl': 'radl',
			'rdge': 'rdg', 'causeway': 'cswy', 'parkwy': 'pkwy', 'juncton': 
	    'jct', 'statn': 'sta', 'gardn': 'gdn', 'mntain': 'mtn',
			'crssng': 'xing', 'rapid': 'rpd', 'key': 'ky', 'plns': 'plns', 
	    'wy': 'way', 'cor': 'cor', 'ramp': 'ramp', 'throughway': 'trwy',
			'estates': 'ests', 'ck': 'crk', 'loaf': 'lf', 'hvn': 'hvn', 'wall': 
	    'wall', 'hollow': 'holw', 'canyon': 'cyn', 'clb': 'clb',
			'cswy': 'cswy', 'village': 'vlg', 'cr': 'crk', 'trce': 'trce', 
	    'cp': 'cp', 'cv': 'cv', 'ct': 'cts', 'pr': 'pr', 'frg': 'frg',
			'jction': 'jct', 'pt': 'pt', 'mssn': 'msn', 'frk': 'frk', 'brdge': 
	    'brg', 'cent': 'ctr', 'spur': 'spur', 'frt': 'ft', 'pk': 'park',
			'fry': 'fry', 'pl': 'pl', 'lanes': 'ln', 'gtway': 'gtwy', 'prk': 
	    'park', 'vws': 'vws', 'stravenue': 'stra', 'lgt': 'lgt',
			'hiway': 'hwy', 'ctr': 'ctr', 'prt': 'prt', 'ville': 'vl', 'plain': 
	    'pln', 'mount': 'mt', 'mls': 'mls', 'loop': 'loop',
			'riv': 'riv', 'centr': 'ctr', 'is': 'is', 'prr': 'pr', 'vl': 'vl', 
	    'avn': 'ave', 'vw': 'vw', 'ave': 'ave', 'spng': 'spg',
			'hiwy': 'hwy', 'dam': 'dm', 'isle': 'isle', 'crcl': 'cir', 'sqre': 
	    'sq', 'jct': 'jct', 'jctn': 'jct', 'mountain': 'mtn',
			'keys': 'kys', 'parkways': 'pkwy', 'drives': 'drs', 'tunl': 'tunl', 
	    'jcts': 'jcts', 'knl': 'knl', 'center': 'ctr',
			'driv': 'dr', 'tpke': 'tpke', 'sumitt': 'smt', 'canyn': 'cyn', 
	    'ldg': 'ldg', 'harbr': 'hbr', 'rest': 'rst', 'shoars': 'shrs',
			'vist': 'vis', 'gdn': 'gdn', 'islnds': 'iss', 'hills': 'hls', 
	    'cresent': 'cres', 'point': 'pt', 'lake': 'lk', 'vlly': 'vly',
			'strav': 'stra', 'crossroad': 'xrd', 'bnd': 'bnd', 'strave': 
	    'stra', 'stravn': 'stra', 'knol': 'knl', 'vlgs': 'vlgs',
			'forge': 'frg', 'cntr': 'ctr', 'cape': 'cpe', 'height': 'hts', 
	    'lck': 'lck', 'highwy': 'hwy', 'trnpk': 'tpke', 'rpd': 'rpd',
			'boulv': 'blvd', 'circles': 'cirs', 'valleys': 'vlys', 'vst': 
	    'vis', 'creek': 'crk', 'mall': 'mall', 'spring': 'spg',
			'brg': 'brg', 'holws': 'holw', 'lf': 'lf', 'est': 'est', 'xing': 
	    'xing', 'trace': 'trce', 'bottom': 'btm',
			'streme': 'strm', 'isles': 'isle', 'circ': 'cir', 'forks': 'frks', 
	    'burg': 'bg', 'run': 'run', 'trls': 'trl',
			'radial': 'radl', 'lakes': 'lks', 'rue': 'rue', 'vlys': 'vlys', 
	    'br': 'br', 'cors': 'cors', 'pln': 'pln',
			'pike': 'pike', 'extension': 'ext', 'island': 'is', 'frd': 'frd', 
	    'lcks': 'lcks', 'terr': 'ter',
			'union': 'un', 'extensions': 'exts', 'pkwys': 'pkwy', 'islands': 
	    'iss', 'road': 'rd', 'shrs': 'shrs',
			'roads': 'rds', 'glens': 'glns', 'springs': 'spgs', 'missn': 'msn', 
	    'ridge': 'rdg', 'arcade': 'arc',
			'bayou': 'byu', 'crsnt': 'cres', 'junctn': 'jct', 'way': 'way', 
	    'valley': 'vly', 'fork': 'frk',
			'mountains': 'mtns', 'bottm': 'btm', 'forg': 'frg', 'ht': 'hts', 
	    'ford': 'frd', 'hl': 'hl',
			'grdn': 'gdn', 'fort': 'ft', 'traces': 'trce', 'cnyn': 'cyn', 
	    'cir': 'cir', 'un': 'un', 'mtn': 'mtn',
			'flats': 'flts', 'anex': 'anx', 'gatway': 'gtwy', 'rapids': 'rpds', 
	    'villiage': 'vlg', 'flds': 'flds',
			'coves': 'cvs', 'rvr': 'riv', 'av': 'ave', 'pikes': 'pike', 'grv': 
	    'grv', 'vista': 'vis', 'pnes': 'pnes',
			'forests': 'frst', 'field': 'fld', 'branch': 'br', 'grn': 'grn', 
	    'dale': 'dl', 'rds': 'rds', 'annex': 'anx',
			'sqr': 'sq', 'cove': 'cv', 'squ': 'sq', 'skyway': 'skwy', 'ridges': 
	    'rdgs', 'hwy': 'hwy', 'tunnl': 'tunl',
			'underpass': 'upas', 'cliff': 'clf', 'lane': 'ln', 'land': 'land',
			'bch': 'bch', 'dvd': 'dv', 'curve': 'curv',
	    'cpe': 'cpe', 'summit': 'smt', 'gardens': 'gdns'}


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
    opt['chosen_formats'] = json.loads(opt['chosen_formats']['chosen']);
    for ii in opt['chosen_formats']: opt['formats'][ii] = json.loads(opt['formats'][ii])
    if arguments == {}:
        opt['address'] = None
        opt['keep'] = None
    else:
        opt['address'] = int(arguments['--address']) if arguments['--address'] else None
        opt['keep'] = [int(ii) for ii in arguments['--keep'].split(',')] if arguments ['--keep'] else None
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
        self.chosen_formats = opt['chosen_formats']
        self.formats = opt['formats']
        self.status = ''
	
    def doFix(self):
	# create file-handle for infile
	self.outfile = 'out_'+self.infile
	with open(self.infile,'rb') as incsv:
	    # sniff to check dialect
	    dialect = csv.Sniffer().sniff(incsv.read(1024))
	    '''this is to make it ignore quote characters... they 
	    will all get translated out of the output later on 
	    anyway... and maybe later we should expect a bug
	    where the NON address fields have extra quotes in
	    them for certain input formats, but at least this
	    is working now with our format...
	    '''
	    dialect.quoting = csv.QUOTE_NONE
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
	    # if hashead, write a header out, otherwise just do to first line what will be done to all
	    if(hashead): csvout.writerow(itemgetter(*self.keep)(line1)+tuple(self.chosen_formats))
	    else: 
		incsv.seek(0) # this resets inrows to the first row also
	    for row in inrows:
		'''The enclosing ' '.join(FOO.split()) pattern is a fast way of
		replacing runs of various types of whitespace with a single
		space character. https://stackoverflow.com/a/2077944
		
		The FOO in the above pseudocode is the original address string
		but converted to unicode with bad characters replaced with \ufffd
		instead of erroring out. https://stackoverflow.com/a/12468274
		
		Then we do a bunch of translating-- remove quote marks (both kinds)
		by translating them to None, and then replace the unirubbish with 
		spaces (and if your address has a malformed ligature or something in 
		the middle of a street name, tough luck, now you live on 
		'Encyclop Dia Drive'). And if there are multiple runs of spaces, they
		get collapsed to one space as explained above. This is the place to
		add other stuff to remove or replace as we discover it.
		
		Finally, ord() returns the numeric offset of a character... because 
		unicode(FOO).translate(BAR) requires BAR to be a dict object with 
		numeric values and labels, the numbers representing the offsets of what
		is mapped to what. Note that to express a unicode character you have to
		do u'X' rather than 'X', and in this case it's not a type-able character
		so X is an escaped sequence.
		'''
		row[self.address] = ' '.join(unicode(row[self.address],errors='replace').translate({
		  ord('"'):None, ord("'"):None, ord(u'\ufffd'):ord(' ')
		  }).split());
		#row[self.address] = unicode(row[self.address],errors='replace').replace('"','').replace("'",'')
		try: tagged = ua.tag(row[self.address])[0]
		except ua.RepeatedLabelError: 
		    csvout.writerow(itemgetter(*self.keep)(row) + tuple(row[self.address]*len(self.chosen_formats)))
		else:
		    ooii = []
		    for ii in self.chosen_formats: 
			oojj = []
			for jj in self.formats[ii]['addrparts']: 
			    if jj in tagged.keys():
				if jj in self.formats[ii]['abbr']:
				    oojj += [nrsfx(re.sub('\\.','',tagged[jj]))]
				else:
				    oojj += [tagged[jj]]
			if len(oojj) == 1:
			  # if something went wierd and there is only one part of this address, use the original address instead
			  ooii += [row[self.address]]
			else:
			  ooii += [' '.join(oojj)]
		    try: csvout.writerow(itemgetter(*self.keep)(row) + tuple(ooii))
		    except: 
			import pdb; pdb.set_trace()


if __name__=='__main__':
    userargs = docopt(__doc__, argv=argv[1:])
    if userargs['--infile']:
        log.info(Addfix(args=userargs).doFix())
    else:
	log.error('The -f argument must specify the name of a CSV file')
