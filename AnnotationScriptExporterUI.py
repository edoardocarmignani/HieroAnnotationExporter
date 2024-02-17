# -*- coding: utf-8 -*-

"""AnnotationScriptExporterUI.py: UI for Annotation Script Exporter Task."""

__author__ = 'Edoardo Carmignani'
__copyright__ = 'Copyright ©2024 Edoardo Carmignani. All rights reserved.'

__license__ = 'MIT'
__version__ = '0.1.0'
__email__ = 'edoardo.carmignani@gmail.com'
__date__ = '2024.Feb.17'


from AnnotationScriptExporterTask import (AnnotationScriptExporterTask, AnnotationScriptExporterPreset)
from PySide2 import (QtCore, QtWidgets)
from hiero.ui.FnTaskUIFormLayout import TaskUIFormLayout
import hiero.ui

class AnnotationScriptExporterUI(hiero.ui.TaskUIBase):
    def __init__(self, preset):
        """Initialize"""
        hiero.ui.TaskUIBase.__init__(self, AnnotationScriptExporterTask, preset,  'Annotation Script Exporter')

    def _on_includeeffects_change(self, state):
        self._preset._properties['include_effects'] = (state == QtCore.Qt.Checked)

    def initializeAndPopulateUI(self, widget: QtWidgets.QWidget, exportTemplate):
        """Using this method to override layout stretch and customizing UI further."""

        self.initializeUI(widget)
        layout: QtWidgets.QVBoxLayout = widget.layout()
        layout.setContentsMargins(9, 9, 9, 5)
        form_layout = TaskUIFormLayout()

        _fx = QtWidgets.QCheckBox()
        _fx.setCheckState(QtCore.Qt.Unchecked)
        if self._preset._properties['include_effects']:
            _fx.setCheckState(QtCore.Qt.Checked)
        _fx.stateChanged.connect(self._on_includeeffects_change)
        form_layout.addRow('Include Soft Effects:', _fx)

        _credits = QtWidgets.QLabel()
        _credits.setAlignment(QtCore.Qt.AlignBottom)
        _credits.setText('<span style="color:#666">©2024 Edoardo Carmignani. All rights reserved.')

        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(_credits)


hiero.ui.taskUIRegistry.registerTaskUI(AnnotationScriptExporterPreset, AnnotationScriptExporterUI)