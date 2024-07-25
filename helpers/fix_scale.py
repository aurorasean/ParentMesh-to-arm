import bpy
from .. scene_helper import SceneHelper


class FixScale(bpy.types.Operator):

    bl_idname = "view3d.fix_scale"
    bl_label = "Fix Scale"

    def execute(self, context):
        selected = SceneHelper.getSelected()
        if(selected != None):
            deltaScale = selected.scale
            print('find me: %s', selected.scale)

            if(deltaScale[0] != 1 or deltaScale[1] != 1 or deltaScale[2] != 1):                                
                bpy.ops.object.transform_apply(
                    location=False, rotation=False, scale=True)
                bpy.context.object.delta_scale[0] = 1
                bpy.context.object.delta_scale[1] = 1
                bpy.context.object.delta_scale[2] = 1

                print('scale fixed %s' % selected.delta_scale)

        return {'FINISHED'}
