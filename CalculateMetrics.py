# This code is for testing the Perk Evaluator slicer module
# By calculating metrics on a single transform sequence for a single metric

# TODO: Don't calculate on ScopeTipToScope

import os


# User-defined
analyzePracticeData = False
saveResults = True

# EXPERT
#inputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Data\Attending\ReformattedTracking'
#outputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CalculateMetricsOutput\Expert'

# NOVICE

inputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Data\Novices'
outputPath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Analysis\PerkTutorResults2022\CalculateMetricsOutput\Novice'

metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\ColonoscopyAnalysis\Colonoscopy-metrics'
leftHandedPatientIDs = ['026','062','067','101','152']


# Make list of all possible practice data names
formatter = "{:04d}".format
practiceDataNameList = [formatter(i) for i in range(1000)]

patientPaths = []
for file in os.listdir(inputPath):
    d = os.path.join(inputPath, file)
    if os.path.isdir(d):
        patientPaths.append(d)
        

for patient in patientPaths:
    
    slicer.mrmlScene.Clear()
    
    patientID = os.path.basename(patient)
        
    # Find path of all metric scripts
    metricScriptPathList = []
    for file in os.listdir(metricScriptPath):
        filepath = os.path.join(metricScriptPath,file)
        metricScriptPathList.append(filepath)
    
    # Load master scene from patient filepath
    for file in os.listdir(patient):
        if file.endswith("-Scene.mrb") or file.endswith("-Scene.mrml"):
            try:
                slicer.util.loadScene(os.path.join(patient,file))
            except RuntimeError:
                pass
        elif file == "RasToReference.h5" or file == "ScopeTipToScope.h5":
            slicer.util.loadTransform(os.path.join(patient,file))
    
    peNode = slicer.vtkMRMLPerkEvaluatorNode()
    logic = slicer.modules.perkevaluator.logic()
    
    slicer.mrmlScene.AddNode(peNode)
    
    for script in metricScriptPathList:
        # Load scripts
        metricScript = slicer.util.loadNodeFromFile(script,"Python Metric Script")
        
        # Pervasive metrics already are loaded in with 3 roles set
        # If we load a pervasive metric, we will need to set these manually
        
        if not logic.GetMetricPervasive(metricScript.GetID()):
            metricInstance = logic.CreateMetricInstance(metricScript)
            
            # Instantiate scripts
            metricInstance.SetAssociatedMetricScriptID(metricScript.GetID())
            peNode.AddMetricInstanceID(metricInstance.GetID())
    
    # Set transform role
    scopeTransform = slicer.mrmlScene.GetFirstNodeByName("ScopeToReference")
    # Set all needle roles to the ScopeToReference transform
    logic.SetMetricInstancesRolesToID(peNode,scopeTransform.GetID(),"Needle",slicer.vtkMRMLMetricInstanceNode.TransformRole)
    
    leftTransform = slicer.mrmlScene.GetFirstNodeByName("LeftHandToReference")
    rightTransform = slicer.mrmlScene.GetFirstNodeByName("RightHandToReference")
    
    if patientID[:3] in leftHandedPatientIDs:
        leftTransform.SetName("DominantHandToReference")
        rightTransform.SetName("NonDominantHandToReference")
        
    else:
        # Patient 166 requires me to run this twice
        # Wish I could tell you why
        leftTransform.SetName("NonDominantHandToReference")
        leftTransform.SetName("NonDominantHandToReference")
        rightTransform.SetName("DominantHandToReference")
        
    logic.SetMetricInstancesRolesToID(peNode,leftTransform.GetID(),"LeftTool",slicer.vtkMRMLMetricInstanceNode.TransformRole)
    logic.SetMetricInstancesRolesToID(peNode,rightTransform.GetID(),"RightTool",slicer.vtkMRMLMetricInstanceNode.TransformRole)
    
    # Load calibration transforms
    ScopeTipToScope = slicer.mrmlScene.GetFirstNodeByName("ScopeTipToScope")
    ReferenceToRAS = slicer.mrmlScene.GetFirstNodeByName("RasToReference")
    ReferenceToRAS.Inverse()
    
    # Reference -> RAS
        # LH -> Reference
        # RH -> Reference
    
        # Scope -> Reference
            # ScopeTip -> Scope
    
    
    # Construct transform hierarchy outlined above
    rightTransform.SetAndObserveTransformNodeID(ReferenceToRAS.GetID())
    leftTransform.SetAndObserveTransformNodeID(ReferenceToRAS.GetID())
    ScopeTipToScope.SetAndObserveTransformNodeID(scopeTransform.GetID())
    scopeTransform.SetAndObserveTransformNodeID(ReferenceToRAS.GetID())
    
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
            outputFolder = os.path.join(outputPath,patientID)
            if not os.path.exists(outputFolder):
                os.makedirs(outputFolder)
            
            # save node to csv file
            slicer.util.saveNode(resultTableNode,os.path.join(outputFolder,sequenceName+".csv"))
