""" This file contains functions used to ensure CEDA compliance

"""
__all__ = ["create_upload_file"]

def create_upload_file(filepath=None, site=None, instrument=None, height=None, write_yaml=False, date_range=None):
    """ Creates a JSON (with a yaml extension for CEDA reasons) object 
        for export for a CEDA upload

        Args:
            filepath (str or Path, default=None): Path for file output. If file not passed a 
            dictionary is returned
            site (str, default=None): Three letter site code (such as BSD for Bilsdale)
            instrument (str, default=None): Name of instrument
            height (str, default=None): Height of instrument
            write_yaml (bool, default=False): If True write to YAML, otherwise JSON file is written
            date_range (tuple, default=None): Start, end Python datetime objects
        Returns:
            dict or None: Dictionary if no filepath is given, otherwise None
    """
    import json
    import yaml
    from pathlib import Path
    from HUGS.Util import get_datapath

    if filepath:
        filepath = Path(filepath)

    compliance_file = "ceda_compliance.json"
    compliance_path = get_datapath(filename=compliance_file)

    # Load in JSON for storing data for CEDA compliance
    # JSON feels cleaner to work with/read here
    with open(compliance_path, "r") as f:
        ceda_comp = json.load(f)

    if not site:
        raise ValueError("Site must be given")

    site = site.upper()
    
    # Ensure height is in the format we want
    height = str(height).lower().replace(" ", "")
    if not height.endswith("m"):
        height = f"{height}m"

    site_title = ceda_comp[site]["title"]
    site_description = ceda_comp[site]["description"]
    site_instrument = ceda_comp[site]["instruments"][instrument]

    data = {}
    # Lookup the site data in ceda_compliance dictionary for site_description etc
    data["title"] = site_title
    # Get this from a YAML file that has each site saved
    data["description"] = site_description
    # Similarly load from YAML?yaml
    # Where site_authors is a dict containing authors
    data["authors"] = [{"firstname": "HUGS", "surname": "Cloud"},
                       {"firstname": "", "surname": ""},
                       {"firstname": "", "surname": ""}]

    # Here we'll have to add in the degree notation?
    data["bbox"] = {"north": ceda_comp[site]["latitude"], "south": "",
                    "east": "", "west": ceda_comp[site]["longitude"]}
    
    data["time_range"] = {"start": "2014-05-02 00:00:00",
                          "end": "2014-31-12 23:00:00"}

    # These can be loaded in from YAML / JSON
    data["lineage"] = ceda_comp[site]["lineage"]
    data["quality"] = ceda_comp[site]["quality"]

    data["docs"] = [{"title": site_title, "url": ceda_comp[site]["url"]}]

    data["project"] = {"catalogue_url": ceda_comp[site]["catalogue_url"], "title": site_title, "description": site_description,
                       "PI": {"firstname": "HUGS", "lastname": "Cloud"}, "funder": "NERC", "grant_number": "HUGS_Grant"}

    data["instrument"] = {"catalogue_url": site_instrument["catalogue_url"],
                          "title": site_instrument["title"],
                          "description": site_instrument["description"],
                          "height": height}

    # This is empty in the examples sent
    data["computation"] = {"catalogue_url": "",
                           "title": "",
                           "description": ""}

    if filepath:
        with open(filepath, "w") as f:
            if write_yaml:
                yaml.dump(data, stream=f, indent=4)
            else:
                json.dump(data, fp=f, indent=4)

        return None
    else:
        return data
