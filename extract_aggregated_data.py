'''
Assuming the financial_aggregating script has been run, with organisations matched and stored...

Going to use the pickled results and do some filtering, etc. to get to some results

But would like to know what organisations have been checked/found/matched for reference

Date updated: 2022/11/15
'''

import pandas as pd
import numpy as np

import xlsxwriter

from __future__ import unicode_literals
import unittest
import re
import sys


import math

# %%
# load pickled matched data
new_oscar = pd.read_pickle('2022_10_17_matched_oscar.pkl')

# %%
# CHECKING MATCHING ROUTINE AREA...
# read in the original oscar file
oscar = pd.read_csv('Source files\\2021_OSCAR_Extract_2020_21.txt', delimiter='|', encoding='cp1252') # skiprows=12, )
# read in set of organisations being matched against
checked_orgs = pd.read_excel('oscar_organisation_matching_checked.xlsx', sheet_name='2022_09_05')

# %%
# create lists of matching organisations

# from original oscar dataset
original_oscar_organisation_list = oscar['ORGANISATION_LONG_NAME'].unique()

# %%
# from checked_orgs
checked_oscar_organisation_list = checked_orgs['ORGANISATION_LONG_NAME'].unique()
checked_organisation_list = checked_orgs['ONS names'].unique()

# from new_oscar dataset
checked_new_oscar_organisation_list = new_oscar['ORGANISATION_LONG_NAME'].unique()
checked_new_oscar_ifg_name = new_oscar['Checked_Organisation_Name'].unique()
checked_new_oscar_ifg_type = new_oscar['IfG_Organisation_Type'].unique()

# %%
# write findings into an excel workbook
with pd.ExcelWriter('organisation_checking_2011_11_15.xlsx') as writer:

    original_oscar_df = pd.DataFrame(original_oscar_organisation_list,
                                    columns=['OSCAR NAME'])
    original_oscar_df.to_excel(writer, sheet_name='OriginalOSCAR')

    checked_oscar_df = pd.DataFrame(list(zip(checked_oscar_organisation_list, checked_organisation_list)),
                                   columns=['OSCAR NAME', 'ONS name'])
    checked_oscar_df.to_excel(writer, sheet_name='MatchedOSCAR')

    new_oscar_df = pd.DataFrame(list(zip(checked_new_oscar_organisation_list, checked_new_oscar_ifg_name, checked_new_oscar_ifg_type)),
                               columns = ['OSCAR NAME', 'Checked (IfG) name', 'IfG type'])

    new_oscar_df.to_excel(writer, sheet_name='TypeOSCAR')

    writer.save()

# %%
# aggregating financial numbers for checking - want to run a couple of different cuts from OSCAR pickle
# choose cut here

# financial year, final outturns
R13 = new_oscar[new_oscar['VERSION_CODE']=='R13']

# positive values
R13_positive = R13[R13['AMOUNT']>0]

# use groupby for target categories
groupby_categories = [
    'ORGANISATION_LONG_NAME',
    'Checked_Organisation_Name',
    'IfG_Organisation_Type',
    'ORGANISATION_TYPE_L1_LONG_NAME',
    'PESA_ECONOMIC_BUDGET_CODE',
    'PESA_ECONOMIC_GROUP_CODE',
    'INCOME_CATEGORY_SHORT_NAME',
    'CHART_OF_ACCOUNTS_L5_LONG_NAME',
    'ECONOMIC_BUDGET_CODE',
    'CONTROL_BUDGET_L0_LONG_NAME',
    'ACCOUNTING_AUTHORITY_L0_CODE',
    'ECONOMIC_CATEGORY_LONG_NAME',
    'ECONOMIC_GROUP_LONG_NAME'
]

oscar_grouped = R13_positive.groupby(groupby_categories)['AMOUNT'].sum()

oscar_grouped_df = oscar_grouped.to_frame()

oscar_grouped_df.reset_index(inplace=True)

oscar_grouped_df['AMOUNT'].sum()

oscar_grouped_df

# %%
# check organisation list is sustained in these cells below
len(oscar_grouped_df['ORGANISATION_LONG_NAME'].unique())

# %%
len(R13_positive['ORGANISATION_LONG_NAME'].unique())

# %%
set(oscar_grouped_df['ORGANISATION_LONG_NAME'].unique()) ^ set(R13_positive['ORGANISATION_LONG_NAME'].unique())

# %%
R13_positive[R13_positive['ORGANISATION_LONG_NAME']=='Independent Commission for Aid Impact']

# %%
oscar_grouped_df.to_excel('2022_11_15_oscar_grouped.xlsx')

# %%
len(checked_orgs)

# %%
# want a refined checked dataframe with only the above categories
# clean the checked dataframe

# have storage lists for putting clean information
org_code_all = []
checked_org_name_all = []
org_type_all = []
exact_status_all = []

# run through each row
for j in range(0, len(checked_orgs)):

    # for the organisation name
    if type(checked_orgs['ONS name (manual)'][j]) is str:
        # this looks for a replacement name if given
        checked_org_name = checked_orgs['ONS name (manual)'][j]
    elif type(checked_orgs['Check flag'][j]) is str:
        # this checks if there has been a check flag raised during manual tagging
        # will not look further for an org name
        # instead will say check
        checked_org_name = 'CHECK: ' + checked_orgs['ORGANISATION_LONG_NAME'][j]
    else:
        # the original name was correct
        checked_org_name = checked_orgs['ORGANISATION_LONG_NAME'][j]


    # for the other categories
    # all codes are given
    org_code = checked_orgs['ORGANISATION_CODE'][j]

    # org type
    if type(checked_orgs['Type_of_organisation'][j]) is str:
        org_type = checked_orgs['Type_of_organisation'][j]
    else:
        org_type = 'CHECK'

    # exact status
    if type(checked_orgs['Exact Status'][j]) is str:
        exact_status = checked_orgs['Exact Status'][j]
    else:
        exact_status = 'CHECK'

    # assemble the information
    org_code_all.append(org_code)
    checked_org_name_all.append(checked_org_name)
    org_type_all.append(org_type)
    exact_status_all.append(exact_status)


# pull into a single checked dataframe
checked_orgs_df = pd.DataFrame(zip(org_code_all, checked_org_name_all, org_type_all, exact_status_all),
                              columns=['Organisation_Code', 'Checked_Organisation_Name', 'IfG_Organisation_Type', 'IfG_Organisation_Status'])

# %%
# add flags into the OSCAR dataframe

chk_org_name = []
ifg_org_type = []
ifg_org_stat = []

for j in range(0, len(oscar)):

    org_code = oscar['ORGANISATION_CODE'][j]

    # check the name with the code only appears once...
    org_long_name = oscar['ORGANISATION_LONG_NAME'][j]

    if len(oscar[oscar['ORGANISATION_LONG_NAME']==org_long_name]['ORGANISATION_CODE'].unique()) == 1:
        # proceed as before
        chk_org_name.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values[0])
        ifg_org_type.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Type'].values[0])
        ifg_org_stat.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Status'].values[0])

    elif len(oscar[oscar['ORGANISATION_LONG_NAME']==org_long_name]['ORGANISATION_CODE'].unique()) > 1:

        # if the current code matches, no need to panic
        if len(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values) == 1:
            # as before
            chk_org_name.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values[0])
            ifg_org_type.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Type'].values[0])
            ifg_org_stat.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Status'].values[0])
        elif len(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values) == 0:
            # try the other code
            # match the codes
            # try the other code
            org_code_list = oscar[oscar['ORGANISATION_LONG_NAME']==org_long_name]['ORGANISATION_CODE'].unique().tolist()
            org_code_list.remove(org_code)
            if len(org_code_list) == 1:
                org_code = org_code_list[0]
            else:
                print('still too many organisations')
            chk_org_name.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values[0])
            ifg_org_type.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Type'].values[0])
            ifg_org_stat.append(checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Status'].values[0])
        else:
            print('struggling')


    elif len(oscar[oscar['ORGANISATION_LONG_NAME']==org_long_name]['ORGANISATION_CODE'].unique()) == 0:
        print('FUCK - no matches found')


    if (j/10000).is_integer is True:
        print(str(100*(j/len(oscar)))+' completed')




# add these to the OSCAR dataframe
oscar['Checked_Organisation_Name'] = chk_org_name
oscar['IfG_Organisation_Type'] = ifg_org_type
oscar['IfG_Organisation_Status'] = ifg_org_stat

# %%
oscar_orgs = oscar[['ORGANISATION_LONG_NAME', 'ORGANISATION_CODE']]

# %%
red_oscar_orgs = oscar_orgs.drop_duplicates(subset = 'ORGANISATION_LONG_NAME', keep='first')

# %%
red_oscar_orgs.reset_index(drop=True)

# %%
# now need to compare the two reduced (red_) organisation lists using thefuzz!

# 17-10-2022
#   To filter dataframe before matching organisations

# find the unique list of organisations from OSCAR (again)
org_long_name_list = oscar['ORGANISATION_LONG_NAME'].unique()

# for each segment/organisation, do something...
for j in range(0, len(org_long_name_list)):

    # take out the segment from oscar
    oscar_segment = oscar[oscar['ORGANISATION_LONG_NAME']==org_long_name_list[j]]
    # reset its index
    oscar_segment.reset_index(drop=True, inplace=True)

    # take the top code & long name
    org_long_name = org_long_name_list[j]
    org_code = oscar_segment['ORGANISATION_CODE'][0]

    # run a matching routine
    oscar_segment = organisation_matching(org_code, org_long_name, checked_orgs_df, oscar_segment)

    # pull out the values desired
    org_summary_df = summarise_org_spending(org_code, org_long_name, oscar_segment)

    # append the segments again for future reference
    if j == 0:
        new_oscar = oscar_segment
        summary_totals = org_summary_df
    else:
        new_oscar = pd.concat([new_oscar, oscar_segment], ignore_index=True)
        summary_totals = pd.concat([summary_totals, org_summary_df], ignore_index=True)

    print(j)


# %%
# function to check orgs

def organisation_matching(org_code, org_long_name, checked_orgs_df, oscar_segment):

    chk_org_name = checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['Checked_Organisation_Name'].values[0]
    ifg_org_type = checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Type'].values[0]
    ifg_org_stat = checked_orgs_df[checked_orgs_df['Organisation_Code']==org_code]['IfG_Organisation_Status'].values[0]

    # add these to the OSCAR dataframe
    oscar_segment['Checked_Organisation_Name'] = chk_org_name
    oscar_segment['IfG_Organisation_Type'] = ifg_org_type
    oscar_segment['IfG_Organisation_Status'] = ifg_org_stat

    return oscar_segment

# function to get out the summary values

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

def combine_and_summarise_org_spending(org_code, org_long_name, oscar_segment):

    # combine the CONTROL_BUDGET_L0_LONG_NAME and ECONOMIC_BUDGET_CODE

    for j in range(0, len(oscar_segment)):

        try:
            combined_cat = oscar_segment['ECONOMIC_BUDGET_CODE'][j] + " " + oscar_segment['CONTROL_BUDGET_L0_LONG_NAME'][j]
        except TypeError:
            combined_cat = str(oscar_segment['ECONOMIC_BUDGET_CODE'][j]) + " " + str(oscar_segment['CONTROL_BUDGET_L0_LONG_NAME'][j])


        if j == 0:
            combined_cat_list = [combined_cat]
        else:
            combined_cat_list.append(combined_cat)

    oscar_segment['Combined_IfG_Categories'] = combined_cat_list

    # pull out the categories on the combined category
    categories_all_values = oscar_segment.groupby('Combined_IfG_Categories')['AMOUNT'].sum()

    # sum non-negative values
    categories_positive = oscar_segment.groupby('Combined_IfG_Categories')['AMOUNT'].sum()

    # filter out the NON-BUDGET, NON-VOTED categories and sum
    categories_all_values_filter_budget =

    # filter out the NON-BUDGET, NON-VOTED categories and sum positive values
    categories_positive_filter_budget =

    # cast series to dataframe
    categories_df = categories.to_frame().T
    # reset index accordingly
    categories_df.reset_index(inplace=True, drop=True)

    # add org information into it
    categories_df['Checked_Organisation_Name'] = oscar_segment['Checked_Organisation_Name'][0]
    categories_df['IfG_Organisation_Type'] = oscar_segment['IfG_Organisation_Type'][0]
    categories_df['IfG_Organisation_Status'] = oscar_segment['IfG_Organisation_Status'][0]

    return categories_df, oscar_segment


# %%
#   To filter dataframe after matching organisations

# find the unique list of organisations from new_oscar
org_long_name_list = new_oscar['ORGANISATION_LONG_NAME'].unique()

# for each segment/organisation, do something...
for j in range(0, len(org_long_name_list)):

    # take out the segment from oscar
    oscar_segment = new_oscar[new_oscar['ORGANISATION_LONG_NAME']==org_long_name_list[j]]
    # reset its index
    oscar_segment.reset_index(drop=True, inplace=True)

    # take the top code & long name
    org_long_name = org_long_name_list[j]
    org_code = oscar_segment['ORGANISATION_CODE'][0]

    # pull out the categories
    comb_org_summary_df, comb_oscar_summary = combine_and_summarise_org_spending(org_code, org_long_name, oscar_segment)

    # append the segments again for future reference
    if j == 0:
        comb_summary_totals = comb_org_summary_df
        comb_oscar_summary_all = comb_oscar_summary
    else:
        comb_summary_totals = pd.concat([comb_summary_totals, comb_org_summary_df], ignore_index=True)
        comb_oscar_summary_all = pd.concat([comb_oscar_summary_all, comb_oscar_summary], ignore_index=True)
    print(j)


# %%
# pickle up the dataframes!

new_oscar.to_pickle('2022_10_17_matched_oscar.pkl')
summary_totals.to_pickle('2022_10_17_summary_L0_orgs.pkl')
comb_summary_totals.to_pickle('2022_10_17_combined_summaries_orgs.pkl')
comb_oscar_summary_all.to_pickle('2022_10_17_comb_matched_oscar.pkl')

# %%
# save up the summaries in an excel sheet

with pd.ExcelWriter('oscar_summaries.xlsx') as writer:

    summary_totals.to_excel(writer, sheet_name='L0_summary')
    comb_summary_totals.to_excel(writer, sheet_name='comb_cat_summary')

# %%
# 2022-10-25 work starts here
# uses the already matched and pickled OSCAR data
# load pickled matched data

new_oscar = pd.read_pickle('2022_10_17_matched_oscar.pkl')

# %%
# extract the R13 version data

R13_df = new_oscar[new_oscar['VERSION_CODE']=='R13']

R13_df['AMOUNT'].sum()

# %%
listing = R13_df['ORGANISATION_LONG_NAME'].unique()
org_long_name = pd.DataFrame(listing)

# %%
R13_df[R13_df['ORGANISATION_LONG_NAME'] .str.contains('FCA')]['ORGANISATION_LONG_NAME'].unique()

# %%
# sum of annual spending

R13_df['AMOUNT'].sum()

# %%
# check it's for one financial year

R13_df['YEAR_SHORT_NAME'].unique()

# %%
# find the unique list of organisations from OSCAR (again)
org_long_name_list = R13_df['ORGANISATION_LONG_NAME'].unique()

# for each segment/organisation, do something...
for j in range(0, len(org_long_name_list)):

    # take out the segment from the selected part of the data
    oscar_segment = R13_df[R13_df['ORGANISATION_LONG_NAME']==org_long_name_list[j]]
    # reset its index
    oscar_segment.reset_index(drop=True, inplace=True)

    # take the top code & long name
    org_long_name = org_long_name_list[j]
    org_code = oscar_segment['ORGANISATION_CODE'][0]

    # pull out the values desired
    # take the spending summary based on prior values
    org_summary_df = summarise_org_spending(org_code, org_long_name, oscar_segment)
    # make a cut using the combined categories
    comb_org_summary_df, comb_oscar_summary = combine_and_summarise_org_spending(org_code, org_long_name, oscar_segment)

    # append the segments again for future reference
    if j == 0:
        summary_totals = org_summary_df
        comb_summary_totals = comb_org_summary_df
        comb_oscar_summary_all = comb_oscar_summary
    else:
        summary_totals = pd.concat([summary_totals, org_summary_df], ignore_index=True)
        comb_summary_totals = pd.concat([comb_summary_totals, comb_org_summary_df], ignore_index=True)
        comb_oscar_summary_all = pd.concat([comb_oscar_summary_all, comb_oscar_summary], ignore_index=True)

with pd.ExcelWriter('oscar_summaries_2.xlsx') as writer:

    summary_totals.to_excel(writer, sheet_name='L0_summary')
    comb_summary_totals.to_excel(writer, sheet_name='comb_cat_summary')

# %%
# function to get out the summary values

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

# %%
def combine_and_summarise_org_spending(org_code, org_long_name, oscar_segment):

    # combine the CONTROL_BUDGET_L0_LONG_NAME and ECONOMIC_BUDGET_CODE

    for j in range(0, len(oscar_segment)):

        try:
            combined_cat = oscar_segment['ECONOMIC_BUDGET_CODE'][j] + " " + oscar_segment['CONTROL_BUDGET_L0_LONG_NAME'][j]
        except TypeError:
            combined_cat = str(oscar_segment['ECONOMIC_BUDGET_CODE'][j]) + " " + str(oscar_segment['CONTROL_BUDGET_L0_LONG_NAME'][j])

        if j == 0:
            combined_cat_list = [combined_cat]
        else:
            combined_cat_list.append(combined_cat)

    oscar_segment['Combined_IfG_Categories'] = combined_cat_list

    # pull out the categories on the combined category
    categories = oscar_segment.groupby('Combined_IfG_Categories')['AMOUNT'].sum()

    # cast series to dataframe
    categories_df = categories.to_frame().T
    # reset index accordingly
    categories_df.reset_index(inplace=True, drop=True)

    # add org information into it
    categories_df['Checked_Organisation_Name'] = oscar_segment['Checked_Organisation_Name'][0]
    categories_df['IfG_Organisation_Type'] = oscar_segment['IfG_Organisation_Type'][0]
    categories_df['IfG_Organisation_Status'] = oscar_segment['IfG_Organisation_Status'][0]

    return categories_df, oscar_segment

# %%
new_oscar[new_oscar['Checked_Organisation_Name']=='NS&I']

# %%
# build out a sample of the OSCAR dataset

# find number of unique values per category, print up to 10

list_of_cat_lists = []

for j in range(0, len(oscar.columns)):

    if len(oscar[oscar.columns[j]].unique()) <= 10:

        cat_list = oscar[oscar.columns[j]].unique()

    else:

        cat_list = oscar[oscar.columns[j]].unique()[:10]


    list_of_cat_lists.append(cat_list)


# Save up the sample category information
workbook = xlsxwriter.Workbook('oscar_category_snapshot.xlsx')
worksheet = workbook.add_worksheet()

# %%
# write column names and unique value sets
for j in range(0, len(oscar.columns)):

    # write category list
    worksheet.write(j+1, 0, oscar.columns[j])

    # write the different unique values
    for k in range(0, len(list_of_cat_lists[j])):

        if type(list_of_cat_lists[j][k]) is not str:
            if np.isnan(list_of_cat_lists[j][k]):
                worksheet.write(j+1, 1+k, 'nan')
            else:
                worksheet.write(j+1, 1+k, list_of_cat_lists[j][k])
        else:
            worksheet.write(j+1, 1+k, list_of_cat_lists[j][k])

    # if more than 10 values, then add elipsis at the end
    if len(list_of_cat_lists[j]) == 10:

        worksheet.write(j+1, 1+11, '...')

# add titles
worksheet.write(0, 0, 'OSCAR CATEGORIES')
worksheet.write(0, 1, 'Sample values from OSCAR')


# %%
workbook.close()