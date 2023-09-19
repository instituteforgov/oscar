# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in an in-year release of OSCAR data and process it so it can be added
        to our aggregated OSCAR data
    Inputs
        - csv: 'OSCAR_in_year_dataset_June_2023.csv'
    Outputs
        None
    Parameters
        - column_renamings: Dictionary of column names used in the in-year data,
            and the renaming we want to apply
        - columns_to_drop: List of columns we want to drop from the in-year data
    Notes
        None
'''

import os

import pandas as pd

# %%
# DEFINE PARAMETERS
column_renamings = {
    'Economic Budget Code': 'PESA_ECONOMIC_BUDGET_CODE',
    'PESA Economic Group Code': 'PESA_ECONOMIC_GROUP_CODE',
    'Control Budget Code': 'CONTROL_BUDGET_L0_LONG_NAME',
    'Control Budget Detail Code': 'CONTROL_BUDGET_L1_LONG_NAME',
    'Economic Category Long Name': 'ECONOMIC_CATEGORY_LONG_NAME',
    'Economic Category Code': 'ECONOMIC_CATEGORY_CODE',
    'Amount': 'AMOUNT',
    'Segment Department Long Name': 'DEPARTMENT_GROUP_LONG_NAME',
    'Organisation Code': 'ORGANISATION_CODE',
    'Organisation': 'ORGANISATION_LONG_NAME',
    'Year': 'Financial_Year',
}

columns_to_drop = [
    'Quarter',
    'Month'
]

# %%
# READ IN IN-YEAR OSCAR DATA
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/In-year data'
)

df_inyear = pd.read_csv('OSCAR_in_year_dataset_June_2023.csv', encoding='cp1252')

# %%
# RUN CHECKS ON DATA
# Check column names are as expected
assert set(df_inyear.columns) == set(
    [
        'Organisation Code',
        'Organisation',
        'Control Budget Code',
        'Control Budget Detail Code',
        'Segment Department Long Name',
        'Sub Segment Code',
        'Sub Segment Long Name',
        'Economic Category Code',
        'Economic Category Long Name',
        'Economic Budget Code',
        'PESA Economic Group Code',
        'Version',
        'Year',
        'Quarter',
        'Month',
        'Amount',
    ]
), 'Column names not as expected'

# %%
# Check there's only one Version
assert len(df_inyear['Version'].unique()) == 1, 'More than one Version in in-year data'

# %%
# Check that for any one organisation, only one organisation code is used
assert df_inyear.groupby('Organisation')['Organisation Code'].nunique().max(), \
    'More than one organisation code for an organisation'

# %%
# EDIT DATA
# Rename columns
df_inyear = df_inyear.rename(columns=column_renamings)

# %%
# Drop columns we don't need
df_inyear = df_inyear.drop(columns=columns_to_drop)

# %%
# Add a column to indicate when the data was added
df_inyear['Added'] = pd.to_datetime('today')

# %%
# Exclude non-budget, non-voted spend
# NB: Note that these differ from what we get in the full year data - the values
# we get in the CONTROL_BUDGET_L0_LONG_NAME column differ and we don't
# have a ACCOUNTING_AUTHORITY_L0_CODE column here
df_inyear = df_inyear[
    (df_inyear['CONTROL_BUDGET_L0_LONG_NAME'] != 'TOTAL NON-BUDGET') &
    ~(df_inyear['Sub Segment Long Name'].str.upper().str.contains('NON-VOTED')) &
    ~(df_inyear['Sub Segment Long Name'].str.upper().str.contains('NON VOTED'))
]

# %%
# Reorder columns
df_inyear = df_inyear[
    [
        'PESA_ECONOMIC_BUDGET_CODE',
        'PESA_ECONOMIC_GROUP_CODE',
        'CONTROL_BUDGET_L0_LONG_NAME',
        'CONTROL_BUDGET_L1_LONG_NAME',
        'ECONOMIC_CATEGORY_LONG_NAME',
        'ECONOMIC_CATEGORY_CODE',
        'AMOUNT',
        'DEPARTMENT_GROUP_LONG_NAME',
        'ORGANISATION_CODE',
        'ORGANISATION_LONG_NAME',
        'Financial_Year',
        'Version',
        'Sub Segment Code',
        'Sub Segment Long Name',
        'Added',
    ]
]

# %%
# SUM SPENDING
df_inyear_annual = df_inyear.groupby(
    [
        'ORGANISATION_LONG_NAME',
        'ORGANISATION_CODE',
        'CONTROL_BUDGET_L0_LONG_NAME',
        'CONTROL_BUDGET_L1_LONG_NAME',
        'DEPARTMENT_GROUP_LONG_NAME',
        'Sub Segment Code',
        'Sub Segment Long Name',
        'ECONOMIC_CATEGORY_LONG_NAME',
        'ECONOMIC_CATEGORY_CODE',
        'PESA_ECONOMIC_GROUP_CODE',
        'PESA_ECONOMIC_BUDGET_CODE',
        'Version',
        'Financial_Year',
        'Added'
    ]
).agg({'AMOUNT': 'sum'}).reset_index()

# %%
df_inyear_annual

# %%
# READ IN PREVIOUS OSCAR DATA, FROM WHICH WE'LL PULL IN ORG DETAILS
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/Data'
)

df_previous = pd.read_pickle('2022_11_22_matched_oscar_21_22.pkl')

# %%
df_previous
