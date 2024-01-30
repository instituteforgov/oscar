# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Compare OSCAR annual data
        - To see whether column names are consistent
        - To see whether presence of nulls is consistent
    Inputs
        - txt: '2022_OSCAR_Extract_2017_18.txt'
        - txt: '2022_OSCAR_Extract_2018_19.txt'
        - txt: '2022_OSCAR_Extract_2019_20.txt'
        - txt: '2022_OSCAR_Extract_2020_21.txt'
        - csv: 'MFO-R13-2021-22.csv'
        - csv: 'MFO-R13-2022-23.csv'
    Outputs
        - pkl: 'df_all_201718_202223.pkl'
            - NB: This creates a very large file
        - xlsx: 'Nulls in annual data.xlsx'
    Parameters
        - files: Dictionary of file names
    Notes
        None
'''

import os

import pandas as pd
from pandas.io.formats import excel

from ds_utils import dataframe_operations as do

# %%
# READ IN ANNUAL OSCAR DATA
files = {
    '201718': '2022_OSCAR_Extract_2017_18.txt',
    '201819': '2022_OSCAR_Extract_2018_19.txt',
    '201920': '2022_OSCAR_Extract_2019_20.txt',
    '202021': '2022_OSCAR_Extract_2020_21.txt',
    '202122': 'MFO-R13-2021-22.csv',
    '202223': 'MFO-R13-2022-23.csv',
}

source_data_annual_file_path_stub = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/Annual data/'
)

dict_annual = {
    year: pd.read_csv(
        source_data_annual_file_path_stub + year + '/' + file_name,
        encoding='cp1252',
        sep='|' if '.txt' in file_name else ','
    )
    for year, file_name in files.items()
}

# %%
# CHECK THAT COLUMNS ARE THE SAME IN ALL DFS
for df in dict_annual.values():
    assert set(df.columns) == set(dict_annual['202223'].columns)

# %%
# PRODUCE COMBINED DF
df_all = pd.concat(
    [df for df in dict_annual.values()]
)

# %%
# CLEAN YEAR_SHORT_NAME
# NB: This handles the two formats we see: 2017-18 and 202122
df_all['YEAR_SHORT_NAME'] = (
    df_all['YEAR_SHORT_NAME'].astype(str).str[:4] + '/' +
    df_all['YEAR_SHORT_NAME'].astype(str).str[-2:]
)

# %%
# SAVE TEMPORARY COPY OF DATA
temp_file_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/temp/'
)

df_all.to_pickle(temp_file_path + 'df_all_201718_202223.pkl')

# %%
# COUNT NUMBER OF COLUMN NULLS
df_all_column_nulls = do.count_column_nulls(
    df_all,
    groupby=['YEAR_SHORT_NAME'],
    transpose=True,
    percent=True,
    format='{:,.1g}'
)

# %%
# REORDER COLUMNS
df_all_column_nulls = df_all_column_nulls[[
    '2017/18',
    '2018/19',
    '2019/20',
    '2020/21',
    '2021/22',
    '2022/23',
]]

# %% SAVE DETAILS OF NULLS TO EXCEL
docs_file_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Docs/'
)

excel.ExcelFormatter.header_style = None

df_all_column_nulls.to_excel(
    docs_file_path + 'Nulls in annual data.xlsx',
    freeze_panes=(1, 1),
    engine='xlsxwriter',
    engine_kwargs={
        'options': {
            'strings_to_numbers': True,
        }
    }
)
