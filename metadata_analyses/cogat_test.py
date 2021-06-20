# test cogat functions

import pytest
from cogat import load_cogat_terms, get_cogat_matches


@pytest.fixture
def termdict():
    return(load_cogat_terms())


# smoke test
def test_load(termdict):
    assert 'task' in termdict
    assert 'concept' in termdict
    assert 'disorder' in termdict


@pytest.mark.parametrize(
    "input, matches",
    [('a working memory task', ['memory', 'working memory']),
     ('reading impairment', ['dyslexia'])])
def test_matches(input, matches, termdict):
    cogat_matches = get_cogat_matches(input, termdict)
    for match in matches:
        assert match in [i[0] for i in cogat_matches]


# tests that should fail
@pytest.mark.parametrize(
    "input, nonmatches",
    [('rememory', ['memory'])])
def test_false_matches(input, nonmatches, termdict):
    cogat_matches = get_cogat_matches(input, termdict)
    for match in nonmatches:
        assert match not in [i[0] for i in cogat_matches]
