# test extraction

import sys
sys.path.append('.')
from parse_metadata import extract_nsf_grants
import pytest
import pandas as pd
import re
    
@pytest.mark.parametrize("grantstring, grantnum", 
    [('R01-DC013274 and NSF BCS-1358794 ','BCS-1358794'),
    ('NSF CAREER 1848370','NSF-1848370'),
    ('Grants NSFECCS1533257','ECC-1533257'),
    ('NSFNCS-FR 1926781','NCS-1926781'),
    ('NSF 1452485', 'NSF-1452485'),
    ('NSF GRFP DGE-1644868 ', 'DGE-1644868'),
    ('NSF STC award (CCF-1231216)', 'CCF-1231216'),
    ('National Science Foundation (1533623 to J.I.G. and J.W.K.). ', 'NSF-1533623'),
    ('US NSF Career Award 1055560', 'NSF-1055560'),
    ('NSF grant #1835200', 'NSF-1835200'),
    ('NSF #BCS-1533625', 'BCS-1533625'),
    ('National Science Foundation through the NCS program (#1633817)', 'NCS-1633817'),
    ('NSF grants #1607251', 'NSF-1607251')])
def test_extract(grantstring, grantnum):
    g = extract_nsf_grants(grantstring)
    assert grantnum in g
