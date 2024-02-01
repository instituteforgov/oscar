## Order in which to run scripts
| Script | Purpose |
| ----------- | ----------- |
| `create_organisation_lookup.py` | Create a lookup table of organisation codes, organisation names and IfG classifications (edited organisation name, organisation type, organisation sub-type) |
| `check_<annual/inyear>_data_structure.py` | Compare OSCAR data
    - To see whether column names are consistent
    - To see whether presence of nulls is consistent
    - To see how VERSION_CODE varies by year
|
| `check_<annual/inyear>_organisations.py` | Read in an annual/in-year release of OSCAR data and compare it to the master list of organisations |
| `process_<annual/inyear>_data.py` | Read in an annual/in-year release of OSCAR data and process it so it can be added to our aggregated OSCAR data |
