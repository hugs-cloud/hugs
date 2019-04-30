import pytest
import xarray
import os

from data_processing import process_crds as procCRDS

"""
This is a very limited test bench for the processing functions

TODO expand it with  more checks on the processing of the data
"""
test_path = os.path.dirname(__file__)

def test_read_datafile():
    # Test that a datafile is read in correctly and
    # produces a valid xarray.Dataset and a list of species

    folder = "data/proc_test_data/CRDS"
    filename = "bsd.picarro.1minute.248m.dat"

    file_path = os.path.join(test_path, folder, filename)
    test_dset, species = procCRDS.read_data_file(data_file=file_path)

    assert isinstance(test_dset, xarray.Dataset)
    assert isinstance(species, list)


def test_search_data_files():

    site = "BSD"
    folder = "data/proc_test_data/CRDS"
    folder_path = os.path.join(test_path, folder)
    search_string = ".*.1minute.*.dat"

    file_list = procCRDS.search_data_files(data_folder=folder_path, site=site,
                                            search_string=search_string)

    test_filename = "bsd.picarro.1minute.248m.dat"

    assert len(file_list) == 1
    assert isinstance(file_list, list)
    assert file_list[0].split("/")[-1] == test_filename


def test_find_inlets():

    site = "BSD"
    folder = "data/proc_test_data/CRDS"
    folder_path = os.path.join(test_path, folder)
    search_string = ".*.1minute.*.dat"

    file_list = procCRDS.search_data_files(data_folder=folder_path, site=site,
                                          search_string=search_string)

    inlets = procCRDS.find_inlets(file_list)
    
    test_inlet_type = "248m"

    assert inlets[0] == test_inlet_type


def test_load_from_JSON():

    test_file = "test.json"
    metadata_folder = "data/proc_test_data"

    folder_path = os.path.join(test_path, metadata_folder)
    
    test_dict = procCRDS.load_from_JSON(folder_path, test_file)

    assert test_dict["ACRONYM"]["directory"] == "test_dir"


def test_processing_data():
    
    site = "BSD"
    folder = "data/proc_test_data/CRDS"
    folder_path = os.path.join(test_path, folder)
    search_string = ".*.1minute.*.dat"

    file_list = procCRDS.search_data_files(data_folder=folder_path, site=site,
                                            search_string=search_string)
    inlets = procCRDS.find_inlets(file_list)

    species_data = procCRDS.process_data(data_files=file_list, inlets=inlets, site="BSD")

    assert isinstance(species_data[0], xarray.Dataset)