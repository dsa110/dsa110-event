from astropy import units, coordinates, table
import pickle
import os

def find_associations(ra, dec, mode='nvss', nvss_radius=5, nvss_flux=400, atnf_radius=5,
                      nvsscat='nvss_astropy.pkl', atnfcat='atnfcat_v1.56.txt'):
    """ Find cataloged NVSS/pulsar sources near (RA, Dec) in degrees.
    Major check is for bright NVSS sources during VLASS (mode='nvss')
    For mode='pulsar', it will return any pulsar in atnf catalog.
    nvss_radius (arcsec), nvss_flux (mJy), atnf_radius (arcsec) define cross match.
    Returns boolean (for now)
    """

    workdir = ''
    assert mode.lower() in ['pulsar', 'nvss']

    if os.path.exists(workdir + nvsscat) and mode.lower() == 'nvss':
        print("Loading NVSS catalog")
        with open(workdir + nvsscat, 'rb') as pkl:
            catalog = pickle.load(pkl)
            fluxes = pickle.load(pkl)
    elif os.path.exists(workdir + atnfcat) and mode.lower() == 'pulsar':
        print("Loading ATNF catalog")
        tab = table.Table.read(workdir + atnfcat, format='ascii')
        catalog = coordinates.SkyCoord(ra=tab['RAJ'], dec=tab['DECJ'], unit=(units.hourangle, units.deg))
    else:
        print(f"No catalog found for mode {mode} in {workdir}")
        return None

    coord = coordinates.SkyCoord(ra, dec, unit='deg')

    if mode.lower() == 'nvss':
        print("Comparing SkyCoord for candidates to NVSS.")
        ind, sep2, sep3 = coord.match_to_catalog_sky(catalog)
        if sep2.value < nvss_radius and fluxes[ind] > nvss_flux:
            return True
        else:
            return False
    elif mode.lower() == 'pulsar':
        print("Comparing SkyCoord for candidates to ATNF.")
        ind, sep2, sep3 = coord.match_to_catalog_sky(catalog)
        if sep2.value < atnf_radius:
            return True
        else:
            return False
