'''
Script to join/merge organisations between years in OSCAR

This now uses the full matching across all years

'''

import pandas as pd
import numpy as np

from __future__ import unicode_literals
import unittest
import re
import sys
import pycodestyle

import math

baseline_oscar = pd.read_pickle('2022_11_22_matched_oscar_21_22.pkl')

# simplifies the data to a list of organisations and organisation codes (used within OSCAR)
baseline_oscar_orgs_df = organisation_code_extraction(baseline_oscar)

file_names = ['2015_OSCAR_Extract_2010_11.txt',
              '2015_OSCAR_Extract_2011_12.txt',
              '2015_OSCAR_Extract_2012_13.txt',
              '2015_OSCAR_Extract_2013_14.txt',
              '2015_OSCAR_Extract_2014_15.txt',
              '2017 OSCAR Extract 2015-16.csv',
              '2017 OSCAR Extract 2016-17.csv',
              '2022_OSCAR_Extract_2017_18.txt',
              '2022_OSCAR_Extract_2018_19.txt',
              '2022_OSCAR_Extract_2019_20.txt',
              '2022_OSCAR_Extract_2020_21.txt',
              '2022_OSCAR_Extract_2021_22.txt']

for j in range(0, len(file_names)):

    file_location = 'Source files\\' + file_names[j]

    new_oscar = pd.read_csv(file_location, delimiter='|', encoding='cp1252')

    # bring organisations and codes out into a unique dataframe
    new_oscar_orgs_df = organisation_code_extraction(new_oscar)

    # compare organisations from this year to current year and add checking information
    checked_new_oscar_orgs_df, unfound_orgs_df = checking_organisations(new_oscar_orgs_df, baseline_oscar, file_names[j])

    # want to group organisation information over the months into a single data line
    all_oscar_df, summary_totals_df = grouping_by_organisation(new_oscar, checked_new_oscar_orgs_df)

    # add year information into these dataframes
    all_oscar_df['Financial_Year'] = file_names[j][-11:-4]
    summary_totals_df['Financial_year'] = file_names[j][-11:-4]

    # save up the findings
    all_oscar_df.to_pickle(file_names[j][:-4]+'_matched.pkl')
    summary_totals_df.to_pickle(file_names[j][:-4]+'_summary_L0.pkl')

    # clean and group the oscar data
    cleaned_grouped_df = clean_group_oscar_lite(all_oscar_df)

    # assemble the information into a single place...
    if j == 0:
        all_values = cleaned_grouped_df
        positive_values = cleaned_grouped_df[cleaned_grouped_df['AMOUNT']>0]
        all_unfound_orgs_df = unfound_orgs_df
    else:
        all_values = pd.concat([all_values, cleaned_grouped_df], ignore_index=True)
        positive_values = pd.concat([positive_values, cleaned_grouped_df[cleaned_grouped_df['AMOUNT']>0]], ignore_index=True)
        all_unfound_orgs_df = pd.concat([all_unfound_orgs_df, unfound_orgs_df], ignore_index=True)

    with pd.ExcelWriter('oscar_2021_22_test_rerun.xlsx') as writer:

        all_values.to_excel(writer, sheet_name='all_values')
#        positive_values.to_excel(writer, sheet_name='positive_values')
        all_unfound_orgs_df.to_excel(writer, sheet_name='unfound')

# this is to run against the updated organisation mapping done by Nat (and will do change in status over time)

for j in range(0, len(file_names)):

    # find the files
    file_location = 'Source files\\' + file_names[j]

    # read the pickle file...
    all_oscar_df = pd.read_pickle(file_names[j][:-4]+'_matched.pkl')

    # consider and update the IfG organisation information
    all_oscar_df = additional_organisation_matching(all_oscar_df, file_names[j][:-4])

    # clean and group the oscar data
    cleaned_grouped_df = clean_group_oscar_lite(all_oscar_df)

    # assemble the information into a single place...
    if j == 0:
        all_values = cleaned_grouped_df
        positive_values = cleaned_grouped_df[cleaned_grouped_df['AMOUNT']>0]
    else:
        all_values = pd.concat([all_values, cleaned_grouped_df], ignore_index=True)
        positive_values = pd.concat([positive_values, cleaned_grouped_df[cleaned_grouped_df['AMOUNT']>0]], ignore_index=True)

    with pd.ExcelWriter('oscar_2021_22_release_summarised_5.xlsx') as writer:

        all_values.to_excel(writer, sheet_name='all_values')
        positive_values.to_excel(writer, sheet_name='positive_values')

def additional_organisation_matching(all_oscar_df, file_names):

    # load in the additional checking
    additional_organisations = pd.read_excel('oscar_organisation_matching_unfound.xlsx')

    org_type = []
    org_status = []

    # pull organisation and match by long name
    for j in range(0, len(all_oscar_df)):

        new_match_info = additional_organisations[additional_organisations['ORGANISATION_LONG_NAME'] == all_oscar_df['ORGANISATION_LONG_NAME'][j]]

        org_type.append(new_match_info['Type_of_organisation'])
        org_status.append(new_match_info['Exact status'])

    all_oscar_df['Type_of_organisation'] = org_type
    all_oscar_df['Exact status'] = org_status

    # save the resulting file
    oscar_df.to_pickle(file_name+'_matched_over_time.pkl')

    return all_oscar_df

# build information into the new oscar dataset
def organisation_matching(org_code, org_long_name, checked_orgs_df, oscar_segment):

    chk_org_name = checked_orgs_df[checked_orgs_df['ORGANISATION_CODE']==org_code]['Checked_Organisation_Name'].values[0]
    ifg_org_type = checked_orgs_df[checked_orgs_df['ORGANISATION_CODE']==org_code]['IfG_Organisation_Type'].values[0]
    ifg_org_stat = checked_orgs_df[checked_orgs_df['ORGANISATION_CODE']==org_code]['IfG_Organisation_Status'].values[0]

    # add these to the OSCAR dataframe
    oscar_segment['Checked_Organisation_Name'] = chk_org_name
    oscar_segment['IfG_Organisation_Type'] = ifg_org_type
    oscar_segment['IfG_Organisation_Status'] = ifg_org_stat

    return oscar_segment


def summarise_org_spending(org_code, org_long_name, oscar_segment):

    # pull out the categories on the CONTROL_BUDGET_L0_LONG_NAME
    categories = oscar_segment.groupby('CONTROL_BUDGET_L0_LONG_NAME')['AMOUNT'].sum()

    # cast series to dataframe
    categories_df = categories.to_frame().T
    # reset index accordingly
    categories_df.reset_index(inplace=True, drop=True)

    # add org information into it
    categories_df['Checked_Organisation_Name'] = oscar_segment['Checked_Organisation_Name'][0]
    categories_df['IfG_Organisation_Type'] = oscar_segment['IfG_Organisation_Type'][0]
    categories_df['IfG_Organisation_Status'] = oscar_segment['IfG_Organisation_Status'][0]

    return categories_df


def grouping_by_organisation(new_oscar, grouped_new_oscar_df):

    # find the unique list of organisations from OSCAR (again)
    org_long_name_list = new_oscar['ORGANISATION_LONG_NAME'].unique()

    # for each segment/organisation, do something...
    for j in range(0, len(org_long_name_list)):

        # take out the segment from new_oscar
        oscar_segment = new_oscar[new_oscar['ORGANISATION_LONG_NAME']==org_long_name_list[j]]
        # reset its index
        oscar_segment.reset_index(drop=True, inplace=True)

        # take the top code & long name
        org_long_name = org_long_name_list[j]
        org_code = oscar_segment['ORGANISATION_CODE'][0]

        # run a matching routine
        oscar_segment = organisation_matching(org_code, org_long_name, grouped_new_oscar_df, oscar_segment)

        # pull out the values desired
        org_summary_df = summarise_org_spending(org_code, org_long_name, oscar_segment)

        # append the segments again for future reference
        if j == 0:
            all_oscar = oscar_segment
            summary_totals = org_summary_df
        else:
            all_oscar = pd.concat([all_oscar, oscar_segment], ignore_index=True)
            summary_totals = pd.concat([summary_totals, org_summary_df], ignore_index=True)

    return all_oscar, summary_totals

def organisation_code_extraction(new_oscar):

    # make a list of unique oscar organisations from the current data release
    new_oscar_orgs = new_oscar['ORGANISATION_LONG_NAME'].unique()

    # find the associated code for each organisation
    new_org_codes = []

    for org in new_oscar_orgs:

        # find org in the new_oscar dataset
        org_df = new_oscar[new_oscar['ORGANISATION_LONG_NAME']==org]

        # find unique codes
        org_code = org_df['ORGANISATION_CODE'].unique()

        if len(org_code) > 1:
            print('more than one org code found for '+org+': '+org_code)
            new_org_codes.append(org_code[0])
        else:
            new_org_codes.append(org_code[0])

    # cast results into a dataframe listing only the organisations and codes from the oscar file
    new_oscar_orgs_df = pd.DataFrame(list(zip(new_oscar_orgs, new_org_codes)),
                                     columns=['ORGANISATION_LONG_NAME','ORGANISATION_CODE'])

    return new_oscar_orgs_df


def checking_organisations(new_oscar_orgs_df, baseline_oscar, file_name):

    # initialise somewhere to store the checking information
    chk_org = []
    typ_org = []
    sts_org = []
    unfound_orgs = []

    # run through the list of organisations in latest dataset and find matched information from the baseline
    for j in range(0, len(new_oscar_orgs_df)):

        try:
            chk_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['Checked_Organisation_Name'].iloc[0])
            typ_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['IfG_Organisation_Type'].iloc[0])
            sts_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['IfG_Organisation_Status'].iloc[0])
        except IndexError:
            print(new_oscar_orgs_df['ORGANISATION_LONG_NAME'][j] + ' not found in ' + file_name)
            chk_org.append('CHECK_NEW')
            typ_org.append('CHECK_NEW')
            sts_org.append('CHECK_NEW')
            unfound_orgs.append(new_oscar_orgs_df['ORGANISATION_LONG_NAME'][j])

    # assemble into one dataframe

    checked_orgs_df = new_oscar_orgs_df
    checked_orgs_df['Checked_Organisation_Name'] = chk_org
    checked_orgs_df['IfG_Organisation_Type'] = typ_org
    checked_orgs_df['IfG_Organisation_Status'] = sts_org

    unfound_orgs_df = pd.DataFrame(unfound_orgs, columns=[file_name])

    return checked_orgs_df, unfound_orgs_df


def checking_organisations_no_unfound(new_oscar_orgs_df, baseline_oscar, file_name):

    # read in unfound checking
    unfound_org_df = pd.read_excel('oscar_organisation_matching_unfound.xlsx')

    # initialise somewhere to store the checking information
    chk_org = []
    typ_org = []
    sts_org = []

    # run through the list of organisations in latest dataset and find matched information from the baseline
    for j in range(0, len(new_oscar_orgs_df)):

        try:
            chk_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['Checked_Organisation_Name'].iloc[0])
            typ_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['IfG_Organisation_Type'].iloc[0])
            sts_org.append(baseline_oscar[baseline_oscar['ORGANISATION_CODE']==new_oscar_orgs_df['ORGANISATION_CODE'][j]]['IfG_Organisation_Status'].iloc[0])
        except IndexError:
            chk_org.append(new_oscar_orgs_df['ORGANISATION_LONG_NAME'][j])
            typ_org.append(unfound_org_df[unfound_org_df['ORGANISATION_LONG_NAME']==new_oscar_orgs_df['ORGANISATION_LONG_NAME'][j]]['Type_of_organisation']) #.iloc[0])
            sts_org.append(unfound_org_df[unfound_org_df['ORGANISATION_LONG_NAME']==new_oscar_orgs_df['ORGANISATION_LONG_NAME'][j]]['Exact Status']) #.iloc[0])

    # assemble into one dataframe

    checked_orgs_df = new_oscar_orgs_df
    checked_orgs_df['Checked_Organisation_Name'] = chk_org
    checked_orgs_df['IfG_Organisation_Type'] = typ_org
    checked_orgs_df['IfG_Organisation_Status'] = sts_org

    return checked_orgs_df


def clean_group_oscar_lite(all_oscar):

    # filter oscar dataframe to be only R13 final outturn numbers
    R13_df = all_oscar[all_oscar['VERSION_CODE']=='R13']

    # ensure only confirmed data is brought through
    annual_data = R13_df[R13_df['STATUS_CODE']=='CONFIRMED']

    # exclude NON-BUDGET, NON-VOTED
#    cleaned_data = annual_data[annual_data['CONTROL_BUDGET_L0_LONG_NAME']!='NON-BUDGET']
#    cleaned_data = cleaned_data[cleaned_data['ACCOUNTING_AUTHORITY_L0_CODE']!='NON-VOTED']
    cleaned_data = annual_data
    # reset index of cleaned data
    cleaned_data.reset_index(drop=True, inplace=True)

    # take each organisation in turn for grouping...
    organisations = cleaned_data['ORGANISATION_LONG_NAME'].unique()
    # for each orgasnisation
    for j in range(0, len(organisations)):
        # reset index (i.e. obtain oscar segment)
        org_data = cleaned_data[cleaned_data['ORGANISATION_LONG_NAME']==organisations[j]].reset_index(drop=True)
        # group the data according to a set of budgetry groups
        org_grouped = org_data.groupby([
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
            'ORGANISATION_TYPE_L1_LONG_NAME'])['AMOUNT'].sum().to_frame()

        # add in general informatino for the organisation
        org_grouped['BUDGETING_ORGANISATIONS_CODE'] = org_data['BUDGETING_ORGANISATIONS_CODE'][0]
        org_grouped['DEPARTMENT_GROUP_CODE'] = org_data['DEPARTMENT_GROUP_CODE'][0]
        org_grouped['DEPARTMENT_GROUP_LONG_NAME'] = org_data['DEPARTMENT_GROUP_LONG_NAME'][0]
        org_grouped['ORGANISATION_CODE'] = org_data['ORGANISATION_CODE'][0]
        org_grouped['ORGANISATION_LONG_NAME'] = org_data['ORGANISATION_LONG_NAME'][0]
        org_grouped['ORGANISATION_TYPE_L1_CODE'] = org_data['ORGANISATION_TYPE_L1_CODE'][0]
        org_grouped['Checked_Organisation_Name'] = org_data['Checked_Organisation_Name'][0]
        org_grouped['IfG_Organisation_Type'] = org_data['IfG_Organisation_Type'][0]
        org_grouped['IfG_Organisation_Status'] = org_data['IfG_Organisation_Status'][0]
        org_grouped['Financial_Year'] = org_data['Financial_Year'][0]

        # assemble the information into a single dataframe
        if j == 0:
            cleaned_group_df = org_grouped
        else:
            cleaned_group_df = pd.concat([cleaned_group_df, org_grouped], ignore_index=False)

    # reset index of cleaned up data
    cleaned_group_df.reset_index(inplace=True)

    return cleaned_group_df


def clean_group_oscar(all_oscar):

    # filter oscar dataframe to be only R13 final outturn numbers
    R13_df = all_oscar[all_oscar['VERSION_CODE']=='R13']

    # ensure only confirmed data is brought through
    annual_data = R13_df[R13_df['STATUS_CODE']=='CONFIRMED']

    # exclude NON-BUDGET, NON-VOTED
    cleaned_data = annual_data[annual_data['CONTROL_BUDGET_L0_LONG_NAME']!='NON-BUDGET']
    cleaned_data = cleaned_data[cleaned_data['ACCOUNTING_AUTHORITY_L0_CODE']!='NON-VOTED']
    # reset index of cleaned data
    cleaned_data.reset_index(drop=True, inplace=True)

    # take each organisation in turn for grouping...
    organisations = cleaned_data['ORGANISATION_LONG_NAME'].unique()
    # for each orgasnisation
    for j in range(0, len(organisations)):
        # reset index (i.e. obtain oscar segment)
        org_data = cleaned_data[cleaned_data['ORGANISATION_LONG_NAME']==organisations[j]].reset_index(drop=True)
        # group the data according to a set of budgetry groups
        org_grouped = org_data.groupby([
            'PESA_ECONOMIC_BUDGET_CODE',
            'PESA_ECONOMIC_GROUP_CODE',
            'CONTROL_BUDGET_L0_LONG_NAME',
            'CONTROL_BUDGET_L1_LONG_NAME',
            'ECONOMIC_CATEGORY_LONG_NAME',
            'ECONOMIC_CATEGORY_CODE',
            'ACCOUNTING_AUTHORITY_L0_CODE',
            'ECONOMIC_GROUP_LONG_NAME',
            'INCOME_CATEGORY_SHORT_NAME',
            'CHART_OF_ACCOUNTS_L5_LONG_NAME'])['AMOUNT'].sum().to_frame()

        # add in general informatino for the organisation
        org_grouped['BUDGETING_ORGANISATIONS_CODE'] = org_data['BUDGETING_ORGANISATIONS_CODE'][0]
        org_grouped['DEPARTMENT_GROUP_CODE'] = org_data['DEPARTMENT_GROUP_CODE'][0]
        org_grouped['DEPARTMENT_GROUP_LONG_NAME'] = org_data['DEPARTMENT_GROUP_LONG_NAME'][0]
        org_grouped['ORGANISATION_CODE'] = org_data['ORGANISATION_CODE'][0]
        org_grouped['ORGANISATION_LONG_NAME'] = org_data['ORGANISATION_LONG_NAME'][0]
        org_grouped['ORGANISATION_TYPE_L1_CODE'] = org_data['ORGANISATION_TYPE_L1_CODE'][0]
        org_grouped['Checked_Organisation_Name'] = org_data['Checked_Organisation_Name'][0]
        org_grouped['IfG_Organisation_Type'] = org_data['IfG_Organisation_Type'][0]
        org_grouped['IfG_Organisation_Status'] = org_data['IfG_Organisation_Status'][0]
        org_grouped['Financial_Year'] = org_data['Financial_Year'][0]

        # assemble the information into a single dataframe
        if j == 0:
            cleaned_group_df = org_grouped
        else:
            cleaned_group_df = pd.concat([cleaned_group_df, org_grouped], ignore_index=False)

    # reset index of cleaned up data
    cleaned_group_df.reset_index(inplace=True)

    return cleaned_group_df

baseline_oscar['CONTROL_BUDGET_L1_LONG_NAME'].unique()

# %%
baseline_oscar.columns

# %%
all_oscar_df.columns

# %%
grouped_cleaned_data = cleaned_data.groupby(['BUDGETING_ORGANISATIONS_CODE', 'DEPARTMENT_GROUP_CODE',
       'DEPARTMENT_GROUP_LONG_NAME', 'ORGANISATION_CODE',
       'ORGANISATION_LONG_NAME', 'ORGANISATION_TYPE_CODE',
       'ORGANISATION_TYPE_LONG_NAME', 'ORGANISATION_TYPE_L1_CODE',
       'ORGANISATION_TYPE_L1_LONG_NAME'])['AMOUNT'].sum()

# %%
grouped_cleaned_data.to_frame()

# %%
cleaned_data

# %%
R13_df['STATUS_CODE'].unique()

# %%
all_oscar_df = pd.read_pickle(file_names[0][:-4]+'_matched.pkl')

new_matching_information = pd.read_excel('Change in Status from WM23 folder.xlsx')

# %%
# build up a focused list for checking...
oscar_unique_orgs = all_oscar_df['ORGANISATION_LONG_NAME'].unique()

# flesh this out with critical information
for j in range(0, len(oscar_unique_orgs)):
    # match the unique organisation
    oscar_unique_mini = all_oscar_df[all_oscar_df['ORGANISATION_LONG_NAME']==oscar_unique_orgs[j]]
    # take the first row
    oscar_unique_mini = oscar_unique_mini.iloc[0][['YEAR_NO','ORGANISATION_LONG_NAME', 'ORGANISATION_CODE', 'Checked_Organisation_Name',
       'IfG_Organisation_Type', 'IfG_Organisation_Status', 'Financial_Year']]
    # put series as a dataframe
    oscar_mini_df = oscar_unique_mini.to_frame().T
    if j == 0:
        oscar_mini_all_df = oscar_mini_df
    else:
        oscar_mini_all_df = pd.concat([oscar_mini_all_df, oscar_mini_df])

# %%
oscar_mini_all_df

# %%
new_matching_information

# %%
for j in range(0, len(file_names)):

    file_location = 'Source files\\' + file_names[j]

    # read the pickle file...
    all_oscar_df = pd.read_pickle(file_names[j][:-4]+'_matched.pkl')

    # clean and group the oscar data
    cleaned_grouped_df = clean_group_oscar_lite(all_oscar_df)

    if j == 0:
        data_df = cleaned_grouped_df
    else:
        data_df = pd.concat([data_df, cleaned_grouped_df], ignore_index=True)

# %%

for j in range(0, len(file_names)):

    all_oscar_df = pd.read_pickle(file_names[j][:-4]+'_matched.pkl')

    orgs_for_checking = all_oscar_df['ORGANISATION_LONG_NAME'].unique()

    for k in range(0, len(orgs_for_checking)):

        org_name = orgs_for_checking[k]

        # check for this in the new classifications
        new_info = new_classifications[new_classifications['ORGANISATION_LONG_NAME']==org_name]

        if len(new_info) == 0:
            # do nothing and keep original information
            oscar_df = all_oscar_df[all_oscar_df['ORGANISATION_LONG_NAME']==org_name].reset_index(drop=True)

        else:
            new_info.reset_index(inplace=True, drop=True)

            oscar_df = all_oscar_df[all_oscar_df['ORGANISATION_LONG_NAME']==org_name].reset_index(drop=True)
            oscar_df['IfG_Organisation_Type'] = new_info['Type_of_organisation'][0]
            oscar_df['IfG_Organisation_Status'] = new_info['Exact Status'][0]

        if k == 0:
            extra_checked_oscar_df = oscar_df
        else:
            extra_checked_oscar_df = pd.concat([extra_checked_oscar_df, oscar_df], ignore_index=True)

    # write information to pickle
    extra_checked_oscar_df.to_pickle(file_names[j][:-4]+'_extra_checked.pkl')

    # condense this into group to avoid massive dataframe...
    extra_checked_oscar_df = clean_group_oscar(extra_checked_oscar_df)

    if j == 0:
        all_extra_checked = extra_checked_oscar_df
    else:
        all_extra_checked = pd.concat([all_extra_checked, extra_checked_oscar_df], ignore_index=True)

    print(j)

all_extra_checked.to_excel('extra_checked_oscar_2023.xlsx')

# %%
all_extra_checked['Financial_Year'].unique()

# %%
extra_cleaned_grouped = clean_group_oscar(all_extra_checked)

extra_cleaned_grouped.to_excel('extra_checked_grouped_oscar_2023.xlsx')

# %%
all_extra_checked[all_extra_checked['IfG_Organisation_Status']=='CHECK_NEW']['ORGANISATION_LONG_NAME'].unique()

# %%
# quick run through final characterisations...
checked = all_extra_checked[all_extra_checked['IfG_Organisation_Status']!='CHECK_NEW']
checked = checked[checked['IfG_Organisation_Status']!='CHECK']

# %%
checked.reset_index(inplace=True, drop=True)

# %%
remaining = pd.read_excel('quick_last_check.xlsx')

# %%
for j in range(0, len(remaining)):

    next_line = all_extra_checked[all_extra_checked['ORGANISATION_LONG_NAME']==remaining['ORGANISATION_LONG_NAME'][j]].reset_index(drop=True)

    next_line['IfG_Organisation_Type'] = remaining['IfG_Organisation_Type'][j]
    next_line['IfG_Organisation_Status'] = remaining['IfG_Organisation_Status'][j]

    checked = pd.concat([checked, next_line], ignore_index=True)

# %%
checked.to_excel('extra_checked_oscar_2023_2.xlsx')

