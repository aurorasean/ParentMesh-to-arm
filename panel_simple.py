import os
import bpy

from . import addon


def AssignVertexColour(colour):
    mode = bpy.context.object.mode

    bpy.ops.paint.vertex_paint_toggle()
    bpy.context.object.data.use_paint_mask = True

    ## this should make it support backwards compatibility with older versions of blender
    try:
        bpy.context.scene.tool_settings.unified_paint_settings.color = colour
        bpy.context.scene.tool_settings.unified_paint_settings.color = colour
    except:
        print("Colour not found")
        pass

    try:
        bpy.data.brushes["Draw"].color = colour
    except:
        pass

    bpy.ops.paint.vertex_color_set()
    bpy.ops.paint.vertex_color_set()
    bpy.ops.paint.vertex_paint_toggle()
    bpy.ops.object.mode_set(mode=mode)


class panel_simple:
    def draw(parent, context):
        layout = parent.layout
        enabled = False
        if context.object != None:
            mode = context.object.mode
            if mode == "EDIT":
                enabled = True
            else:
                enabled = False

        row = layout.row()

        row = layout.row()
        row.operator("view3d.parent_mesh_armature", text="Create Armature from Parents")

        row = layout.row()
        row.operator("view3d.move_to_origin", text="Move to origin")
        row = layout.row()
        row.operator("view3d.move_to_constraint", text="Move to constraint")
        row = layout.row()
        row.operator("wm.collection_export_all", text="Export all")
        rowCheckbox = layout.row()
        rowCheckbox.prop(
            context.scene,
            "selectedObjectsOnly",
        )
        rowCheckbox = layout.row()
        rowCheckbox.prop(
            context.scene,
            "createSkin",
        )
        rowCheckbox = layout.row()
        rowCheckbox.prop(
            context.scene,
            "movetoOrigin",
        )
        rowVertex = layout.row()
        rowVertex.label(text="Material to Vertex colour")
        rowVertex = layout.row()

        box = rowVertex.box()
        rowVertex = box.row()
        rowVertex.operator(
            "view3d.material_to_vertex_paint", icon="FREEZE", text="All objects"
        )

        rowVertex = box.row()
        rowVertex.operator(
            "view3d.material_to_vertex_paint_select",
            icon="DOT",
            text="Selected objects",
        )
        row = layout.row()

        row = layout.row()
        row.enabled = enabled
        row.label(text="Assign vertex colour")

        row = layout.row()
        box = row.box()
        row = box.row()
        col = row.column()

        libs = addon.get_libraries()

        # Add a dropdown for selecting a library
        row_lib = layout.row()
        row_lib.label(text="Library:")
        row_lib.prop(context.scene, "sean_library_folder", text="")

        selectedLibrary = context.scene.sean_library_folder
        colors = addon.get_colours(selectedLibrary)
        for color in colors:
            ccc = colors[color][color].icon_id
            if ccc is None:
                continue

            row = box.row()
            colourValue = colors[color].colour
            colourValueStr = f"{colourValue[0]:.2f}, {colourValue[1]:.2f}, {colourValue[2]:.2f}"
            operator = row.operator(
                "sean_painter.operator", icon_value=ccc, text=f"{color}"
            )
            if(colors[color] is not None and operator is not None):
                operator.color = colors[color].colour

        row = layout.row()
        row.label(text="Helpers")

        col = row.column()
        col.operator("view3d.fix_scale", text="Fix scale")
