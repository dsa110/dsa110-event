import datetime
import os

import pytz
import voeventparse as vp


def create_voevent():
    """ template syntax for voeventparse creation of voevent
    """

    v = vp.Voevent(stream='astronomy.physics.science.org/super_exciting_events',
                   stream_id=123, role=vp.definitions.roles.test)

    vp.set_who(v, date=datetime.datetime.utcnow(),
               author_ivorn="voevent.4pisky.org")

    vp.set_author(v, title="4PiSky Testing Node",
                  shortName="Tim"
    )

    int_flux = vp.Param(name='int_flux',
                        value="2.0e-3",
                        unit='Janskys',
                        ucd='em.radio.100-200MHz',
                        dataType='float',
                        ac=False)
    int_flux.Description = 'Integrated Flux'

    p_flux = vp.Param(name='peak_flux',
                      value=1.5e-3,
                      unit='Janskys',
                      ucd='em.radio.100-200MHz',
                      ac=True
    )
    p_flux.Description = 'Peak Flux'

    v.What.append(vp.Group(params=[p_flux, int_flux], name='source_flux'))

    amb_temp = vp.Param(name="amb_temp",
                        value=15.5,
                        unit='degrees',
                        ucd='phys.temperature')

    amb_temp.Description = "Ambient temperature at telescope"
    v.What.append(amb_temp)

    vp.add_where_when(v,
                      coords=vp.Position2D(ra=123.5, dec=45, err=0.1,
                                           units='deg',
                                           system=vp.definitions.sky_coord_system.utc_fk5_geo),
                      obs_time=datetime.datetime(2013, 1, 31, 12, 5, 30,
                                                 tzinfo=pytz.utc),
                      observatory_location=vp.definitions.observatory_location.geosurface)

    print("\n***Here is your WhereWhen:***\n")
    print(vp.prettystr(v.WhereWhen))

    print("\n***And your What:***\n")
    print(vp.prettystr(v.What))

    vp.add_how(v, descriptions='Discovered via 4PiSky',
               references=vp.Reference('http://4pisky.org'))

    vp.add_why(v, name='')

    vp.assert_valid_as_v2_0(v)

    return vp


def write_voevent(vp, outname='new_voevent_example.xml'):
    with open(outname, 'wb') as f:
        vp.dump(v, f)

        print("Wrote your voevent to ", os.path.abspath(outname))
