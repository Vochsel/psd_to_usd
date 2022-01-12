from psd_tools import PSDImage

import os
import tempfile, shutil

from pxr import Usd, UsdGeom, Tf

from .converter import utils, layer
from .converter import conversion_context, conversion_options

def convert(psd_path, usd_path):

    output_usd_path = usd_path

    is_usdz = False
    if "usdz" in usd_path:
        is_usdz = True
        output_usd_path = output_usd_path[:-1]

    working_dir = ""

    # If .usd, .usda, .usdc use output file path
    working_dir = os.path.dirname(output_usd_path)

    # If .usdz generate temp dir
    if is_usdz:
        working_dir = tempfile.mkdtemp()
        output_usd_path = os.path.join(working_dir, os.path.basename(output_usd_path))

    conversion_context["working_dir"] = working_dir

    tex_dir = os.path.join(working_dir, "tex")

    try:
        os.makedirs(tex_dir)
    except:
        pass

    usd_stage = Usd.Stage.CreateInMemory()

    psd = PSDImage.open(psd_path)
    if conversion_options['output_combined']:
        psd.composite().save(os.path.join(tex_dir, utils.make_image_path("combined")))

    conversion_context["canvas_size"] = psd.size

    for _layer in psd:
        layer_image = _layer.composite()        
        
        _img_path = os.path.join(tex_dir, utils.make_image_path(_layer.name))
        
        if conversion_options['use_absolute_paths']:
            _img_path = os.path.abspath(_img_path)

        layer_image.save(_img_path)

        _path = "/" + Tf.MakeValidIdentifier(_layer.name)

        layer.convert(usd_stage, _path, _img_path, _layer)

    usd_stage.Export(output_usd_path)



    if is_usdz:
        # Zip usd
        utils.zip_usd(usd_path, output_usd_path)

        # Cleanup temp
        try:
            shutil.rmtree(working_dir)
        except OSError as e:
            print("Error: {} : {}".format(working_dir, e.strerror))