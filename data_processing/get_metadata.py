import pandas as pd
import uuid
import datetime

# def get_metadata(data_file):

def unanimous(seq):
    """ Checks that all values in an iterable object
        are the same

        Args:
            seq: Iterable object
        Returns
            bool: True if all values are the same

    """
    it = iter(seq.values())
    try:
        first = next(it)
    except StopIteration:
        return True
    else:
        return all(i == first for i in it)


def parse_date_time(date, time):
    """ This function takes two strings and creates a datetime object 
        
        Args:
            date (str): The date in a YYMMDD format
            time (str): The time in the format hhmmss
            Example: 104930 for 10:49:30
        Returns:
            datetime: Datetime object

    """
    if len(date) != 6:
        raise ValueError("Incorrect date format, should be YYMMDD")
    if len(time) != 6:
        raise ValueError("Incorrect time format, should be hhmmss")

    combined = date + time

    return datetime.datetime.strptime(combined, "%y%m%d%H%M%S")

def get_date_range(start, end):
    """ Takes two tuples and gets a datetime for both

        Args:
            start (tuple (str,str)): Start date and time
            end (tuple (str,str)): End date and time
        Returns:
            tuple (datetime, datetime): Start and end 
            datetime objects

    """
    start_datetime = parse_date_time(*start)
    end_datetime = parse_date_time(*end)

    return start_datetime, end_datetime


def calc_time_delta(start, end):
    """ Calculates the time delta between the first and last
        reading

        Unsure if this is needed
    
        Args:
            start (datetime): First measurement
            end (datetime): Last measurement
        Returns:
            timedelta: Timedelta            
    """

    return False


def parse_filename(filename):
    """ Extracts the resolution from the passed string

        Args:
            resolution_str (str): Resolution extracted from the filename
        Returns:
            tuple (str, str, str, str): Site, instrument, resolution
            and height (m)

    """
    # Split the filename to get the site and resolution
    split_filename = filename.split(".")

    site = split_filename[0]
    instrument = split_filename[1]
    resolution_str = split_filename[2]
    height = split_filename[3]

    if(resolution_str == "1minute"):
        resolution = "1m"
    elif(resolution_str == "hourly"):
        resolution = "1h"
    
    return site, instrument, resolution, height


def find_gases(data):
    """ Find the gases measured in the dataframe
    
        Args:
            data (Pandas.DataFrame): Measurement data
        Returns:
            list: List containing measured gases

    """
    # Slice the dataframe
    head_row = data.head(1)

    gases = {}
    # Take the first row of the DataFrame
    gas_row = 0
    # Loop over the gases and find each unique value
    for column in head_row.columns:
        s = head_row[column][gas_row]
        if s != "-":
            gases[s] = gases.get(s, 0) + 1

    # Check that we have the same number of columns for each gas
    if not unanimous(gases):
        raise ValueError(
            "Each gas does not have the same number reading of columns")

    n_cols = list(gases.values())[0]

    return n_cols, list(gases.keys())

    

def parse_metadata(filename, data):
    """ Extracts the metadata from the datafile and creates a dictionary
        that can then be saved to JSON

        Args:
            filename (str): Filename for parsing
            dataframe (Pandas.DataFrame): Dataframe containing the
            experinmental data
        Returns:
            dict: Dictionary containing metadata
    """
    # Dict for storage of metadata
    metadata = {}

    # Not a huge fan of these hardcoded values
    # TODO - will these change at some point?
    start_date = data[0][2]
    start_time = data[1][2]
    end_date = data.iloc[-1][0]
    end_time = data.iloc[-1][1]

    start_data = start_date, start_time
    end_data = end_date, end_time

    # Find gas measured and port used
    type_meas = data[2][2]
    port = data[3][2]

    # Start and end datetime objects
    start, end = get_date_range(start=start_data, end=end_data)

    # Extract data from the filename
    site, instrument, resolution, height = parse_filename(filename=filename)

    # Parse the dataframe to find the gases - this might be excessive
    gases = find_gases(data)

    metadata["site"] = site
    metadata["instrument"] =
    metadata["resolution"] = resolution
    metadata["height"] = height
    metadata["start_datetime"] = start
    metadata["end_datetime"] = end
    metadata["port"] = port
    metadata["type"] = type_meas
    metadata["gases"] = gases
    
    return metadata


def get_uuid():
    """ Returns a random UUID

        Returns:
            str: Random UUID
    """
    return uuid.uuid4()


def parse_file(filename):
    """ This function controls the parsing of the datafile. It calls
        other functions that help to break the datafile apart and
        
        Args:
            filename (str): Name of file to parse

        Returns:
            list: List 
    """

    # Read everything
    data = pd.read_csv(filename, header=None, skiprows=1, sep=r"\s+")

    header = data.head(2)

    metadata = parse_metadata(filename, data)
    
    # Now split the datafile into separate gases

    # Number of columns before the get to the measurement data
    skip_cols = sum([header[column][0] == "-" for column in header.columns])
    # Expect 3 columns for each gas
    gas_width = 3

    

    # Make dataframes for each gas
    gas1 = data.iloc[:, skip_cols: skip_cols + gas_width]
    gas2 = data.iloc[:, skip_cols + gas_width: skip_cols + 2*gas_width]
    gas3 = data.iloc[:, skip_cols + 2*gas_width: skip_cols + 3*gas_width]

    # Package each gas
    for gas in gases:
        


    # UUIDS for
    # Daterange
    # Each gas
    # Site
    # 
    
    # UUIDs for these pieces of data
    # Package each into a dict with its own UUID and data
    # Is this sensible?

    # UUID
    # Data description - hwo to automate this?
    # data





    



    


    

parse_file()

# def get_metadata(metadata_frame, daterange):
#     """ This function takes a Pandas dataframe containing the raw meta data

#     """

    # Work through the gases and add them to a set ?

    # info_columns = 0
    # # Count the number of columns we can skip
    # for column in metadata.columns:
    #     if metadata[column][0] == "-":
    #         info_columns += 1

        


    # # Iterate through the columns and read the data
    # for column in metadata.columns:
    #     if metadata[column][0] == "-":
            





    # No need to reinterpret the header string
    # Create header list

    # Meta data
    # --------------------
    # File creation date - is this necessary? Can it harm?
    # daterange in file
    # Type and port?
    # Take the 3 gases from the file and create an xarray from them?
    # Store the metadata as JSON?
    # Make a dict of the header file

    # Either have the data for each gas containing the daterange as well or
    # 

    # site
    # daterange
    # resolution - 1 minute etc accuracy - not this! better word
    # height - 248m etc
    # gases - subkeys 

    # Store the data separately
    # Use the metadata to read the data file that's associated by UID to it

    # Create UIDs
    # store these in some kind of database? 


    # Query the gases in the file

    # Gas data
    # Each gas gets its own UID
    # Within one piece of data take c, stdev and count number
    # This will contain the 
    
    # for i in df_header.columns:
    #     # Here i is an integer starting at 1
    #     # Ignore the metadata - 
    #     if df_header[i][0] != '-':
    #         metadata.append(df_header[i][0].upper() + df_header[i][1])

    #         # This takes in the readings 
    #         if df_header[i][1] == "C":
    #             species.append(df_header[i][0].upper())
    #     else:
    #         header.append(df_header[i][1].upper())

