# UIMocapMatcher.py
import imp, re
import sys, os
import time
import maya.cmds as cmds

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from functools import partial
from shutil import copyfile
from distutils.dir_util import copy_tree

from ...G_CPSystem import UtilPathManager
imp.reload(UtilPathManager)

from . import FUNCMocapMatcher
imp.reload(FUNCMocapMatcher)

PathUtil = UtilPathManager.PathManager

AboutSC      = FUNCMocapMatcher.AboutSourceChain()
AboutADS    = FUNCMocapMatcher.AboutAdvancedSkeleton()

# GlobalVariables::About System & Application
g_PATH_HOME = os.environ["HOME"]
g_PATH_MAYA_APP = os.environ["MAYA_APP_DIR"]
g_PATH_MAYA_VERSION = None
try:
    g_PATH_MAYA_VERSION = cmds.about(q=True, majorVersion=True)
except:
    g_PATH_MAYA_VERSION = cmds.about(q=True, version=True)

g_PATH_MAYA_CODING_PANDA_LOG = PathUtil.ConvertAbsPath(g_PATH_MAYA_APP + "/" + g_PATH_MAYA_VERSION + "/scripts/.CodingPandaLog")

# GlobalVariables::About Package
g_PATH_PACKAGE = os.path.dirname(__file__)
g_PATH_PACKAGE_SAVE = PathUtil.ConvertAbsPath(g_PATH_PACKAGE + "/save")
g_PATH_PACKAGE_SOURCE = PathUtil.ConvertAbsPath(g_PATH_PACKAGE + "/source")

class mainWindow(QWidget):
    
    def __init__(self, parent=None):
        
        super(mainWindow, self).__init__(parent)
        
        # Attributes
        self.Subobjects = list()
        self.Subobject_add = None
        self.Subobject_deleted = None

        self.path_pack      = ""
        self.path_save      = ""
        self.path_source  = ""

        self.job = None
        self.jobs = dict()
        self.jobs_info = list()

        # install
        self.__init__install()
        
        # Left Layout   
        self.leftQGB = QGroupBox("Motion Capture's Animation Transfer")
        self.leftQGB.setMinimumWidth(420)
        self.leftQVBL = QVBoxLayout(self.leftQGB)
        self.leftQVBL.setAlignment(Qt.AlignTop)
        self.sourceQLB = QLabel("Source")
        self.sourceQLB.setAlignment(Qt.AlignCenter)
        self.targetQLB = QLabel("Target")
        self.targetQLB.setAlignment(Qt.AlignCenter)
        self.sourceAndTargetQHBL = QHBoxLayout()
        self.sourceAndTargetQHBL.addWidget(self.sourceQLB)
        self.sourceAndTargetQHBL.addWidget(self.targetQLB)
        self.leftQVBL.addLayout(self.sourceAndTargetQHBL)
        self.selSourceQPB = QPushButton("Select")
        self.selTargetQPB = QPushButton("Select")
        self.selSourceAndTargetQHBL = QHBoxLayout()
        self.selSourceAndTargetQHBL.addWidget(self.selSourceQPB)
        self.selSourceAndTargetQHBL.addWidget(self.selTargetQPB)
        self.leftQVBL.addLayout(self.selSourceAndTargetQHBL)
        self.nsQLB = QLabel("Namespace")
        self.nsQLB.setAlignment(Qt.AlignLeft)
        self.nsQlbQHBL = QHBoxLayout()
        self.nsQlbQHBL.addWidget(self.nsQLB)
        self.leftQVBL.addLayout(self.nsQlbQHBL)
        self.sourceNsQLE = QLineEdit()
        self.sourceNsQLE.setAlignment(Qt.AlignCenter)
        self.targetNsQLE = QLineEdit()
        self.targetNsQLE.setAlignment(Qt.AlignCenter)
        self.sourceAndTargetNsQleQHBL = QHBoxLayout()
        self.sourceAndTargetNsQleQHBL.addWidget(self.sourceNsQLE)
        self.sourceAndTargetNsQleQHBL.addWidget(self.targetNsQLE)
        self.leftQVBL.addLayout(self.sourceAndTargetNsQleQHBL)
        self.worldTransformQLB = QLabel("World Transform")
        self.worldTransformQLB.setAlignment(Qt.AlignLeft)
        self.worldTransformQLB.setMinimumWidth(320)
        self.transferWorldTranslateQCB = QCheckBox("translate")
        self.transferWorldTranslateQCB.setChecked(True)
        self.transferWorldRotateQCB = QCheckBox("rotate")
        self.transferWorldRotateQCB.setChecked(True)
        self.worldPositionTitleQHBL = QHBoxLayout()
        self.worldPositionTitleQHBL.addWidget(self.worldTransformQLB)
        self.worldPositionTitleQHBL.addWidget(self.transferWorldTranslateQCB)
        self.worldPositionTitleQHBL.addWidget(self.transferWorldRotateQCB)
        self.leftQVBL.addLayout(self.worldPositionTitleQHBL)
        self.sourceWorldPositionQLE = QLineEdit()
        self.sourceWorldPositionQPB = QPushButton("Select")
        self.targetWorldPositionQLE = QLineEdit()
        self.targetWorldPositionQPB = QPushButton("Select")
        self.worldPositionQHBL = QHBoxLayout()
        self.worldPositionQHBL.addWidget(self.sourceWorldPositionQLE)
        self.worldPositionQHBL.addWidget(self.sourceWorldPositionQPB)
        self.worldPositionQHBL.addWidget(self.targetWorldPositionQLE)
        self.worldPositionQHBL.addWidget(self.targetWorldPositionQPB)
        self.leftQVBL.addLayout(self.worldPositionQHBL)
        self.scTypeQLB = QLabel("Select Source Chain's Type")
        self.scTypeQHBL = QHBoxLayout()
        self.scTypeQHBL.setAlignment(Qt.AlignLeft)
        self.scTypeQHBL.addWidget(self.scTypeQLB)
        self.leftQVBL.addLayout(self.scTypeQHBL)
        self.sourceSCTypeQCB = QComboBox()
        self.targetSCTypeQCB = QComboBox()
        self.sourceAndTargetTypeQHBL = QHBoxLayout()
        self.sourceAndTargetTypeQHBL.addWidget(self.sourceSCTypeQCB)
        self.sourceAndTargetTypeQHBL.addWidget(self.targetSCTypeQCB)
        self.leftQVBL.addLayout(self.sourceAndTargetTypeQHBL)
        self.sideMarkerLocationQLB = QLabel("Side Marker's Name & Location")
        self.sideMarkerLocationQLB.setAlignment(Qt.AlignLeft)
        self.sideMarkerLocationQHBL = QHBoxLayout()
        self.sideMarkerLocationQHBL.addWidget(self.sideMarkerLocationQLB)
        self.leftQVBL.addLayout(self.sideMarkerLocationQHBL)
        self.sourceSideMarkerLocationQCB = QComboBox()
        self.sourceSideMarkerLocationQCB.addItem("Prefix")
        self.sourceSideMarkerLocationQCB.addItem("Suffix")
        self.targetSideMarkerLocationQCB = QComboBox()
        self.targetSideMarkerLocationQCB.addItem("Prefix")
        self.targetSideMarkerLocationQCB.addItem("Suffix")
        self.sideMarkerLocationQHBL = QHBoxLayout()
        self.sideMarkerLocationQHBL.addWidget(self.sourceSideMarkerLocationQCB)
        self.sideMarkerLocationQHBL.addWidget(self.targetSideMarkerLocationQCB)
        self.leftQVBL.addLayout(self.sideMarkerLocationQHBL)
        self.sourceLeftSideMarkerQLE = QLineEdit("Left")
        self.sourceLeftSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.targetLeftSideMarkerQLE = QLineEdit("Left")
        self.targetLeftSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.sourceAndTargetLeftSideMarkerQleQHBL = QHBoxLayout()
        self.sourceAndTargetLeftSideMarkerQleQHBL.addWidget(self.sourceLeftSideMarkerQLE)
        self.sourceAndTargetLeftSideMarkerQleQHBL.addWidget(self.targetLeftSideMarkerQLE)
        self.leftQVBL.addLayout(self.sourceAndTargetLeftSideMarkerQleQHBL)
        self.sourceMiddleSideMarkerQLE = QLineEdit("Middle")
        self.sourceMiddleSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.targetMiddleSideMarkerQLE = QLineEdit("Middle")
        self.targetMiddleSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.sourceAndTargetMiddleSideMarkerQleQHBL = QHBoxLayout()
        self.sourceAndTargetMiddleSideMarkerQleQHBL.addWidget(self.sourceMiddleSideMarkerQLE)
        self.sourceAndTargetMiddleSideMarkerQleQHBL.addWidget(self.targetMiddleSideMarkerQLE)
        self.leftQVBL.addLayout(self.sourceAndTargetMiddleSideMarkerQleQHBL)
        self.sourceRightSideMarkerQLE = QLineEdit("Right")
        self.sourceRightSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.targetRightSideMarkerQLE = QLineEdit("Right")
        self.targetRightSideMarkerQLE.setAlignment(Qt.AlignCenter)
        self.sourceAndTargetRightSideMarkerQleQHBL = QHBoxLayout()
        self.sourceAndTargetRightSideMarkerQleQHBL.addWidget(self.sourceRightSideMarkerQLE)
        self.sourceAndTargetRightSideMarkerQleQHBL.addWidget(self.targetRightSideMarkerQLE)
        self.leftQVBL.addLayout(self.sourceAndTargetRightSideMarkerQleQHBL)
        self.SubobjectsQW = QWidget()
        self.SubobjectsQVBL = QVBoxLayout(self.SubobjectsQW)
        self.SubobjectsQVBL.setAlignment(Qt.AlignTop)
        self.SubobjectsQSA = QScrollArea()
        self.SubobjectsQSA.setWidget(self.SubobjectsQW)
        self.SubobjectsQSA.setWidgetResizable(True)
        self.SubobjectsQSA.setAlignment(Qt.AlignTop)
        self.leftQVBL.addWidget(self.SubobjectsQSA)
        self.addSubobjectQPB = QPushButton("Add New Component")
        self.extraQPB = QPushButton()
        self.extraQMN = QMenu()
        self.extraQMN.addAction("Delete All", self.__action__deleteAll)
        self.extraQMN.addAction("Clear   All", self.__action__clearAll)
        self.extraQMN.addAction("save Source", self.__action__saveSource)
        self.extraQMN.addAction("save Target", self.__action__saveTarget)
        self.extraQMN.addAction("Open Log Directory", self.__action__openLogDirectory)
        self.extraQPB.setMenu(self.extraQMN)
        self.extraQPB.setMaximumWidth(18)
        self.addSubobjectQHBL = QHBoxLayout()
        self.addSubobjectQHBL.addWidget(self.addSubobjectQPB)
        self.addSubobjectQHBL.addWidget(self.extraQPB)
        self.leftQVBL.addLayout(self.addSubobjectQHBL)
        self.enterQPB = QPushButton("Enter")
        self.enterQHBL = QHBoxLayout()
        self.enterQHBL.addWidget(self.enterQPB)
        self.leftQVBL.addLayout(self.enterQHBL)
        
        # Right Layout
        self.rightQGB = QGroupBox()
        self.rightQGB.setMinimumWidth(240)
        self.rightQVBL = QVBoxLayout(self.rightQGB)
        self.rightQVBL.setAlignment(Qt.AlignTop)        
        self.jobListQGB = QGroupBox("List")
        self.jobListQGB.setMinimumHeight(256)
        self.jobListQGB.setMaximumHeight(256)
        self.jobListQLW = QListWidget()
        self.jobListQLW.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.jobListQVBL = QVBoxLayout(self.jobListQGB)
        self.jobListQVBL.addWidget(self.jobListQLW)
        self.rightQVBL.addWidget(self.jobListQGB)
        self.listEditItemQPB = QPushButton("Edit")
        self.listDeleteItemQPB = QPushButton("Delete")
        self.listButtonsQHBL = QHBoxLayout()
        self.listButtonsQHBL.addWidget(self.listEditItemQPB)
        self.listButtonsQHBL.addWidget(self.listDeleteItemQPB)
        self.rightQVBL.addLayout(self.listButtonsQHBL)
        self.optionsQGB = QGroupBox("Options")
        self.optionsQVBL = QVBoxLayout(self.optionsQGB)
        self.optionsQVBL.setAlignment(Qt.AlignTop)
        self.setZeroPosQLB = QLabel("Set WorldZero At First Frame")
        self.setZeroPosQLB.setMinimumWidth(284)
        self.setZeroPosQCB = QCheckBox()
        self.setZeroPosQHBL = QHBoxLayout()
        self.setZeroPosQHBL.addWidget(self.setZeroPosQLB)
        self.setZeroPosQHBL.addWidget(self.setZeroPosQCB)
        # self.optionsQVBL.addLayout(self.setZeroPosQHBL)
        self.deleteDummyQLB = QLabel("Delete Dummy Automatically")
        self.deleteDummyQLB.setMinimumWidth(284)
        self.deleteDummyQCB = QCheckBox()
        self.deleteDummyQHBL = QHBoxLayout()
        self.deleteDummyQHBL.addWidget(self.deleteDummyQLB)
        self.deleteDummyQHBL.addWidget(self.deleteDummyQCB)
        # self.optionsQVBL.addLayout(self.deleteDummyQHBL)
        self.rightQVBL.addWidget(self.optionsQGB)    

        self.mocapToAdQGB = QGroupBox("Mocap to AdvancedSkeleton")
        self.mocapToAdQGB.setCheckable(True)
        self.mocapToAdQVBL = QVBoxLayout(self.mocapToAdQGB)
        self.mocapToAdQVBL.setAlignment(Qt.AlignTop)
        self.rightQVBL.addWidget(self.mocapToAdQGB)
        self.animToCtrlsQLB = QLabel("Animation To Ctrls")
        self.animToCtrlsQLB.setMinimumWidth(284)
        self.animToCtrlsQCB = QCheckBox()
        self.animToCtrlsQHBL = QHBoxLayout()
        self.animToCtrlsQHBL.addWidget(self.animToCtrlsQLB)
        self.animToCtrlsQHBL.addWidget(self.animToCtrlsQCB)
        # self.mocapToAdQVBL.addLayout(self.animToCtrlsQHBL)
        self.IKInfoQGB = QGroupBox("About IK")
        self.mocapToAdQVBL.addWidget(self.IKInfoQGB)
        self.IKInfoQVBL = QVBoxLayout(self.IKInfoQGB)
        self.IKQLB = QLabel("IK")
        self.IKQLB.setMinimumWidth(70)
        self.IKQLB.setMaximumWidth(70)
        self.IKQLB.setAlignment(Qt.AlignCenter)
        self.IKStartQLB = QLabel("Start")
        self.IKStartQLB.setMinimumWidth(70)
        self.IKStartQLB.setMaximumWidth(70)
        self.IKStartQLB.setAlignment(Qt.AlignCenter)
        self.IKPoleQLB = QLabel("Pole")
        self.IKPoleQLB.setMinimumWidth(70)
        self.IKPoleQLB.setMaximumWidth(70)
        self.IKPoleQLB.setAlignment(Qt.AlignCenter)
        self.IKEndQLB = QLabel("End")
        self.IKEndQLB.setMinimumWidth(70)
        self.IKEndQLB.setMaximumWidth(70)
        self.IKEndQLB.setAlignment(Qt.AlignCenter)
        self.IKQHBL = QHBoxLayout()
        self.IKQHBL.setAlignment(Qt.AlignLeft)
        self.IKQHBL.addWidget(self.IKQLB)
        self.IKQHBL.addWidget(self.IKStartQLB)
        self.IKQHBL.addWidget(self.IKPoleQLB)
        self.IKQHBL.addWidget(self.IKEndQLB)
        self.IKInfoQVBL.addLayout(self.IKQHBL)
        self.IKArmQLE = QLineEdit("Arm")
        self.IKArmQLE.setMinimumWidth(70)
        self.IKArmQLE.setMaximumWidth(70)
        self.IKArmQLE.setAlignment(Qt.AlignCenter)
        self.IKArmStartQLE = QLineEdit("Shoulder")
        self.IKArmStartQLE.setMinimumWidth(70)
        self.IKArmStartQLE.setMaximumWidth(70)
        self.IKArmStartQLE.setAlignment(Qt.AlignCenter)
        self.IKArmPoleQLE = QLineEdit("Elbow")
        self.IKArmPoleQLE.setMinimumWidth(70)
        self.IKArmPoleQLE.setMaximumWidth(70)
        self.IKArmPoleQLE.setAlignment(Qt.AlignCenter)
        self.IKArmEndQLE = QLineEdit("Wrist")
        self.IKArmEndQLE.setMinimumWidth(70)
        self.IKArmEndQLE.setMaximumWidth(70)
        self.IKArmEndQLE.setAlignment(Qt.AlignCenter)
        self.IKArmQHBL = QHBoxLayout()
        self.IKArmQHBL.setAlignment(Qt.AlignLeft)
        self.IKArmQHBL.addWidget(self.IKArmQLE)
        self.IKArmQHBL.addWidget(self.IKArmStartQLE)
        self.IKArmQHBL.addWidget(self.IKArmPoleQLE)
        self.IKArmQHBL.addWidget(self.IKArmEndQLE)
        self.IKInfoQVBL.addLayout(self.IKArmQHBL)
        self.IKLegQLE = QLineEdit("Leg")
        self.IKLegQLE.setMinimumWidth(70)
        self.IKLegQLE.setMaximumWidth(70)
        self.IKLegQLE.setAlignment(Qt.AlignCenter)
        self.IKLegStartQLE = QLineEdit("Hip")
        self.IKLegStartQLE.setMinimumWidth(70)
        self.IKLegStartQLE.setMaximumWidth(70)
        self.IKLegStartQLE.setAlignment(Qt.AlignCenter)
        self.IKLegPoleQLE = QLineEdit("Knee")
        self.IKLegPoleQLE.setMinimumWidth(70)
        self.IKLegPoleQLE.setMaximumWidth(70)
        self.IKLegPoleQLE.setAlignment(Qt.AlignCenter)
        self.IKLegEndQLE = QLineEdit("Ankle")
        self.IKLegEndQLE.setMinimumWidth(70)
        self.IKLegEndQLE.setMaximumWidth(70)
        self.IKLegEndQLE.setAlignment(Qt.AlignCenter)
        self.IKLegQHBL = QHBoxLayout()
        self.IKLegQHBL.setAlignment(Qt.AlignLeft)
        self.IKLegQHBL.addWidget(self.IKLegQLE)
        self.IKLegQHBL.addWidget(self.IKLegStartQLE)
        self.IKLegQHBL.addWidget(self.IKLegPoleQLE)
        self.IKLegQHBL.addWidget(self.IKLegEndQLE)
        self.IKInfoQVBL.addLayout(self.IKLegQHBL)
        self.IKSpineQLB = QLabel("Spine IK")
        self.IKSpineQLB.setMinimumWidth(70)
        self.IKSpineQLB.setMaximumWidth(70)
        self.IKSpineQLB.setAlignment(Qt.AlignCenter)
        self.IKSpineStartQLE = QLineEdit("Spine1")
        self.IKSpineStartQLE.setMinimumWidth(70)
        self.IKSpineStartQLE.setMaximumWidth(70)
        self.IKSpineStartQLE.setAlignment(Qt.AlignCenter)
        self.IKSpinePoleQLE = QLineEdit("Spine2")
        self.IKSpinePoleQLE.setMinimumWidth(70)
        self.IKSpinePoleQLE.setMaximumWidth(70)
        self.IKSpinePoleQLE.setAlignment(Qt.AlignCenter)
        self.IKSpineEndQLE = QLineEdit("Spine3")
        self.IKSpineEndQLE.setMinimumWidth(70)
        self.IKSpineEndQLE.setMaximumWidth(70)
        self.IKSpineEndQLE.setAlignment(Qt.AlignCenter)
        self.IKSpineQHBL = QHBoxLayout()
        self.IKSpineQHBL.setContentsMargins(0, 10, 0, 0)
        self.IKSpineQHBL.setAlignment(Qt.AlignLeft)
        self.IKSpineQHBL.addWidget(self.IKSpineQLB)
        self.IKSpineQHBL.addWidget(self.IKSpineStartQLE)
        self.IKSpineQHBL.addWidget(self.IKSpinePoleQLE)
        self.IKSpineQHBL.addWidget(self.IKSpineEndQLE)
        self.IKInfoQVBL.addLayout(self.IKSpineQHBL)
        self.IKFKSpineQLB = QLabel("Spine FK")
        self.IKFKSpineQLB.setMinimumWidth(70)
        self.IKFKSpineQLB.setMaximumWidth(70)
        self.IKFKSpineQLB.setAlignment(Qt.AlignCenter)
        self.IKFKSpineStartQLE = QLineEdit("Root")
        self.IKFKSpineStartQLE.setMinimumWidth(70)
        self.IKFKSpineStartQLE.setMaximumWidth(70)
        self.IKFKSpineStartQLE.setAlignment(Qt.AlignCenter)
        self.IKFKSpinePoleQLE = QLineEdit("Spine1")
        self.IKFKSpinePoleQLE.setMinimumWidth(70)
        self.IKFKSpinePoleQLE.setMaximumWidth(70)
        self.IKFKSpinePoleQLE.setAlignment(Qt.AlignCenter)
        self.IKFKSpineEndQLE = QLineEdit("Chest")
        self.IKFKSpineEndQLE.setMinimumWidth(70)
        self.IKFKSpineEndQLE.setMaximumWidth(70)
        self.IKFKSpineEndQLE.setAlignment(Qt.AlignCenter)
        self.IKFKSpineQHBL = QHBoxLayout()
        self.IKFKSpineQHBL.setAlignment(Qt.AlignLeft)
        self.IKFKSpineQHBL.addWidget(self.IKFKSpineQLB)
        self.IKFKSpineQHBL.addWidget(self.IKFKSpineStartQLE)
        self.IKFKSpineQHBL.addWidget(self.IKFKSpinePoleQLE)
        self.IKFKSpineQHBL.addWidget(self.IKFKSpineEndQLE)
        self.IKInfoQVBL.addLayout(self.IKFKSpineQHBL)

        self.playbackOptionsQGB = QGroupBox("Playback Options")
        self.playbackOptionsQGB.setMinimumHeight(64)
        self.playbackOptionsQGB.setMaximumHeight(64)
        self.playbackOptionsQVBL = QVBoxLayout(self.playbackOptionsQGB)
        self.frameRangeQLB = QLabel("Start/End")
        self.frameStartQLE = QLineEdit()
        self.frameStartQLE.setMaximumWidth(64)
        self.frameEndQLE = QLineEdit()
        self.frameEndQLE.setMaximumWidth(64)
        self.frameQHBL = QHBoxLayout()
        self.frameQHBL.addWidget(self.frameRangeQLB)
        self.frameQHBL.addWidget(self.frameStartQLE)
        self.frameQHBL.addWidget(self.frameEndQLE)
        self.playbackOptionsQVBL.addLayout(self.frameQHBL)
        self.rightQVBL.addWidget(self.playbackOptionsQGB)
        
        self.exportQGB = QGroupBox("FBX Exporter")
        self.exportQVBL = QVBoxLayout(self.exportQGB)
        self.exportQVBL.setAlignment(Qt.AlignTop)
        self.multiExportQLB = QLabel("Use Multi-Export")
        self.multiExportQLB.setMinimumWidth(284)
        self.multiExportQCB = QCheckBox()
        self.multiExportQHBL = QHBoxLayout()
        self.multiExportQHBL.addWidget(self.multiExportQLB)
        self.multiExportQHBL.addWidget(self.multiExportQCB)
        self.exportQVBL.addLayout(self.multiExportQHBL)
        self.nsHierarchyQLB = QLabel("Keep namespaces in hierarchy")
        self.nsHierarchyQLB.setMinimumWidth(284)
        self.nsHierarchyQCB = QCheckBox()
        self.nsHierarchyQHBL = QHBoxLayout()
        self.nsHierarchyQHBL.addWidget(self.nsHierarchyQLB)
        self.nsHierarchyQHBL.addWidget(self.nsHierarchyQCB)
        self.exportQVBL.addLayout(self.nsHierarchyQHBL)
        self.nsFilenameQLB = QLabel("Use namespace when set filename exported")
        self.nsFilenameQLB.setMinimumWidth(284)
        self.nsFilenameQCB = QCheckBox()
        self.nsFilenameQHBL = QHBoxLayout()
        self.nsFilenameQHBL.addWidget(self.nsFilenameQLB)
        self.nsFilenameQHBL.addWidget(self.nsFilenameQCB)
        self.exportQVBL.addLayout(self.nsFilenameQHBL)
        self.dirQLB = QLabel("Path")
        self.dirQLE = QLineEdit()
        self.dirQPB = QPushButton("O")
        self.dirQPB.setMinimumWidth(24)
        self.dirQHBL = QHBoxLayout()
        self.dirQHBL.addWidget(self.dirQLB)
        self.dirQHBL.addWidget(self.dirQLE)
        self.dirQHBL.addWidget(self.dirQPB)
        self.exportQVBL.addLayout(self.dirQHBL)
        # self.rightQVBL.addWidget(self.exportQGB)
        
        # LR Layout
        self.LRLayoutQHBL = QHBoxLayout()
        self.LRLayoutQHBL.addWidget(self.leftQGB)
        self.LRLayoutQHBL.addWidget(self.rightQGB)
        
        # Bottom Widget        
        self.executeOptionsSelectedOnlyQCB = QCheckBox("Execute Jobs selected only")
        self.executeOptionsQVBL = QVBoxLayout()
        self.executeOptionsQVBL.addWidget(self.executeOptionsSelectedOnlyQCB)
        self.executeQPB = QPushButton("Execute")
        self.cancelQPB = QPushButton("Cancel")
        self.cancelQPB.setMaximumWidth(128)        
        self.bottomButtonsQHBL = QHBoxLayout()
        self.bottomButtonsQHBL.addWidget(self.executeQPB)
        self.bottomButtonsQHBL.addWidget(self.cancelQPB)
        
        # Main Layout
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.LRLayoutQHBL)
        self.mainLayout.addLayout(self.executeOptionsQVBL)
        self.mainLayout.addLayout(self.bottomButtonsQHBL)
        
        self.setWindowTitle("Motion Capture's Animation Transfer")
        self.setMinimumHeight(904)
        self.setMaximumHeight(904)
        
        self.__init__self()
        self.__connect__()

    def __init__install(self):

        self.path_pack = PathUtil.ConvertAbsPath(g_PATH_MAYA_CODING_PANDA_LOG + '/MYMocapMatcher')
        self.path_save = PathUtil.ConvertAbsPath(self.path_pack + "/save")
        self.path_source = PathUtil.ConvertAbsPath(self.path_pack + "/source")

        if not os.path.isdir(self.path_pack):
            PathUtil.CreateDirectoryTree(self.path_pack)

        if not os.path.isdir(self.path_save):
            copy_tree(g_PATH_PACKAGE_SAVE, self.path_save)

        if not os.path.isdir(self.path_source):
            copy_tree(g_PATH_PACKAGE_SOURCE, self.path_source)

    def __init__self(self):
        self.__initUI__Subobjects()
        self.__initUI__sourceSCTypeQCB()
        self.__initUI__targetSCTypeQCB()
        self.__initUI__setZeroPosQCB()
        self.__initUI__deleteDummyQCB()
        self.__initUI__mocapToAdQGB()
        self.__initUI__animToCtrlsQCB()
        self.__initUI__frameStartQLE()
        self.__initUI__frameEndQLE()
        self.__initUI__dirQLE()
        
    def __initUI__Subobjects(self):
        for index in range(16):
            self.addSubobject()

    def __initUI__Subobjects_backgroundColor(self):
        pass

    def __initUI__sourceSCTypeQCB(self):
        self.UpdateDataListQCB(self.sourceSCTypeQCB)

    def __initUI__targetSCTypeQCB(self):

        self.UpdateDataListQCB(self.targetSCTypeQCB)

    def __initUI__setZeroPosQCB(self):
        self.setZeroPosQCB.setChecked(True)

    def __initUI__deleteDummyQCB(self):
        self.deleteDummyQCB.setChecked(True)

    def __initUI__mocapToAdQGB(self):
        self.mocapToAdQGB.setChecked(False)

    def __initUI__animToCtrlsQCB(self):
        self.animToCtrlsQCB.setChecked(True)

    def __initUI__frameStartQLE(self):
        self.frameStartQLE.setText(str(cmds.playbackOptions(q=True, minTime=True)))

    def __initUI__frameEndQLE(self):
        self.frameEndQLE.setText(str(cmds.playbackOptions(q=True, maxTime=True)))

    def __initUI__dirQLE(self):
        self.dirQLE.setText(g_PATH_HOME)
        
    def __connect__(self):
        self.addSubobjectQPB.clicked.connect(self.__connect__addSubobject)
        self.selSourceQPB.clicked.connect(partial(self.__connect__selQPB, self.sourceNsQLE))
        self.selTargetQPB.clicked.connect(partial(self.__connect__selQPB, self.targetNsQLE))
        self.sourceWorldPositionQPB.clicked.connect(partial(self.__connect__selectWorldPosition, self.sourceWorldPositionQLE))
        self.targetWorldPositionQPB.clicked.connect(partial(self.__connect__selectWorldPosition, self.targetWorldPositionQLE))
        self.sourceSCTypeQCB.currentIndexChanged.connect(self.__connect__currentIndexChanged_sourceSCTypeQCB)
        self.targetSCTypeQCB.currentIndexChanged.connect(self.__connect__currentIndexChanged_targetSCTypeQCB)
        self.listEditItemQPB.clicked.connect(self.__connect__listEditQPB)
        self.listDeleteItemQPB.clicked.connect(self.__connect__listDeleteQPB)
        self.enterQPB.clicked.connect(self.__connect__enterQPB)
        self.executeQPB.clicked.connect(self.__connect__executeQPB)
        self.cancelQPB.clicked.connect(self.__connect__cancel)

    def __connect__selQPB(self, p_QLineEdit):

        sel = cmds.ls(sl=True)[0]

        # About Namespace
        namespace = ""
        if len(sel.split(":")) < 2:
            print("Can't continue process :: Must Create namespace")
            return 0
        elif len(sel.split(":")) > 2:
            print("Can't Continue process :: detected namespaces too many")
            return 0
        else:
            namespace = sel.split(":")[0]

        p_QLineEdit.setText(namespace)

    def __connect__selectWorldPosition(self, p_QLineEdit):
        select = cmds.ls(sl=True)[0]
        p_QLineEdit.setText(select.split(":")[-1])
        
    def __connect__addSubobject(self):        
        self.Subobject_add = Subobject(self)
        self.Subobjects.append(self.Subobject_add)        
        self.SubobjectsQVBL.addWidget(self.Subobject_add)

    def __connect__listEditQPB(self):
        
        selected = self.jobListQLW.currentItem().text()

        self.job = self.jobs[selected]
        sideMarkerLocation = self.job["sideMarkerLocation"]
        sourceChain = self.job["sourceChain"]
        namespace = self.job["namespace"]
        worldPosition = self.job["worldPosition"]
        sideMarker = self.job["sideMarker"]
        sourceChainType = self.job["type"]
        withPoleVector = self.job["IKHandleInfo"]["withPoleVector"]
        withoutPoleVector = self.job["IKHandleInfo"]["withoutPoleVector"]

        # Edit::sideMarkerLocation
        self.sourceSideMarkerLocationQCB.setCurrentIndex(sideMarkerLocation[0])
        self.targetSideMarkerLocationQCB.setCurrentIndex(sideMarkerLocation[1])

        # Edit::sourceChainType
        self.sourceSCTypeQCB.setCurrentText(sourceChainType[0])
        self.targetSCTypeQCB.setCurrentText(sourceChainType[1])

        # Edit::sourceChain
        _index = 0
        for srcSourceChain, trgSourceChain in zip(sourceChain[0], sourceChain[1]):

            Subobject = self.Subobjects[_index]
            Subobject.sourceNameQLE.setText(srcSourceChain)
            Subobject.targetNameQLE.setText(trgSourceChain)

            _index += 1

        self.sourceNsQLE.setText(namespace[0])
        self.targetNsQLE.setText(namespace[1])

        self.sourceWorldPositionQLE.setText(worldPosition[0])
        self.targetWorldPositionQLE.setText(worldPosition[1])

        self.sourceLeftSideMarkerQLE.setText(sideMarker[0][0])
        self.sourceMiddleSideMarkerQLE.setText(sideMarker[0][1])
        self.sourceRightSideMarkerQLE.setText(sideMarker[0][2])

        self.targetLeftSideMarkerQLE.setText(sideMarker[1][0])
        self.targetMiddleSideMarkerQLE.setText(sideMarker[1][1])
        self.targetRightSideMarkerQLE.setText(sideMarker[1][2])

        self.IKArmQLE.setText(withPoleVector[0][0])
        self.IKArmStartQLE.setText(withPoleVector[0][1])
        self.IKArmPoleQLE.setText(withPoleVector[0][2])
        self.IKArmEndQLE.setText(withPoleVector[0][3])

        self.IKLegQLE.setText(withPoleVector[1][0])
        self.IKLegStartQLE.setText(withPoleVector[1][1])
        self.IKLegPoleQLE.setText(withPoleVector[1][2])
        self.IKLegEndQLE.setText(withPoleVector[1][3])

        self.IKSpineStartQLE.setText(withoutPoleVector[0][0])
        self.IKSpinePoleQLE.setText(withoutPoleVector[1][0])
        self.IKSpineEndQLE.setText(withoutPoleVector[2][0])

        self.IKFKSpineStartQLE.setText(withoutPoleVector[0][1])
        self.IKFKSpinePoleQLE.setText(withoutPoleVector[1][1])
        self.IKFKSpineEndQLE.setText(withoutPoleVector[2][1])

        # Update jobListQLw
        self.jobs.pop(selected)
        self.jobListQLW.clear()
        self.jobListQLW.addItems(self.jobs.keys())

    def __connect__listDeleteQPB(self):
        selectedItems = self.jobListQLW.selectedItems()
        for selectedItem in selectedItems:
            selectedItemName = selectedItem.text()
            self.jobs.pop(selectedItemName)

        self.jobListQLW.clear()
        self.jobListQLW.addItems(self.jobs.keys())
        
    def __connect__cancel(self):        
        self.close()

    def __connect__currentIndexChanged_sourceSCTypeQCB(self):
        
        selected = self.sourceSCTypeQCB.currentText()

        try:
            components = self.ReadSaveData(selected)
        except:
            components = list()

        counts_Subobjects = len(self.Subobjects)
        counts_components = len(components)
        if counts_Subobjects  < counts_components:
            for i in range(counts_components-counts_Subobjects):
                self.__connect__addSubobject()

        for index, Subobject in enumerate(self.Subobjects):
            try:
                data = components[index].replace("\n", "")
            except:
                data = ""

            self.Subobjects[index].sourceNameQLE.setText(data)

    def __connect__currentIndexChanged_targetSCTypeQCB(self):

        selected = self.targetSCTypeQCB.currentText()

        if selected == "AdvancedSkeleton":
            self.mocapToAdQGB.setChecked(True)

        try:
            components = self.ReadSaveData(selected)
        except:
            components = list()

        counts_Subobjects = len(self.Subobjects)
        counts_components = len(components)
        if counts_Subobjects  < counts_components:
            for i in range(counts_components-counts_Subobjects):
                self.__connect__addSubobject()

        for index, Subobject in enumerate(self.Subobjects):
            try:
                data = components[index].replace("\n", "")
            except:
                data = ""
            
            self.Subobjects[index].targetNameQLE.setText(data)

    def __connect__enterQPB(self):

        job_name = self.CreateJob()
        if job_name:
            self.jobListQLW.addItem(job_name)            
            self.CleanUpLeftQVBL()
            return True
        else:
            return False

    def __connect__executeQPB(self):
        self.ExecuteJobs()

    # QMenu::QAction
    def __action__deleteAll(self):
        for index, Subobject in enumerate(self.Subobjects):
            self.Subobjects[index] = None
            Subobject.deleteLater()

    def __action__clearAll(self):
        for Subobject in self.Subobjects:
            Subobject.sourceNameQLE.setText("")
            Subobject.targetNameQLE.setText("")

    def __action__saveSource(self):

        components = list()

        for Subobject in self.Subobjects:
            components.append(Subobject.sourceNameQLE.text())

        createNew = SaveDataQDG(components, self.sourceSCTypeQCB, self)
        createNew.show()

    def __action__saveTarget(self):
        
        components = list()

        for Subobject in self.Subobjects:
            components.append(Subobject.targetNameQLE.text())

        createNew = SaveDataQDG(components, self.targetSCTypeQCB, self)
        createNew.show()

    def __action__openLogDirectory(self):
        
        if os.name == "nt":
            os.startfile(self.path_save)
        elif os.name == "posix":
            os.system("xdg-open {p}".format(p=self.path_save))
        else:
            raise Exception("This OperateSystem is not supported!!")

    def CleanUpLeftQVBL(self):

        # Clean Up
        self.sourceNsQLE.setText("")        
        self.targetNsQLE.setText("")
        self.sourceSCTypeQCB.setCurrentIndex(0)
        self.targetSCTypeQCB.setCurrentIndex(0)
        self.sourceSideMarkerLocationQCB.setCurrentIndex(0)
        self.targetSideMarkerLocationQCB.setCurrentIndex(0)
        self.sourceLeftSideMarkerQLE.setText("Left")
        self.targetLeftSideMarkerQLE.setText("Left")
        self.sourceMiddleSideMarkerQLE.setText("Middle")
        self.targetMiddleSideMarkerQLE.setText("Middle")
        self.sourceRightSideMarkerQLE.setText("Right")
        self.targetRightSideMarkerQLE.setText("Right")
        self.sourceWorldPositionQLE.setText("")
        self.targetWorldPositionQLE.setText("")

        for Subobject in self.Subobjects:
            Subobject.sourceNameQLE.setText("")
            Subobject.targetNameQLE.setText("")
            Subobject.activeState = True
            Subobject.SetDisplayActiveStateOfSubobject(True)

    def SetDisabledUI(self, *args):

        for arg in args:
            try:
                arg.setDisabled(True)
            except:
                continue
        
    def addSubobject(self):
        
        self.Subobject_add = Subobject(self)
        self.Subobjects.append(self.Subobject_add)
        self.SubobjectsQVBL.addWidget(self.Subobject_add)
        
    def insertSubobject(self, source):
        
        index = self.SubobjectsQVBL.indexOf(source)
        
        self.Subobject_add = Subobject(self)
        self.Subobjects.insert(self.Subobjects.index(source), self.Subobject_add)
        self.SubobjectsQVBL.insertWidget(int(index+1), self.Subobject_add)
        
    def deleteSubobject(self, target):
        
        self.Subobjects.remove(target)
        target.deleteLater()

    def GetSaveDataList(self):

        dataList = list()
        for child in os.listdir(self.path_save):
            if len(child.split(".")) < 2:
                continue
            else:
                dataList.append(child.split(".")[0])

        return dataList

    def ReadSaveData(self, filename):

        savefile = self.path_save + "/" + "{fn}.txt".format(fn=filename)

        components = None
        with open(savefile, 'r') as data:
            components = data.readlines()

        return components

    def UpdateDataListQCB(self, pDataListQCB):

        dataList = self.GetSaveDataList()
        dataList.insert(0, "Select")
        dataList.append("New")

        _selected = pDataListQCB.currentText()
        pDataListQCB.clear()

        for data in dataList:
            pDataListQCB.addItem(data)

        pDataListQCB.setCurrentText(_selected)

    def UpdateMayaViewport(self, frame=None):

        cmds.currentTime(frame)
        cmds.refresh()

        return True

    def GetWorkListFromjobListQLW(self):

        workList = list()

        count = self.jobListQLW.count()
        for index in range(count):
            workList.append(self.GetWorkFromjobListQLW(index))

        return workList

    def GetWorkFromjobListQLW(self, index):
        return self.jobListQLW.item(index).text()

    def GetSourceWorldPosition(self):
        return self.sourceWorldPositionQLE.text()

    def GetTargetWorldPosition(self):
        return self.targetWorldPositionQLE.text()

    def GetSourceNamespace(self):
        return self.sourceNsQLE.text()

    def GetTargetNamespace(self):
        return self.targetNsQLE.text()

    def GetSourceType(self):
        return self.sourceSCTypeQCB.currentText()

    def GetTargetType(self):
        return self.targetSCTypeQCB.currentText()

    def GetSourceSideMarkerLocation(self):
        return self.sourceSideMarkerLocationQCB.currentIndex()

    def GetTargetSideMarkerLocation(self):
        return self.targetSideMarkerLocationQCB.currentIndex()

    def GetTransferWorldScaleQCB(self):
        return self.transferWorldScaleQCB.isChecked()

    def GetTransferWorldRotateQCB(self):
        return self.transferWorldRotateQCB.isChecked()

    def GetTransferWorldTranslateQCB(self):
        return self.transferWorldTranslateQCB.isChecked()

    def GetSourceSideMarkers(self):

        left     = self.sourceLeftSideMarkerQLE.text()
        middle = self.sourceMiddleSideMarkerQLE.text()
        right    = self.sourceRightSideMarkerQLE.text()

        return (left, middle, right)

    def GetTargetSideMarkers(self):

        left     = self.targetLeftSideMarkerQLE.text()
        middle = self.targetMiddleSideMarkerQLE.text()
        right   = self.targetRightSideMarkerQLE.text()

        return (left, middle, right)

    def GetSubobjectValues(self):
        values = list()
        for Subobject in self.Subobjects:
            source = Subobject.sourceNameQLE.text()
            target = Subobject.targetNameQLE.text()

            values.append((source, target))

        return values

    def GetSourceSubobjectValues(self):
        values = list()
        for Subobject in self.Subobjects:
            value = Subobject.sourceNameQLE.text()
            if Subobject.activeState:
                values.append(value)

        return values

    def GetTargetSubobjectValues(self):
        values = list()
        for Subobject in self.Subobjects:
            value = Subobject.targetNameQLE.text()
            if Subobject.activeState:
                values.append(value)

        return values

    def GetArmFKIK(self):
        ik_name = self.IKArmQLE.text()

        start   = self.IKArmStartQLE.text()
        pole     = self.IKArmPoleQLE.text()
        end       = self.IKArmEndQLE.text()

        return (ik_name, start, pole, end)

    def GetSpineFKIK(self):

        fk_start   = self.IKFKSpineStartQLE.text()
        fk_pole     = self.IKFKSpinePoleQLE.text()
        fk_end       = self.IKFKSpineEndQLE.text()

        ik_start   = self.IKSpineStartQLE.text()
        ik_pole     = self.IKSpinePoleQLE.text()
        ik_end       = self.IKSpineEndQLE.text()

        return ([fk_start, ik_start], [fk_pole, ik_pole], [fk_end, ik_end])

    def GetLegFKIK(self):
        ik_name = self.IKLegQLE.text()

        start   = self.IKLegStartQLE.text()
        pole     = self.IKLegPoleQLE.text()
        end       = self.IKLegEndQLE.text()

        return (ik_name, start, pole, end)

    def GetAnimationStartFrame(self):
        return int(float(self.frameStartQLE.text()))

    def GetAnimationEndFrame(self):
        return int(float(self.frameEndQLE.text()))

    def CheckIsNodeExisting(self, node):
        if cmds.ls(node):
            return True
        else:
            return False

    def GetJobsSelectedOnly(self):

        selectedItems = list()
        for selectedItem in self.jobListQLW.selectedItems():
            selectedItems.append(selectedItem.text())

        return selectedItems

    def CheckAreNodesExisting(self, *args):
        nodes = args
        for node in nodes:
            if not self.CheckIsNodeExisting(node):
                return False

        return True

    def TransferWorldPosition(self):

        source = self.job["worldPosition"][0]
        target = self.job["worldPosition"][1]

        if not source or not target:
            return False

        source = AboutSC.GetFullName(source, self.job["namespace"][0])
        target = AboutSC.GetFullName(target, self.job["namespace"][1])

        setWorldTranslate = self.transferWorldTranslateQCB.isChecked()
        setWorldRotate        = self.transferWorldRotateQCB.isChecked()

        target_dummy = AboutSC.CreateDummy(target, source, pc=setWorldTranslate, oc=setWorldRotate)[0]

        return (target, target_dummy)

    def CreateFKTargetsConnectedWithSourceJnts(self):

        connectFKCtrls = list()
        for srcSourceChain, trgSourceChain in zip(self.job["sourceChain"][0], self.job["sourceChain"][1]):
            for srcSideMarker, trgSideMarker in zip(self.job["sideMarker"][0], self.job["sideMarker"][1]):
                srcJnt          = AboutSC.GetFullName(srcSourceChain, self.job["namespace"][0], srcSideMarker, self.job["sideMarkerLocation"][0])
                trgJnt          = AboutSC.GetFullName(trgSourceChain, self.job["namespace"][1], trgSideMarker, self.job["sideMarkerLocation"][1])
                trgFKCtrl   = AboutADS.GetFKCtrl(trgSourceChain, self.job["namespace"][1], trgSideMarker, self.job["sideMarkerLocation"][1])

                if cmds.ls(srcJnt) and cmds.ls(trgJnt) and cmds.ls(trgFKCtrl):
                    pass
                else:
                    continue

                trgFKCtrl_dummy = AboutADS.ConnectFKCtrlDummyToMocapJoint(srcJnt, trgFKCtrl)[0]
                connectFKCtrls.append([trgFKCtrl, trgFKCtrl_dummy])

        return  connectFKCtrls

    def CreateIKTargetsConnectedWithFK(self):
        namespace = self.job["namespace"][1]
        sideMarkers = self.job["sideMarker"][1]
        sideMarkerLocation = self.job["sideMarkerLocation"][1]

        ikHandleInfos = self.job["IKHandleInfo"]["withPoleVector"]
        connectIKHandlesWithPoleVector = list()

        FKIKNames = self.job["IKHandleInfo"]["withoutPoleVector"]
        connectIKHandlesWithoutPoleVector = list()

        for sideMarker in sideMarkers:            
            for ikHandleInfo in ikHandleInfos:
                connectIKHandleWithPoleVector = AboutADS.ConnectIKHandleToFKCtrlWithPoleVector(ikHandleInfo[0], ikHandleInfo[1], ikHandleInfo[2], ikHandleInfo[3], namespace, sideMarker, sideMarkerLocation)
                if connectIKHandleWithPoleVector:                
                    connectIKHandlesWithPoleVector.append(connectIKHandleWithPoleVector)

            for FKIKName in FKIKNames:
                connectIKHandleWithoutPoleVector = AboutADS.ConnectIKHandlesToFKCtrlWithoutPoleVector(FKIKName, namespace, sideMarker, sideMarkerLocation)
                if connectIKHandleWithoutPoleVector:
                    connectIKHandlesWithoutPoleVector.append(connectIKHandleWithoutPoleVector)

        return (connectIKHandlesWithPoleVector, connectIKHandlesWithoutPoleVector)

    def CreateJob(self):

        self.job = dict()
        self.job["namespace"]                      = (self.GetSourceNamespace(), self.GetTargetNamespace())
        self.job["type"]                                  = (self.GetSourceType(), self.GetTargetType())
        self.job["sideMarker"]                    = (self.GetSourceSideMarkers(), self.GetTargetSideMarkers())
        self.job["sideMarkerLocation"] = (self.GetSourceSideMarkerLocation(), self.GetTargetSideMarkerLocation())
        self.job["worldPosition"]             = (self.GetSourceWorldPosition(), self.GetTargetWorldPosition())
        self.job["sourceChain"]                  = (self.GetSourceSubobjectValues(), self.GetTargetSubobjectValues())

        self.job["IKHandleInfo"]                                               = dict()
        self.job["IKHandleInfo"]["withPoleVector"]        = list()
        self.job["IKHandleInfo"]["withoutPoleVector"] = list()

        if self.mocapToAdQGB.isChecked():
            self.job["IKHandleInfo"]["withPoleVector"].append(self.GetArmFKIK())
            self.job["IKHandleInfo"]["withPoleVector"].append(self.GetLegFKIK())            
            self.job["IKHandleInfo"]["withoutPoleVector"] = self.GetSpineFKIK()

        self.job["name"] = "{sns}:{st}|{tns}:{tt}".format(sns=self.job["namespace"][0], st=self.job["type"][0],
                                                                                                       tns=self.job["namespace"][1], tt=self.job["type"][1])

        self.job["frameRange"] = [self.GetAnimationStartFrame(), self.GetAnimationEndFrame()]
        self.jobs[self.job["name"]] = self.job

        return self.job["name"]

    def ExecuteJob(self, job):

        self.job = self.jobs[job]
        for key in self.job:
            print("{} is {}".format(key, self.job[key]))

        startFrame = self.job["frameRange"][0]
        endFrame = self.job["frameRange"][1]

        # WorldPosition [Root]
        worldPos = self.TransferWorldPosition()

        # about FK [ FKCtrl, FKCtrl_dummy ]
        fks = self.CreateFKTargetsConnectedWithSourceJnts()

        # about IK  [  ]
        iks = self.CreateIKTargetsConnectedWithFK()

        return [startFrame, endFrame, worldPos, fks, iks]

    def ExecuteJobs(self):        

        # Get Global Frame Range( Scene Frame Range)
        scene_startFrame = int(float(cmds.playbackOptions(q=True, minTime=True)))
        scene_endFrame = int(float(cmds.playbackOptions(q=True, maxTime=True)))

        # Get Jobs be Executed
        if self.executeOptionsSelectedOnlyQCB.isChecked():
            self.jobs_executed = self.GetJobsSelectedOnly()
        else:
            self.jobs_executed = self.jobs

        for job in self.jobs_executed:
            job_info = self.ExecuteJob(job)
            self.jobs_info.append(job_info)

        for frame in range(scene_startFrame, scene_endFrame+1):

            self.UpdateMayaViewport(frame)

            for job_info in self.jobs_info:

                animationStartFrame = job_info[0]
                animationEndFrame = job_info[1]

                if frame  < animationStartFrame or frame > animationEndFrame:
                    continue

                worldPos                        = job_info[2]
                worldPosCtrl               = worldPos[0]
                worldPosCtrl_dummy = worldPos[1]

                AboutSC.TransferChannel(worldPosCtrl_dummy, worldPosCtrl, t=True, r=True)
                AboutSC.SetKeyframeChannel(worldPosCtrl, frame, t=True, r=True)

                # FK ============================================================
                fks = job_info[3]
                for fk in fks:
                    fkCtrl = fk[0]
                    fkCtrl_dummy = fk[1]

                    AboutSC.TransferChannel(fkCtrl_dummy, fkCtrl, r=True)
                    AboutSC.SetKeyframeChannel(fkCtrl, frame, r=True)

                # IK ============================================================
                ik = job_info[4]
                ikHandlesWithPoleVector = ik[0]
                for ikHandleWithPoleVector in ikHandlesWithPoleVector:
                    ikHandle                        = ikHandleWithPoleVector[0]
                    ikHandle_dummy          = ikHandleWithPoleVector[1]
                    ikPoleVector               = ikHandleWithPoleVector[2]
                    ikPoleVector_dummy = ikHandleWithPoleVector[3]

                    AboutSC.TransferChannel(ikHandle_dummy, ikHandle, t=True, r=True)
                    AboutSC.SetKeyframeChannel(ikHandle, frame, t=True, r=True)
                    AboutSC.TransferLocatorWorldPosition(ikPoleVector_dummy, ikPoleVector)
                    AboutSC.SetKeyframeChannel(ikPoleVector, frame, t=True)

                ikHandlesWithoutPoleVector = ik[1]
                for ikHandleWithoutPoleVector in ikHandlesWithoutPoleVector:
                    ikHandle               = ikHandleWithoutPoleVector[0]
                    ikHandle_dummy = ikHandleWithoutPoleVector[1]

                    AboutSC.TransferChannel(ikHandle_dummy, ikHandle, r=True)
                    AboutSC.SetKeyframeChannel(ikHandle, frame, r=True)

        try:
            cmds.delete("*:*dummy")
        except:
            print("*:*dummy* is not existing!!")

        finishWindow = NotifyMessageQDG("MocapMatcher finish ", self)
        finishWindow.show()

class Subobject(QWidget):
    
    def __init__(self, friendUI, parent=None):
        
        super(Subobject, self).__init__(parent)

        # Attributes
        self.activeState = True

        # UI
        self.friendUI = friendUI
        
        self.sourceNameQLE = QLineEdit()
        self.sourceNameQLE.setAlignment(Qt.AlignCenter)
        self.targetNameQLE = QLineEdit()
        self.targetNameQLE.setAlignment(Qt.AlignCenter)
        self.deleteQPB = QPushButton()
        self.deleteQMN = QMenu()
        self.deleteQMN.addAction("Active/Non-Active", self.__action__active)
        self.deleteQMN.addAction("Insert", self.__action__insert)
        self.deleteQMN.addAction("Delete", self.__action__delete)
        self.deleteQPB.setMenu(self.deleteQMN)
        self.deleteQPB.setMaximumHeight(18)
        self.deleteQPB.setMaximumWidth(17)
        
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.addWidget(self.sourceNameQLE)
        self.mainLayout.addWidget(self.targetNameQLE)
        self.mainLayout.addWidget(self.deleteQPB)
        
        # self.__connect__()
        
    def __connect__(self):
        pass
        
    def __action__insert(self):
        self.friendUI.insertSubobject(self)
        
    def __action__delete(self):
        self.friendUI.deleteSubobject(self)

    def __action__active(self):
        
        self.activeState = not self.activeState
        print(self.activeState)
        self.SetDisplayActiveStateOfSubobject(self.activeState)

    def SetDisplayActiveStateOfSubobject(self, activeState):

        if not activeState:
            self.sourceNameQLE.setStyleSheet("""QLineEdit{background-color: rgba(255, 0, 0, 128)}""")
            self.targetNameQLE.setStyleSheet("""QLineEdit{background-color: rgba(255, 0, 0, 128)}""")
        else:
            self.sourceNameQLE.setStyleSheet("""QLineEdit{background-color: rgba(16,16,16,128)}""")
            self.targetNameQLE.setStyleSheet("""QLineEdit{background-color: rgba(16,16,16,128)}""")

        return True

class SaveDataQDG(QDialog):

    def __init__(self,components, targetSCTypeQCB, parent=None):

        super(SaveDataQDG, self).__init__(parent)

        # Attributes
        self.parent = parent
        self.targetSCTypeQCB = targetSCTypeQCB
        self.components = components

        # UI
        self.setWindowTitle("Create & Save New Type")

        self.nameQLB = QLabel("Name : ")
        self.nameQLE = QLineEdit()
        self.nameQLE.setMinimumWidth(256)
        self.nameQHBL = QHBoxLayout()
        self.nameQHBL.setAlignment(Qt.AlignCenter)
        self.nameQHBL.addWidget(self.nameQLB)
        self.nameQHBL.addWidget(self.nameQLE)

        self.createQPB = QPushButton("Create")
        self.cancelQPB = QPushButton("Cancel")
        self.bottomButtonsQHBL = QHBoxLayout()
        self.bottomButtonsQHBL.setAlignment(Qt.AlignRight)
        self.bottomButtonsQHBL.addWidget(self.createQPB)
        self.bottomButtonsQHBL.addWidget(self.cancelQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.nameQHBL)
        self.mainLayout.addLayout(self.bottomButtonsQHBL)

        self.__connect__()

    def __connect__(self):
        self.createQPB.clicked.connect(self.__connect__createQPB)
        self.cancelQPB.clicked.connect(self.__connect__cancelQPB)

    def __connect__createQPB(self):

        name = self.nameQLE.text()
        filePath = self.parent.path_save + "/" + "{n}.txt".format(n=name)

        if not filePath:
            print("Please Enter Type name")
            return 0

        with open(filePath, "w") as f:
            for component in self.components:
                f.write(str(component) + "\n")

        # Backup
        source = self.parent.sourceSCTypeQCB.currentText()
        target = self.parent.targetSCTypeQCB.currentText()

        _components = list()
        for subobject in self.parent.Subobjects:
            _components.append([subobject.sourceNameQLE.text(), subobject.targetNameQLE.text()])

        self.parent.UpdateDataListQCB(self.parent.sourceSCTypeQCB)
        self.parent.UpdateDataListQCB(self.parent.targetSCTypeQCB)
        self.parent.sourceSCTypeQCB.setCurrentText(source)
        self.parent.targetSCTypeQCB.setCurrentText(target)

        for index, subobject in enumerate(self.parent.Subobjects):
            subobject.sourceNameQLE.setText(_components[index][0])
            subobject.targetNameQLE.setText(_components[index][1])

        self.targetSCTypeQCB.setCurrentText(name)

        self.close()

    def __connect__cancelQPB(self):
        self.close()
        del(self)

class NotifyMessageQDG(QDialog):

    def __init__(self, notifyMessageText, parent=None):

        super(NotifyMessageQDG, self).__init__(parent)

        self.notifyMessage = notifyMessageText

        self.notifyMessageQLB = QLabel(self.notifyMessage)
        self.notifyMessageQHBL = QHBoxLayout()
        self.notifyMessageQHBL.setAlignment(Qt.AlignCenter)
        self.notifyMessageQHBL.addWidget(self.notifyMessageQLB)

        self.okQPB = QPushButton("OK")
        self.buttonQHBL = QHBoxLayout()
        self.buttonQHBL.setAlignment(Qt.AlignCenter)
        self.buttonQHBL.addWidget(self.okQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.notifyMessageQHBL)
        self.mainLayout.addLayout(self.buttonQHBL)

        self.__connect__()

    def  __connect__(self):
        self.okQPB.clicked.connect(self.__connect__okQPB)

    def __connect__okQPB(self):
        self.close()
        del(self)