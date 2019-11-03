#    Rigify for MB-Lab
#    Copyright (C) 2019 Daniel Engler

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

bl_info = {
    "name": "Rigify for MB-Lab",
    "description": "Rigify for MB-Lab",
    "author": "Daniel Engler",
    "version": (0, 6, 1),
    "blender": (2, 81, 0),
    "location": "View3D > Tools > Rigify for MB-Lab",
    "category": "Characters"
}

import bpy
import importlib

if 'add_rig' in globals():
    importlib.reload(add_rig)
    importlib.reload(generate_rig)
    importlib.reload(panel)
    importlib.reload(rename_vertex_groups)

from . import add_rig, generate_rig, panel, rename_vertex_groups

from .add_rig import RIGIFYFORMBLAB_OT_addrig
from .generate_rig import RIGIFYFORMBLAB_OT_generaterig
from .panel import RIGIFYFORMBLAB_OT_enable_rigify, RIGIFYFORMBLAB_PT_panel
from .rename_vertex_groups import (RIGIFYFORMBLAB_OT_rename_vertex_groups,
                                   RIGIFYFORMBLAB_OT_unrename_vertex_groups)


def register():
   bpy.utils.register_class(RIGIFYFORMBLAB_OT_addrig)
   bpy.utils.register_class(RIGIFYFORMBLAB_OT_rename_vertex_groups)
   bpy.utils.register_class(RIGIFYFORMBLAB_OT_unrename_vertex_groups)
   bpy.utils.register_class(RIGIFYFORMBLAB_OT_generaterig)
   bpy.utils.register_class(RIGIFYFORMBLAB_OT_enable_rigify)
   bpy.utils.register_class(RIGIFYFORMBLAB_PT_panel)


def unregister():
   bpy.utils.unregister_class(RIGIFYFORMBLAB_PT_panel)
   bpy.utils.unregister_class(RIGIFYFORMBLAB_OT_enable_rigify)
   bpy.utils.unregister_class(RIGIFYFORMBLAB_OT_generaterig)
   bpy.utils.unregister_class(RIGIFYFORMBLAB_OT_unrename_vertex_groups)
   bpy.utils.unregister_class(RIGIFYFORMBLAB_OT_rename_vertex_groups)
   bpy.utils.unregister_class(RIGIFYFORMBLAB_OT_addrig)


if __name__ == "__main__":
    register()
