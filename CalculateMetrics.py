# This code is for testing the Perk Evaluator slicer module
# By calculating metrics on a single transform sequence for a single metric

# TODO: Implement transform hierarchy
    # Load calibration files
    # Apply transforms
# TODO: calculate on all patients in a directory
# TODO: Fix memory leaks

slicer.mrmlScene.Clear()

import os

# User-defined
analyzePracticeData = False
saveResults = True

# Make list of all possible practice data names
formatter = "{:04d}".format
practiceDataNameList = [formatter(i) for i in range(1000)]

# User-defined
patientPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Data\Novices\PerkLab5\2017-04-29\26-PracticeSecondHalf-Posttest'
metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\ColonoscopyAnalysis\Colonoscopy-metrics'
outputSavePath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022'

patientID = os.path.basename(patientPath)

# Find path of all metric scripts
metricScriptPathList = []
for file in os.listdir(metricScriptPath):
    filepath = os.path.join(metricScriptPath,file)
    metricScriptPathList.append(filepath)

# Load master scene from patient filepath
for file in os.listdir(patientPath):
    if file.endswith("-Scene.mrb"):
        slicer.util.loadScene(os.path.join(patientPath,file))

peNode = slicer.vtkMRMLPerkEvaluatorNode()
logic = slicer.modules.perkevaluator.logic()

slicer.mrmlScene.AddNode(peNode)

for script in metricScriptPathList:
    # Load scripts
    metricScript = slicer.util.loadNodeFromFile(script,"Python Metric Script")
    
    # Pervasive metrics already are loaded in with 3 roles set
    # If we load a pervasive metric, we will need to set these manually
    
    # To avoid this problem, all metrics being run will need to be made pervasive
    '''
    if not logic.GetMetricPervasive(metricScript.GetID()):
        metricInstance = logic.CreateMetricInstance(metricScript)
        
        # Instantiate scripts
        metricInstance.SetAssociatedMetricScriptID(metricScript.GetID())
        peNode.AddMetricInstanceID(metricInstance.GetID())
        
        scope = slicer.mrmlScene.GetFirstNodeByName("ScopeToReference")
        metricInstance.SetRoleID(transform.GetID(),"Any",slicer.vtkMRMLMetricInstanceNode.TransformRole)
    '''
        


# Set transform role
scopeTransform = slicer.mrmlScene.GetFirstNodeByName("ScopeToReference")
# Set all needle roles to the ScopeToReference transform
logic.SetMetricInstancesRolesToID(peNode,scopeTransform.GetID(),"Needle",slicer.vtkMRMLMetricInstanceNode.TransformRole)

leftTransform = slicer.mrmlScene.GetFirstNodeByName("LeftHandToReference")
logic.SetMetricInstancesRolesToID(peNode,leftTransform.GetID(),"LeftTool",slicer.vtkMRMLMetricInstanceNode.TransformRole)

rightTransform = slicer.mrmlScene.GetFirstNodeByName("RightHandToReference")
logic.SetMetricInstancesRolesToID(peNode,rightTransform.GetID(),"RightTool",slicer.vtkMRMLMetricInstanceNode.TransformRole)


allSequenceBrowsers = slicer.mrmlScene.GetNodesByClass("vtkMRMLSequenceBrowserNode")
for browser in allSequenceBrowsers:

    # Don't compute on empty sequences
    if browser.GetNumberOfItems() == 0:
        continue
    
    # Don't compute on practice data if the user doesn't want to
    if browser.GetName() in practiceDataNameList and analyzePracticeData == False:
        continue
    
    # Set tracked sequence browser
    peNode.SetTrackedSequenceBrowserNodeID(browser.GetID())
    
    sequenceName = browser.GetName()
    
    # Set output metrics table
    tableName = sequenceName+"_results"
    resultTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", tableName)
    peNode.SetMetricsTableID(resultTableNode.GetID())
    
    # Compute
    logic.ComputeMetrics(peNode)
    

    if saveResults == True:
        # Make new folder if it doesn't exist
        outputFolder = os.path.join(outputSavePath,patientID)
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)
        
        # save node to csv file
        slicer.util.saveNode(resultTableNode,os.path.join(outputFolder,sequenceName+".csv"))
