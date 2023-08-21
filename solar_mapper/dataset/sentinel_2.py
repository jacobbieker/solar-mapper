from pystac.extensions.eo import EOExtension as eo
import pystac_client
import planetary_computer
from odc.stac import configure_rio, stac_load
import json
from rasterio.features import rasterize

'''
TODO:
1. Download the files from Zenodo if not already exists
2. Unzip the files
3. Load the GeoJSON file
4. For each tile in the GeoJSON file, find the corresponding Sentinel 2 image
5. Download the Sentinel 2 image
'''

# Configuration for ODC-STAC
cfg = {
    "sentinel-2-l2a": {
        "assets": {
            "*": {"data_type": "uint16", "nodata": 0},
            "SCL": {"data_type": "uint8", "nodata": 0},
            "visual": {"data_type": "uint8", "nodata": 0},
        },
    },
    "*": {"warnings": "ignore"},
}

def get_catalog():
    return pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

def get_area_of_interest(feature, time_period:str="2023-04-01/2023-08-01", catalog=get_catalog()):
    ## returns the coords in the GeoJSON
    resolution = 10
    area_of_interest = feature['geometry']
    ## Search sentinel 2 catalog
    items = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=time_period,
        query={"eo:cloud_cover": {"lt": 10}},
    ).get_all_items()

    stack = stac_load(
        items,
        chunks={"x": 2048, "y": 2048},
        stac_cfg=cfg,
        patch_url=planetary_computer.sign,
        resolution=resolution,
    )

    return stack

def make_segmentation_maps(pv_site, stack):
    """
    Convert GeoJSON PV Site polygons to segmentation maps

    This creates a segmentation map from the stack and GeoJSON in the PV site
    and adds it as a dataset in the stack

    Args:
        pv_site:
        stack:

    Returns:

    """
    return NotImplementedError("Masking is not implemented yet")

def get_aoi_around_pv_sites(pv_sites):
    """
    Generate area of interest around PV sites of a minimum size

    This will get overlapping tiles

    Args:
        pv_sites:

    Returns:

    """
    return NotImplementedError("AOI generation is not implemented yet")

def build_dataset_of_stacks(tile_file, pv_file):
    pass

