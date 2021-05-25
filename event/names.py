import random
import string
from astropy import time


def makename(mjd, specnum):
    """ Use mjd and specnum to create unique name for event.
    """

    dt = time.Time(mjd, format='mjd', scale='utc').to_datetime()
    suffix = ''.join([random.choice(string.ascii_letters) for _ in range(3)])
        
    return f'{dt.year}{dt.month}{dt.day}_{specnum}_{suffix}'
