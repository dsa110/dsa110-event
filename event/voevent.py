import os
import datetime
import json
import pytz
from astropy import time
from xml.dom import minidom

try:
    import voeventparse as vp
except ImportError:
    pass

tns_dict = {
  "frb_report": {
    "0": {
      "ra": {
        "value": "",
        "error": "",
        "units": "deg"
      },
      "dec": {
        "value": "",
        "error": "",
        "units": "deg"
      },
      "reporting_groupid": "",
      "groupid": "",
      "internal_name": "",
      "at_type": "5",
      "reporter": "",
      "discovery_datetime": "",
      "barycentric_event_time": "",
      "transient_redshift": "",
      "host_name": "",
      "host_redshift": "",
      "repeater_of_objid": "",
      "public_webpage": "http://code.deepsynoptic.org/dsa110-archive",
      "region_ellipse": "",
      "region_ellipse_unitid": "27",
      "region_polygon": "",
      "region_filename": "",
      "dm": "",
      "dm_err": "",
      "dm_unitid": "25",
      "galactic_max_dm": "",
      "galactic_max_dm_model": "",
      "remarks": "",
      "photometry": {
        "photometry_group": {
          "0": {
            "obsdate": "",
            "flux": "",
            "flux_error": "",
            "limiting_flux": "",
            "flux_units": "",
            "filter_value": "",
            "instrument_value": "",
            "snr": "",
            "fluence": "",
            "fluence_err": "",
            "fluence_unitid": "22",
            "exptime": "",
            "observer": "",
            "burst_width": "",
            "burst_width_err": "",
            "burst_width_unitid": "23",
            "burst_bandwidth": "",
            "burst_bandwidth_err": "",
            "burst_bandwidth_unitid": "24",
            "scattering_time": "",
            "scattering_time_err": "",
            "scattering_time_unitid": "23",
            "dm_struct": "",
            "dm_struct_err": "",
            "dm_struct_unitid": "25",
            "rm": "",
            "rm_err": "",
            "rm_unitid": "26",
            "frac_lin_pol": "",
            "frac_lin_pol_err": "",
            "frac_circ_pol": "",
            "frac_circ_pol_err": "",
            "ref_freq": "",
            "ref_freq_unitid": "24",
            "inst_bandwidth": "",
            "inst_bandwidth_unitid": "24",
            "channels_no": "",
            "sampling_time": "",
            "sampling_time_unitid": "23",
            "comments": ""
          },
        }
      },
#      "related_files": {
#        "0": {
#          "related_file_name": "",
#          "related_file_comments": ""
#        },
#      }
    }
  }
}


def create_voevent(jsonfile=None, deployment=False, **kwargs):
    """ template syntax for voeventparse creation of voevent
    """

    required = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr']
    preferred = ['fluence', 'p_flux', 'importance', 'dmerr']

    # set values
    dd = kwargs.copy()
    if jsonfile is not None:   # as made by caltechdata.set_metadata
        for k, v in trigger.items():
            if k in required + preferred:
                dd[k] = v

    assert all([k in dd for k in required]), f'Input keys {list(dd.keys())} not complete (requires {required})'

    dt = time.Time(dd['mjds'], format='mjd').to_datetime(timezone=pytz.utc)  # topocentric, top of band

    # create voevent instance
    role = vp.definitions.roles.observation if deployment else vp.definitions.roles.test
    v = vp.Voevent(stream='edu.caltech.dsa-110', stream_id=1, role=role)

    vp.set_who(v, date=datetime.datetime.utcnow(),
               author_ivorn=f"caltech/dsa-110#{str(dd['internalname']}/{str(dd['mjds'])}")

    vp.set_author(v, contactName="Casey Law", contactEmail="claw@astro.caltech.edu")

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

    # radecerr converted to degrees for VOEvent
    vp.add_where_when(v,
                      coords=vp.Position2D(ra=str(dd['ra']), dec=str(dd['dec']), err=str(dd['radecerr']/3600),
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
    """ Takes VOEvent object and writes as xml. 
    """

    with open(outname, 'w') as f:
        voxml = vp.dumps(v)
        xmlstr = minidom.parseString(voxml).toprettyxml(indent="   ")
        f.write(xmlstr)
        print("Wrote your voevent to ", os.path.abspath(outname))


def get_voevent(inname):
    """ Use voeventparse to read voevent.
    """

    with open(inname, 'rb') as fp:
        ve = vp.load(fp)

    return ve


def set_tns_dict(ve, phot_dict={}, event_dict={}):
    """ assign values to TNS dictionary. Most values taken from parsed VOEvent file.

    Optional dictionary input to overload some fields:
    - phot_dict is dictionary for "photometry" keys to set: "snr", "flux", "flux_error", "fluence", "burst_width"
    - event_dict is dictionary for other TNS keys (from frb_report set): "internal_name", "remarks", "repeater_of_objid"
    """

    # TODO: ra/dec errors separately, flux/flux_error
    # TODO: galactic_max_dm, galactic_max_dm_model
    
    tns_dict['frb_report']['0']["internal_name"] = str(ve.Why.Name)
    tns_dict['frb_report']['0']["reporter"] = "Casey J. Law"
    pos = vp.get_event_position(ve)
    tns_dict['frb_report']['0']['ra']['value'] = pos.ra
    tns_dict['frb_report']['0']['dec']['value'] = pos.dec
    tns_dict['frb_report']['0']['ra']['error'] = pos.err
    tns_dict['frb_report']['0']['dec']['error'] = pos.err
    dt = vp.get_event_time_as_utc(ve)
    dtstring = f'{dt.date().isoformat()} {dt.time().isoformat()}'
    tns_dict['frb_report']['0']["discovery_datetime"] = dtstring
    tns_dict['frb_report']['0']["reporting_groupid"] = 132  # DSA-110
    tns_dict['frb_report']['0']["groupid"] = 132  # DSA-110
    tns_dict['frb_report']['0']['proprietary_period_groups'] = ["132"]  # DSA-110

    if "end_prop_period" in event_dict:
        tns_dict['frb_report']['0']["end_prop_period"] = str(event_dict["end_prop_period"])

    tns_dict['frb_report']['0']["at_type"] = 5  # FRBs
    params = vp.get_grouped_params(ve)
    tns_dict['frb_report']['0']["dm"] = params['event parameters']['dm']['value']
    try:
        tns_dict['frb_report']['0']["dmerr"] = params['event parameters']['dm_error']['value']
    except KeyError:
        pass
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["snr"] = params['event parameters']['snr']['value']
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["burst_width"] = params['event parameters']['width']['value']
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["filter_value"] = 129
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["instrument_value"] = 239
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux"] = 0   # TODO: set this in Jy
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux_error"] = 0   # TODO: set this in Jy
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["limiting_flux"] = 0
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["obsdate"] = dtstring
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["flux_units"] = "8"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["ref_freq"] = "1405"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["inst_bandwidth"] = "187.5"
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["channels_no"] = 768
    tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]["sampling_time"] = 0.262

    # set photometry values
    for key, value in phot_dict.items():
        if key in tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"]:
            print(f'Overloading event key {key} with {value}')
            tns_dict['frb_report']['0']["photometry"]["photometry_group"]["0"][key] = value
            
    # overload other values
    for key, value in event_dict.items():
        if key in tns_dict['frb_report']['0']:
            print(f'Overloading event key {key} with {value}')
            tns_dict['frb_report']['0'][key] = value
            
    return tns_dict


def write_tns(dd, outname):
    """ Use json to write TNS dict
    """

    with open(outname, 'w') as fp:
        json.dump(dd, fp)
