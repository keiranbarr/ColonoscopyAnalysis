import os
import csv

class Metric:

    def __init__(self,name):
        self.name = name
        self.values = []
    
    def AddValue(self,value):
        self.values.append(value)

resultsPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CalculateMetricsOutput'
metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\ColonoscopyAnalysis\Colonoscopy-metrics'
outputDataPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\AnalyzeResultsOutput'

metricsObjectsList = []

for metric in os.listdir(metricScriptPath):
    name = os.path.splitext(metric)[0]
    
    newMetricObject = Metric(name)
    metricsObjectsList.append(newMetricObject)
 
 
for file in os.listdir(resultsPath):
    d = os.path.join(resultsPath, file)
    if os.path.isdir(d):
        patientID = file[:3]
        #print("\nPATIENT NUMER: " + patientID + "\n")
        for spreadsheet in os.listdir(d):
            with open(os.path.join(d,spreadsheet)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    metricName = row[0]
                    metricRoles = row[1]
                    metricUnit = row[2]
                    metricValue = row[3]
                        
                    for metricObject in metricsObjectsList:
                        if metricObject.name == metricName.replace(" ",""):
                            metricObject.AddValue(metricValue)

                    
with open(os.path.join(outputDataPath,"aggregateData.csv"), mode='w') as output_file:
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for metricObject in metricsObjectsList:
        data = metricObject.values
        data.insert(0,metricObject.name)
        output_writer.writerow(data)