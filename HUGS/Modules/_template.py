
__all__ = ["Template"]

# TODO - look into what's causing the logging messages in the first place
# This does stop them

class Template:
    """ Interface for processnig Template data

        Instances of Template should be created using the
        CRDS.create() function
        
    """
    _crds_root = "TEMPLATE"
    # Use uuid.uuid4() to create a unique fixed UUID for this object
    _crds_uuid = "CHANGEME"

    def __init__(self):
        self._creation_datetime = None
        self._stored = False
        # Processed data
        self._proc_data = None
        # Datasource UUIDs
        self._datasources = []

    def is_null(self):
        """ Check if this is a null object

            Returns:
                bool: True if object is null
        """
        return self._datasources is None

    @staticmethod
    def create():
        """ This function should be used to create CRDS objects

            Returns:
                CRDS: CRDS object 
        """
        from Acquire.ObjectStore import get_datetime_now as _get_datetime_now

        c = CRDS()
        c._creation_datetime = _get_datetime_now()

        return c


    @staticmethod
    def read_folder(folder_path, recursive=False):
        """ Read all data matching filter in folder

            Args:
                folder_path (str): Path of folder
        """
        from glob import glob as _glob
        from os import path as _path
        from HUGS.Modules import CRDS as _CRDS

        # This finds data files in sub-folders
        folder_path = _path.join(folder_path, "./*.dat")
        # This finds files in the current folder, get recursive
        # folder_path = _path.join(folder_path, "*.dat")
        filepaths = _glob(folder_path, recursive=True)

        if len(filepaths) == 0:
            raise FileNotFoundError("No data files found")

        for fp in filepaths:
            Template.read_file(data_filepath=fp)


    @staticmethod
    def read_file(data_filepath):
        """ Creates a CRDS object holding data stored within Datasources

            TODO - currently only works with a single Datasource

            Args:
                filepath (str): Path of file to load
            Returns:
                None
        """
        from pandas import read_csv as _read_csv
        from Acquire.ObjectStore import datetime_to_string as _datetime_to_string
        from HUGS.Processing import create_datasources as _create_datasources

        # Load in the object from the object store
        # This can be replaced with Template.create for testing
        temp = Template.load()

        # Get the filename from the filepath
        filename = data_filepath.split("/")[-1]

        # This function should split the data into a format that
        # can be given to the Datasources. See the read_data function for this format
        gas_data = template.read_data(data_filepath=data_filepath)

        # Create Datasources, save them to the object store and get their UUIDs
        datasource_uuids = _create_datasources(gas_data)

        # Add the Datasources to the list of datasources associated with this object
        template.add_datasources(datasource_uuids)

        template.save()

        return template

    def read_data(self, data_filepath):
        """ Separates the gases stored in the dataframe in 
            separate dataframes and returns a dictionary of gases
            with an assigned UUID as gas:UUID and a list of the processed
            dataframes

            Args:
                data (Pandas.Dataframe): Dataframe containing all data
            Returns:
                tuple (str, str, list): Name of gas, ID of Datasource of this data and a list Pandas DataFrames for the 
                date-split gas data
        """
        from pandas import RangeIndex as _RangeIndex
        from pandas import concat as _concat
        from pandas import read_csv as _read_csv
        from pandas import datetime as _pd_datetime
        from pandas import NaT as _pd_NaT
        from uuid import uuid4 as _uuid4

        from HUGS.Processing import read_metadata

        # Create metadata here
        metadata = read_metadata(filename=data_filepath, data=data, data_type="CRDS")

        data_list = []
        for n in range(n_gases):
            # Create a copy of the metadata dict
            species_metadata = metadata.copy()
            species_metadata["species"] = species

            data_list.append((species, species_metadata, datasource_id, gas_data))

        return data_list

    def to_data(self):
        """ Return a JSON-serialisable dictionary of object
            for storage in object store

            Returns:
                dict: Dictionary version of object
        """
        from Acquire.ObjectStore import datetime_to_string as _datetime_to_string

        d = {}
        # These should be able to stay the same
        d["creation_datetime"] = _datetime_to_string(self._creation_datetime)
        d["stored"] = self._stored
        d["datasources"] = self._datasources
    
        return d

    @staticmethod
    def from_data(data, bucket=None):
        """ Create a CRDS object from data

            Args:
                data (str): JSON data
                bucket (dict, default=None): Bucket for data storage
            Returns:
                CRDS: CRDS object created from data
        """
        from Acquire.ObjectStore import string_to_datetime as _string_to_datetime
        from HUGS.ObjectStore import get_bucket as _get_bucket

        if data is None or len(data) == 0:
            return CRDS()

        if bucket is None:
            bucket = _get_bucket()
        
        c = CRDS()
        c._creation_datetime = _string_to_datetime(data["creation_datetime"])
        c._datasources = data["datasources"]
        c._stored = False

        return c

    def save(self, bucket=None):
        """ Save the object to the object store

            Args:
                bucket (dict, default=None): Bucket for data
            Returns:
                None
        """
        if self.is_null():
            return

        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from Acquire.ObjectStore import string_to_encoded as _string_to_encoded
        from HUGS.ObjectStore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        crds_key = "%s/uuid/%s" % (CRDS._crds_root, CRDS._crds_uuid)

        self._stored = True
        _ObjectStore.set_object_from_json(bucket=bucket, key=crds_key, data=self.to_data())

    @staticmethod
    def load(bucket=None):
        """ Load a CRDS object from the datastore using the passed
            bucket and UUID

            Args:
                uuid (str): UUID of CRDS object
                key (str, default=None): Key of object in object store
                bucket (dict, default=None): Bucket to store object
            Returns:
                Datasource: Datasource object created from JSON
        """
        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from HUGS.ObjectStore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        key = "%s/uuid/%s" % (CRDS._crds_root, CRDS._crds_uuid)
        data = _ObjectStore.get_object_from_json(bucket=bucket, key=key)

        return CRDS.from_data(data=data, bucket=bucket)

   @staticmethod
    def exists(bucket=None):
        """ Query the object store to check if a template object already exists

            Args:
                bucket (dict, default=None): Bucket for data storage
            Returns:
                bool: True if CRDS object exists in object store
        """
        from HUGS.ObjectStore import exists as _exists
        from HUGS.ObjectStore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        key = "%s/uuid/%s" % (CRDS._crds_root, CRDS._crds_uuid)

        return _exists(bucket=bucket, key=key)

    def add_datasources(self, datasource_uuids):
        """ Add the passed list of Datasources to the current list

            Args:
                datasource_uuids (list): List of Datasource UUIDs
            Returns:
                None
        """
        self._datasources.extend(datasource_uuids)

    def uuid(self):
        """ Return the UUID of this object

            Returns:
                str: UUID of  object
        """
        return CRDS._crds_uuid

    def datasources(self):
        """ Return the list of Datasources for this object

            Returns:
                list: List of Datasources
        """
        return self._datasources