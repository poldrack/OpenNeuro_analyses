# parse metadata records to obtain funding information

import json
import re
import pandas as pd


grant_codes = list(pd.read_csv('ActivityCodes.csv')['ACT_CODE'])
institute_codes = list(pd.read_csv('IC_abbrevs.csv', header=None).loc[:, 0])
grant_codes.remove('S10')


# load brain initiative grants
def get_bi_project_numbers(bi_grant_file):

    bi_grants = pd.read_csv(bi_grant_file).dropna()
    return([i.split('-')[0] for i in bi_grants['Project Number']])


def get_bi_grant_nums(project_nums):
    # extract <IC><num> code from full project number
    def extract_grant_num(p):
        p = re.sub('^\d+', '', p).replace(' ', '')  # remove leading digit and spaces
        return(p[3:])
    return([extract_grant_num(i) for i in project_nums])


def get_bi_grant_types(project_nums):
    def extract_grant_type(p):
        p = re.sub('^\d+', '', p).replace(' ', '')  # remove leading digit and spaces
        return(p[:3])

    bi_grant_types = [extract_grant_type(i) for i in project_nums]
    return(list(set(bi_grant_types)))


def get_bi_institutes(grant_codes):
    bi_institutes = [i[:2] for i in grant_codes]
    return(list(set(bi_institutes)))


def extract_funding_info(f, snapshot=None, verbose=False):
    # pull Funding and Acknowledgments from dataset metadata
    if snapshot is None:
        snapshot = 'latestSnapshot'
    if f['data']['snapshot'] is None:
        return None
    md = f['data']['snapshot']
    id = md['id']

    if 'Funding' in md['description'] and md['description']['Funding'] is not None:
        funding = md['description']['Funding']
    else:
        funding = []

    if 'Acknowledgements' in md['description'] and md['description']['Acknowledgements'] is not None:
        funding.append(md['description']['Acknowledgements'])

    if verbose:
        print(funding)

    return(funding)

def left_strip(s, delim):
    return s[s.find(delim):]

def strip_non_alnum(s):
    alphanumeric_filter = filter(str.isalnum, s)
    return "".join(alphanumeric_filter)

def remove_grant_codes(s):
    fixed = s
    for rem_string in grant_codes:
        fixed = fixed.replace(rem_string, '')
    return fixed

def bespoke_fix(s):
    # bespoke fixes for particular datasets
    replacements = {
                    'R01MH-': 'R01MH',
                    'R01-MH-': 'R01MH',
                    'RO1': 'R01',
                    '01A1': '',
                    'NIMH': 'MH'
                    }
    for k, r in replacements.items():
        if s.find(k) > -1:
            s = s.replace(k, r)
    return s
 

'''
   First we remove or replace known wonky sequences,
   Then we break the input string up into a list of all substrings that start with a capital letter, and consist only
   of '-', white space, numbers, and capital letters,
   I had tried to remove all non alpha numeric characters, but dashes and spaces proved useful stopping points for future regex,
   We then remove all known grant codes from each of the substrings,
   Then we search for two capital letters, and any sequence of 5 numbers or more, the call to group() gets the first 
   instance of this match. If there are a lot of problems with this logic, we may want to, get the last instance of
   them, or do a findall and attempt further tests to determine which set of two letters, or numbers is most
   appropriate.
'''
def extract_nih_grants(s, verbose=False):
    s = bespoke_fix(s)
    first_pass_regex = re.compile("[A-Z0-9][A-Z0-9\s-]+")
    potentials = first_pass_regex.findall(s)
    # potentials = [strip_non_alnum(x) for x in potentials]
    # print(potentials)
    potentials = [remove_grant_codes(x) for x in potentials]
    good = []
    for potential in potentials:
        two_letters = re.search("[A-Z]{2}", potential)
        found_digits = re.search("[\d]{5,}", potential)
        if (two_letters and found_digits):
            good.append(two_letters.group() + found_digits.group())
    print(potentials, good)

    return good
    


if __name__ == "__main__":
    verbose = True
    metadata_file = 'funding_metadata.json'
    bi_grant_file = 'funded_awards-2021-05-30T12-08-20.csv'

   # get brain intitiative grant info
    bi_grant_df = pd.read_csv(bi_grant_file).dropna()
    bi_project_nums = get_bi_project_numbers(bi_grant_file)
    bi_grants = get_bi_grant_nums(bi_project_nums)
    if verbose:
        print(f'found {len(bi_grants)} BI grants')
    

    # load ON metadata and parse
    with open(metadata_file) as f:
        funding = json.load(f)
    if verbose:
        print(f'found metadata for {len(funding)} OpenNeuro datasets')
    
    grant_info = {}
    grants_cited = {}
    for k, md in funding.items():
        if md is None:
            continue
        f = extract_funding_info(md)
        # don't store entries with no funding/ackowledgments
        if f is not None and len(f) > 0:
            grant_info[k] = f
    print(f'found {len(grant_info)} datasets with possible funding info')

    # find grants for each dataset
    for k, gi in grant_info.items():
        grants_cited[k] = []
        for s in gi:
            grants_found = extract_nih_grants(s)
            for grant in grants_found:
                grants_cited[k].append(grant)

    # consolidate all grants
    all_grants = []
    for k, grants in grants_cited.items():
        if len(grants) > 0:
            all_grants += grants
    all_grants = list(set(all_grants))
    
    # crossreference against bi grants
    bi_matches = []
    for g in all_grants:
        if g in bi_grants:
            bi_matches.append(g)
        
    print(f'{len(all_grants)} unique NIH grants cited in OpenNeuro')
    print(f'{len(bi_matches)} BI grants cited in OpenNeuro')

    for i in bi_matches:
        project_match = [p for p in bi_grant_df['Project Number'] if p.find(i) > -1]
        matching_grant = bi_grant_df.query('`Project Number` == "%s"' % project_match[0])
        print(project_match)
        print(matching_grant['Title'].values[0])
        print(matching_grant['Investigator'].values[0])
        print('')