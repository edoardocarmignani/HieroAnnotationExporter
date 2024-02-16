from PySide2 import QtWidgets, QtCore
from hiero.exporters import FnScriptLayout
from typing import Dict, List, Literal
import hiero.core
import itertools
import os


class AnnotationScriptExporterTask(hiero.core.TaskBase):

    def __init__(self, initDict):
        hiero.core.TaskBase.__init__(self, initDict)
        self._progress = 0.0

    def startTask(self):
        hiero.core.TaskBase.startTask(self)
        return

    def get_annotations_frames(self) -> List[int]:
        ann: List[hiero.core.Annotation] = [note for note in itertools.chain( *itertools.chain(*self._item.source().subTrackItems()) ) if isinstance(note, hiero.core.Annotation)]
        frame_list: List[int] = [f.timelineIn() for f in ann]
        return frame_list

    def annotation_group_ui(self, group, frames):

        group.addTabKnob('Annotations')
        group.addRawKnob(
            'addUserKnob {3 annotation_key l annotation -STARTLINE}')
        group.addRawKnob('addUserKnob {3 annotation_count l of -STARTLINE}')
        group.addRawKnob(
            'addUserKnob {22 prev l @KeyLeft -STARTLINE T "k = nuke.thisNode()\[\'annotation_key\']\\ncurFrame = nuke.frame()  \\nnewFrame = curFrame\\ncurve = k.animation(0)\\nfor key in reversed(curve.keys()):\\n  if key.x < curFrame:\\n    newFrame = key.x\\n    break\\nnuke.frame( newFrame )\\n"}')
        group.addRawKnob(
            'addUserKnob {22 next l @KeyRight -STARTLINE T "k = nuke.thisNode()\[\'annotation_key\']\\ncurFrame = nuke.frame()  \\nnewFrame = curFrame\\ncurve = k.animation(0)\\nfor key in curve.keys():\\n  if key.x > curFrame:\\n    newFrame = key.x\\n    break\\nnuke.frame( newFrame )\\n"}')

        if frames:
            annotation_keyframes = ''.join([' x%s %s' % (frame, index + 1)
                                        for index, frame in enumerate(frames)])
            group.addRawKnob('annotation_key {{curve %s}}' % annotation_keyframes)
            group.addRawKnob('annotation_count %s' % len(frames))

    def get_track_effects(self):
        self._script.pushLayoutContext('clip', 'Soft Effects')
        effects = [item for item in self._item.linkedItems() if isinstance(item, hiero.core.EffectTrackItem)]
        for fx in effects:
            fx.addToNukeScript(self._script, addLifetime=False)
        self._script.popLayoutContext()


    def taskStep(self):
        path = self.resolvedExportPath()
        source_in = self._clip.sourceIn()
        frames = self.get_annotations_frames()
        frames = list(map(lambda x: x + source_in, frames))

        self._script = hiero.core.nuke.ScriptWriter()

        if self._preset.properties()['include_effects']:
            self.get_track_effects()

        self._script.pushLayoutContext('write', 'Annotations')
        group = self._clip.addAnnotationsToNukeScript(self._script, firstFrame=source_in, trimmed=False)
        group[0].setKnob('xpos', 0)
        group[0].setKnob('ypos', 0)
        group[0].setKnob('label', self._clip.name())
        self.annotation_group_ui(group[0], frames)
        self._script.popLayoutContext()

        FnScriptLayout.scriptLayout(self._script)
        self._script.writeToDisk(path)

        self._finished = True
        self._progress = 1.0
        return False

    def finishTask(self):
        print('Finished')
        return


class AnnotationScriptExporterPreset(hiero.core.TaskPresetBase):
    def __init__(self, name, properties):
        hiero.core.TaskPresetBase.__init__(self, AnnotationScriptExporterTask, name)

        self.properties()['include_effects'] = False
        self.properties().update(properties)


hiero.core.taskRegistry.registerTask(AnnotationScriptExporterPreset, AnnotationScriptExporterTask)