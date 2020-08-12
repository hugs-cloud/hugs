__all__ = ["read_metadata"]


def read_metadata(filepath, data, data_type):
    """ Process the metadata and create a JSON serialisable
            dictionary for saving to object store

            Args:
                filepath (pathlib.Path): Filename to process
                data (Pandas.DataFrame): Raw data
                data_type (str): Data typw (CRDS, GC etc) to parse
            Returns:
                dict: Dictionary of metadata
        """
    from HUGS.Processing import DataTypes

    filename = filepath.name

    data_type = DataTypes[data_type.upper()].name

    if data_type == "CRDS":
        metadata = _parse_CRDS(filename=filename, data=data)
    elif data_type == "GC":
        metadata = _parse_GC(filename=filename, data=data)

    return metadata


def _parse_CRDS(filename, data):
    """ Parse CRDS files and create a metadata dict

            Args:
                filename (str): Name of data file
                data (Pandas.DataFrame): Raw data
            Returns:
                dict: Dictionary containing metadata
        """
    # Find gas measured and port used
    type_meas = data[2][2]
    port = data[3][2]

    # Split the filename to get the site and resolution
    split_filename = filename.split(".")

    if len(split_filename) < 4:
        raise ValueError(
            "Error reading metadata from filename. The expected format is \
            {site}.{instrument}.{time resolution}.{height}.dat"
        )

    site = split_filename[0]
    instrument = split_filename[1]
    resolution_str = split_filename[2]
    inlet = split_filename[3]

    if resolution_str == "1minute":
        resolution = "1_minute"
    elif resolution_str == "hourly":
        resolution = "1_hour"
    else:
        resolution = "Not read"

    metadata = {}
    metadata["site"] = site
    metadata["instrument"] = instrument
    metadata["time_resolution"] = resolution
    metadata["inlet"] = inlet
    metadata["port"] = port
    metadata["type"] = type_meas

    return metadata


def _parse_GC(filename, data):
    """ Parse GC files and create a metadata dict

        Args:
            filename (str): Name of data file
            data (Pandas.DataFrame): Raw data
        Returns:
            dict: Dictionary containing metadata
    """
    split_filename = filename.split(".")
    # If we haven't been able to split the filename raise an error
    split_hyphen = split_filename[0].split("-")
    if len(split_hyphen) < 2:
        site = split_hyphen[0]
        instrument = "unknown"
    else:
        site = split_hyphen[0]
        instrument = split_hyphen[1]

    metadata = {}
    metadata["site"] = site
    metadata["instrument"] = instrument

    return metadata
