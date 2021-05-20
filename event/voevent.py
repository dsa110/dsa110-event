import os
import datetime
import pytz
import voeventparse as vp


def create_voevent(deployment=False, **kwargs):
    """ template syntax for voeventparse creation of voevent
    """

    required = ['fluence', 'p_flux', 'ra', 'dec', 'radecerr', 'dm', 'dmerr', 'width', 'snr', 'internalname']
    assert all([k in kwargs for k in required])

    # TODO: set this correctly
    dt = datetime.datetime.utcnow()  # datetime(yyyy, mm, dd, hh, mm, ss, tzinfo=pytz.utc)  

    # create voevent instance
    role = vp.definitions.roles.observation if deployment else vp.definitions.roles.test
    v = vp.Voevent(stream='',  # TODO: check
                   stream_id=1, role=role)

    vp.set_who(v, date=datetime.datetime.utcnow(),
               author_ivorn="voevent.dsa-110.caltech.org") # TODO: check

    vp.set_author(v, title="DSA-110 Testing Node",
                  shortName="Casey"
    )

    fluence = vp.Param(name='fluence',
                        value=kwargs[fluence],
                        unit='Jansky ms',
                        ucd='em.radio.750-1500MHz', # TODO: check
                        dataType='float',
                        ac=False)
    fluence.Description = 'Fluence'

    p_flux = vp.Param(name='peak_flux',
                      value=kwargs[p_flux],
                      unit='Janskys',
                      ucd='em.radio.750-1500MHz',
                      dataType='float',
                      ac=True
    )
    p_flux.Description = 'Peak Flux'

    dm = vp.Param(name="dm",
                  value=kwargs[dm],
                  unit="pc/cm^3",
                  ucd="phys.dispMeasure;em.radio.750-1500MHz" 
                  dataType='float',
                  ac=True
    )
    dm.Description = 'Dispersion Measure'
    
    dmerr = vp.Param(name="dm_error",
                  value=kwargs[dmerr],
                  unit="pc/cm^3",
                  ucd="phys.dispMeasure;em.radio.750-1500MHz" 
                  dataType='float',
                  ac=True
    )
    dmerr.Description = 'Dispersion Measure error'

    width = vp.Param(name="width",
                     value=kwargs[width],
                     unit="ms",
                     ucd="time.duration;src.var.pulse",
                     dataType='float',
                     ac=True
    )
    width.Description = 'Temporal width of burst'

    snr = vp.Param(name="snr",
                     value=kwargs[snr],
                     ucd="stat.snr",
                     dataType='float',
                     ac=True
    )
    snr.Description = 'Signal to noise ratio'
    
    v.What.append(vp.Group(params=[p_flux, fluence, dm, dmerr, width, snr], name='event parameters'))

    vp.add_where_when(v,
                      coords=vp.Position2D(ra=kwargs[ra], dec=kwargs[dec], err=kwargs[radecerr],
                                           units='deg',
                                           system=vp.definitions.sky_coord_system.utc_fk5_geo),
                      obs_time=dt
                      observatory_location='OVRO')

    print("\n***Here is your WhereWhen:***\n")
    print(vp.prettystr(v.WhereWhen))

    print("\n***And your What:***\n")
    print(vp.prettystr(v.What))

    vp.add_how(v, descriptions='Discovered with DSA-110',
               references=vp.Reference('http://deepsynoptic.org'))

    vp.add_why(v, name=internalname, description='New candidate FRB')

    vp.assert_valid_as_v2_0(v)

    return vp


def write_voevent(vp, outname='new_voevent_example.xml'):
    with open(outname, 'wb') as f:
        vp.dump(v, f)

        print("Wrote your voevent to ", os.path.abspath(outname))
