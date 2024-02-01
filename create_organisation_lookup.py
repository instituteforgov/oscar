# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Create a lookup table of organisation codes, organisation names and IfG classifications
        (edited organisation name, organisation type, organisation sub-type)
    Inputs
        - pkl: 'data/oscar_2021_2022_annual.pkl'
        - xlsx: '../Collated OSCAR data.xlsx'
    Outputs
        - pkl: 'data/df_organisations_lookup.pkl'
    Parameters
        XXX
    Notes
        - 2021/22 annual data (oscar_2021_2022_annual.pkl) is used as an import as it contains
        some organisations that aren't in the collated OSCAR data - perhaps organisation that
        have not had any non-budget, non-voted spend
        - 2022/23 in-year June 2023 data (oscar_2022_2023_inyear_june_2023.pkl) isn't used as an
        import as it doesn't contain anything that's not in the collated OSCAR data
        - Manual classification docs aren't used as, with very few exceptions, they don't contain
        anything that's not in the collated OSCAR data
'''

import os

import pandas as pd

from utils.functions import strip_trailing_dept_initialism

# %%
# READ IN DATASETS
# Collated OSCAR data
root_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/'
)

df_collated_data = pd.read_excel(
    root_path + 'Collated OSCAR data.xlsx',
    sheet_name='all_values',
)
df_collated_data = df_collated_data[
    df_collated_data['PESA_ECONOMIC_BUDGET_CODE'] != 'Total'
]

# 2021-22 annual data
scripts_data_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/data/'
)

df_202122_annual = pd.read_pickle(scripts_data_path + 'oscar_2021_2022_annual.pkl')

# %%
# CLEAN DATA
# Fix Financial_Year format
df_collated_data['Financial_Year'] = (
    df_collated_data['Financial_Year'].astype(str).str.replace('_', '/')
)

# %%
# Drop records with 'CHECK' IfG_Organisation_Type
df_202122_annual = df_202122_annual[
    df_202122_annual['IfG_Organisation_Type'] != 'CHECK'
]

# %%
# Remove trailing 'BEIS', 'DCMS' strings from ORGANISATION_LONG_NAME, Checked_Organisation_Name
df_collated_data = strip_trailing_dept_initialism(
    df=df_collated_data,
    col='ORGANISATION_LONG_NAME',
)
df_collated_data = strip_trailing_dept_initialism(
    df=df_collated_data,
    col='Checked_Organisation_Name',
)
df_202122_annual = strip_trailing_dept_initialism(
    df=df_202122_annual,
    col='ORGANISATION_LONG_NAME',
)
df_202122_annual = strip_trailing_dept_initialism(
    df=df_202122_annual,
    col='Checked_Organisation_Name',
)

# %%
# Trim whitespace from IfG_Organisation_Status
df_collated_data['IfG_Organisation_Status'] = df_collated_data[
    'IfG_Organisation_Status'
].str.strip()
df_202122_annual['IfG_Organisation_Status'] = df_202122_annual[
    'IfG_Organisation_Status'
].str.strip()

# %%
# Make IfG_Organisation_Status sentence case, bar the string 'NDPB'
df_collated_data['IfG_Organisation_Status'] = (
    df_collated_data['IfG_Organisation_Status'].str.capitalize().str.replace(
        r'ndpb|Ndpb', 'NDPB', regex=True
    )
)
df_202122_annual['IfG_Organisation_Status'] = (
    df_202122_annual['IfG_Organisation_Status'].str.capitalize().str.replace(
        r'ndpb|Ndpb', 'NDPB', regex=True
    )
)

# %%
# CREATE LOOKUP TABLE
# Create lookup tables from each dataset
df_collated_data_lookup = df_collated_data[[
    'ORGANISATION_CODE',
    'ORGANISATION_LONG_NAME',
    'Checked_Organisation_Name',
    'IfG_Organisation_Type',
    'IfG_Organisation_Status'
]].drop_duplicates()

df_202122_annual_lookup = df_202122_annual[[
    'ORGANISATION_CODE',
    'ORGANISATION_LONG_NAME',
    'Checked_Organisation_Name',
    'IfG_Organisation_Type',
    'IfG_Organisation_Status'
]].drop_duplicates()

# %%
# Add latest financial year to df_collated_data_lookup
df_collated_data_lookup = df_collated_data_lookup.merge(
    df_collated_data.groupby(
        ['ORGANISATION_CODE', 'ORGANISATION_LONG_NAME']
    )['Financial_Year'].max().reset_index(),
    how='left',
    on=['ORGANISATION_CODE', 'ORGANISATION_LONG_NAME']
).rename(
    columns={'Financial_Year': 'Latest financial year'}
)

# %%
# Add latest financial year to df_collated_data_lookup
df_202122_annual_lookup['Latest financial year'] = '2021/22'

# %%
# Create master lookup table
df_lookup = pd.concat([
    df_collated_data_lookup,
    df_202122_annual_lookup
]).sort_values(
    by=['ORGANISATION_CODE', 'ORGANISATION_LONG_NAME', 'Latest financial year']
).drop_duplicates(
    subset=[c for c in df_collated_data_lookup.columns if c != 'Latest financial year'],
    keep='last'
).reset_index(drop=True)

# %%
# IMPORT NEW DATA
source_annual_202223_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/Annual data/202223/'
)
file_name_new = 'MFO-R13-2022-23.csv'

df_new = pd.read_csv(source_annual_202223_path + file_name_new, encoding='cp1252')

# %%
# CLEAN DATA
# Remove trailing 'BEIS', 'DCMS' strings from ORGANISATION_LONG_NAME
df_new = strip_trailing_dept_initialism(
    df=df_new,
    col='ORGANISATION_LONG_NAME',
)

# %%
# MANUALLY ADD NEW ORGANISATIONS TO LOOKUP
# Source: https://www.gov.uk/government/organisations/advanced-research-and-invention-agency
# Seems to be an alternative name for Parliament: Restoration and Renewal - same organisation
# code (PRR079) is used
df_lookup = pd.concat([
    df_lookup,
    pd.DataFrame(
        {
            'ORGANISATION_CODE': 'ARI084',
            'ORGANISATION_LONG_NAME': 'Advanced Research and Invention Agency',
            'Checked_Organisation_Name': 'Advanced Research and Invention Agency',
            'IfG_Organisation_Type': 'Public body',
            'IfG_Organisation_Status': 'Executive NDPB',
            'Latest financial year': '2022/23'
        },
        index=[0]
    ),
    pd.DataFrame(
        {
            'ORGANISATION_CODE': 'UKT013',
            'ORGANISATION_LONG_NAME': 'Department for Business and Trade',
            'Checked_Organisation_Name': 'Department for Business and Trade',
            'IfG_Organisation_Type': 'Department',
            'IfG_Organisation_Status': 'Department',
            'Latest financial year': '2022/23'
        },
        index=[0]
    ),
    pd.DataFrame(
        {
            'ORGANISATION_CODE': 'BIS084',
            'ORGANISATION_LONG_NAME': 'Department for Science, Innovation and Technology',
            'Checked_Organisation_Name': 'Department for Science, Innovation and Technology',
            'IfG_Organisation_Type': 'Department',
            'IfG_Organisation_Status': 'Department',
            'Latest financial year': '2022/23'
        },
        index=[0]
    ),
    pd.DataFrame(
        {
            'ORGANISATION_CODE': 'PRR079',
            'ORGANISATION_LONG_NAME': 'Parliamentary Works Grant',
            'Checked_Organisation_Name': 'Parliamentary Works Grant',
            'IfG_Organisation_Type': 'Houses of Parliament',
            'IfG_Organisation_Status': 'Houses of Parliament',
            'Latest financial year': '2022/23'
        },
        index=[0]
    ),
]).reset_index(drop=True)

# %%
# SAVE LOOKUP TO PICKLE
scripts_data_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/data/'
)

df_lookup.to_pickle(scripts_data_path + 'df_organisations_lookup.pkl')
