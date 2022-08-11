# This script is intended to be run 3rd, after analyze results has been run on experts and novices
# This script will combine the two spreadsheets by adding another identifier for expert vs novice data
# It will also transpose the spreadsheet to make viewing easier
# This script assumes the same sets of metrics and roles were calculated on both datasets

# TODO: make roles separate columns
# i.e. 3 columns for each metric (avg_vel_scope,avg_vel_RH, etc)

import os
import csv
import numpy as np
import pandas as pd

expertSpreadsheetPath = r"P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\AnalyzeResultsOutput\Experts\aggregateData.csv"
noviceSpreadsheetPath = r"P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\AnalyzeResultsOutput\Novices\aggregateData.csv"
outputPath = r"P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CombineExpertAndNoviceSpreadsheetsOutput"

expertSpreadsheet = []
noviceSpreadsheet = []

output = []

# It doesn't matter which one is added to which, just as long as the 2nd one's headers are removed
novice = pd.read_csv(noviceSpreadsheetPath,header=None)
transposed_novice = (novice.values).T

expert = pd.read_csv(expertSpreadsheetPath,header=None)
transposed_expert = (expert.values).T
        
first_row = np.insert(transposed_novice[0],0,"Group")
first_row = np.insert(first_row,1,"Sequence_group")


output.append(first_row)

for row in transposed_novice[1:]:

    sequence = row[0]
    
    if sequence.endswith('A') or sequence.endswith('B'):
        row = np.insert(row,0,"Pre-trained novice")
        row = np.insert(row,1,sequence[:-1])
        output.append(row)
        
    if sequence.endswith('C') or sequence.endswith('D'):
        row = np.insert(row,0,"Post-trained novice")
        row = np.insert(row,1,sequence[:-1])
        output.append(row)
        
for row in transposed_expert[1:]:
    sequence = row[0]
    row = np.insert(row,0,"Expert")
    row = np.insert(row,1,sequence[:-1])
    output.append(row)


with open(os.path.join(outputPath,"novice_expert_combined_data.csv"), newline='', mode='w') as output_file:
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
    for row in output:
        output_writer.writerow(row)