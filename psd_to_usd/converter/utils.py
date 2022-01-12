from . import conversion_options

def make_image_path(image_name):
    return "{}.{}".format(image_name, conversion_options['image_type'])

from pxr import Sdf, UsdUtils


def zip_usd(usdzip_path, usd_path):    
    UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(usd_path), usdzip_path)
