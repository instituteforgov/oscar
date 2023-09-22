# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in an in-year release of OSCAR data and compare it to the master list of organisations
    Inputs
        - csv: 'OSCAR_in_year_dataset_June_2023.csv'
        - pkl: 'oscar_2021_2022_annual.pkl'
    Outputs
        None
    Parameters
        None
    Notes
        None
'''

# %%
import os

import pandas as pd

# %%
# Read in in-year OSCAR data
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/In-year data'
)

df_inyear = pd.read_csv('OSCAR_in_year_dataset_June_2023.csv', encoding='cp1252')

# %%
df_inyear

# %%
# Read in master list of organisations
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/Data'
)

df_master = pd.read_pickle('oscar_2021_2022_annual.pkl')

# %%
# Get unique organisation names in in-year OSCAR data not in master list
set(
    df_inyear['Organisation'].unique()
) - set(
    df_master['ORGANISATION_LONG_NAME'].unique()
)
