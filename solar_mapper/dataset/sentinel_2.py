import pystac_client
import planetary_computer
from datetime import datetime, timedelta
from odc.stac import configure_rio, stac_load
import xarray as xr
import numpy as np
import rioxarray
import json
import geopandas as gpd
import rasterio
from rasterio.crs import CRS
from rasterio.features import rasterize, warp
from pyproj import Transformer
from shapely.geometry import Point
from shapely.ops import transform
import pyproj
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon

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


def get_area_of_interest(feature, time_period: str = "2023-04-01/2023-08-01", num_samples=100, sortby_clouds=True,
                         catalog=get_catalog()):
    ## returns the coords in the GeoJSON
    resolution = 10
    area_of_interest = feature['geometry']
    ## Search sentinel 2 catalog
    items = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=time_period,
        sortby="eo:cloud_cover" if sortby_clouds else None,
    ).pages()
    all_items = [item for page in items for item in page]
    all_items = all_items[:num_samples]  # Limit to max_images
    print(all_items)
    stack = stac_load(
        all_items,
        chunks={"x": 1024, "y": 1024},
        stac_cfg=cfg,
        #crs="EPSG:4326",
        #resolution=0.00009009
        crs="utm",
        resolution=resolution,
    )
    # Always check that the time is in order
    stack = stack.sortby("time", ascending=True)

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
    # Project the feature to the desired CRS
    feature_proj = warp.transform_geom(
        CRS.from_epsg(4326),
        CRS.from_epsg(stack.spatial_ref.values),
        pv_site['geometry']
    )
    out_shape = stack.isel(time=0).visual.shape
    # Convert each point in geometry to pixel coordinates
    coords = feature_proj['coordinates'][0]
    y_coords = stack.y.values
    x_coords = stack.x.values
    for i, coord in enumerate(coords):
        # Have to convert to pixel coordinates, so get closest pixels
        y_coord = np.abs(y_coords - coord[1]).argmin()
        x_coord = np.abs(x_coords - coord[0]).argmin()
        coords[i] = [int(x_coord), int(y_coord)]
    pv_site['geometry']['coordinates'] = [coords]
    output = rasterize(shapes=[pv_site['geometry']], out_shape=out_shape, fill=0, default_value=1)
    # Add the segmentation map to the stack
    stack['segmentation_map'] = xr.DataArray(output, dims=['y', 'x'])
    return stack


def randomly_sample_from_valid_times(example: dict, start_time: datetime, end_time: datetime,
                                     search_delta: timedelta = timedelta(days=90), num_samples: int = 1) -> xr.Dataset:
    """
    Randomly sample a time period from the valid times of an example

    Args:
        example: Example GeoJSON
        start_time: datetime of the start period to search from
        end_time: datetime of the end period to search from
        search_delta: length of the time period to search
        num_samples: number of samples to take

    Returns:
        Image stack from that period, with at most num_samples
    """
    # Pick a random time period within start_time and end_time, and after 'Date' field in example['properties']
    example_date = datetime.strptime(example['properties']['Date'], "%Y-%m-%d %H:%M:%S")
    start_time = max(start_time, example_date)
    end_time = max(end_time, example_date + search_delta)
    search_start_time = start_time + (end_time - start_time - search_delta) * np.random.random()
    search_period = search_start_time.strftime("%Y-%m-%d") + "/" + (search_start_time + search_delta).strftime(
        "%Y-%m-%d")
    stack = get_area_of_interest(example, time_period=search_period, num_samples=num_samples)
    return stack


def get_training_example(examples: list, start_time: datetime, end_time: datetime, search_delta: timedelta,
                         num_samples: int = 1) -> xr.Dataset:
    """
    Randomly sample an example from a list of examples

    Args:
        examples: List of example GeoJSONs
        start_time: datetime of the start period to search from
        end_time: datetime of the end period to search from
        search_delta: length of the time period to search
        num_samples: number of samples to take

    Returns:
        Image stack from that period, with at most num_samples
    """
    example = examples[np.random.randint(len(examples))]
    return randomly_sample_from_valid_times(example, start_time, end_time, search_delta, num_samples)
