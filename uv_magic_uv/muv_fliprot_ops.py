# <pep8-80 compliant>

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh
from bpy.props import BoolProperty, IntProperty
from . import muv_common

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "4.0"
__date__ = "XX XXX 2015"


# flip/rotate
class MUV_FlipRot(bpy.types.Operator):
    """Flip and Rotate UV."""

    bl_idname = "uv.muv_fliprot"
    bl_label = "Flip/Rotate UV"
    bl_description = "Flip/Rotate UV"
    bl_options = {'REGISTER', 'UNDO'}

    flip = BoolProperty(
        name="Flip UV",
        description="Flip UV...",
        default=False)

    rotate = IntProperty(
        default=0,
        name="Rotate UV",
        min=0,
        max=30)

    def execute(self, context):
        self.report({'INFO'}, "Flip/Rotate UVs.")
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        if muv_common.check_version(2, 73, 0) >= 0:
            bm.faces.ensure_lookup_table()
        
        # get UV layer
        if not bm.loops.layers.uv:
            self.report({'WARNING'}, "Object must have more than one UV map.")
            return {'CANCELLED'}
        uv_layer = bm.loops.layers.uv.verify()
        
        # get selected face
        dest_uvs = []
        dest_pin_uvs = []
        dest_face_indices = []
        for face in bm.faces:
            if face.select:
                dest_face_indices.append(face.index)
                uvs = []
                pin_uvs = []
                for l in face.loops:
                    uvs.append(l[uv_layer].uv.copy())
                    pin_uvs.append(l[uv_layer].pin_uv)
                dest_uvs.append(uvs)
                dest_pin_uvs.append(pin_uvs)
        if len(dest_uvs) == 0 or len(dest_pin_uvs) == 0:
            self.report({'WARNING'}, "No faces are selected.")
            return {'CANCELLED'}
        self.report({'INFO'}, "%d face(s) are selected." % len(dest_uvs))

        # paste
        for idx, duvs, dpuvs in zip(dest_face_indices, dest_uvs, dest_pin_uvs):
            duvs_fr = [uv.copy() for uv in duvs]
            dpuvs_fr = [pin_uv for pin_uv in dpuvs]
            # flip UVs
            if self.flip is True:
                duvs_fr.reverse()
                dpuvs_fr.reverse()
            # rotate UVs
            for n in range(self.rotate):
                uv = duvs_fr.pop()
                pin_uv = dpuvs_fr.pop()
                duvs_fr.insert(0, uv)
                dpuvs_fr.insert(0, pin_uv)
            # paste UVs
            for l, duv, dpuv in zip(bm.faces[idx].loops, duvs_fr, dpuvs_fr):
                l[uv_layer].uv = duv
                l[uv_layer].pin_uv = dpuv
        self.report({'INFO'}, "%d faces are flipped/rotated." % len(dest_uvs))

        bmesh.update_edit_mesh(obj.data)

        return {'FINISHED'}
