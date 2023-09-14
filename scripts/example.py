from solar_mapper.dataset.sentinel_2 import get_training_example
from solar_mapper.dataset.utils import get_global_pv_mapping_polygons
import datetime
import os
import fsspec

# Get the polygons to use
polygons = get_global_pv_mapping_polygons()
# Generate random examples with the train polygons up to 2018
train_example = get_training_example(polygons["train"], start_time=datetime.datetime(2016, 1, 1),end_time=datetime.datetime(2018, 1, 1),search_delta=datetime.timedelta(days=90),num_samples=8)
print(train_example)
