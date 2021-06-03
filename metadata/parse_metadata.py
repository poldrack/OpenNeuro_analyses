# parse metadata records to obtain funding information

import json
import re
import pandas as pd


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


def extract_nih_grants(s, verbose=False):
    """extract nih grants from a funding string
    using a set of heuristics"""
    
    # load nih grant and institute codes from files
    grant_codes = list(pd.read_csv('ActivityCodes.csv')['ACT_CODE'])
    #grant_codes.remove('S10')
    institute_codes = list(pd.read_csv('IC_abbrevs.csv', header=None).loc[:, 0])

    def hasNumbers(inputString):
        return any(char.isdigit() for char in inputString)

    # bespoke fixes for particular datasets
    replacements = {'R01MH-': 'R01MH',
                    'R01-MH-': 'R01MH',
                    'RO1': 'R01',
                    '01A1': ''}
    for k, r in replacements.items():
        if s.find(k) > -1:
            s = s.replace(k, r)

    # remove all punctuation so we can split by spaces
    s = re.sub(r"[(),.;@#?!&$]+\ *", " ", s) #s.translate(str.maketrans(' ', ' ', string.punctuation))
    if verbose:
        print(s)

    # consolidate code and grant number if there are spaces between
    # also remove dash within grant code
    for g in grant_codes:
        if s.find(g + ' ') > -1:
            print('replacing', s)
            s = s.replace(g + ' ', g)
            print(s)
            print('')
        if s.find(g + '-') > -1:
            print('replacing', s)
            s = s.replace(g + '-', g)
            print(s)
            print('')
    
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