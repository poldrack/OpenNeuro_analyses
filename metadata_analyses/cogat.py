# utility functions for accessing cognitive atlas

from cognitiveatlas.api import get_task, get_concept, get_disorder
from collections import defaultdict
import json
from urllib.error import URLError
import re


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

    concept_df = get_concept().pandas
    terms['concept'] = cogat_dict_from_df(concept_df, 'concept', max_returns)

    disorder_df = get_disorder().pandas
    terms['disorder'] = cogat_dict_from_df(disorder_df, 'disorder', max_returns)
    return(terms)


def get_cogat_matches(text, termdict, verbose=False):
    # use re to identify whole word matches and ignore substring matches
    matches = []
    for termtype, terms in termdict.items():
        for term, td in terms.items():
            searchterms = [term.lower()]
            if 'alias' in td and len(td['alias']) > 0:
                for alias in td['alias'].split(','):
                    searchterms.append(alias.lower())
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


if __name__ == "__main__":
    # get terms from API and save
    load_cogat_terms()
