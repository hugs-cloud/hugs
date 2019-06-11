""" Describes a single instrument at a site
    An instrument contains DataSources

    DataSources could also be called sensors

"""

__all__ = ["Instrument"]


class Instrument:
    """ This class holds information regarding an instrument.
        An instrument may be a set of Datasources or a single
        Datasource at a Site.

        Instrument instances should be created with the
        Instrument.create() function

    """
    _instrument_root = "instruments"

    def __init__(self):
        """ This only creates a null Instrument
            Create should be used to create Instrument objects
        """
        self._uuid = None
        self._name = None
        self._creation_datetime = None
        self._labels = None
        # self._height = None
        # self._site = None
        # self._network = None
        self._datasources = []
        self._datasources_metadata = {}
    
    @staticmethod
    def create(name, **kwargs):
        """ Creates an Instrument object

            Args:
                name (str): Name of instrument
                site (str): Site at which instrument is based
                network (str): Network site associated with
            Returns:
                Instrument: Instrument object
        """
        from Acquire.ObjectStore import create_uuid as _create_uuid
        from Acquire.ObjectStore import get_datetime_now as _get_datetime_now


        i = Instrument()
        i._uuid = _create_uuid()
        i._creation_datetime = _get_datetime_now()
        i._name = name
        # Save the passed keywords as 
        i._labels = kwargs
        
        # To hold UIDs of all DataSources associated with this Instrument
        i._datasources = {}

        return i

    def is_null(self):
        """ Check if this is a null Instrument

            Returns:
                bool: True if null
        """
        return self._uuid is None

    def to_data(self):
        """ Creates a JSON serialisable dictionary to store this object
            in the object store

            Returns:
                dict: Dictionary created from this object
        """
        from Acquire.ObjectStore import datetime_to_string as _datetime_to_string

        d = {}
        d["UUID"] = self._uuid
        d["name"] = self._name
        d["creation_datetime"] = _datetime_to_string(self._creation_datetime)
        d["labels"] = self._labels

        return d

    @staticmethod
    def from_data(data):
        """ Creates an Instrument object from a JSON file

            Args:
                data (dict): JSON data from which to create object
            Returns:
                Instrument: Instrument object from data
        """
        if data is None or len(data) == 0:
            return Instrument()

        from Acquire.ObjectStore import string_to_datetime as _string_to_datetime

        i = Instrument()
        i._uuid = data["UUID"]
        i._name = data["name"]
        i._creation_datetime = _string_to_datetime(data["creation_datetime"])
        i._labels = data["labels"]

        return i

    def save(self, bucket=None):
        """ Save this Instrument as a JSON object on the object store
    
            This function also saves the name and UID of the Instrument
            to the object store with a key

            {instrument_root}/name/{instrument_name}/{instrument_uid}
            
            Args:
                bucket (dict): Bucket to hold data
            Returns:
                None
        """
        if self.is_null():
            return
        
        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from Acquire.ObjectStore import string_to_encoded as _string_to_encoded
        from objectstore._hugs_objstore import get_bucket as _get_bucket

        if bucket is None:
            bucket = _get_bucket()

        instrument_key = "%s/uuid/%s" % (Instrument._instrument_root, self._uuid)
        _ObjectStore.set_object_from_json(bucket=bucket, key=instrument_key, data=self.to_data())

        encoded_name = _string_to_encoded(self._name)
        string_key = "%s/name/%s/%s" % (Instrument._instrument_root, encoded_name, self._uuid)
        _ObjectStore.set_string_object(bucket=bucket, key=string_key, string_data=self._uuid)

    @staticmethod
    def load(bucket=None, uuid=None, name=None):
        """ Load an Instrument from the object store either by name or UUID

            uuid or name must be passed to the function

            Args:
                bucket (dict, default=None): Bucket to hold data
                uuid (str, default=None): UUID of Instrument
                name (str, default=None): Name of Instrument
            Returns:
                Instrument: Instrument object
        """
        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from objectstore._hugs_objstore import get_bucket as _get_bucket

        if uuid is None and name is None:
            raise ValueError("Both uuid and name cannot be None")

        if bucket is None:
            bucket = _get_bucket()
        if uuid is None:
            uuid = Instrument._get_uid_from_name(bucket=bucket, name=name)

        key = "%s/uuid/%s" % (Instrument._instrument_root, uuid)
        data = _ObjectStore.get_object_from_json(bucket=bucket, key=key)

        return Instrument.from_data(data)

    # Need the DataSources associated with this Instrument
    def get_datasources(self):
        """ Returns a JSON serialisable dictionary of the DataSources
            associated with this Instrument

            Returns:
                dict: Dictionary of DataSources and related information
        """        
        return self._datasources
        
    @staticmethod
    def _get_uid_from_name(bucket, name):
        """ Gets the UID of an instrument from its name

            Args:
                bucket (dict): Bucket holding data
                name (str): Name of Instrument
            Returns:
                str: UID of Instrument
        """
        from Acquire.ObjectStore import ObjectStore as _ObjectStore
        from Acquire.ObjectStore import string_to_encoded as _string_to_encoded

        encoded_name = _string_to_encoded(name)

        prefix = "%s/name/%s" % (Instrument._instrument_root, encoded_name)

        uuid = _ObjectStore.get_all_object_names(bucket=bucket, prefix=prefix)

        if(len(uuid) > 1):
            raise ValueError("There should only be one instrument with this name")

        return uuid[0].split("/")[-1]

    # def create_datasource(self, name):
    #     """ Creates a DataSource object and adds its information to the list of
    #         DataSources. Instrument, site and network data is taken from this
    #         Instrument instance.

    #         Args:
    #             name (str): Name for DataSource
    #     """
    #     from modules._datasource import Datasource

    #     datasource = DataSource.create(name=name, instrument=self._name, 
    #                                     site=self._site, network=self._network)

    #     self._datasources[datasource._uuid] = {"name": name, "created": datasource._creation_datetime}

    #     return datasource

    def add_datasource(self, datasource):
        """ Add a Datasource to this Instrument

            Args:
                datsource (Datasource): Datasource object to add
            Returns:
                None
        """
        datasource_dict = {}
        
        # TODO - how to properly get the gas name?
        datasource_dict["gas_type"] = datasource._name
        datasource_dict["date_range"] = datasource._labels[datasource.get_daterange()]
        datasource_dict["gas_type"] = datasource._labels["gas_type"]
        # More datas?

        self._datasources_metadata[datasource._uuid] = datasource_dict
        self._datasources.append(datasource)


    def get_datasources(self, raw_data):
        """ Create or get an exisiting Datasource for each gas in the file

            TODO - currently this function will only take data from a single Datasource
            
            Args:
                raw_data (list): List of Pandas.Dataframes
            Returns:
                Datasource: Datasource containing data
        """
        from modules import Datasource as _Datasource

        # Where gas_data is a list of tuples
        gas_data = parse_gases(raw_data)

        datasources = []

        for gas_name, datasource_id, data in gas_data:
            if _Datasource.exists(datasource_id=datasource_id):
                datasource = _Datasource.load(uuid=datasource_id)
            else:
                datasource = _Datasource.create(name=gas_name)

            # Add the dataframes to the datasource
            for dataframe in data:
                datasource.add_data(dataframe)

            datasources.append(datasource)

        return datasources


    def search_labels(self, search_term):
            """ Search the labels of this Instruemnt

                WIP

            """
            return False

    def add_label(self, key, value):
        """ Add a label to the labels dictionary.

            Note: this may overwrite existing data

            Args:
                key (str): Key for label
                value (str): Value for label
            Returns:
                None
        """
        self._labels[key] = value





        






        










        
