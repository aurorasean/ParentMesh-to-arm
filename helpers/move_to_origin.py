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

class MoveToOrigin(bpy.types.Operator):
    bl_idname = "view3d.move_to_origin"
    bl_label = "Move to origin"
    bl_description = "Move to origin"
    allowedTypes = ["MESH"]

    def getDictChildren(self) -> list[DataHold]:
        data = []
        for obj in bpy.data.objects:
            if (
                obj.visible_get()
                and str(obj.type) in self.allowedTypes
            ):
                pc = DataHold(obj.name, str(obj.type) in self.allowedTypes)
                data.append(pc)

        return data

    def move_to_origin(
        self,
    ):
        data = self.getDictChildren()
        SceneHelper.unselectAll()
        for d in data:
            
            SceneHelper.selectObject(d.name)
            obj = SceneHelper.getSelected()
            location = obj.matrix_world.to_translation()
            if(len(obj.constraints)>0):
                obj.constraints.remove(obj.constraints['Armature'])
                
            bpy.ops.transform.translate(
                value=(
                    location[0] * -1,
                    location[1] * -1,
                    location[2] * -1,
                )
            )
            bpy.context.view_layer.objects.active = SceneHelper.getSelected()
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            SceneHelper.unselectAll()

    def execute(self, context):
        # reset the actions stored
        self.move_to_origin()
        return {"FINISHED"}

        print("Finished")
