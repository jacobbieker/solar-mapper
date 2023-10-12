from solar_mapper.dataset.sentinel_2 import get_example_with_segmentation_map
from solar_mapper.dataset.utils import get_global_pv_mapping_polygons
import datetime

# Get the polygons to use
polygons = get_global_pv_mapping_polygons()
# Generate random examples with the train polygons up to 2018, and add mask from PV site
train_example = get_example_with_segmentation_map(polygons['train'][0],
                                                  start_time=datetime.datetime(2015, 1, 1),
                                                  end_time=datetime.datetime(2018, 12, 31),
                                                  search_delta=datetime.timedelta(days=90),
                                                  num_samples=8)
print(train_example)
seg_mask = train_example['segmentation_map']
# How many pixels are non-zero in the segmentation map? Should come out to 394
print(f"Number of non-zero pixels in segmentation map: {seg_mask.sum().values}")
import matplotlib.pyplot as plt
import numpy as np
# Get the index of the first non-zero element
non_zero_idx = np.nonzero(seg_mask.values)
# Get the center of the non-zero elements
non_zero_center = np.mean(non_zero_idx, axis=1)
print(non_zero_center)
# Get the cutout
seg_mask_cutout = seg_mask.where(seg_mask != 0).isel(x=slice(int(non_zero_center[1]-100), int(non_zero_center[1]+100)), y=slice(int(non_zero_center[0]-100), int(non_zero_center[0]+100)))
plt.imshow(seg_mask_cutout)
plt.show()
# Visual
plt.imshow(train_example['visual'].isel(time=0,x=slice(int(non_zero_center[1]-100), int(non_zero_center[1]+100)), y=slice(int(non_zero_center[0]-100), int(non_zero_center[0]+100))))
plt.show()
