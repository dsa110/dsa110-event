import os
import datetime
import json
import pytz
from astropy import time
import voeventparse as vp
from xml.dom import minidom


def create_voevent(triggerfile=None, deployment=False, **kwargs):
    """ template syntax for voeventparse creation of voevent
    """

    required = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr']
    preferred = ['fluence', 'p_flux', 'importance', 'dmerr']

    # set values
    dd = kwargs.copy()
    if triggerfile is not None:
        with open(triggerfile, 'r') as fp:
            trigger = json.load(fp)

        for k, v in trigger.items():  # should be one entry in T2 json trigger file
            dd['internalname'] = k
            for kk, vv in v.items():
                if kk in required + preferred:
                    dd[kk] = vv

    assert all([k in dd for k in required]), f'Input keys {list(dd.keys())} not complete (requires {required})'

    # TODO: set this correctly
    dt = time.Time(dd['mjds'], format='mjd').to_datetime(timezone=pytz.utc)

    # create voevent instance
    role = vp.definitions.roles.observation if deployment else vp.definitions.roles.test
    v = vp.Voevent(stream='',  # TODO: check
                   stream_id=1, role=role)

    vp.set_who(v, date=datetime.datetime.utcnow(),
               author_ivorn="voevent.dsa-110.caltech.org") # TODO: check

    vp.set_author(v, title="DSA-110 Testing Node",
                  contactName="Casey Law", contactEmail="claw@astro.caltech.edu"
    )

    params = []
    dm = vp.Param(name="dm",
                  value=str(dd['dm']),
                  unit="pc/cm^3",
                  ucd="phys.dispMeasure;em.radio.750-1500MHz",
                  dataType='float',
                  ac=True
    )
    dm.Description = 'Dispersion Measure'
    params.append(dm)

    width = vp.Param(name="width",
                     value=str(dd['width']),
                     unit="ms",
                     ucd="time.duration;src.var.pulse",
                     dataType='float',
                     ac=True
    )
    width.Description = 'Temporal width of burst'
    params.append(width)

    snr = vp.Param(name="snr",
                     value=str(dd['snr']),
                     ucd="stat.snr",
                     dataType='float',
                     ac=True
    )
    snr.Description = 'Signal to noise ratio'
    params.append(snr)
    
    if 'fluence' in dd:
        fluence = vp.Param(name='fluence',
                           value=str(dd['fluence']),
                           unit='Jansky ms',
                           ucd='em.radio.750-1500MHz', # TODO: check
                           dataType='float',
                           ac=False)
        fluence.Description = 'Fluence'
        params.append(fluence)

    if 'p_flux' in dd:
        p_flux = vp.Param(name='peak_flux',
                          value=str(dd['p_flux']),
                          unit='Janskys',
                          ucd='em.radio.750-1500MHz',
                          dataType='float',
                          ac=True
        )
        p_flux.Description = 'Peak Flux'
        params.append(p_flux)

    if 'dmerr' in dd:
        dmerr = vp.Param(name="dm_error",
                         value=str(dd['dmerr']),
                         unit="pc/cm^3",
                         ucd="phys.dispMeasure;em.radio.750-1500MHz",
                         dataType='float',
                         ac=True
        )
        dmerr.Description = 'Dispersion Measure error'
        params.append(dmerr)

    v.What.append(vp.Group(params=params, name='event parameters'))

    vp.add_where_when(v,
                      coords=vp.Position2D(ra=str(dd['ra']), dec=str(dd['dec']), err=str(dd['radecerr']),
                                           units='deg', system=vp.definitions.sky_coord_system.utc_fk5_geo),
                      obs_time=dt,
                      observatory_location='OVRO')

    print("\n***Here is your WhereWhen:***\n")
    print(vp.prettystr(v.WhereWhen))

    print("\n***And your What:***\n")
    print(vp.prettystr(v.What))

    vp.add_how(v, descriptions='Discovered with DSA-110',
               references=vp.Reference('http://deepsynoptic.org'))

    if 'importance' in dd:
        vp.add_why(v, importance=str(dd['importance']))
    else:
        vp.add_why(v)
    v.Why.Name=str(dd['internalname'])

    vp.assert_valid_as_v2_0(v)

    return v


def write_voevent(v, outname='new_voevent_example.xml'):
    with open(outname, 'w') as f:
        voxml = vp.dumps(v)
        xmlstr = minidom.parseString(voxml).toprettyxml(indent="   ")
        f.write(xmlstr)
        print("Wrote your voevent to ", os.path.abspath(outname))
