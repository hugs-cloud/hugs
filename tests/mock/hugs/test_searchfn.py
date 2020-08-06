import os
import pytest
from datetime import datetime

from Acquire.Client import Service

from HUGS.Client import Process, RankSources, Search


@pytest.fixture(scope="session")
def tempdir(tmpdir_factory):
    d = tmpdir_factory.mktemp("tmp_searchfn")
    return str(d)


@pytest.fixture(scope="session")
def load_crds(authenticated_user):
    hugs = Service(service_url="hugs")
    _ = hugs.call_function(function="clear_datasources", args={})

    def test_folder(filename):
        dir_path = os.path.dirname(__file__)
        test_folder = "../../../tests/data/search_data"
        return os.path.join(dir_path, test_folder, filename)

    files = [
        "bsd.picarro.1minute.108m.min.dat",
        "hfd.picarro.1minute.100m.min.dat",
        "tac.picarro.1minute.100m.min.dat",
    ]
    filepaths = [test_folder(f) for f in files]

    process = Process(service_url="hugs")

    process.process_files(
        user=authenticated_user,
        files=filepaths,
        data_type="CRDS",
        hugs_url="hugs",
        storage_url="storage",
    )

@pytest.fixture(scope="session")
def load_two_crds(authenticated_user):
    hugs = Service(service_url="hugs")
    _ = hugs.call_function(function="clear_datasources", args={})

    def test_folder(filename):
        dir_path = os.path.dirname(__file__)
        test_folder = "../../../tests/data/search_data"
        return os.path.join(dir_path, test_folder, filename)

    files = [
        "bsd.picarro5310.1minute.108m.min.dat",
        "bsd.picarro5310.1minute.248m.min.dat"
    ]

    filepaths = [test_folder(f) for f in files]

    process = Process(service_url="hugs")

    process.process_files(
        user=authenticated_user,
        files=filepaths,
        data_type="CRDS",
        hugs_url="hugs",
        storage_url="storage",
    )


def test_search_bsd(load_crds):
    search = Search(service_url="hugs")

    search_term = "co"
    location = "bsd"
    data_type = "CRDS"

    results = search.search(species=search_term, locations=location, data_type=data_type)

    bsd_res = results["co_bsd"]

    del bsd_res["metadata"]["source_name"]

    expected_metadata = {
        "site": "bsd",
        "instrument": "picarro",
        "time_resolution": "1_minute",
        "inlet": "108m",
        "height": "108m",
        "port": "9",
        "type": "air",
        "species": "co",
        "data_type": "timeseries",
    }

    assert bsd_res["metadata"] == expected_metadata


def test_search_and_rank(load_two_crds):
    # First we need to rank the data
    r = RankSources(service_url="hugs")
    sources = r.get_sources(site="bsd", species="co", data_type="CRDS")

    uuid_108m = sources['bsd_co_108m']["uuid"]
    uuid_248m = sources['bsd_co_248m']["uuid"]

    del sources['bsd_co_108m']["uuid"]
    del sources['bsd_co_248m']["uuid"]

    assert sources == {'bsd_co_108m': {'rank': 0, 'daterange': '2019-03-06T14:03:30_2020-07-04T11:44:30'}, 
                        'bsd_co_248m': {'rank': 0, 'daterange': '2019-03-06T13:23:30_2020-07-05T03:38:30'}}

    daterange_108 = r.create_daterange(start=datetime(2019, 3, 7), end=datetime(2019, 9, 15))
    daterange_248 = r.create_daterange(start=datetime(2019, 9, 16), end=datetime(2020, 7, 5))

    new_rankings = {'bsd_co_108m': {'rank': 1, 'daterange': daterange_108 , 'uuid': uuid_108m}, 
                    'bsd_co_248m': {'rank': 1, 'daterange': daterange_248, 'uuid': uuid_248m}}

    r.rank_sources(updated_rankings=new_rankings, data_type="CRDS")

    updated_sources = r.get_sources(site="bsd", species="co", data_type="CRDS")

    assert updated_sources["bsd_co_108m"]["rank"] == {'1': ['2019-03-07T00:00:00_2019-09-15T00:00:00']}
    assert updated_sources["bsd_co_248m"]["rank"] == {'1': ['2019-09-16T00:00:00_2020-07-05T00:00:00']}

    # Now we need to search for the data and ensure we get the correct datasets
    search = Search(service_url="hugs")

    species = "co"
    location = "bsd"
    data_type = "CRDS"

    results = search.search(species=species, locations=location, data_type=data_type)

    print("Search results: ", results)


def test_single_site_search(load_two_crds):
    search = Search(service_url="hugs")

    species = "co"
    location = "bsd"
    data_type = "CRDS"
    inlet = "108m"
    instrument = "picarro5310"

    results = search.search(species=species, locations=location, data_type=data_type, inlet=inlet, instrument=instrument)

    assert len(results["bsd_co_picarro5310_108m"]["keys"]) == 7
    assert results["bsd_co_picarro5310_108m"]["metadata"] == {'site': 'bsd', 'instrument': 'picarro5310', 'time_resolution': '1_minute', 
                                                                'inlet': '108m', 'port': '2', 'type': 'air', 'species': 'co', 
                                                                'data_type': 'timeseries'}


def test_search_multispecies_singlesite(load_crds):
    search = Search(service_url="hugs")

    search_term = ["co", "co2"]
    location = "bsd"
    data_type = "CRDS"

    results = search.search(
        species=search_term, locations=location, data_type=data_type
    )

    assert list(results.keys()) == ["bsd_co_108m", "bsd_co_108m"]

    assert len(results["bsd_co_108m"]["keys"]) == 23
    assert len(results["bsd_co_108m"]["keys"]) == 23


def test_search_multisite_co(load_crds):
    search = Search(service_url="hugs")

    search_term = "co"
    location = ["bsd", "hfd", "tac"]
    data_type = "CRDS"

    results = search.search(
        species=search_term, locations=location, data_type=data_type
    )

    assert list(results.keys()) == ["bsd_co_108m", "hfd_co_100m"]

    key_dates = sorted(results["hfd_co_100m"]["keys"])[:10]

    key_dates = [v.split("/")[-1] for v in key_dates]

    expected_dates = [
        "2013-11-20-20:02:30+00:00_2013-11-30-20:02:30+00:00",
        "2013-12-01-02:52:30+00:00_2013-12-31-22:54:30+00:00",
        "2014-01-01-02:01:30+00:00_2014-12-31-21:32:30+00:00",
        "2014-03-10-18:36:30+00:00_2014-05-31-23:58:30+00:00",
        "2014-06-01-03:05:30+00:00_2014-08-31-21:35:30+00:00",
        "2014-09-01-00:42:30+00:00_2014-11-30-21:38:30+00:00",
        "2015-01-01-00:42:30+00:00_2015-12-31-21:31:30+00:00",
        "2015-03-01-01:42:30+00:00_2015-05-31-22:00:30+00:00",
        "2015-06-01-01:10:30+00:00_2015-08-31-20:59:30+00:00",
        "2015-09-01-00:06:30+00:00_2015-11-30-22:06:30+00:00",
    ]

    assert key_dates == expected_dates


def test_search_multiplesite_multiplespecies(load_crds):
    search = Search(service_url="hugs")

    search_term = ["ch4", "co2"]
    location = ["bsd", "hfd", "tac"]
    data_type = "CRDS"

    results = search.search(
        species=search_term, locations=location, data_type=data_type
    )

    assert sorted(list(results.keys())) == [
        "bsd_ch4_108m",
        "bsd_co_108m",
        "hfd_ch4_100m",
        "hfd_co2_100m",
        "tac_ch4_100m",
        "tac_co2_100m",
    ]

    assert len(results["bsd_ch4_108m"]["keys"]) == 23
    assert len(results["hfd_ch4_100m"]["keys"]) == 25
    assert len(results["tac_ch4_100m"]["keys"]) == 30
    assert len(results["bsd_co_108m"]["keys"]) == 23
    assert len(results["hfd_co2_100m"]["keys"]) == 25
    assert len(results["tac_co2_100m"]["keys"]) == 30


def test_returns_readable_results():
    search = Search(service_url="hugs")

    search_term = ["ch4"]
    location = ["bsd"]

    search.search(species=search_term, locations=location, data_type="CRDS")

    assert search.results() == {'bsd_ch4_108m': 'Daterange : 2014-01-30-13:33:30+00:00 - 2019-07-04-04:23:30+00:00'}


def test_search_download():
    search = Search(service_url="hugs")

    search_term = ["ch4"]
    location = ["bsd"]

    search.search(species=search_term, locations=location, data_type="CRDS")

    data = search.download("bsd_ch4_108m")

    data_attributes = data["bsd_ch4_108m"].attrs
    assert data_attributes["data_owner"] == "Simon O'Doherty"
    assert data_attributes["station_longitude"] == pytest.approx(-1.15033)
    assert data_attributes["station_latitude"] == pytest.approx(54.35858)
    assert data_attributes["station_long_name"] == 'Bilsdale, UK'
    assert data["bsd_ch4_108m"]["ch4"][0] == pytest.approx(1960.25)
