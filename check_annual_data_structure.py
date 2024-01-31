# %%
# !/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose
        Compare OSCAR annual data
        - To see whether column names are consistent
        - To see whether presence of nulls is consistent
        - To see how VERSION_CODE varies by year
    Inputs
        - txt: '../Source/Annual data/201718/2022_OSCAR_Extract_2017_18.txt'
        - txt: '../Source/Annual data/201819/2022_OSCAR_Extract_2018_19.txt'
        - txt: '../Source/Annual data/201920/2022_OSCAR_Extract_2019_20.txt'
        - txt: '../Source/Annual data/202021/2022_OSCAR_Extract_2020_21.txt'
        - csv: '../Source/Annual data/202122/MFO-R13-2021-22.csv'
        - csv: '../Source/Annual data/202223/MFO-R13-2022-23.csv'
    Outputs
        - pkl: 'temp/df_all_201718_202223.pkl'
            - NB: This creates a very large file
        - xlsx: '../Docs/Data structure - annual.xlsx'
    Parameters
        - files: Dictionary of file names
    Notes
        None
    Future developments
        - Move data checks to functions
        - Move data cleaning to functions
'''

import os

import pandas as pd
from pandas.io.formats import excel

from ds_utils import dataframe_operations as do

# %%
# DEFINE PARAMETERS
files = {
    '201718': '2022_OSCAR_Extract_2017_18.txt',
    '201819': '2022_OSCAR_Extract_2018_19.txt',
    '201920': '2022_OSCAR_Extract_2019_20.txt',
    '202021': '2022_OSCAR_Extract_2020_21.txt',
    '202122': 'MFO-R13-2021-22.csv',
    '202223': 'MFO-R13-2022-23.csv',
}

# %%
# READ IN NEW DATA
new_source_data_path_stub = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Source/Annual data/'
)

dict_annual = {
    year: pd.read_csv(
        new_source_data_path_stub + year + '/' + file_name,
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
temp_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Scripts/temp/'
)

df_all.to_pickle(temp_path + 'df_all_201718_202223.pkl')

# %%
# CHECK DATA STRUCTURE
# Tally nulls by column and year
df_null_x_year = do.count_column_nulls(
    df_all,
    groupby=['YEAR_SHORT_NAME'],
    transpose=True,
    percent=True,
    format='{:,.1g}'
)
df_null_x_year = df_null_x_year[[
    '2017/18',
    '2018/19',
    '2019/20',
    '2020/21',
    '2021/22',
    '2022/23',
]]

# %%
# Produce cross-tab of capital spend by year and month
df_version_code_x_year = pd.crosstab(
    df_all['VERSION_CODE'],
    df_all['YEAR_SHORT_NAME'],
)

# %%
# SAVE TO EXCEL
docs_path = (
    'C:/Users/' + os.getlogin() + '/'
    'Institute for Government/' +
    'Data - General/' +
    'Public finances/OSCAR/' +
    'Docs/'
)

excel.ExcelFormatter.header_style = None

with pd.ExcelWriter(
    docs_path + 'Data structure - annual.xlsx',
    engine='xlsxwriter',
    engine_kwargs={
        'options': {
            'strings_to_numbers': True,
        }
    }
) as writer:

    df_null_x_year.to_excel(
        writer,
        sheet_name='Nulls x year',
        freeze_panes=(1, 1),
    )
    df_version_code_x_year.to_excel(
        writer,
        sheet_name='Version code x year',
        freeze_panes=(1, 1),
    )
