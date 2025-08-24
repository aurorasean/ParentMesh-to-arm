import bpy

from .. import addon


class ColourCreateData():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def returnColour(self):
        return (self.x, self.y, self.z)


class AssignVertex():
    colours = {
        "orange": ColourCreateData(0.8, 0.4, 0),
        "red": ColourCreateData(1, 0, 0),
        "blue": ColourCreateData(0, 0, 1),
        "green": ColourCreateData(0, 1, 0),
        "yellow": ColourCreateData(1, 1, 0),
        "purple": ColourCreateData(0.8, 0, 0.8),
        "cyan": ColourCreateData(0, 1, 1),
        "brown": ColourCreateData(0.4, 0.2, 0),
        "mageneta": ColourCreateData(0.8, 0, 0.4),
        "black": ColourCreateData(0, 0, 0),
        "lgreen": ColourCreateData(0.6, 1, 0.6),
        "lblue": ColourCreateData(0, 0.4, 1),
        "lred": ColourCreateData(0.8, 0, 0),
        "dgreen": ColourCreateData(0, 0.8, 0),
        "lyellow": ColourCreateData(0.4, 0.4, 0),
        "royalblue": ColourCreateData(0.254901960784314, 0.411764705882353, 0.882352941176471),
        "slateblue": ColourCreateData(0.415686274509804, 0.352941176470588, 0.803921568627451),
        "orchid": ColourCreateData(0.854901960784314, 0.43921568627451, 0.83921568627451),
        "lavender": ColourCreateData(0.901960784313726, 0.901960784313726, 0.980392156862745),
        "lightcoral": ColourCreateData(0.941176470588235, 0.501960784313725, 0.501960784313725),
        "lawngreen": ColourCreateData(0.486274509803922, 0.988235294117647, 0),
    }

    def AssignVertexColourCustom(self, colour):
        mode = bpy.context.object.mode

        bpy.ops.paint.vertex_paint_toggle()
        bpy.context.object.data.use_paint_mask = True
        bpy.data.brushes["Draw"].color = colour
        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.object.mode_set(mode=mode)
    def convert255To1(self, value):
        return value / 255.0
    def AssignVertexColourValue(self, colourValue):
        mode = bpy.context.object.mode
        bpy.ops.paint.vertex_paint_toggle()
        bpy.context.object.data.use_paint_mask = True

        base255Colour = (self.convert255To1(colourValue[0]), self.convert255To1(colourValue[1]), self.convert255To1(colourValue[2]))

        try:
            bpy.context.scene.tool_settings.unified_paint_settings.color = base255Colour
            bpy.context.scene.tool_settings.unified_paint_settings.color = base255Colour
        except (Exception) as e:
            print("Colour crash %s" % e)
        try:
            bpy.data.brushes["Draw"].color = base255Colour
        except:
            pass

        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.object.mode_set(mode=mode)
    def AssignVertexColour(self, colour):
        mode = bpy.context.object.mode

        selected = self.colours[colour]
        bpy.ops.paint.vertex_paint_toggle()
        bpy.context.object.data.use_paint_mask = True

        try:
            bpy.context.scene.tool_settings.unified_paint_settings.color = selected.returnColour()
            bpy.context.scene.tool_settings.unified_paint_settings.color = selected.returnColour()
        except:
            print("Colour not found")
            pass

        try:
            bpy.data.brushes["Draw"].color = selected.returnColour()
        except:
            pass

        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_color_set()
        bpy.ops.paint.vertex_paint_toggle()
        bpy.ops.object.mode_set(mode=mode)


class AssignVertex_Generic(bpy.types.Operator):
    assign = AssignVertex()
    bl_idname = "sean_painter.operator"
    bl_label = "Assign vertex generic"
    color: bpy.props.FloatVectorProperty(size=3, default=(1, 0, 1))

    def execute(self, context):
        colourValueStr = f"{self.color[0]:.2f}, {self.color[1]:.2f}, {self.color[2]:.2f}"
        print('color value: %s' % colourValueStr)
        selected = self.color
        self.assign.AssignVertexColourValue(selected)
        return {'FINISHED'}


class AssignVertex_Custom(bpy.types.Operator):
    assign = AssignVertex()
    bl_idname = "view3d.assignvertex_custom"
    bl_label = "Assign vertex custom"
    
    def execute(self, context):
        tempColour = context.scene.mytool_color
        colour = (tempColour[0], tempColour[1], tempColour[2])
        self.assign.AssignVertexColourCustom(colour)
        return {'FINISHED'}

