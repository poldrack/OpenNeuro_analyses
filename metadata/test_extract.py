# test extraction

#import sys
#sys.path.append('.')
#from parse_metadata import extract_nih_grants
import pytest
import pandas as pd
import re

def extract_nih_grants(s, verbose=False):
    """extract nih grants from a funding string
    using a set of heuristics"""
    
    # load nih grant and institute codes from files
    grant_codes = list(pd.read_csv('ActivityCodes.csv')['ACT_CODE'])
    #grant_codes.remove('S10')
    institute_codes = list(pd.read_csv('IC_abbrevs.csv', header=None).loc[:, 0])

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

    # detect and fix common combinations
    for gc in grant_codes:
        for ic in institute_codes:
            for patterns in [(f'{gc}-{ic}', f'{gc}{ic}'),
                             (f'{gc} {ic}', f'{gc}{ic}')]:
                if s.find(patterns[0]) > -1:
                    s.replace(*patterns)
            
    # bespoke fixes for particular datasets
    replacements = {'RO1': 'R01',
                    '01A1': ''}
    for k, r in replacements.items():
        if s.find(k) > -1:
            s = s.replace(k, r)
    
    # remove all punctuation so we can split by spaces
    s = re.sub(r"[(),.;@#?!&$]+\ *", " ", s) #s.translate(str.maketrans(' ', ' ', string.punctuation))
    if verbose:
        print(s)

    potential_grant_strings = []
    for i in s.split(' '):
        if not hasNumbers(i):
            if verbose:
                print('skipping', i)
        # drop anything that doesn't have any numbers
        else:
            # remove any trailing year codes
            i_s = i.split('-')
            # remove leading digits
            code_clean = re.sub('^\d+', '', i_s[0])
            is_nih = False
            for instcode in institute_codes:
                if code_clean.find(instcode) > -1:
                    is_nih = True
            if is_nih:
                for grantcode in grant_codes:
                    code_clean = code_clean.replace(grantcode, '')
                potential_grant_strings.append(code_clean)
                
    return(potential_grant_strings)

@pytest.mark.parametrize("grantstring, grantnum", 
    [(' 1R01MH112345 ','MH112345'),
    (' 1R01MH112345-02 ','MH112345'),
    (' 1-R01MH112345-02 ','MH112345'),
    (' 1R01-MH112345 ','MH112345'),
    ('NIH grant P30 AG010124', 'AG010124'),
    ('K01ES-025442', 'ES025442'),
    ('S10 OD 021480', 'OD021480')])
def test_extract(grantstring, grantnum):
    g = extract_nih_grants(grantstring)
    assert grantnum in g