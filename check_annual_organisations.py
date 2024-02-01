# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in an annual release of OSCAR data and compare it to the master list of organisations
    Inputs
        - csv: '../Source/Annual data/202223/MFO-R13-2022-23.csv'
        - pkl: 'data/df_organisations_lookup.pkl'
    Outputs
        None
    Parameters
        None
    Notes
        None
    Future developments
        - Convert this into a function that can be called from either process_inyear_data.py
        or process_annual_data.py
'''

# %%
import os

import pandas as pd

from utils.functions import strip_trailing_dept_initialism

# %%
# READ IN DATASETS
# Read in annual OSCAR data
new_source_data_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/Annual data/202223/'
)

df_new = pd.read_csv(new_source_data_path + 'MFO-R13-2022-23.csv', encoding='cp1252')

# %%
# Read in organisations lookup
scripts_data_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/data/'
)

df_lookup = pd.read_pickle(scripts_data_path + 'df_organisations_lookup.pkl')

# %%
# CLEAN DATA
# Remove trailing 'BEIS', 'DCMS' strings from ORGANISATION_LONG_NAME
df_new = strip_trailing_dept_initialism(
    df=df_new,
    col='ORGANISATION_LONG_NAME',
)

# %%
# COMPARE DATASETS
# Get unique organisation names in annual OSCAR data not in master list
set(
    df_new['ORGANISATION_LONG_NAME'].unique()
) - set(
    df_lookup['ORGANISATION_LONG_NAME'].unique()
)

# %%
df_new.loc[
    df_new['ORGANISATION_LONG_NAME'].str.endswith('BEIS')
]['ORGANISATION_LONG_NAME'].unique()

# %%
df_new.loc[
    df_new['ORGANISATION_LONG_NAME_2'] != df_new['ORGANISATION_LONG_NAME']
][['ORGANISATION_LONG_NAME', 'ORGANISATION_LONG_NAME_2']]
