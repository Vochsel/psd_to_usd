from pxr import Usd, UsdGeom, Gf, UsdShade, Sdf
import os

from . import conversion_options, conversion_context


def convert(usd_stage, prim_path, image_path, psd_layer):
    root_prim = usd_stage.DefinePrim(prim_path, "Xform")

    # Geometry

    usd_geom = UsdGeom.Mesh.Define(usd_stage, prim_path + "/geo")

    if not psd_layer.visible:
        usd_geom.CreateVisibilityAttr().Set(UsdGeom.Tokens.invisible)
    
    _canvas_size = conversion_context["canvas_size"]


    _top = max(psd_layer.top, 0)
    _bottom = min(psd_layer.bottom, _canvas_size[1])
    _left = max(psd_layer.left , 0)
    _right = min(psd_layer.right, _canvas_size[0])

    _h = ( psd_layer.height - abs(psd_layer.top))  / psd_layer.height
    _b = ( psd_layer.height - abs(psd_layer.bottom))  / psd_layer.height

    if abs(psd_layer.bottom) - abs(psd_layer.top) == psd_layer.height:
        _b = 0
        _h = 1

    _l = ( psd_layer.width - abs(psd_layer.left))  / psd_layer.width
    _r = ( psd_layer.width - abs(psd_layer.right))  / psd_layer.width

    if abs(psd_layer.right) - abs(psd_layer.left) == psd_layer.width:
        _l = 0
        _r = 1

    _uv_bl = (_l, _b)
    _uv_br = (_r, _b)
    _uv_tr = (_r, _h)
    _uv_tl = (_l, _h)

    _offset = psd_layer.layer_id

    usd_points = [
        Gf.Vec3f(_left, _offset, _bottom),
        Gf.Vec3f(_right, _offset, _bottom),
        Gf.Vec3f(_right, _offset,  _top),
        Gf.Vec3f(_left, _offset,  _top),
    ]

    usd_fvi = [0, 1, 2, 3]
    usd_fvc = [4]
    usd_uvs = [_uv_bl, _uv_br, _uv_tr, _uv_tl]

    # Material

    usd_image_path = image_path

    usd_geom.CreatePrimvar("st",
                           Sdf.ValueTypeNames.TexCoord2fArray,
                           UsdGeom.Tokens.varying).Set(usd_uvs)

    usd_geom.CreatePointsAttr().Set(usd_points)
    usd_geom.CreateFaceVertexIndicesAttr().Set(usd_fvi)
    usd_geom.CreateFaceVertexCountsAttr().Set(usd_fvc)

    usd_mat = UsdShade.Material.Define(usd_stage, prim_path + "/mat")

    usd_shade_pv_reader = UsdShade.Shader.Define(
        usd_stage, usd_mat.GetPrim().GetPrimPath().AppendChild("texture_coords"))
    usd_shade_pv_reader.CreateIdAttr().Set("UsdPrimvarReader_float2")
    # usd_shade_pv_reader.CreateInput("varname").Set("set")
    usd_shade_pv_reader.CreateInput('varname', Sdf.ValueTypeNames.Token).Set(
        'st')  # .ConnectToSource(stInput)

    usd_shade_uv_texture = UsdShade.Shader.Define(
        usd_stage, usd_mat.GetPrim().GetPrimPath().AppendChild("uv_texture"))
    usd_shade_uv_texture.CreateIdAttr().Set("UsdUVTexture")
    usd_shade_uv_texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(
        os.path.join("F:/dev/repos/vochsel/psd_to_usd/", usd_image_path))

    usd_shade_uv_texture.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("clamp")
    usd_shade_uv_texture.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("clamp")
    usd_shade_uv_texture.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
        usd_shade_pv_reader.ConnectableAPI(), 'result')
    usd_shade_uv_texture.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
    usd_shade_uv_texture.CreateOutput('a', Sdf.ValueTypeNames.Float)

    usd_shade_preview_surface = UsdShade.Shader.Define(
        usd_stage, usd_mat.GetPrim().GetPrimPath().AppendChild("preview_surface"))
    usd_shade_preview_surface.CreateIdAttr().Set("UsdPreviewSurface")
    usd_shade_preview_surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(usd_shade_uv_texture.ConnectableAPI(), 'rgb')
    usd_shade_preview_surface.CreateInput("opacity", Sdf.ValueTypeNames.Float).Set(psd_layer.opacity/255.0)
    usd_shade_preview_surface.CreateInput("opacity", Sdf.ValueTypeNames.Color3f).ConnectToSource(usd_shade_uv_texture.ConnectableAPI(), 'a')

    usd_mat.CreateSurfaceOutput().ConnectToSource(
        usd_shade_preview_surface.ConnectableAPI(), "surface")

    binding = UsdShade.MaterialBindingAPI.Apply(usd_geom.GetPrim())
    if binding:
        binding.Bind(usd_mat)

    return usd_geom
