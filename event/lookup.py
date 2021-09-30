from astropy import units, coordinates, table
import pickle
import os

def find_associations(ra, dec, mode='both', nvss_radius=60, nvss_flux=400, atnf_radius=60,
                      nvsscat='nvss_astropy.pkl', atnfcat='atnfcat_v1.56.txt'):
    """ Find cataloged NVSS/pulsar sources near (RA, Dec) in degrees.
    Major check is for bright NVSS sources during VLASS (mode='nvss')
    For mode='pulsar', it will return any pulsar in atnf catalog.
    nvss_radius (arcsec), nvss_flux (mJy), atnf_radius (arcsec) define cross match.
    Returns boolean (for now)
    """

    workdir = ''
    assert mode.lower() in ['pulsar', 'nvss', 'both']

    if os.path.exists(workdir + nvsscat) and mode.lower() in ['nvss', 'both']:
        print("Loading NVSS catalog")
        with open(workdir + nvsscat, 'rb') as pkl:
            catalogn = pickle.load(pkl)
            fluxesn = pickle.load(pkl)
    else:
        print(f"No catalog found for mode {mode} in {workdir}")
        return None

    if os.path.exists(workdir + atnfcat) and mode.lower() in ['pulsar', 'both']:
        print("Loading ATNF catalog")
        tab = table.Table.read(workdir + atnfcat, format='ascii')
        cataloga = coordinates.SkyCoord(ra=tab['RAJ'], dec=tab['DECJ'], unit=(units.hourangle, units.deg))
    else:
        print(f"No catalog found for mode {mode} in {workdir}")
        return None

    coord = coordinates.SkyCoord(ra, dec, unit='deg')
    associations = []

    if mode.lower() in ['nvss', 'both']:
        print("Comparing SkyCoord for candidates to NVSS.")
        ind, sep2, sep3 = coord.match_to_catalog_sky(catalogn)
        if sep2.value < nvss_radius and fluxesn[ind] > nvss_flux:
            associations.append((catalogn[ind], sep2.value))

    if mode.lower() in ['pulsar', 'both']:
        print("Comparing SkyCoord for candidates to ATNF.")
        ind, sep2, sep3 = coord.match_to_catalog_sky(cataloga)
        if sep2.value < atnf_radius:
            associations.append((cataloga[ind], sep2.value))

    return associations
