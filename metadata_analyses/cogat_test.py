# test cogat functions

import pytest
from cogat import load_cogat_terms


def get_cogat_matches(text, termdict):
    matches = []
    for termtype, terms in termdict.items():
        for term, td in terms.items():
            searchterms = [term.lower()]
            if 'alias' in td and len(td['alias']) > 0:
                for alias in td['alias'].split(','):
                    print('search alias', term, alias)
                    searchterms.append(alias.lower())
            for t in searchterms:
                if len(t) == 0:
                    continue
                t = t.lower()
                if t in text:
                    matches.append(term)
    return(list(set(matches)))


@pytest.fixture
def termdict():
    return(load_cogat_terms())


# smoke test
def test_load(termdict):
    assert 'task' in termdict
    assert 'concept' in termdict
    assert 'disorder' in termdict


@pytest.mark.parametrize("input, matches",
    [('a working memory task', ['memory', 'working memory']),
    ])
def test_matches(input, matches, termdict):
    cogat_matches = get_cogat_matches(input, termdict)
    for match in matches:
        assert match in cogat_matches
