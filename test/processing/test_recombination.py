# import datetime
# import os
# import pandas as pd
# import pytest
# import xarray

# from HUGS.Modules import Instrument, CRDS, Datasource
# from HUGS.ObjectStore import get_object, get_local_bucket
# from HUGS.Processing import get_datasources, parse_gases, combine_sections, search_store

# @pytest.fixture(scope="session")
# def keylist():
#     filename = "bsd.picarro.1minute.248m.dat"
#     dir_path = os.path.dirname(__file__)
#     test_data = "../data/proc_test_data/CRDS"
#     filepath = os.path.join(dir_path, test_data, filename)

#     crds = CRDS.read_file(filepath)
#     # Get the keylist
#     bucket = get_local_bucket()
#     # Create and store data
#     crds.save(bucket=bucket)

#     start = datetime.datetime.strptime("2014-01-30", "%Y-%m-%d")
#     end = datetime.datetime.strptime("2014-01-31", "%Y-%m-%d")

#     keys = search_store(bucket=bucket, root_path="datasource", start_datetime=start, end_datetime=end)

#     return keys

# # def test_get_datasources(keylist):
# #     bucket = get_local_bucket()

# #     datasources = _recombination.get_sections(bucket, keylist)

# #     gas_names = ["co", "co2", "ch4"]
# #     recorded_gas_names = [datasources[0]._name, datasources[1]._name, datasources[2]._name]

# #     assert sorted(gas_names) == sorted(recorded_gas_names)
# #     assert len(datasources) == 3


# def test_combine_sections():
#     bucket = get_local_bucket(empty=True)

#     filename = "bsd.picarro.1minute.248m.dat"
#     dir_path = os.path.dirname(__file__)
#     test_data = "../data/proc_test_data/CRDS"
#     filepath = os.path.join(dir_path, test_data, filename)

#     # Split and combine without passing through the object store
#     raw_data = pd.read_csv(filepath, header=None, skiprows=1, sep=r"\s+")

#     # raw_data = raw_data.dropna(axis=0, how="any")
#     # raw_data.index = pd.RangeIndex(raw_data.index.size)
#     # datasource_ids, dataframes = parse_gases(raw_data)

#     gas_data = parse_gases(raw_data)

#     _, _, dataframes = zip(*gas_data)
#     complete = combine_sections(dataframes)

#     # Load in from object store
#     crds = CRDS.read_file(filepath)

#     # Get the instrument
#     instrument_uuids = list(crds._instruments)

#     # Get UUID from Instrument
#     instrument =  Instrument.load(bucket=bucket, uuid=instrument_uuids[0])

#     # Get Datasource IDs from Instrument
#     uuid_list = [d._uuid for d in instrument._datasources]
#     datasources = get_datasources(bucket, uuid_list)
#     combined = combine_sections(dataframes)

#     assert combined.equals(complete)


# # def test_convert_to_netcdf(): 
# #     filename = "bsd.picarro.1minute.248m.dat"
# #     dir_path = os.path.dirname(__file__)
# #     test_data = "../data/proc_test_data/CRDS"
# #     filepath = os.path.join(dir_path, test_data, filename)

# #     raw_data = pd.read_csv(filepath, header=None, skiprows=1, sep=r"\s+")
# #     gas_data = parse_gases(raw_data)
# #     dataframes = [data for _, data in gas_data]
# #     complete = combine_sections(dataframes)

# #     filename = _recombination.convert_to_netcdf(complete)

# #     # Open the NetCDF and check it's valid?
# #     x_dataset = complete.to_xarray()

# #     ds = xarray.open_dataset(filename)

# #     os.remove(filename)

# #     assert ds.equals(x_dataset)
    




