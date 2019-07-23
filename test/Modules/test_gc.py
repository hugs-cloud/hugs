# Testing the GC class
import datetime
import pytest
import pandas as pd
import os
import uuid

from Acquire.ObjectStore import datetime_to_string, string_to_datetime, datetime_to_datetime
from HUGS.Modules import GC
from HUGS.Processing import read_metadata
from HUGS.ObjectStore import get_local_bucket
from HUGS.ObjectStore import get_object_names
from HUGS.Util import get_datetime_epoch

@pytest.fixture(scope="session")
def data_path():
    return os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "../data/proc_test_data/GC/capegrim-medusa.18.C"

@pytest.fixture(scope="session")
def precision_path():
    return os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "../data/proc_test_data/GC/capegrim-medusa.18.precisions.C"

@pytest.fixture
def gc():
    gc = GC.create()
    gas_data = gc.read_data(data_filepath=data_path, precision_filepath=precision_path, site=site, instrument=instrument)

gc_fixed_uuid = GC._gc_uuid

@pytest.fixture
def mock_uuid(monkeypatch):
    def mock_uuid():
        return gc_fixed_uuid

    monkeypatch.setattr(uuid, 'uuid4', mock_uuid)

@pytest.fixture
def gc(mock_uuid):
    gc = GC.create()
    gc._uuid = "123"
    gc._creation_datetime = datetime_to_datetime(datetime.datetime(1970,1,1))
    return gc

def test_read_data(data_path, precision_path):
    # Capegrim
    site = "CGO"
    instrument = "GCMD"

    gc = GC.create()
    gas_data, species, metadata = gc.read_data(data_filepath=data_path, precision_filepath=precision_path, site=site, instrument=instrument)

    head_data = gas_data.head(1)
    tail_data = gas_data.tail(1)

    assert head_data.first_valid_index() == pd.Timestamp("2018-01-01 00:23:22.500")
    assert head_data["propane repeatability"].iloc[0] == 0.22325
    assert head_data["c-propane repeatability"].iloc[0] == 0.10063

    assert tail_data.first_valid_index() == pd.Timestamp("2018-01-31 23:42:22.500")
    assert tail_data["propane repeatability"].iloc[0] == 0.16027
    assert tail_data["c-propane repeatability"].iloc[0] == 0.06071

    assert species[:8] == ['NF3', 'CF4', 'PFC-116', 'PFC-218', 'PFC-318', 'C4F10', 'C6F14', 'SF6'] 

    assert metadata["site"] == "capegrim"
    assert metadata["instrument"] == "medusa"


def test_read_precision(precision_path):
    gc = GC.create()

    precision, precision_series = gc.read_precision(precision_path)

    prec_test = ['NF3', 'CF4', 'PFC-116', 'PFC-218', 'PFC-318', 'C4F10', 'C6F14', 'SF6']
    end_prec_test = ['ethene', 'ethane', 'propane', 'c-propane', 'benzene', 'toluene', 'COS', 'desflurane']

    assert precision_series[:8] == prec_test
    assert precision_series[-8:] == end_prec_test

    precision_head = precision.head(1)
    
    assert precision_head.iloc[0,0] == 0.02531
    assert precision_head.iloc[0,2] == 0.08338
    assert precision_head.iloc[0,5] == 10
    assert precision_head.iloc[0,7] == 10
    assert precision_head.iloc[0,10] == 0.00565
    
def test_split(data_path, precision_path):
    # Capegrim
    site = "CGO"
    instrument = "GCMD"

    gc = GC.create()
    data, species, metadata = gc.read_data(data_filepath=data_path, precision_filepath=precision_path, site=site, instrument=instrument)
    metadata = read_metadata(filename=data_path, data=None, data_type="GC")
    gas_data = gc.split(data=data, site=site, species=species, metadata=metadata)

    assert gas_data[0][0] == "NF3"
    assert gas_data[0][1] == {'inlet': '75m_4', 'instrument': 'medusa', 'site': 'capegrim', 'species': 'NF3'}
    
    head_data = gas_data[0][3].head(1)
    assert head_data["NF3"].iloc[0] == pytest.approx(1.603)
    assert head_data["NF3 repeatability"].iloc[0] == pytest.approx(0.02531)
    assert head_data["NF3 status_flag"].iloc[0] == 0
    assert head_data["NF3 integration_flag"].iloc[0] == 0
    assert head_data["Inlet"].iloc[0] == "75m_4"


def test_to_data(gc):
    data = gc.to_data()

    assert data["stored"] == False
    assert data["creation_datetime"] == datetime_to_string(datetime.datetime(1970,1,1))


def test_from_data(gc):
    data = gc.to_data()

    gc_new = GC.from_data(data)

    assert gc_new._stored == False
    assert gc_new._creation_datetime == datetime_to_datetime(datetime.datetime(1970,1,1))


def test_save(gc):
    gc.save()

    bucket = get_local_bucket()
    prefix = "%s/uuid/%s" % (GC._gc_root, GC._gc_uuid)
    objs = get_object_names(bucket, prefix)

    assert objs[0].split("/")[-1] == GC._gc_uuid


def test_load(gc):
    gc.save()
    gc_new = GC.load()

    assert gc_new._stored == False
    assert gc_new._creation_datetime == datetime_to_datetime(datetime.datetime(1970,1,1))

def test_exists(gc):
    bucket = get_local_bucket()
    gc.save(bucket=bucket)

    assert GC.exists(bucket=bucket) == True