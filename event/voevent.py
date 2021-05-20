import os
import datetime
import pytz
from astropy import time
import voeventparse as vp
from xml.dom import minidom


def create_voevent(deployment=False, **kwargs):
    """ template syntax for voeventparse creation of voevent
    """

    required = ['fluence', 'p_flux', 'ra', 'dec', 'radecerr', 'dm', 'dmerr', 'width', 'snr', 'internalname', 'mjd', 'importance']
    assert all([k in kwargs for k in required])

    # TODO: set this correctly
    dt = time.Time(kwargs['mjd'], format='mjd').to_datetime(timezone=pytz.utc)

    # create voevent instance
    role = vp.definitions.roles.observation if deployment else vp.definitions.roles.test
    v = vp.Voevent(stream='',  # TODO: check
                   stream_id=1, role=role)

    vp.set_who(v, date=datetime.datetime.utcnow(),
               author_ivorn="voevent.dsa-110.caltech.org") # TODO: check

    vp.set_author(v, title="DSA-110 Testing Node",
                  contactName="Casey Law", contactEmail="claw@astro.caltech.edu"
    )

    fluence = vp.Param(name='fluence',
                       value=kwargs['fluence'],
                       unit='Jansky ms',
                       ucd='em.radio.750-1500MHz', # TODO: check
                       dataType='float',
                       ac=False)
    fluence.Description = 'Fluence'

    p_flux = vp.Param(name='peak_flux',
                      value=kwargs['p_flux'],
                      unit='Janskys',
                      ucd='em.radio.750-1500MHz',
                      dataType='float',
                      ac=True
    )
    p_flux.Description = 'Peak Flux'

    dm = vp.Param(name="dm",
                  value=kwargs['dm'],
                  unit="pc/cm^3",
                  ucd="phys.dispMeasure;em.radio.750-1500MHz",
                  dataType='float',
                  ac=True
    )
    dm.Description = 'Dispersion Measure'
    
    dmerr = vp.Param(name="dm_error",
                     value=kwargs['dmerr'],
                     unit="pc/cm^3",
                     ucd="phys.dispMeasure;em.radio.750-1500MHz",
                     dataType='float',
                     ac=True
    )
    dmerr.Description = 'Dispersion Measure error'

    width = vp.Param(name="width",
                     value=kwargs['width'],
                     unit="ms",
                     ucd="time.duration;src.var.pulse",
                     dataType='float',
                     ac=True
    )
    width.Description = 'Temporal width of burst'

    snr = vp.Param(name="snr",
                     value=kwargs['snr'],
                     ucd="stat.snr",
                     dataType='float',
                     ac=True
    )
    snr.Description = 'Signal to noise ratio'
    
    v.What.append(vp.Group(params=[p_flux, fluence, dm, dmerr, width, snr], name='event parameters'))

    vp.add_where_when(v,
                      coords=vp.Position2D(ra=kwargs['ra'], dec=kwargs['dec'], err=kwargs['radecerr'],
                                           units='deg',
                                           system=vp.definitions.sky_coord_system.utc_fk5_geo),
                      obs_time=dt,
                      observatory_location='OVRO')

    print("\n***Here is your WhereWhen:***\n")
    print(vp.prettystr(v.WhereWhen))

    print("\n***And your What:***\n")
    print(vp.prettystr(v.What))

    vp.add_how(v, descriptions='Discovered with DSA-110',
               references=vp.Reference('http://deepsynoptic.org'))

    vp.add_why(v, importance=kwargs['importance'])
    v.Why.Name=kwargs['internalname']
    vp.assert_valid_as_v2_0(v)

    return v


def write_voevent(v, outname='new_voevent_example.xml'):
    with open(outname, 'w') as f:
        voxml = vp.dumps(v)
        xmlstr = minidom.parseString(voxml).toprettyxml(indent="   ")
        f.write(xmlstr)
        print("Wrote your voevent to ", os.path.abspath(outname))
