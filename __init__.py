from .helpers.assign_vertex import (
    AssignVertex_Generic,
)

from .helpers.assign_vertex import AssignVertex_Custom
from .helpers.fix_scale import FixScale
from .helpers.material_to_vertexpaint import MaterialToVertexPaint
from .helpers.material_to_vertexpaint_selected import MaterialToVertexPaintSelected
from .helpers.parent_mesher import Parent_Mesher
from .helpers.animer import Animer
from .helpers.move_to_origin import MoveToOrigin
from .helpers.move_to_constraint import MoveToConstraint

from .MaterialPainter.materialPainter_Panel import MaterialPainter_Panel
from .panel import Panel
import bpy

bl_info = {
    "name": "Sean Helpers",
    "author": "Sean Thomas<aurorasean@gmail.com",
    "description": "Sean Helpers",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D",
    "category": "Object",
}

classes = (
    Parent_Mesher,
    Animer,
    Panel,
    MoveToOrigin,
    MoveToConstraint,
    MaterialToVertexPaint,
    AssignVertex_Generic,
    FixScale,
    MaterialToVertexPaintSelected,
    MaterialPainter_Panel,
)

register, unregister = bpy.utils.register_classes_factory(classes)