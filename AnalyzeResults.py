# This code is for consolidating all of the output from CalculateMetrics into one spreadsheet for analysis

# TODO: don't use scopetoReference

# Analyses to run:
    # expert v novice
    # pre v post (trend over time)
    # perktutor v qualitive scoring

import os
import csv


# User defined
inputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CalculateMetricsOutput\Novice'
outputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\AnalyzeResultsOutput\Novices'

metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\ColonoscopyAnalysis\Colonoscopy-metrics'
excludeRolesList = ["Any = ScopeToReference"]



# Here's an example of the class hierarchy:

# Metric AverageVelocity:
    # Role ScopeTipToScope (<-- has avg scope velocity values for every participant)
    # Role RightHandToReference (<-- has avg RH velocity values for every participant)
    # Role LeftHandToReference (<-- has avg LH velocity values for every participant)

class Role:
    def __init__(self,name):
        self.name = name
        self.values = []
        self.sequences = []
        
    def AddValue(self,value):
        self.values.append(value)
        
    def AddSequence(self,sequence):
        self.sequences.append(sequence)
    
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
                
    def AddSequenceToRole(self,sequence,rolename):
        for role in self.roles:
            if role.name == rolename:
                role.AddSequence(sequence)
                
    def DoesRoleExist(self,rolename):
        for role in self.roles:
            if role.name == rolename:
                return True
        return False



# The list that will contain all found and loaded metrics in the defined path
metricsObjectsList = []

for metric in os.listdir(metricScriptPath):
    name = os.path.splitext(metric)[0]
    metricsObjectsList.append(Metric(name))
 
for file in os.listdir(inputPath):
    
    d = os.path.join(inputPath, file)
    
    # Results path is a parent directory containing many directories for each patient
    # This line ensures it runs on these patient directories and not "loose" files
    if os.path.isdir(d):
        
        patientID = file[:3]
        #print("\nPATIENT NUMER: " + patientID + "\n")
        
        # Each patient directory contains 8+ spreadsheets, one for each sequence
        for spreadsheet in os.listdir(d):
            sequence = os.path.splitext(spreadsheet)[0]
            with open(os.path.join(d,spreadsheet)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                
                for row in csv_reader:
                    
                    metricName = row[0]
                    metricRoles = row[1]
                    metricUnit = row[2]
                    metricValue = row[3]
                    
                    if metricRoles == "Any = LeftHandToReference":
                        print("LH: "+patientID)
                        
                    if metricRoles == "Any = RightHandToReference":
                        print("RH: "+patientID)
                        
                    # Find corresponding metric object for the metric on this row
                    for metricObject in metricsObjectsList:
                        
                        # If we found the matching metric and we care about the role
                        if metricObject.name == metricName.replace(" ","") and metricRoles not in excludeRolesList:
                            
                            if not metricObject.DoesRoleExist(metricRoles):                                    
                                metricObject.AddRole(metricRoles)
                        
                            metricObject.AddValueToRole(metricValue,metricRoles)
                            metricObject.AddSequenceToRole(sequence,metricRoles)


with open(os.path.join(outputPath,"aggregateData.csv"), mode='w') as output_file:
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    sequenceKey = ["Sequence"]
    for sequence in metricsObjectsList[0].roles[0].sequences:
        sequenceKey.append(sequence)

    output_writer.writerow(sequenceKey)

    for metricObject in metricsObjectsList:
                
        for role in metricObject.roles:
            
            row = [metricObject.name+" ("+role.name.split(" = ")[1] + ")"]
            
            for index, value in enumerate(role.values):
                
                row.append(value)
                
            output_writer.writerow(row)
        
