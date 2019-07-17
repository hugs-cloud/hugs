import datetime
import os
import pytest
import uuid
import pandas as pd

from Acquire.ObjectStore import ObjectStore
from Acquire.ObjectStore import string_to_encoded

from HUGS.ObjectStore import get_dated_object
from HUGS.ObjectStore import get_dated_object_json
from HUGS.Modules import Datasource
from HUGS.ObjectStore import get_local_bucket

mocked_uuid = "00000000-0000-0000-00000-000000000000"

mocked_uuid2 = "10000000-0000-0000-00000-000000000001"

@pytest.fixture(scope="session")
def data():
    filename = "bsd.picarro.1minute.248m.dat"
    dir_path = os.path.dirname(__file__)
    test_data = "../data/proc_test_data/CRDS"
    filepath = os.path.join(dir_path, test_data, filename)

    return pd.read_csv(filepath, header=None, skiprows=1, sep=r"\s+")

@pytest.fixture
def datasource():
    return Datasource.create(name="test_name", instrument="test_instrument",
                                site="test_site", network="test_network")

@pytest.fixture
def mock_uuid(monkeypatch):

    def mock_uuid():
        return mocked_uuid

    monkeypatch.setattr(uuid, 'uuid4', mock_uuid)


@pytest.fixture
def mock_uuid2(monkeypatch):

    def mock_uuid():
        return mocked_uuid2

    monkeypatch.setattr(uuid, 'uuid4', mock_uuid)


# @pytest.fixture(scope="session")
# def save_data_in_store(mock_uuid):
#     bucket = local_bucket.get_local_bucket()
#     datasource = get_datasources(raw_data=data)[0]
#     original_slice = datasource._data.head(1)

#     # data = Datasource.create(name="test_name", instrument="test_instrument", site="test_site",
#     #                          network="test_network", data=datasource._data)
#     # data.save(bucket)

#     print("Save data in store uuid : ", datasource._uuid)

#     datasource.save(bucket)

def test_save(mock_uuid2):
    bucket = get_local_bucket()

    datasource = Datasource.create(name="test_name", instrument="test_instrument", site="test_site", network="test_network")

    datasource.save(bucket)

    prefix = "%s/uuid/%s" % (Datasource._datasource_root, datasource._uuid)

    objs = ObjectStore.get_all_object_names(bucket, prefix)

    assert objs[0].split("/")[-1] == mocked_uuid2


def test_creation(mock_uuid, datasource):
    assert datasource._uuid == mocked_uuid
    assert datasource._name == "test_name"
    # assert datasource._instrument == "test_instrument"
    # assert datasource._site == "test_site"
    # assert datasource._network == "test_network"


def test_to_data(mock_uuid, datasource):
    data = datasource.to_data()

    assert data["UUID"] == mocked_uuid
    assert data["name"] == "test_name"
    # assert data["instrument"] == "test_instrument"
    # assert data["site"] == "test_site"
    # assert data["network"] == "test_network"

def test_from_data(mock_uuid):
    
    datasource = Datasource.create(name="test_name_two", instrument="test_instrument_two",
                                              site="test_site_two", network="test_network_two")

    bucket = get_local_bucket()

    data = datasource.to_data()
    new_datasource = Datasource.from_data(bucket=bucket, data=datasource.to_data(), shallow=False)

    assert new_datasource._name == "test_name_two"
    assert new_datasource._uuid == mocked_uuid

    assert new_datasource._labels["instrument"] == "test_instrument_two"
    assert new_datasource._labels["site"] == "test_site_two"
    assert new_datasource._labels["network"] == "test_network_two"




    
