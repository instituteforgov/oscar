# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Produce a file of 2017/18-2022/23 capital spend by month and carry out analysis
    Inputs
        - pkl: 'temp/df_all_201718_202223.pkl'
    Outputs
        - csv: '../Ad-hoc analysis/Capital spend by month/Capital spend by month, 201718-202223.csv'
    Parameters
        None
    Notes
        None
'''

import os

from IPython.display import display
import pandas as pd

from utils.functions import convert_month_string_to_code

# %%
# READ IN DATA
# Data for analysis
temp_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/temp/'
)

df_all = pd.read_pickle(temp_path + 'df_all_201718_202223.pkl')

# %%
# CLEAN DATA
# Clean months, converting e.g. Jan-18 to P10
df_all = convert_month_string_to_code(df_all, 'MONTH_SHORT_NAME')

# %%
# RESTRICT DATA
# Restrict rowset to 'R13' (2017/18-2020/21)/'Forecast' (2021/22-2022/23) records
# NB: It sounds like this is outturn data for a whole year: see README.md
df_all = df_all.loc[
    df_all['VERSION_CODE'].isin(['R13', 'Forecast'])
]

# %%
# Drop entirely NaN columns
df_all = df_all.dropna(axis=1, how='all')

# %%
# Restrict to capital spend
df_capital = df_all.loc[
    df_all['ECONOMIC_BUDGET_CODE'] == 'CAPITAL'
]

# %%
# SAVE TO CSV
adhoc_analysis_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Ad-hoc analysis/'
)

df_capital.to_csv(
    adhoc_analysis_path + 'Capital spend by month/Capital spend by month, 201718-202223.csv',
    chunksize=10000,
    index=False,
)

# %%
# ANALYSIS
# Produce cross-tab of capital spend by year and month
with pd.option_context('display.float_format', '{:,.0f}'.format):
    display(
        pd.crosstab(
            df_capital['YEAR_SHORT_NAME'],
            df_capital['MONTH_SHORT_NAME'],
            values=df_capital['AMOUNT'],
            aggfunc='sum'
        )
    )

# %%
