# Source
Published [here](https://www.gov.uk/government/collections/hmt-oscar-publishing-from-the-database#full-publication-update-history) (and, in the case of 2022/23 annual data which doesn't show up there, [here](https://www.gov.uk/government/publications/oscar-ii-publishing-raw-data-from-the-database)).

Two types of dataset are available:
- 'In-year' data
- 'Annual' data

Columns differ between the in-year and the annual data.

## 'In-year' data
A single variant is available. Contains:
- Actuals for earlier months in the year
- Planned figures for later months in the year

## 'Annual' data
Two variants are available:
- In-year (sic): Contains month-by-month actuals for the year. (NB: This differs from the non-Annual in-year data.)
- Outturn: Contains aggregated, annual actuals for the year

### Format
2017/18-2020/21: A single pipe-separated (|) `.txt` file per year

2021/22-2022/23: Separate `.csv` files for each month, including a month 13 dataset, R13

See `VERSION_CODE` in [Data dictionary](#Data-dictionary) for details of files to use, and rows to use within each file, to analyse outturn.

# Data dictionary
## 'Annual' data
**`BUDGETING_ORGANISATIONS_CODE`**
- 2017/18-2020/21: 'CENTRAL EXCHEQUER', 'DEPARTMENTS', 'DEVOLVED ADMINISTRATIONS', 'LOCAL GOVERNMENT'
- 2021/22-2022/23: `null`

**`MONTH_SHORT_NAME`**
- 2017/18-2020/21: 'Period 0 - <yy-yy>', 'Apr-<yy>', 'May-<yy>', ..., 'Mar-<yy>'
- 2021/22-2022/23: 'P01', 'P02', ..., 'P12'

**`ORGANISATION_CODE`**
- Six-character code consisting of three letters and three digits
- Not uniquely tied to `ORGANISATION_LONG_NAME` values:
- Can change even where there is no change in `ORGANISATION_LONG_NAME`, for example where there is a change in departmental group e.g. Nuclear Decommissioning Authority is NDA066 up to partway through 2015/16, then becomes NDA084
- Can stay the same even where there is a change in `ORGANISATION_LONG_NAME` e.g. DID030 relates to the Department for International Development up to 2016/17 and Foreign, Commonwealth and Development Office subsequently

**`PESA_ECONOMIC_BUDGET_CODE`**
- 2017/18-2020/21: 'CAPITAL', 'RESOURCE', 'OTHER NON-BUDGET', `null`
- 2021/22-2022/23: `null`

**`VERSION_CODE`**
- 2017/18-2020/21: 'PLANS', 'R0', 'R1' ... 'R13', where PLANS relates to planned expenditure, 'R0'-'R12' relate to forecast outturns and 'R13' relates to outturn.
- 2021/22-2022/23 R13 file: 'Forecast', where this relates to outturn data in the case of the R13 file

Therefore to analyse outturn:
- 2017/18-2020/21: Use records with `VERSION_CODE` 'R13'
- 2021/22-2022/23: Use records from R13 file (all have 'Forecast' `VERSION_CODE`)

Ref: _Understanding the OSCAR II Data Release 2023_ [page 8](https://assets.publishing.service.gov.uk/media/654d073dc0e068000e1b2d0c/Understanding_OSCAR_II_Data_Release_2023.pdf#page=8), [page 9](https://assets.publishing.service.gov.uk/media/654d073dc0e068000e1b2d0c/Understanding_OSCAR_II_Data_Release_2023.pdf#page=9)
