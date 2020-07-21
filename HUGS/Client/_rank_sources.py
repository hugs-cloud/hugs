__all__ = ["RankSources"]

import copy
from Acquire.Client import Wallet


class RankSources:
    """
    This class is used to select the primary datasources for species from different sites
    """
    def __init__(self, service_url=None):

        wallet = Wallet()
        self._service = wallet.get_service(service_url=f"{service_url}/hugs")

        self._before_ranking = {}

    def get_sources(self, site, species):
        """ Get the datasources for this site and species to allow a ranking to be set

            Args:
                site (str): Three letter site code
                species (str): Species name
            Returns:
                dict: Dictionary of datasource metadata
        """
        from HUGS.Util import valid_site

        if self._service is None:
            raise PermissionError("Cannot use a null service")

        # Check the site code here? Raise an error if it's not recognized
        if len(site) != 3 or not valid_site(site):
            # raise InvalidSiteError(f"{site} is not a valid site code")
            raise ValueError(f"{site} is not a valid site code")

        args = {"site": site, "species": species}

        response = self._service.call_function(function="get_sources", args=args)

        self._before_ranking = copy.deepcopy(response)

        return response

    def rank_sources(self, updated_ranking):
        """ Assign the precendence of sources for each

            Args:
                updated_ranking (dict): Dictionary of ranking
            Returns:
                None
        """
        if updated_ranking == self._before_ranking:
            raise TypeError("Ranking must be updated")

        args = {"ranking": updated_ranking}

        response = self._service.call_function(function="rank_sources", args=args)

        return response

    def create_daterange(self, start, end):
        """ Create a JSON serialisable daterange string for use in ranking dict

            Args:
                start (datetime): Start of daterange
                end (datetime): End of daterange
            Returns:
                str: Serialisable daterange string
        """
        from Acquire.ObjectStore import datetime_to_string

        return "".join([datetime_to_string(start), "_", datetime_to_string(end)])
