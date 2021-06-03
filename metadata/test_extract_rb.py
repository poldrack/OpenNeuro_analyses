# test extraction

import sys
sys.path.append('.')
from parse_metadata import extract_nih_grants
import pytest
import pandas as pd
import re
    
@pytest.mark.parametrize("grantstring, grantnum", 
    [(' 1R01MH112345 ','MH112345'),
    (' 1R01MH112345-02 ','MH112345'),
    (' 1-R01MH112345-02 ','MH112345'),
    (' 1R01-MH112345 ','MH112345'),
    ('NIH grant P30 AG010124', 'AG010124'),
    ('K01ES-025442', 'ES025442'),
    ('S10 OD 021480', 'OD021480'),
    ('1R01-DA021146', 'DA021146'),
    ('Funded by NIH grant U01NS103780 (RP, RA and MH)', 'NS103780')])
def test_extract(grantstring, grantnum):
    g = extract_nih_grants(grantstring)
    assert grantnum in g

big_str = "We are thankful to the staff at Duke’s Brain Imaging Analysis Center  BIAC for assistance with data collection as well as NIH support  S10 OD 021480 for BIAC’s super computing cluster The GPU used for this research was donated by the NVIDIA Corporation We are incredibly grateful to Shariq Iqbal for helpful discussions and key analysis insights We also thank Dianna Amasino and Sam Dore for early data collection Research reported in this publication was supported by a BD2K Career Development Award  K01ES-025442 to J M P an NIMH R01108627 to S H and a National Science Foundation Graduate Research Fellowship under NSF GRFP DGE-1644868 and a Duke Dean’s Graduate Fellowship to K M "
print(extract_nih_grants(big_str))
