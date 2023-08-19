from pystac.extensions.eo import EOExtension as eo
import pystac_client
import planetary_computer


'''
TODO:
1. Download the files from Zenodo if not already exists
2. Unzip the files
3. Load the GeoJSON file
4. For each tile in the GeoJSON file, find the corresponding Sentinel 2 image
5. Download the Sentinel 2 image
'''

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

import rasterio
from rasterio import windows
from rasterio import features
from rasterio import warp
import os
import numpy as np
from PIL import Image

import json

# Load GeoJSON file
with open('trn_tiles.geojson') as f:
    geojson = json.load(f)

first_feature = geojson['features'][1]

print("First record in the training tiles GeoJSON is: ", first_feature)

len(geojson['features'])

time_of_interest = "2023-04-01/2023-08-01"
def access_href_area(feature):
    # img_name = feature['properties']['tj']
    asset_href = None
    ## returns the coords in the GeoJSON
    area_of_interest = feature['geometry']
    ## Search sentinel 2 catalog
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        intersects=area_of_interest,
        datetime=time_of_interest,
        query={"eo:cloud_cover": {"lt": 10}},
    )

    # Check how many items were returned
    items = search.item_collection()

    if len(items) > 0:
        least_cloudy_item = min(items, key=lambda item: eo.ext(item).cloud_cover)

        print(
            f"Choosing {least_cloudy_item.id} from {least_cloudy_item.datetime.date()}"
            f" with {eo.ext(least_cloudy_item).cloud_cover}% cloud cover"
        )

        ### Save Href to this image
        asset_href = least_cloudy_item.assets["visual"].href

    return asset_href


def get_tile_of_interest(feature, asset_href, resize_image=True):
    area_of_interest = feature['geometry']
    img_name = feature['properties']['tj']
    with rasterio.open(asset_href) as ds:
        aoi_bounds = features.bounds(area_of_interest)
        warped_aoi_bounds = warp.transform_bounds("epsg:4326", ds.crs, *aoi_bounds)
        aoi_window = windows.from_bounds(transform=ds.transform, *warped_aoi_bounds)
        band_data = ds.read(window=aoi_window)

    img = Image.fromarray(np.transpose(band_data, axes=[1, 2, 0]))
    if resize_image:
        w = img.size[0]
        h = img.size[1]
        aspect = w / h
        target_w = 800
        target_h = (int)(target_w / aspect)
        img.resize((target_w, target_h), Image.Resampling.BILINEAR)
    filename = str(img_name)+'.jpg'
    img.save(os.path.join('images_tiles', filename))

for i in range(save_num):
    feature = geojson['features'][i]
    asset_href = access_href_area(feature)
    get_tile_of_interest(feature, asset_href)

import json

# Load GeoJSON file
with open('trn_polygons.geojson') as f:
    geojson = json.load(f)

first_feature = geojson['features'][1]

print("First record in the training tiles GeoJSON is: ", first_feature)
print("Num Polygons: ", len(geojson['features']))

search = catalog.search(
    collections=["sentinel-2-l2a"],
    intersects=area_of_interest,
    datetime=time_of_interest,
    query={"eo:cloud_cover": {"lt": 10}},
)

# Check how many items were returned
items = search.item_collection()
print(f"Returned {len(items)} Items")

area_of_interest = {
    "type": "Polygon",
    "coordinates": [
        [
            [
                -79.74307343871824,
                43.43797670357279
            ],
            [
                -79.70502419679973,
                43.43797670357279
            ],
            [
                -79.70502419679973,
                43.45342384517309
            ],
            [
                -79.74307343871824,
                43.45342384517309
            ],
            [
                -79.74307343871824,
                43.43797670357279
            ]
        ]
    ],
}

least_cloudy_item = min(items, key=lambda item: eo.ext(item).cloud_cover)

print(
    f"Choosing {least_cloudy_item.id} from {least_cloudy_item.datetime.date()}"
    f" with {eo.ext(least_cloudy_item).cloud_cover}% cloud cover"
)

import rasterio
from rasterio import windows
from rasterio import features
from rasterio import warp

import numpy as np
from PIL import Image

with rasterio.open(asset_href) as ds:
    aoi_bounds = features.bounds(area_of_interest)
    warped_aoi_bounds = warp.transform_bounds("epsg:4326", ds.crs, *aoi_bounds)
    aoi_window = windows.from_bounds(transform=ds.transform, *warped_aoi_bounds)
    band_data = ds.read(window=aoi_window)

