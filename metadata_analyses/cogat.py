# utility functions for accessing cognitive atlas
# and main function to download and clean up atlas entries

from cognitiveatlas.api import get_task, get_concept, get_disorder
from collections import defaultdict
import json
from urllib.error import URLError
import re
from utils import list_duplicates

def load_cogat_terms(termsfile='../data/cognitiveatlas/terms.json'):
    try:
        with open(termsfile) as f:
            cogat_terms = json.load(f)
        print('using saved cognitive atlas terms')
    except FileNotFoundError:
        cogat_terms = get_cogat_terms()
        with open(termsfile, 'w') as f:
            json.dump(cogat_terms, f)
    return(cogat_terms)


def cogat_dict_from_df(df, term_type, max_returns=None, max_retries=3):
    getters = {'task': get_task,
               'concept': get_concept,
               'disorder': get_disorder}
    # parse outputs from cognitiveatlas and get aliases
    df_dict = {}
    if max_returns is not None:
        df = df.iloc[:max_returns, :]
    for idx in df.index[:]:
        id = df.loc[idx, 'id']
        name = df.loc[idx, 'name'].lower()
        print(id, name)
        # catch the occasional API flakeout
        data = None
        for _ in range(max_retries):
            try:
                data = getters[term_type](id=id).json
                break
            except URLError:
                print('URL error - retrying')
        df_dict[name] = data
    return(df_dict)


def get_cogat_terms(max_returns=None):
    terms = defaultdict(lambda: {})
    task_df = get_task().pandas
    terms['task'] = cogat_dict_from_df(task_df, 'task', max_returns)
    terms['task'] = cleanup_aliases(terms['task'])

    concept_df = get_concept().pandas
    terms['concept'] = cogat_dict_from_df(concept_df, 'concept', max_returns)
    terms['concept'] = cleanup_aliases(terms['concept'])

    disorder_df = get_disorder().pandas
    terms['disorder'] = cogat_dict_from_df(disorder_df, 'disorder', max_returns)
    terms['disorder'] = cleanup_aliases(terms['disorder'])
    return(terms)


def get_cogat_matches(text, termdict, verbose=False):
    # use re to identify whole word matches and ignore substring matches
    matches = []
    # fix issues with terms that too easily match off-target text:
    # "open" as alias to "openness"
    # "EPI" as alias to Eysenck Personality Questionnaire
    # "BIAS" as alias to behavioral investment allocation strategy
    # "TOLD"
    # "bdi" - used for battelle developmental inventory but more common for beck depression index
    # "WIN"
    # "MID"
    terms_to_skip = ['open', 'epi', 'bias', 'told', 'bdi', 'abc', 'win', 'mid']
    for termtype, terms in termdict.items():
        for term, td in terms.items():
            searchterms = [term.lower()]
            if len(td['aliases_clean']) > 0:
                for alias in td['aliases_clean']:
                    if alias.lower() not in terms_to_skip:
                        searchterms.append(alias.lower())
                    elif verbose:
                        print('skipping', alias)
            for t in searchterms:
                if len(t) == 0:
                    continue
                # occasionally an alias will fail due to escaped characters
                # we just skip those
                try:
                    regex = re.compile(r"\b%s\b" % t)
                    for i in regex.findall(text):
                        matches.append((term, termtype))
                        if verbose:
                            print(t, termtype, term)
                except:
                    pass
                    # print('search fails on', t, ' - skipping')
    return(list(set(matches)))


def cleanup_aliases(terms):
    # clean up alias text and remove duplicates
    all_aliases = []
    for k, t in terms.items():
        if 'alias' in t and len(t['alias']) > 0:
            terms[k]['aliases_clean'] = [
                i.strip() for i in re.sub('\(|\)', '', t['alias'].lower()).split(',')]
            print(k, terms[k]['aliases_clean'])
            for a in terms[k]['aliases_clean']:
                all_aliases.append(a)
        else:
            terms[k]['aliases_clean'] = []
    duplicate_aliases = list_duplicates(all_aliases)
    for k, t in terms.items():
        for alias in t['aliases_clean']:
            if alias in duplicate_aliases:
                terms[k]['aliases_clean'].remove(alias)
    return(terms)




if __name__ == "__main__":
    # get terms from API and save
    terms = load_cogat_terms()
