# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in an in-year release of OSCAR data and process it so it can be added
        to our aggregated OSCAR data
    Inputs
        - csv: 'OSCAR_in_year_dataset_June_2023.csv'
        - pkl: 'oscar_2021_2022_annual.pkl'
    Outputs
        None
    Parameters
        - column_renamings: Dictionary of column names used in the in-year data,
            and the renaming we want to apply
        - columns_to_drop: List of columns we want to drop from the in-year data
    Notes
        - We exclude non-budget, non-voted spend, as per previous Whitehall
        Monitor analysis
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
        'Sub Segment Long Name'
    ]
]

# %%
# SUM SPENDING
df_inyear_annual = df_inyear.groupby(
    [
        'PESA_ECONOMIC_GROUP_CODE',
        'PESA_ECONOMIC_BUDGET_CODE',
        'CONTROL_BUDGET_L0_LONG_NAME',
        'CONTROL_BUDGET_L1_LONG_NAME',
        'ECONOMIC_CATEGORY_LONG_NAME',
        'ECONOMIC_CATEGORY_CODE',
        'DEPARTMENT_GROUP_LONG_NAME',
        'ORGANISATION_CODE',
        'ORGANISATION_LONG_NAME',
        'Financial_Year',
        'Sub Segment Code',
        'Sub Segment Long Name',
        'Version',
    ]
).agg({'AMOUNT': 'sum'}).reset_index()

# %%
# READ IN PREVIOUS OSCAR DATA, FROM WHICH WE'LL PULL IN ORG DETAILS
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/data'
)

df_previous = pd.read_pickle('oscar_2021_2022_annual.pkl')

# %%
# MERGE IN ORG DETAILS FROM PREVIOUS OSCAR DATA
# NB: merge() is used here rather than combine_first() as these columns don't
# already exist in the data
df_inyear_annual_merged = df_inyear_annual.merge(
    df_previous[[
            'ORGANISATION_LONG_NAME',
            'ORGANISATION_CODE',
            'IfG_Organisation_Type',
            'IfG_Organisation_Status',
            'Checked_Organisation_Name'
    ]].drop_duplicates(),
    how='left',
    on=['ORGANISATION_CODE'],
    suffixes=(None, '_previous'),
).drop(columns=['ORGANISATION_LONG_NAME_previous'])

# %%
# CARRY OUT CHECKS ON MERGED DATA
# Check that df_inyear_annual_merged has the same number of rows as df_inyear_annual
assert len(df_inyear_annual_merged) == len(df_inyear_annual), \
    'df_inyear_annual_merged has a different number of rows to df_inyear_annual'

# %%
# MERGE IN ORG DETAILS FROM MANUAL CLASSIFICATION
# Read in manual classifications
os.chdir(
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/'
)

df_manual = pd.read_excel(
    'IfG classification of bodies.xlsx',
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
# Merge in manual classifications
# NB: combine_first() is used here rather than merge() as these columns already
# exist in the data, and rather than fillna() as this doesn't rely on
# us having a unique index
# NB: We can't use inplace=True, as combine_first() would return None, which we
# wouldn't be able to reset the index on
df_inyear_annual_merged = df_inyear_annual_merged.set_index('ORGANISATION_LONG_NAME').combine_first(
    df_manual[[
            'ORGANISATION_LONG_NAME',
            'IfG_Organisation_Type',
            'IfG_Organisation_Status',
            'Checked_Organisation_Name'
    ]].drop_duplicates().set_index('ORGANISATION_LONG_NAME'),
).reset_index()

# %%
# Reset order of columns, which is lost by combine_first()
df_inyear_annual_merged = df_inyear_annual_merged[
    [c for c in df_inyear_annual.columns if c not in ['Version', 'AMOUNT']] + [
        'IfG_Organisation_Type',
        'IfG_Organisation_Status',
        'Checked_Organisation_Name',
        'Version',
        'AMOUNT'
    ]
]

# %%
# Drop rows where AMOUNT is NaN
# NB: We need to do this as combine_first() will have created rows where
# an organisation exists in df_manual, even where it doesn't exist in
# df_inyear_annual_merged
df_inyear_annual_merged = df_inyear_annual_merged[
    df_inyear_annual_merged['AMOUNT'].notna()
]

# %%
# CARRY OUT CHECKS ON MERGED DATA
# Check that df_inyear_annual_merged has the same number of rows as df_inyear_annual
assert len(df_inyear_annual_merged) == len(df_inyear_annual), \
    'df_inyear_annual_merged has a different number of rows to df_inyear_annual'

# %%
# EDIT DATA
# Add a column to indicate when the data was added
df_inyear_annual_merged['Added'] = pd.to_datetime('today').date()

# %%
# CARRY OUT FINAL CHECKS ON DATA
# Check that no bodies have IfG_Organisation_Status, Checked_Organisation_Name or
# IfG_Organisation_Type of NaN
assert df_inyear_annual_merged['IfG_Organisation_Status'].isna().sum() == 0, \
    'NaN values in IfG_Organisation_Status column'

assert df_inyear_annual_merged['Checked_Organisation_Name'].isna().sum() == 0, \
    'NaN values in Checked_Organisation_Name column'

assert df_inyear_annual_merged['IfG_Organisation_Type'].isna().sum() == 0, \
    'NaN values in IfG_Organisation_Type column'
