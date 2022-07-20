import os
import csv

# Each metric has typically 3 roles, but it varies
# Hence the need for this
class Role:
    def __init__(self,name):
        self.name = name
        self.values = []
        
    def AddValue(self,value):
        self.values.append(value)

class Metric:
    def __init__(self,name):
        self.name = name
        self.roles = []
    
    def AddRole(self,name):
        self.roles.append(Role(name))
        
    def AddValueToRole(self,value,rolename):
        for role in self.roles:
            if role.name == rolename:
                role.AddValue(value)
                
    def DoesRoleExist(self,rolename):
        for role in self.roles:
            if role.name == rolename:
                return True
        return False

# User defined
resultsPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CalculateMetricsOutput'
metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\ColonoscopyAnalysis\Colonoscopy-metrics'
outputDataPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\AnalyzeResultsOutput'

metricsObjectsList = []

for metric in os.listdir(metricScriptPath):
    name = os.path.splitext(metric)[0]
    
    metricsObjectsList.append(Metric(name))
 
 
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
                        
                    # Find corresponding metric object for the metric on this row
                    for metricObject in metricsObjectsList:
                        
                        if metricObject.name == metricName.replace(" ",""):
                            
                            if not metricObject.DoesRoleExist(metricRoles):
                                metricObject.AddRole(metricRoles)
                        
                            metricObject.AddValueToRole(metricValue,metricRoles)


with open(os.path.join(outputDataPath,"aggregateData.csv"), mode='w') as output_file:
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for metricObject in metricsObjectsList:
        
        roleKey = [metricObject.name+"_roles"]
        metricValues = [metricObject.name+"_values"]

        # Prevents saving results from metrics that weren't loaded correctly
        saveMetricResults = False

        for role in metricObject.roles:
            saveMetricResults = True
            for value in role.values:
                
                roleKey.append(role.name)
                metricValues.append(value)
          
        if saveMetricResults:
            output_writer.writerow(roleKey)
            output_writer.writerow(metricValues)
