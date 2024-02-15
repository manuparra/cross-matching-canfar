from abc import ABC

from pyvo.dal import conesearch


class Catalogue(ABC):
    SCS_URL = None
    _RA_COLUMN = 'RA'
    _DEC_COLUMN = 'DEC'
    _ERR_RA_COLUMN = 'e_RA'
    _ERR_DEC_COLUMN = 'e_DEC'
    """ A catalogue. """
    def _parse_scs_query_results(self, results):
        """ Parse SCS query results.

        :param pyvo.dal.scs.SCSResults results: The SCS query results.
        :return astropy.table.table.Table: An astropy table of results.
        """
        table = results.to_table()
        table.meta['name'] = self.__class__.__name__
        return table

    def scs_query(self, ra, dec, radius):
        """ Query a VO SCS service for a catalogue.

        :param int ra: Right ascension (deg)
        :param int dec: Declination (deg)
        :param int radius: Cone radius.
        """
        results = conesearch(self.SCS_URL, pos=(ra, dec), radius=radius)
        return self._parse_scs_query_results(results)

    @property
    def DEC_COLUMN(self):
        return self._DEC_COLUMN

    @property
    def ERR_DEC_COLUMN(self):
        return self._ERR_DEC_COLUMN

    @property
    def ERR_RA_COLUMN(self):
        return self._ERR_RA_COLUMN

    @property
    def RA_COLUMN(self):
        return self._RA_COLUMN


class Catalogue2MASS(Catalogue):
    """ 2MASS Catalogue. """
    SCS_URL = "https://dc.zah.uni-heidelberg.de/2mass/res/2mass/q/scs.xml"
    _RA_COLUMN = 'RAJ2000'
    _DEC_COLUMN = 'DEJ2000'
    _ERR_RA_COLUMN = None
    _ERR_DEC_COLUMN = None


class CatalogueGAIADR3(Catalogue):
    """ Gaia DR3 Catalogue. """
    SCS_URL = "https://dc.zah.uni-heidelberg.de/gaia/q3/cone/scs.xml"
    _RA_COLUMN = 'ra'
    _DEC_COLUMN = 'dec'
    _ERR_RA_COLUMN = 'ra_error'
    _ERR_DEC_COLUMN = 'dec_error'


class CatalogueLOTSSDR2(Catalogue):
    """ LOTSS DR2 Catalogue. """
    SCS_URL = "https://vo.astron.nl/lotss_dr2/q/src_cone/scs.xml"
    _ERR_RA_COLUMN = 'E_RA'
    _ERR_DEC_COLUMN = 'E_DEC'
    #_RA_COLUMN = 'RA'
    #_DEC_COLUMN = 'DEC'

class CatalogueTGSSADR(Catalogue):
    """ TGSS ADR Catalogue. """
    SCS_URL = "https://vo.astron.nl/tgssadr/q/cone/scs.xml"
