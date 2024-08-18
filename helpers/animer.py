import bpy
import bmesh
import math
import json
from random import random
from ..merge_order import MergeOrder, DataHold
from ..bone_helper import BoneHelper
from ..scene_helper import SceneHelper
from math import pi


class Animer(bpy.types.Operator):
    bl_idname = "view3d.aimer"
    bl_label = "Aimer"
    bl_description = "Aimer"
    index = 0
    bone_prefix = "bn_"
    root_prefix = "rt_"
    allowedTypes = ["MESH", "ARMATURE"]
    meshTypes = ["MESH"]
    N_PLANETS = 6
    START_FRAME = 1
    END_FRAME = 200

    def addAnimation(self, armature):
        bpy.ops.object.posemode_toggle()
        # get each bone from the armature
        # bpy.ops.pose.select_all(action="SELECT")
        bones = bpy.data.objects[armature.name].data.bones
        for dix, bone in enumerate(bones):
            # bpy.data.scenes['Scene'].frame_set(0)
            bpy.context.scene.frame_set(0)
            bone.select = True
            # add animation to the bone
            bpy.ops.anim.keyframe_insert()
            bpy.context.scene.frame_set(30)
            bpy.ops.transform.rotate(value=-0.261911, orient_axis='X', orient_type = 'LOCAL')
            bpy.ops.anim.keyframe_insert()
            bone.select = False
            # break
            pass

        # selectedBones = SceneHelper.getSelectedObjects()
        # armature.animation_data_create()
        # armature.animation_data.action = bpy.data.actions.new(name="armature-action-1")
        # fcurve = armature.animation_data.action.fcurves.new(
        #     data_path="rotation_euler", index=2
        # )
        # k1 = fcurve.keyframe_points.insert(frame=self.START_FRAME, value=0)
        # k1.interpolation = "LINEAR"
        # k2 = fcurve.keyframe_points.insert(
        #     frame=self.END_FRAME, value=(2 + random() * 2) * pi
        # )
        # k2.interpolation = "LINEAR"
        
        bpy.ops.object.posemode_toggle()

    def execute(self, context):
        # reset the actions stored
        self.actionsStored = []
        selectedArm = SceneHelper.getSelected()
        if selectedArm == None:
            print("No armature selected")
            return {"FINISHED"}
        if selectedArm.type != "ARMATURE":
            print("Selected object is not an armature")
            return {"FINISHED"}

        # add animation to the bones of the armature
        self.addAnimation(selectedArm)
        return {"FINISHED"}

        print("Finished")
