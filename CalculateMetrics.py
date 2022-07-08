# This code is for testing the Perk Evaluator slicer module
# By calculating metrics on a single transform sequence for a single metric

# TODO: decide on data organization scheme
# TODO: implement calibration transform hierarchy

# TODO: don't calculate on blank sequence
# TODO: more robust pervasive-proofing
# TODO: save results to excel
# TODO: loop through specified patients

import os

scenePath = r'P:\data\PerkTutor\Colonoscopy\2016-2017-Protocol-Reorganized\Data\Novices\2017-04-29\26-PracticeSecondHalf-Posttest\2017-04-29-Scene.mrb'
metricScriptPath = r'C:\Users\Keiran Barr\Documents\Summer 22\Colonoscopy-metrics'
metricScriptPathList = []

# Find path of all metric scripts
for file in os.listdir(metricScriptPath):
    filepath = os.path.join(metricScriptPath,file)
    metricScriptPathList.append(filepath)
    print(filepath)

slicer.util.loadScene(scenePath)

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
    # Set tracked sequence browser
    peNode.SetTrackedSequenceBrowserNodeID(browser.GetID())
    
    # Set output metrics table
    tableName = browser.GetName()+"_results"
    resultTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", tableName)
    peNode.SetMetricsTableID(resultTableNode.GetID())
    
    # Compute
    logic.ComputeMetrics(peNode)