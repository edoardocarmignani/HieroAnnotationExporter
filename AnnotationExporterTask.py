# -*- coding: utf-8 -*-

"""AnnotationExporterTask.py: Custom exporter to render annotated frames only."""

__author__ = 'Edoardo Carmignani'
__copyright__ = 'Copyright ©2024 Edoardo Carmignani. All rights reserved.'

__license__ = 'MIT'
__version__ = '0.0.1'
__email__ = 'edoardo.carmignani@gmail.com'
__date__ = '2024.Feb.15'


from PySide2 import QtWidgets
from typing import Dict, List, Literal
import hiero.core
import itertools
import os

class AnnotationExporterTask(hiero.core.TaskBase):

    def __init__(self, initDict):
        hiero.core.TaskBase.__init__(self, initDict)
        self._progress = 0.0

    def startTask(self):
        hiero.core.TaskBase.startTask(self)
        return

    def update_ui(self):
        """Update Export Queue for rendering progress bar that will update every taskStep otherwise."""
        for widget in QtWidgets.QApplication.allWidgets():
            if widget.objectName() in ['qt_scrollarea_viewport']:
                widget.update()

    def get_annotations_frames(self) -> List[int]:
        ann: List[hiero.core.Annotation] = [note for note in itertools.chain( *itertools.chain(*self._item.source().subTrackItems()) ) if isinstance(note, hiero.core.Annotation)]
        frame_list: List[int] = [f.timelineIn() for f in ann]
        return frame_list

    def taskStep(self) -> Literal[False]:

        path = self.resolvedExportPath()
        source_in = self._clip.sourceIn()
        source_out = self._clip.sourceOut()
        frames = self.get_annotations_frames()
        frames = list(map(lambda x: x + source_in, frames))

        self._script = hiero.core.nuke.ScriptWriter()

        root = hiero.core.nuke.RootNode(source_in, source_out, showAnnotations=True)
        self._script.addNode(root)
        self._clip.addToNukeScript(self._script)
        self._clip.addAnnotationsToNukeScript(self._script, firstFrame=source_in, trimmed=False)
        format_properties = self._preset._properties['reformat']
        annotations_format = hiero.core.Format(format_properties['width'],
                                               format_properties['height'],
                                               format_properties['pixelAspect'],
                                               format_properties['name'])
        annotations_format.addToNukeScript(self._script)

        frame_text = hiero.core.nuke.Node('Text2')
        frame_text.setKnob('xjustify', 'left')
        frame_text.setKnob('yjustify', 'bottom')
        frame_text.setKnob('global_font_scale', '0.5')
        frame_text.setKnob('enable_background', True)
        frame_text.setKnob('font', '{{ Nunito Sans : Bold : NunitoSans-Bold.ttf : 0 }}')
        self._script.addNode(frame_text)

        # print(self._sequence.format()) # NOTE: maybe use sequence format for export? or UI?

        write = hiero.core.nuke.WriteNode(path)
        write.setKnob('name', 'ANNOTATIONS_OUT')
        self._script.addNode(write)
        self._scriptname = os.path.dirname(path) + '/' + self.clipName() + '.nk'
        self._logname = os.path.dirname(path) + '/' + self.clipName() + '.log'

        c = 1
        for frame in frames:
            self._export_annotated(frame)
            self._progress = c / len(frames)
            self.update_ui()
            # while self.poll() is None:
            #     QtCore.QTimer.singleShot(200, self.poll)
            self._process.wait()
            c += 1

        self._finished = True
        return False

    def _export_annotated(self, frame):
        for node in self._script.getNodes():
            if node.__class__.__name__ == 'WriteNode':
                node.knobs()['first'] = frame
                node.knobs()['last'] = frame
                node.knobs()['use_limit'] = True
            if node.type() == 'Text2':
                node.knobs()['message'] = f'frame: {frame}'
        self._script.writeToDisk(self._scriptname)
        self._process = hiero.core.nuke.executeNukeScript(self._scriptname, open( self._logname, 'w' ))

    # def poll(self):
    #     return self._process.poll()

    def upload_to_frack(self):
        pass

    def progress(self):
        if self._finished:
            return 1.0
        return float(self._progress)

    def finishTask(self):
        try:
            os.remove(self._scriptname)
            os.remove(self._logname)
        except WindowsError as e:
            print(f'Cannot remove: {e}')
        print('Finished.')
        return



class AnnotationExporterPreset(hiero.core.TaskPresetBase):
    def __init__(self, name, properties):
        hiero.core.TaskPresetBase.__init__(self, AnnotationExporterTask, name)

        self.properties()['extension'] = 'png'
        self.properties()['reformat'] = {}
        self.properties()['reformat']['width'] = 1920
        self.properties()['reformat']['height'] = 1080
        self.properties()['reformat']['pixelAspect'] = 1.0
        self.properties()['reformat']['name'] = 'Annotations'
        self.properties().update(properties)

    def addCustomResolveEntries(self, resolver):
        resolver.addResolver('{ext}', 'File format extension', lambda keyword, task: self.properties()['extension'])


hiero.core.taskRegistry.registerTask(AnnotationExporterPreset, AnnotationExporterTask)