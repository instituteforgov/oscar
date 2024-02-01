# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Read in and process annual OSCAR data
    Inputs
        - csv: '../Source/MFO-R13-2022-23.csv'
        - pkl: 'data/df_organisations_lookup.pkl'
    Outputs
        - pkl: 'oscar_2022_2023_annual_p13.pkl'
        - xlsx: 'oscar_2022_2023_annual_p13.xlsx'
    Parameters
        - column_renamings: Dictionary of column names used in the annual data,
        and the renaming we want to apply
        - collated_data_columns: List of columns in the collated OSCAR data
        - control_budget_l0_replacements: Dictionary of CONTROL_BUDGET_L0_LONG_NAME
        values that need to be replaced
        - control_budget_l1_replacements: Dictionary of CONTROL_BUDGET_L1_LONG_NAME
        values that need to be replaced
    Notes
        None
    Future developments
        - Redesign 'Collated OSCAR data.xlsx' to use ECONOMIC_BUDGET_CODE rather than
        PESA_ECONOMIC_BUDGET_CODE
'''

import os

import pandas as pd
from pandas.io.formats import excel

from utils.functions import strip_trailing_dept_initialism

# %%
# DEFINE PARAMETERS
# NB: control_budget_l0_replacements and control_budget_l1_replacements are reversed
# compared to how they're used in process_inyear_data.py - may have unintentionally
# flipped columns there
column_renamings = {
    'YEAR_NO': 'Financial_Year',
}

collated_data_columns = [
    'PESA_ECONOMIC_BUDGET_CODE',
    'PESA_ECONOMIC_GROUP_CODE',
    'CONTROL_BUDGET_L0_LONG_NAME',
    'CONTROL_BUDGET_L1_LONG_NAME',
    'ECONOMIC_CATEGORY_LONG_NAME',
    'ECONOMIC_CATEGORY_CODE',
    'ACCOUNTING_AUTHORITY_L0_CODE',
    'ECONOMIC_GROUP_LONG_NAME',
    'INCOME_CATEGORY_SHORT_NAME',
    'CHART_OF_ACCOUNTS_L5_LONG_NAME',
    'BUDGETING_ORGANISATIONS_CODE',
    'DEPARTMENT_GROUP_CODE',
    'DEPARTMENT_GROUP_LONG_NAME',
    'ORGANISATION_CODE',
    'ORGANISATION_LONG_NAME',
    'ORGANISATION_TYPE_L1_LONG_NAME',
    'ORGANISATION_TYPE_L1_CODE',
    'Financial_Year',
    'Checked_Organisation_Name',
    'IfG_Organisation_Type',
    'IfG_Organisation_Status',
    'AMOUNT',
    'Added',
]

control_budget_l0_replacements = {
    'DEL PROG': 'DEPARTMENTAL EXPENDITURE LIMITS PROGRAMME',
    'DEL ADMIN': 'DEPARTMENTAL EXPENDITURE LIMITS ADMINISTRATION',
    'DEPT AME': 'DEPARTMENTAL ANNUALLY MANAGED EXPENDITURE',
    'NON-DEPT AME': 'NON-DEPARTMENTAL ANNUALLY MANAGED EXPENDITURE',
}

control_budget_l1_replacements = {
    'TOTAL DEL': 'DEPARTMENTAL EXPENDITURE LIMITS',
    'TOTAL AME': 'ANNUALLY MANAGED EXPENDITURE'
}

# %%
# READ IN DATA
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
# Organisations lookup
scripts_data_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/data/'
)

df_lookup = pd.read_pickle(scripts_data_path + 'df_organisations_lookup.pkl')

# %%
# RUN CHECKS ON DATA
# Check columns required for collated data are present
assert all(
    c in df_new.columns for c in collated_data_columns + ['VERSION_CODE', 'YEAR_NO']
    if c not in [
        'Financial_Year',
        'Checked_Organisation_Name',
        'IfG_Organisation_Type',
        'IfG_Organisation_Status',
        'Added',
    ]
), \
    'Not all columns required for collated data are present'

# %%
# Check there's only one YEAR_NO
assert len(df_new['YEAR_NO'].unique()) == 1, 'More than one YEAR_NO in annual data'

# %%
# Check there's only one Version
assert len(df_new['VERSION_CODE'].unique()) == 1, 'More than one Version in annual data'

# %%
# Check that for any one organisation, only one organisation code is used
assert (
    df_new.groupby('ORGANISATION_LONG_NAME')['ORGANISATION_CODE'].nunique().max() == 1
), 'More than one organisation code for an organisation'

# %%
# EDIT DATA
# Rename columns
df_new = df_new.rename(columns=column_renamings)

# %%
# Exclude non-budget, non-voted spend
# NB: Columns and values differ between in-year and annual data
df_new = df_new[
    (df_new['CONTROL_BUDGET_L1_LONG_NAME'] != 'NON-BUDGET') &
    (df_new['ACCOUNTING_AUTHORITY_L1_LONG_NAME'] != 'NON-VOTED')
]

# %%
# Crossfill PESA_ECONOMIC_BUDGET_CODE column with ECONOMIC_BUDGET_CODE values
# NB: This is done to make the data we have fit in the shape 'Collated OSCAR data.xlsx'
# expects - ideally we would use keep the ECONOMIC_BUDGET_CODE column
# TODO: Redesign 'Collated OSCAR data.xlsx' to use ECONOMIC_BUDGET_CODE rather than
# PESA_ECONOMIC_BUDGET_CODE
df_new['PESA_ECONOMIC_BUDGET_CODE'] = df_new['PESA_ECONOMIC_BUDGET_CODE'].fillna(
    df_new['ECONOMIC_BUDGET_CODE']
)

# %%
# Drop columns that aren't in collated data or MONTH_SHORT_NAME
df_new = df_new[[
    c for c in df_new.columns if c in collated_data_columns + ['MONTH_SHORT_NAME']
]]

# %%
# Remove trailing 'BEIS', 'DCMS' strings from ORGANISATION_LONG_NAME
df_new = strip_trailing_dept_initialism(
    df=df_new,
    col='ORGANISATION_LONG_NAME',
)

# %%
# Reorder columns
df_new = df_new[[
    'MONTH_SHORT_NAME',
    'PESA_ECONOMIC_BUDGET_CODE',
    'PESA_ECONOMIC_GROUP_CODE',
    'CONTROL_BUDGET_L0_LONG_NAME',
    'CONTROL_BUDGET_L1_LONG_NAME',
    'ECONOMIC_CATEGORY_LONG_NAME',
    'ECONOMIC_CATEGORY_CODE',
    'ACCOUNTING_AUTHORITY_L0_CODE',
    'ECONOMIC_GROUP_LONG_NAME',
    'INCOME_CATEGORY_SHORT_NAME',
    'CHART_OF_ACCOUNTS_L5_LONG_NAME',
    'BUDGETING_ORGANISATIONS_CODE',
    'DEPARTMENT_GROUP_CODE',
    'DEPARTMENT_GROUP_LONG_NAME',
    'ORGANISATION_CODE',
    'ORGANISATION_LONG_NAME',
    'ORGANISATION_TYPE_L1_LONG_NAME',
    'ORGANISATION_TYPE_L1_CODE',
    'Financial_Year',
    'AMOUNT',
]]

# %%
# SUM SPENDING
# NB: dropna=False is required otherwise NaNs in PESA_ECONOMIC_GROUP_CODE mean
# we get an empty result set
df_new_total = df_new.groupby(
    [c for c in df_new.columns if c not in ['MONTH_SHORT_NAME', 'AMOUNT']],
    dropna=False
).agg({'AMOUNT': 'sum'}).reset_index()

# %%
# MERGE IN ORG DETAILS FROM PREVIOUS OSCAR DATA
# NB: merge() is used here rather than combine_first() as these columns don't
# already exist in the data
df_new_total_merged = df_new_total.merge(
    df_lookup[[
        'ORGANISATION_CODE',
        'ORGANISATION_LONG_NAME',
        'Checked_Organisation_Name',
        'IfG_Organisation_Type',
        'IfG_Organisation_Status',
    ]].drop_duplicates(),
    how='left',
    on=['ORGANISATION_CODE', 'ORGANISATION_LONG_NAME'],
)

# %%
# CARRY OUT CHECKS ON MERGED DATA
# Check that df_new_total_merged has the same number of rows as df_new_total
assert len(df_new_total_merged) == len(df_new_total), \
    'df_new_total_merged has a different number of rows to df_new_total'

# %%
# Check that no bodies have IfG_Organisation_Status, Checked_Organisation_Name or
# IfG_Organisation_Type of NaN
assert df_new_total_merged['Checked_Organisation_Name'].isna().sum() == 0, \
    'NaN values in Checked_Organisation_Name column'

assert df_new_total_merged['IfG_Organisation_Status'].isna().sum() == 0, \
    'NaN values in IfG_Organisation_Status column'

assert df_new_total_merged['IfG_Organisation_Type'].isna().sum() == 0, \
    'NaN values in IfG_Organisation_Type column'

# %%
# Check that no bodies have IfG_Organisation_Status, Checked_Organisation_Name or
# IfG_Organisation_Type featuring 'CHECK'
assert df_new_total_merged[
    df_new_total_merged['Checked_Organisation_Name'].str.contains('CHECK')
].empty, 'Found records with Checked_Organisation_Name featuring the string "CHECK"'

assert df_new_total_merged[
    df_new_total_merged['IfG_Organisation_Type'].str.contains('CHECK')
].empty, 'Found records with IfG_Organisation_Type featuring the string "CHECK"'

assert df_new_total_merged[
    df_new_total_merged['IfG_Organisation_Status'].str.contains('CHECK')
].empty, 'Found records with IfG_Organisation_Status featuring the string "CHECK"'

# %%
# EDIT DATA
# Add a column to indicate when the data was added
df_new_total_merged['Added'] = pd.to_datetime('today').date()

# %%
# Reorder columns
df_new_total_merged = df_new_total_merged[collated_data_columns]

# %%
# Format Financial_Year
df_new_total_merged['Financial_Year'] = (
    df_new_total_merged['Financial_Year'].astype(str).str[:4] + '_' +
    df_new_total_merged['Financial_Year'].astype(str).str[-2:]
)

# %%
# Bring CONTROL_BUDGET_L0_LONG_NAME, CONTROL_BUDGET_L1_LONG_NAME values in line with
# those in collated data
df_new_total_merged['CONTROL_BUDGET_L0_LONG_NAME'].replace(
    control_budget_l0_replacements,
    inplace=True
)

df_new_total_merged['CONTROL_BUDGET_L1_LONG_NAME'].replace(
    control_budget_l1_replacements,
    inplace=True
)

# %%
# SAVE DATA TO PICKLE
df_new_total_merged.to_pickle(scripts_data_path + 'oscar_2022_2023_annual_p13.pkl')

# %%
# SAVE DATA TO EXCEL
temp_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/temp/'
)

excel.ExcelFormatter.header_style = None
df_new_total_merged.to_excel(temp_path + 'oscar_2022_2023_annual_p13.xlsx', index=False)

# %%
