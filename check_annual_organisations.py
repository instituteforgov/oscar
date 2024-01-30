# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in an annual release of OSCAR data and compare it to the master list of organisations
    Inputs
        - csv: 'MFO-R13-2022-23.csv'
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
# Read in annual OSCAR data
file_path_new = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/Annual data/202223'
)
file_name_new = 'MFO-R13-2022-23.csv'

df_new = pd.read_csv(file_path_new + '/' + file_name_new, encoding='cp1252')

# %%
# Read in master list of organisations
scripts_temp_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/Data'
)
file_name_master = 'oscar_2022_2023_inyear_june_2023.pkl'

df_lookup = pd.read_pickle(scripts_temp_path + '/' + file_name_master)

# %%
# Read in manual classifications
file_path_manual = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/'
)
file_name_manual = 'IfG classification of bodies.xlsx'

df_manual = pd.read_excel(
    file_path_manual + '/' + file_name_manual,
    sheet_name='2023',
    usecols=[
        'New organisation name',
        'Name to use',
        'Organisation type',
        'Organisation status',
    ]
)

df_manual = df_manual.rename(
    columns={
        'New organisation name': 'ORGANISATION_LONG_NAME',
        'Name to use': 'Checked_Organisation_Name',
        'Organisation type': 'IfG_Organisation_Type',
        'Organisation status': 'IfG_Organisation_Status',
    }
)

# %%
# Get unique organisation names in annual OSCAR data not in master list
set(
    df_new['ORGANISATION_LONG_NAME'].unique()
) - (
    set(
        df_lookup['ORGANISATION_LONG_NAME'].unique()
    ) | set(
        df_manual['ORGANISATION_LONG_NAME'].unique()
    )
)

# %%
df_new.loc[
    df_new['ORGANISATION_LONG_NAME'].str.endswith('BEIS')
]['ORGANISATION_LONG_NAME'].unique()

# %%
df_new.loc[
    df_new['ORGANISATION_LONG_NAME_2'] != df_new['ORGANISATION_LONG_NAME']
][['ORGANISATION_LONG_NAME', 'ORGANISATION_LONG_NAME_2']]

# %%

# %%
# REMOVE TRAILING 'BEIS', 'DCMS STRINGS FROM ORGANISATION_LONG_NAME IN ALL DATASETS
df_new['ORGANISATION_LONG_NAME'] = df_new['ORGANISATION_LONG_NAME'].str.replace(
    r'\sBEIS|\sDCMS$',
    '',
    regex=True
)
df_manual['ORGANISATION_LONG_NAME'] = df_manual['ORGANISATION_LONG_NAME'].str.replace(
    r'\sBEIS|\sDCMS$',
    '',
    regex=True
)
df_lookup['ORGANISATION_LONG_NAME'] = df_lookup['ORGANISATION_LONG_NAME'].str.replace(
    r'\sBEIS|\sDCMS$',
    '',
    regex=True
)

# %%
df_new.loc[
    df_new['ORGANISATION_LONG_NAME'] == 'Arts Council of England Lottery'
]

# %%
