# !/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd


def convert_month_string_to_code(
    df: pd.DataFrame,
    month_col: str,
):
    '''
        Purpose
            Convert month names to month codes, e.g. Jan-18 to P10

        Parameters
            - df: DataFrame featuring month names
            - month_col: Column containing month names

        Returns
            - df: DataFrame with month names converted to month codes

        Notes
            - This is based on what we believe the month codes used from 2021/22 onwards
            in the OSCAR data are
    '''

    month_regex = {
        r'Jan.*': 'P10',
        r'Feb.*': 'P11',
        r'Mar.*': 'P12',
        r'Apr.*': 'P01',
        r'May.*': 'P02',
        r'Jun.*': 'P03',
        r'Jul.*': 'P04',
        r'Aug.*': 'P05',
        r'Sep.*': 'P06',
        r'Oct.*': 'P07',
        r'Nov.*': 'P08',
        r'Dec.*': 'P09',
        r'Period 0.*': 'P00',
    }

    df[month_col] = df[month_col].replace(
        month_regex,
        regex=True,
    )

    return df
