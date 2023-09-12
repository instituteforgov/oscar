'''
OSCAR organisation matching with ONS lists

Want to compare with fuzzy matching, the list of ONS public bodies from the last 15 years
and the organisations listed in the OSCAR dataset

Push the output out for manual checking of organisation matching

'''

import pandas as pd
import numpy as np

from __future__ import unicode_literals
import unittest
import re
import sys
import pycodestyle

from thefuzz import fuzz
from thefuzz import process
from thefuzz import utils
from thefuzz.string_processing import StringProcessor

# %%
# read in the unfound organisations and simplify into unique list
unfound_organisations = pd.read_excel('oscar_2021_22_release_summaried_4.xlsx', sheet_name='unfound')

# assemble all unfound organsiations
for j in range(1, unfound_organisations.shape[1]):

    if j == 1:
        unfound_list = unfound_organisations.iloc[:, j].tolist()
    else:
        unfound_list.extend(unfound_organisations.iloc[:, j].tolist())

# extract the unique elements
unique_unfound = set(unfound_list)
# drop weird nan values
unique_unfound = [x for x in unique_unfound if str(x) != 'nan']

# %%
# read in the ONS list from excel file

ons_orgs = pd.read_excel('211004 Comparison of CO and ONS public bodies lists.xlsx', sheet_name='ONS Sep 21')

# %%
# reduce this to a list of organisations
red_ons_orgs = ons_orgs['Organisation'].tolist()

# %%
# now need to compare the two reduced (red_) organisation lists using thefuzz!
thresh_score = 70

for j in range(0, len(unique_unfound)): #list_oscar_orgs)):
    # compare with with all the entries in the ONS list

    match = process.extract(unique_unfound[j], red_ons_orgs, scorer=fuzz.token_sort_ratio)

    # get the scores and max_match score
    [match_text, match_score] = take_max_match(match)

    # only take a match if the score is above a threshold
    if match_score >= thresh_score:
        # find the organisation code
        oscar_name = unique_unfound[j]
        ons_name = match_text
        fail_name = ''
    else:
        # nothing found
        oscar_name = unique_unfound[j]
        ons_name = 'none'
        fail_name = match_text

    # build lists for comparing
    if j == 0:
        all_oscar_names = [oscar_name]
        all_ons_names = [ons_name]
        all_match_scores = [match_score]
        all_fail_names = [fail_name]
    else:
        all_oscar_names.append(oscar_name)
        all_ons_names.append(ons_name)
        all_match_scores.append(match_score)
        all_fail_names.append(fail_name)

# assemble lists into a dataframe
matched_organisations = pd.DataFrame({'ORGANISATION_LONG_NAME': all_oscar_names,
                                     'ONS names': all_ons_names,
                                     'Match score': all_match_scores,
                                     'Failed matched names': all_fail_names})

matched_organisations.to_excel('oscar_organisation_matching_unfound.xlsx', sheet_name='2022_12_16')

# %%
# take the max match
def take_max_match(match):

    for j in range(0, len(match)):
        # extract the scores
        if j == 0:
            scores = [match[j][1]]
        else:
            scores.append(match[j][1])

    # find the max score
    max_score = max(scores)

    # index the max score
    max_score_index = scores.index(max_score)

    # take the result
    match_text = match[max_score_index][0]
    match_score = match[max_score_index][1]

    return match_text, match_score


# %%
oscar_orgs
