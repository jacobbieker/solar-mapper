from solar_mapper.dataset.sentinel_2 import get_example_with_segmentation_map
from solar_mapper.dataset.utils import get_global_pv_mapping_polygons
import datetime

# Get the polygons to use
polygons = get_global_pv_mapping_polygons()
# Generate random examples with the train polygons up to 2018, and add mask from PV site
train_example = get_example_with_segmentation_map(polygons['train'][0],
                                                  start_time=datetime.datetime(2016, 1, 1),
                                                  end_time=datetime.datetime(2018, 1, 1),
                                                  search_delta=datetime.timedelta(days=90),
                                                  num_samples=8)
print(train_example)
