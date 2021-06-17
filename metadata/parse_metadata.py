# parse metadata records to obtain funding information

import json
import re
import pandas as pd
from collections import defaultdict
import requests

grant_codes = list(pd.read_csv('../data/nih_data/ActivityCodes.csv')['ACT_CODE'])
institute_codes = list(pd.read_csv('../data/nih_data/IC_abbrevs.csv', header=None).loc[:, 0])
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


def bespoke_fix(s, replacements=None):
    # bespoke fixes for particular datasets
    if replacements is None:
        replacements = {'R01MH-': 'R01MH',
                        'R01-MH-': 'R01MH',
                        'RO1': 'R01',
                        '01A1': '',
                        'NIMH': 'MH',
                        'NIH': ''}
    for k, r in replacements.items():
        if s.find(k) > -1:
            s = s.replace(k, r)
    return s


'''
   Notes from Ross on this version of the extractor:
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
    if verbose:
        print(potentials, good)

    return good


def extract_nsf_grants(s):
    nsf_grants_found = []
    replacements = {' CAREER ': '-',
                    '(DDRI) Grant #': 'NSF-',
                    'NSF Graduate Research Fellowship (#': 'NSF-',
                    'NSFECCS': 'ECC-',
                    'NSFNCS-FR ': 'NCS-',
                    'NCS program (#': 'NCS-',
                    'NSF CAREER award (#': 'NSF-',
                    'National Science Foundation (': 'NSF-',
                    'NSF Career Award ': 'NSF-',
                    'NSF grant #': 'NSF-',
                    'NSF grants #': 'NSF-',
                    '# 1': 'NSF-1',
                    'NSF ': 'NSF-',
                    'NSF1': 'NSF-1',
                    '#BCS': 'BCS',
                    'National Science Foundation 1': 'NSF-1'}
    if (s.find('National Science Foundation') > -1) or (s.find('NSF') > -1):
        # nsf_grants_found.append(s)
        if ('Swiss' in s) or ('China' in s):
            return([])
        s = bespoke_fix(s, replacements)
        s = s.translate(str.maketrans('', '', '!#$%&()*+,./:;<=>?@[\\]^_`{|}~'))
        for s_s in s.split(' '):
            fullmatch = re.findall("[A-Z]{3}-[\d]{6,}", s_s)
            for m in fullmatch:
                nsf_grants_found.append(m)
    return(nsf_grants_found)


def mentions_bi(s):
    # does it mention BRAIN iniative
    return 'brain initiative' in s.lower() or 'BRAIN' in s


def is_nih_grant(grantnum, dummy=False):
    # return True if grant number is found in NIH reporter
    # based on https://gist.github.com/bosborne/8efbd21ffbe3dc8d057d80539114ab07
    if dummy:
        return(True)
    url = 'https://api.federalreporter.nih.gov/v1/Projects/search'
    params = {'query': f'projectNumber:*{grantnum}*'}
    r = requests.get(url, params=params)
    retval = r.json()
    return retval['totalCount'] > 0


def is_nsf_grant(grantnum):
    # return True if grant number is found in NIH reporter
    # based on https://gist.github.com/bosborne/8efbd21ffbe3dc8d057d80539114ab07
    # remove category if present (assumes delimited by dash)
    if '-' in grantnum:
        grantnum = grantnum.split('-')[1]
    url = f'http://api.nsf.gov/services/v1/awards/{grantnum}.json'
    r = requests.get(url)
    retval = r.json()
    return 'award' in retval['response']


if __name__ == "__main__":
    verbose = True
    metadata_file = '../data/openneuro/funding_metadata.json'
    bi_grant_file = '../data/nih_data/funded_awards-2021-05-30T12-08-20.csv'

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
    grants_cited = defaultdict(lambda: [])
    nsf_grants_cited = defaultdict(lambda: [])
    bi_mentions = {}
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
        dsnum = k.split(':')[0]
        for s in gi:
            nih_grants_found = extract_nih_grants(s)
            for grant in nih_grants_found:
                if is_nih_grant(grant):
                    grants_cited[dsnum].append(grant)
            nsf_grants_found = extract_nsf_grants(s)
            for grant in nsf_grants_found:
                if is_nsf_grant(grant):
                    nsf_grants_cited[dsnum].append(grant)
            if mentions_bi(s):
                bi_mentions[k] = s

    for k, grants in grants_cited.items():
        grants_cited[k] = list(set(grants))
    for k, grants in nsf_grants_cited.items():
        nsf_grants_cited[k] = list(set(grants))

    # consolidate all grants
    cited_grants = defaultdict(lambda: [])  # add default []
    cited_bi_grants = defaultdict(lambda: [])
    all_grants = []
    for k, grants in grants_cited.items():
        if len(grants) > 0:
            all_grants += grants
    all_grants = list(set(all_grants))

    # index by datasets
    dataset_grants = defaultdict(lambda: [])
    dataset_grants_nsf = defaultdict(lambda: [])
    for k, grants in grants_cited.items():
        for g in grants:
            dataset_grants[g].append(k)
    for k, grants in nsf_grants_cited.items():
        for g in grants:
            dataset_grants_nsf[g].append(k)

    bi_matches = [g for g in all_grants if g in bi_grants]
    print(f'{len(all_grants)} unique NIH grants cited in OpenNeuro')
    print(f'{len(bi_matches)} BI grants cited in OpenNeuro')

    bi_datasets = []
    for i in bi_matches:
        project_match = [p for p in bi_grant_df['Project Number'] if p.find(i) > -1]
        matching_grant = bi_grant_df.query('`Project Number` == "%s"' % project_match[0])
        print(project_match)
        print(matching_grant['Title'].values[0])
        print(matching_grant['Investigator'].values[0])
        print(dataset_grants[i])
        bi_datasets += dataset_grants[i]
        print('')
    bi_datasets = list(set(bi_datasets))

    print(f'{len(bi_datasets)} unique datasets associated with BI grants')

    all_nsf_grants = []
    for k, grants in nsf_grants_cited.items():
        if grants is not None:
            for g in grants:
                all_nsf_grants.append(g)
    all_nsf_grants = list(set(all_nsf_grants))
    print(f'{len(all_nsf_grants)} unique NSF grants cited in OpenNeuro')
