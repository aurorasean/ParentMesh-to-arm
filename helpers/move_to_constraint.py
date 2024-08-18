import bpy
import bmesh
import math
import json
from random import random
from ..merge_order import MergeOrder, DataHold
from ..bone_helper import BoneHelper
from ..scene_helper import SceneHelper
from math import pi


class DataHold:
    def __init__(self, name: str, isMesh: bool):
        self.name = name
        self.isMesh = isMesh


class MoveToConstraint(bpy.types.Operator):
    bl_idname = "view3d.move_to_constraint"
    bl_label = "Move to constraint"
    bl_description = "Move to constraint"
    allowedTypes = ["MESH"]

    def getDictChildren(self) -> list[DataHold]:
        data = []
        for obj in bpy.data.objects:
            if obj.visible_get() and str(obj.type) in self.allowedTypes:
                pc = DataHold(obj.name, str(obj.type) in self.allowedTypes)
                data.append(pc)

        return data

    def getRtArmature(self):
        for obj in bpy.data.objects:
            if obj.name.startswith("rt_") and obj.type == "ARMATURE":
                return obj
        return None

    def move_to_constraint(
        self,
    ):
        data = self.getDictChildren()
        SceneHelper.unselectAll()
        # get the rt_ armature
        parent = self.getRtArmature()
        if parent == None:
            print("No rt_ armature found")
            return

        SceneHelper.unselectAll()
        for d in data:

            SceneHelper.selectObject(d.name)
            child = SceneHelper.getSelected()
            print('------------------------------------------')
            print(d.name)
            if len(child.constraints) > 0:
                child.constraints.remove(child.constraints["Armature"])

            # get bone related to the d.name from the parent
            boneName = "bn_%s" % (d.name)
            if boneName not in bpy.data.objects[parent.name].data.bones:
                print('Bone not found')
                SceneHelper.unselectAll()
                print('------------------------------------------')
                continue
            bone = bpy.data.objects[parent.name].data.bones[boneName]
            location = bone.matrix_local.translation
            # move it to the bone location first, then constrain it
            bpy.ops.transform.translate(
                value=(
                    location[0],
                    location[1],
                    location[2],
                )
            )

            child.constraints.new("ARMATURE")
            child.constraints["Armature"].targets.new()
            boneName = "bn_%s" % (d.name)
            child.constraints["Armature"].targets[0].target = bpy.data.objects[
                parent.name
            ]
            child.constraints["Armature"].targets[0].subtarget = boneName
            SceneHelper.unselectAll()
            print('------------------------------------------')

    def execute(self, context):
        # reset the actions stored
        self.move_to_constraint()
        return {"FINISHED"}
