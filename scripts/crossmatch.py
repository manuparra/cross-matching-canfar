import argparse

import pylab as plt
import seaborn as sns
from astropy import units
from astropy.coordinates import Angle, ICRS, match_coordinates_sky
from astropy.table import Table, hstack

from catalogue import Catalogue2MASS, CatalogueGAIADR3, CatalogueLOTSSDR2, CatalogueTGSSADR

SUPPORTED_CATALOGUES = {
    '2MASS': Catalogue2MASS,
    'GAIA_DR3': CatalogueGAIADR3,
    'LOTSS_DR2': CatalogueLOTSSDR2,
    'TGSS_ADR': CatalogueTGSSADR,
}


class Crossmatch:
    def __init__(self, ra, dec, radius, ref_catalogue, match_catalogues, max_separation):
        """
        :param float ra: Right ascension (deg)
        :param float dec: Declination (deg)
        :param float radius: Search radius (deg)
        :param Catalogue ref_catalogue: Reference catalogue
        :param list match_catalogues: List of Catalogue(s) to match against reference
        :param float max_separation: Maximum separation in deg
        """
        self.ra = ra
        self.dec = dec
        self.radius = radius
        self.ref_catalogue = ref_catalogue
        self.match_catalogues = match_catalogues
        self.max_separation = max_separation

    def plot(self, crossmatch_results):
        """ Plot the results of a crossmatch.

        :param astropy.table.table.Table crossmatch_results: Crossmatch results
        """
        crossmatch_results_pandas = crossmatch_results.to_pandas()

        palette = sns.color_palette("colorblind")

        # sky plot
        plt.figure(figsize=(10, 8))
        plt.subplot(211)
        plt.title("Sky plot")
        sns.scatterplot(data=crossmatch_results_pandas,
                        x="{}_RA".format(self.ref_catalogue),
                        y="{}_DEC".format(self.ref_catalogue),
                        marker='o', label='reference catalogue ({})'.format(self.ref_catalogue), alpha=0.3)
        for idx, catalogue in enumerate(self.match_catalogues):
            sns.scatterplot(data=crossmatch_results_pandas,
                            x="{}_RA".format(catalogue),
                            y="{}_DEC".format(catalogue),
                            marker='+', label='matched catalogue ({})'.format(catalogue), alpha=0.7)
        plt.xlabel("RA (deg)")
        plt.ylabel("DEC (deg)")
        plt.legend(loc='upper right')

        # histogram of separations
        palette.pop(0)  # remove the first colour in palette to match histogram labels
        sns.set_palette(palette)
        plt.subplot(212)
        plt.title("Histogram of separations")
        for catalogue_name, sep2d_column_name in [(name, '{}_sep2d'.format(name)) for name in self.match_catalogues]:
            sns.histplot(data=crossmatch_results_pandas*3600, x=sep2d_column_name, element="step", kde=True,
                         label=catalogue_name)
        plt.xlabel("Separation (arcsec)")
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.savefig("crossmatch_plot.png")
        plt.show()

    def run(self):
        """ Run crossmatching. """
        # create instances for both reference and match catalogues
        catalogues = [
            SUPPORTED_CATALOGUES.get(self.ref_catalogue)(),
            *[SUPPORTED_CATALOGUES.get(catalogue)() for catalogue in self.match_catalogues]
        ]
        
        # perform SCS query against catalogues
        catalogues_scs = []
        for catalogue in catalogues:
            catalogues_scs.append(Table(
                catalogue.scs_query(ra=self.ra, dec=self.dec, radius=self.radius)))

        # rename the ra and dec columns
        for catalogue, catalogue_scs in zip(catalogues, catalogues_scs):
            catalogue_scs.rename_columns((catalogue.RA_COLUMN, catalogue.DEC_COLUMN), ('RA', 'DEC'))

        # convert coordinates from SCS query results to ICRS coordinate system
        catalogues_scs_icrs = []
        for catalogue, catalogue_scs in zip(catalogues, catalogues_scs):
            catalogues_scs_icrs.append(ICRS(
                ra=Angle(catalogue_scs['RA'], unit=units.deg),
                dec=Angle(catalogue_scs['DEC'], unit=units.deg)
            ))

        # crossmatch catalogues (assume reference is indexed at 0)
        #
        # <crossmatches> is a reordered list of sources in each matching catalogue (catalogcoord) in the same order as
        #   the reference catalogue (matchcoord)
        # <crossmatch_sep2ds> is a list of separations between crossmatched catalogues
        #
        crossmatches = []
        crossmatch_sep2ds = []
        for match_catalogue_scs, match_catalogue_scs_icrs in zip(catalogues_scs[1:], catalogues_scs_icrs[1:]):
            idxs, sep2ds, _ = match_coordinates_sky(
                matchcoord=catalogues_scs_icrs[0],
                catalogcoord=match_catalogue_scs_icrs
            )
            crossmatches.append(match_catalogue_scs[idxs])
            crossmatch_sep2ds.append(Table([sep2ds], names=("sep2d",)))

        # join catalogue tables together using the crossmatched indexes
        crossmatch_results = hstack([
            Table(catalogues_scs[0]),
            *crossmatches,
            *crossmatch_sep2ds
        ],
            join_type='outer',
            table_names=[self.ref_catalogue, *self.match_catalogues, *self.match_catalogues],
            uniq_col_name='{table_name}_{col_name}',
            metadata_conflicts='silent'
        )

        # rename sep2d column for consistency if only one matching catalogue requested
        if len(self.match_catalogues) == 1:
            crossmatch_results.rename_column('sep2d', '{}_sep2d'.format(self.match_catalogues[0]))

        # apply any filters to the table
        filtered_crossmatch_results = crossmatch_results.copy()
        for sep2d_column_name in ['{}_sep2d'.format(name) for name in self.match_catalogues]:
            mask = filtered_crossmatch_results[sep2d_column_name] < self.max_separation
            filtered_crossmatch_results = filtered_crossmatch_results[mask]

        return filtered_crossmatch_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ra", nargs="?", help="right ascension (deg)", type=float, default=191.25)
    parser.add_argument("dec", nargs="?", help="declination (deg)", type=float, default=25)
    parser.add_argument("radius", nargs="?", help="radius (deg)", type=float, default=1)
    parser.add_argument("--ref-catalogue", help="reference catalogue", default="LOTSS_DR2", type=str)
    parser.add_argument("--match-catalogue", help="catalogue to match against reference", default=["TGSS_ADR", "GAIA_DR3", "2MASS"], action='store_true')
    parser.add_argument("--max-separation", help="maximum separation in deg", default=0.01, type=float)
    parser.add_argument("-p", help="plot?", action="store_true")
    args = parser.parse_args()

    #if not any([args.ra, args.dec, args.radius]):
    #    args.ra=191.25
    #    args.dec=25
    #    args.radius=1

    # check reference catalogue is supported
    if args.ref_catalogue not in SUPPORTED_CATALOGUES:
        raise Exception("Unsupported reference catalogue. Supported catalogues are {}".format(
            ', '.join(SUPPORTED_CATALOGUES.keys())))

    # check matching catalogue is supported
    for catalogue in args.match_catalogue:
        if catalogue not in SUPPORTED_CATALOGUES:
            raise Exception("Unsupported match catalogue ({}). Supported catalogues are {}".format(
                catalogue,
                ', '.join(SUPPORTED_CATALOGUES.keys())))

    crossmatch = Crossmatch(ra=args.ra, dec=args.dec, radius=args.radius, ref_catalogue=args.ref_catalogue,
                            match_catalogues=args.match_catalogue, max_separation=args.max_separation)
    crossmatch_results = crossmatch.run()
    if args.p:
        crossmatch.plot(crossmatch_results=crossmatch_results)
    
    # print results and save fits cat to disk
    t=Table(crossmatch_results)
        
    # fix column format issues
    t['Source_Name'] = t['Source_Name'].astype(str)
    t['LOTSS_DR2_S_Code'] = t['LOTSS_DR2_S_Code'].astype(str)
    t['Mosaic_ID'] = t['Mosaic_ID'].astype(str)
    t['mosaic_url'] = t['mosaic_url'].astype(str)
    t['ID'] = t['ID'].astype(str)
    t['TGSS_ADR_S_Code'] = t['TGSS_ADR_S_Code'].astype(str)
    t['Mosaic_Name'] = t['Mosaic_Name'].astype(str)
    t['source_id'] = t['source_id'].astype(str)
    t['mainid'] = t['mainid'].astype(str)


    t.write('crossmatch_cat.fits', format='fits', overwrite=True)
    print("\nSaved crossmatch_cat.fits to disk. \n")
    print("Found {0} sources, printing the first 5... \n".format(len(t)))
    print(t[0:5])
    print("\nColumn names are:")
    print(t.colnames)

    # testing which column formats fail
    #for col in t.colnames:
    #    print(col)
    #    t2=Table(t[col])
    #    t2.write('crossmatch_cat_'+col+'.fits', format='fits', overwrite=True)

