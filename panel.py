import bpy
from .panel_custom import panel_custom
from .panel_simple import panel_simple


from bpy.props import BoolProperty, FloatVectorProperty, StringProperty
from . import addon


def get_asset_libraries(_, __):
    # print("Getting libraries %s" % (_, __))
    return addon.get_libraries()


class Panel(bpy.types.Panel):
    planelCustom = panel_custom()
    bl_idname = "PANEL_PT_PARENT_MESH"
    bl_label = "Parent Mesh Panel"
    bl_category = "Sean Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def get_asset_libraries(self):
        addon.get_libraries()

    def unregister():
        addon.unregister()
        pass

    def register():
        bpy.types.Scene.mytool_color = FloatVectorProperty(
            name="Color Picker",
            subtype="COLOR",
            size=4,
            min=0.0,
            max=1.0,
            default=(1.0, 1.0, 1.0, 1.0),
        )

        bpy.types.Scene.movetoOrigin = BoolProperty(
            name="Move all to origin?",
            description="Moves all remaining meshes to the origin",
            default=True,
        )

        bpy.types.Scene.selectedObjectsOnly = BoolProperty(
            name="Selected Objects?",
            description="Use Selected Objects only",
            default=True,
        )
        # bpy.types.Scene.library = StringProperty(
        #     name="Which Library?",
        #     description="Which Library of textures",
        #     default=True,
        # )
        bpy.types.Scene.createSkin = BoolProperty(
            name="Create a skin?",
            description="Create a skin from the meshes",
            default=True,
        )
        bpy.types.Scene.sean_library_folder = bpy.props.EnumProperty(
            name="sean_library_folder",
            description="Select which asset libraries to use",
            items=get_asset_libraries,
        )
        addon.register()

    def draw(self, context):
        panel_simple.draw(self, context)
        self.planelCustom.draw(self, context)
