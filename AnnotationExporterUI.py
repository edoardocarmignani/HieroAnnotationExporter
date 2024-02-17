# -*- coding: utf-8 -*-

"""AnnotationExporterUI.py: UI for Annotation Exporter Task."""

__author__ = 'Edoardo Carmignani'
__copyright__ = 'Copyright ©2024 Edoardo Carmignani. All rights reserved.'

__license__ = 'MIT'
__version__ = '0.1.0'
__email__ = 'edoardo.carmignani@gmail.com'
__date__ = '2024.Feb.17'


from AnnotationExporterTask import (AnnotationExporterTask, AnnotationExporterPreset)
from PySide2 import (QtCore, QtWidgets)
from hiero.ui.FnTaskUIFormLayout import TaskUIFormLayout
import hiero.ui
import hiero.core


class AnnotationExporterUI(hiero.ui.TaskUIBase):
    def __init__(self, preset):
        """Initialize"""
        hiero.ui.TaskUIBase.__init__(self, AnnotationExporterTask, preset, "Annotation Frames Exporter")

    def _on_format_change(self):
        self.setFormat(self._format.currentFormat())

    def _on_ext_change(self):
        self._preset._properties['extension'] = self._ext.currentText()

    def setFormat(self, format: hiero.core.Format):
        """Set format information in properties.

        Args:
            format (hiero.core.Format): Format object
        """
        self._preset._properties['reformat']['name'] = str(format.name())
        self._preset._properties['reformat']['width'] = int(format.width())
        self._preset._properties['reformat']['height'] = int(format.height())
        self._preset._properties['reformat']['pixelAspect'] = float(format.pixelAspect())

    def initializeAndPopulateUI(self, widget: QtWidgets.QWidget, exportTemplate):
        """Using this method to override layout stretch and customizing UI further."""

        self.initializeUI(widget)
        layout: QtWidgets.QVBoxLayout = widget.layout()
        layout.setContentsMargins(9, 9, 9, 5)
        form_layout = TaskUIFormLayout()

        self._ext = QtWidgets.QComboBox()
        self._ext.addItems(['png', 'jpg'])

        annotations_format = self._preset._properties['reformat']
        self._format = hiero.ui.FormatChooser()
        self._format.setCurrentFormat(hiero.core.Format(annotations_format['width'],
                                                   annotations_format['height'],
                                                   annotations_format['pixelAspect'],
                                                   annotations_format['name']))
        self._format.formatChanged.connect(self._on_format_change)

        _credits = QtWidgets.QLabel()
        _credits.setAlignment(QtCore.Qt.AlignBottom)
        _credits.setText('<span style="color:#666">©2024 Edoardo Carmignani. All rights reserved.')

        form_layout.addRow('Format:', self._format)
        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(_credits)


hiero.ui.taskUIRegistry.registerTaskUI(AnnotationExporterPreset, AnnotationExporterUI)
