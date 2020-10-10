Welcome to the Shop Titans Allcalculator. This tool takes the official
Shop Titans data spreadsheet and parses it to get the up-to-date data on
blueprints, workers, etc. to figure out what items are the most profitable
depending on its configuration.

It does the following:

1. Parses data from the spreadsheet into JSON files - done
2. Parses blueprints, applies all ascension and mastery upgrades - done
3. Calculates data depending on the passed config file - done
4. Applies component costs for accurate profit margins - WIP  


Installation

1. Install [python 3.7](https://www.python.org/downloads/) or later
2. run the following:

`python3.7 main.py --config config.json --spreadsheet spreadsheet.xlsx --generate-data`

3. You can now generate results with:

`python3.7 main.py --config config.json --spreadsheet spreadsheet.xlsx`

You will get `result.json` and `result.txt` that are appropriately calculated to the config

TODO:

- Add support for permanent guild resource boosts that came with the t10 patch
- Better output: preferably as a website that's generated instead of a json and txt file

NOTES:

The spreadsheet does NOT work out-of-the-box. The file that is
in the repository is already modified.

Steps that need to be taken for it to be compatible (use [Libre Office](https://www.libreoffice.org/) if you do 
not have Microsoft Office) are documented here:

1. replace the following headers

![Step 1](images/spreadsheet_modification_step_1.png)

with these:

![Step 2](images/spreadsheet_modification_step_2.png)

2. Save as `.xlsx` (Libre Office can do this, just use the older
format when it prompts you to do so)
