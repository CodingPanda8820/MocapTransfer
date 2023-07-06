# FUNCMocapMatcher.py
import imp, re
import sys, os

import maya.cmds as cmds
imp.reload(cmds)

from functools import partial
from ...G_CPSystem import UtilPathManager
imp.reload(UtilPathManager)

utilPM = UtilPathManager.PathManager

class AboutSourceChain:

    sideMarkers = ["Left", "", "Right"]

    @classmethod
    def GetSideMarkers(cls):
        return cls.sideMarkers

    @classmethod
    def GetFullName(cls, name, namespace="", sideMarker="", sideMarkerLocation=0):

        if not name:
            return ""

        fullName = ""

        if sideMarker:
            if sideMarkerLocation:
                fullName = "{n}{sm}".format(n=name, sm=sideMarker)
            else:
                fullName = "{sm}{n}".format(n=name, sm=sideMarker)
        else:
            fullName = name

        if namespace:
            fullName ="{ns}:{n}".format(ns=namespace, n=fullName)

        return fullName

    @classmethod
    def TransferChannel(self, source, target, t=0, r=0, s=0, translate=0, rotate=0, scale=0):
        if t or translate:
            sourceVal = cmds.getAttr("{}.translate".format(source))[0]
            cmds.setAttr("{}.translate".format(target), sourceVal[0], sourceVal[1], sourceVal[2])
        if r or rotate:
            sourceVal = cmds.getAttr("{}.rotate".format(source))[0]
            cmds.setAttr("{}.rotate".format(target), sourceVal[0], sourceVal[1], sourceVal[2])
        if s or scale:  
            sourceVal = cmds.getAttr("{}.scale".foramt(source))[0]
            cmds.setAttr("{}.scale".format(target), sourceVal[0], sourceVal[1], sourceVal[2])

    @classmethod
    def TransferLocatorWorldPosition(self, locator, target):
        pivot = cmds.xform(locator, q=True, ws=True, sp=True)

        cmds.xform(target, ws=True, t=pivot)

        return True

    @classmethod
    def SetKeyframeChannel(self, target, frame, t=0, r=0, s=0, translate=0, rotate=0, scale=0):
        if t or translate:
            cmds.setKeyframe(target, time=frame, attribute="translate")
        if r or rotate:
            cmds.setKeyframe(target, time=frame, attribute="rotate")
        if s or scale:
            cmds.setKeyframe(target, time=frame, attribute="scale")

    @classmethod
    def SetKeyframeChannels(cls, targets, frame, t=0, r=0, s=0, translate=0, rotate=0, scale=0):
        
        if type(targets) != list:
            targets = [targets]

        for target in targets:
            self.SetKeyframeChannel(target, frame, t, r, s, translate, rotate, scale)

        return True

    @classmethod
    def CreateDummy(cls, name, targetName, pc=0, oc=0, pr=0, setPointConstraint=0, setOrientConstraint=0, setParentConstraint=0):

        print(name, targetName)
        dummy = cmds.duplicate(name, n="{n}_dummy".format(n=name), po=True)[0]

        dummy_pointConstraint   = None
        dummy_orientConstraint = None
        dummy_parentConstraint = None

        if pc or setPointConstraint:
            dummy_pointConstraint = cmds.pointConstraint(targetName, dummy, n="{n}_pointConst".format(n=dummy), mo=True)[0]
        if oc or setOrientConstraint:
            dummy_orientConstraint = cmds.orientConstraint(targetName, dummy, n="{n}_orientConst".format(n=dummy), mo=True)[0]
        if pr or setParentConstraint:
            dummy_parentConstraint = cmds.parentConstraint(targetName, dummy, n="{n}_parentConst".format(n=dummy), mo=True)[0]

        return (dummy, dummy_pointConstraint, dummy_orientConstraint, dummy_parentConstraint)

    @classmethod
    def CheckIsNodeExisting(cls, node):
        if cmds.ls(node):
            return True
        else:
            return False

    @classmethod
    def CheckAreNodesExisting(cls, *args):
        nodes = args
        for node in nodes:
            if not cls.CheckIsNodeExisting(node):
                return False

        return True

class AboutAdvancedSkeleton(AboutSourceChain):

    iks = ["Arm", "Spine", "Leg"]

    ik = dict()
    ik["Leg"]       = ["Hip", "Knee", "Ankle"]
    ik["Arm"]       = ["Shoulder", "Elbow", "Wrist"]
    ik["Spine"]   = ["Root", "Spine1", "Chest"]    

    @classmethod
    def GetSideMarkers(cls):
        return ["_L", "_M", "_R"]
        
    @classmethod
    def GetFKCtrl(cls, name, namespace="", sideMarker="", sideMarkerLocation=0):

        # Comp::Name
        fkCtrl = "FK{n}".format(n = name)

        fkCtrl = cls.GetFullName(fkCtrl, namespace, sideMarker, sideMarkerLocation)

        return fkCtrl

    @classmethod
    def GetFKCtrlFromJointFullName(cls, fullName):
        namespace = fullName.split(":")[0]
        name =fullName.split(":")[1]

        FKCtrl = cls.GetFKCtrl(name, namespace)

        return FKCtrl

    @classmethod
    def ConnectFKCtrlToJnt(cls, ctrl, jnt):

        ctrlDummy = cmds.duplicate(ctrl, n="{}_dummy".format(ctrl), po=True)

        conOrient = cmds.orientConstraint(jnt, ctrlDummy, mo=True)[0]

        return (ctrl, ctrlDummy, conOrient)

    @classmethod
    def SetFKIKBlend(cls, value, namespace="", leg_l=0, leg_r=0, spine_m=0, arm_r=0, arm_l=0):
        if leg_l:
            cls.SetFKIKLeg_L(value, namespace)
        if leg_r:
            cls.SetFKIKLeg_R(value, namespace)
        if spine_m:
            cls.SetFKIKSpine_M(value, namespace)
        if arm_r:
            cls.SetFKIKArm_R(value, namespace)
        if arm_l:
            cls.SetFKIKArm_L(value, namespace)

    @classmethod
    def SetFKIKLeg_L(cls, value, namespace=""):
        if namespace:
            cmds.setAttr("{ns}:FKIKLeg_L.FKIKBlend".format(ns=namespace), value)
        else:
            cmds.setAttr("{ns}:FKIKLeg_R.FKIKBlend".format(ns=namespace), value)

    @classmethod
    def SetFKIKLeg_R(cls, value, namespace=""):
        if namespace:
            cmds.setAttr("{ns}:FKIKLeg_R.FKIKBlend".format(ns=namespace), value)
        else:
            cmds.setAttr("{ns}:FKIKLeg_R.FKIKBlend".format(ns=namespace), value)

    @classmethod
    def SetFKIKSpine_M(cls, value, namespace=""):
        if namespace:
            cmds.setAttr("{ns}:FKIKSpine_M.FKIKBlend".format(ns=namespace), value)
        else:
            cmds.setAttr("{ns}:FKIKSpine_M.FKIKBlend".format(ns=namespace), value)

    @classmethod
    def SetFKIKArm_L(cls, value, namespace=""):
        if namespace:
            cmds.setAttr("{ns}:FKIKArm_L.FKIKBlend".format(ns=namespace), value)
        else:
            cmds.setAttr("{ns}:FKIKArm_L.FKIKBlend".format(ns=namespace), value)

    @classmethod
    def SetFKIKArm_R(cls, value, namespace=""):
        if namespace:
            cmds.setAttr("{ns}:FKIKArm_R.FKIKBlend".format(ns=namespace), value)
        else:
            cmds.setAttr("{ns}:FKIKArm_R.FKIKBlend".format(ns=namespace), value)

    @classmethod
    def GetIKHandleName(cls, ikName, namespace="", sideMarker="", sideMarkerLocator=0):

        ikHandle = "IK{ik}".format(ik=ikName)
        ikHandle = cls.GetFullName(ikHandle, namespace, sideMarker, sideMarkerLocator)

        return ikHandle

    @classmethod
    def GetPoleVectorCtrlName(cls, ikName, namespace="", sideMarker="", sideMarkerLocator=0):

        poleVectorCtrl = "Pole{ik}".format(ik=ikName)
        poleVectorCtrl = cls.GetFullName(poleVectorCtrl, namespace, sideMarker, sideMarkerLocator)

        return poleVectorCtrl

    # Transfer Animation Data From Motion Capture To AdvancedSkeleton
    @classmethod
    def ConnectFKCtrlDummyToMocapJoint(cls, mocapJoint, fkCtrl):

        fkCtrl_dummy = cmds.duplicate(fkCtrl, n="{fkc}_dummy".format(fkc=fkCtrl), po=True)[0]
        fkCtrl_dummy_orientCon = cmds.orientConstraint(mocapJoint, fkCtrl_dummy, mo=True)[0]

        return (fkCtrl_dummy, fkCtrl_dummy_orientCon)

    @classmethod
    def CreateIKHandleDummy(cls, ikHandleName, fkCtrl):

        ikHandle_dummy = cmds.duplicate(ikHandleName, n="{ikn}_dummy".format(ikn=ikHandleName), po=True)[0]
        ikHandle_dummy_parentCon = cmds.parentConstraint(fkCtrl, ikHandle_dummy, mo=True, n="{ikn}_parentConst".format(ikn=ikHandle_dummy))[0]

        return (ikHandle_dummy, ikHandle_dummy_parentCon)

    @classmethod
    def CreatePoleVectorDummy(cls, ikPoleVectorName, fkCtrl):

        _pivot = cmds.xform(fkCtrl, q=True, ws=True, t=True)

        poleVector_dummy = cmds.spaceLocator(n="{ikp}_dummy".format(ikp=ikPoleVectorName))[0]

        cmds.parent(poleVector_dummy, ikPoleVectorName)
        cmds.setAttr("{pvd}.translate".format(pvd=poleVector_dummy), 0.0, 0.0, 0.0)
        cmds.parent(poleVector_dummy, w=True)
        cmds.makeIdentity(poleVector_dummy, apply=True, scale=True, rotate=True, translate=True)

        cmds.move(_pivot[0], _pivot[1], _pivot[2], "{pvd}.rotatePivot".format(pvd=poleVector_dummy))

        pointCon = cmds.pointConstraint(fkCtrl, poleVector_dummy,
                                                                    n="{pvd}_pointCon".format(pvd=poleVector_dummy), mo=True)[0]

        orientCon = cmds.orientConstraint(fkCtrl, poleVector_dummy,
                                                                    n="{pvd}_orientCon".format(pvd=poleVector_dummy), mo=True)[0]

        return (poleVector_dummy, pointCon, orientCon)

    @classmethod
    def ConnectIKHandleToFKCtrlWithPoleVector(cls, ikName, FK_IKHandleRoot,FK_IKPoleVectorTarget, FK_IKHandleTarget,
                                                                                                    namespace="", sideMarker="", sideMarkerLocation=0):

        ikHandle = cls.GetIKHandleName(ikName, namespace, sideMarker, sideMarkerLocation)
        ikPoleVector = cls.GetPoleVectorCtrlName(ikName, namespace, sideMarker, sideMarkerLocation)

        ikHandleRoot               = cls.GetFKCtrl(FK_IKHandleRoot, namespace, sideMarker, sideMarkerLocation)
        ikHandleTarget          = cls.GetFKCtrl(FK_IKHandleTarget, namespace, sideMarker, sideMarkerLocation)
        ikPoleVectorTarget = cls.GetFKCtrl(FK_IKPoleVectorTarget, namespace, sideMarker, sideMarkerLocation)

        if not cls.CheckAreNodesExisting(ikHandle, ikPoleVector, ikHandleRoot, ikHandleTarget, ikPoleVectorTarget):
            return False

        ikHandle_dummy = cls.CreateIKHandleDummy(ikHandle, ikHandleTarget)[0]
        ikPoleVector_dummy = cls.CreatePoleVectorDummy(ikPoleVector, ikPoleVectorTarget)[0]

        return [ikHandle, ikHandle_dummy, ikPoleVector, ikPoleVector_dummy]

    @classmethod
    def ConnectIKHandlesToFKCtrlWithoutPoleVector(cls, FKIKName, namespace="", sideMarker="", sideMarkerLocation=0):

        fkCtrl = cls.GetFKCtrl(FKIKName[0], namespace, sideMarker, sideMarkerLocation)
        ikHandle = cls.GetIKHandleName(FKIKName[1], namespace, sideMarker, sideMarkerLocation)

        if not cls.CheckAreNodesExisting(fkCtrl, ikHandle):
            return False

        ikHandle_dummy = cls.CreateIKHandleDummy(ikHandle, fkCtrl)[0]

        return [ikHandle, ikHandle_dummy]