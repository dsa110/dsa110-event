import csv
import os
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from typing import Optional, Any
from event import tns_api_bulk_report, caltechdata, voevent, labels

OUTPUT_PATH = '/dataz/dsa110/operations/T3/'


@dataclass
class DSAEvent:
    mjds: float
    snr: float
    ibox: float
    dm: float
    ibeam: int
    cntb: int
    cntc: int
    specnum: int
    ra: float
    dec: float
    trigname: str
    snrs0: Optional[float] = None
    snrs1: Optional[float] = None
    snrs2: Optional[float] = None
    snrs3: Optional[float] = None
    snrs4: Optional[float] = None
    snrs5: Optional[float] = None
    snrs6: Optional[float] = None
    snrs7: Optional[float] = None
    snrs8: Optional[float] = None
    snrs9: Optional[float] = None
    beams0: Optional[int] = None
    beams1: Optional[int] = None
    beams2: Optional[int] = None
    beams3: Optional[int] = None
    beams4: Optional[int] = None
    beams5: Optional[int] = None
    beams6: Optional[int] = None
    beams7: Optional[int] = None
    beams8: Optional[int] = None
    beams9: Optional[int] = None
    raerr: Optional[float] = None
    decerr: Optional[float] = None
    radecerr: Optional[float] = None
    dmerr: Optional[float] = None
    gulp: Optional[int] = None
    filterbank: Optional[str] = None
    filfile: Optional[str] = None
    filfile_cand: Optional[str] = None
    filplot_cand: Optional[str] = None
    candplot: Optional[str] = None
    save: Optional[bool] = False
    label: Optional[str] = None
    injected: Optional[bool] = None
    probability: Optional[float] = None
    ibeam_prob: Optional[float] = None
    real: Optional[bool] = None
    T2_json: Optional[str] = None
    T2_csv: Optional[str] = None
    corr03_data: Optional[str] = None
    corr03_header: Optional[str] = None
    corr04_data: Optional[str] = None
    corr04_header: Optional[str] = None
    corr05_data: Optional[str] = None
    corr05_header: Optional[str] = None
    corr06_data: Optional[str] = None
    corr06_header: Optional[str] = None
    corr07_data: Optional[str] = None
    corr07_header: Optional[str] = None
    corr08_data: Optional[str] = None
    corr08_header: Optional[str] = None
    corr10_data: Optional[str] = None
    corr10_header: Optional[str] = None
    corr11_data: Optional[str] = None
    corr11_header: Optional[str] = None
    corr12_data: Optional[str] = None
    corr12_header: Optional[str] = None
    corr14_data: Optional[str] = None
    corr14_header: Optional[str] = None
    corr15_data: Optional[str] = None
    corr15_header: Optional[str] = None
    corr16_data: Optional[str] = None
    corr16_header: Optional[str] = None
    corr18_data: Optional[str] = None
    corr18_header: Optional[str] = None
    corr19_data: Optional[str] = None
    corr19_header: Optional[str] = None
    corr21_data: Optional[str] = None
    corr21_header: Optional[str] = None
    corr22_data: Optional[str] = None
    corr22_header: Optional[str] = None
    bf1_width_bins: Optional[int] = None
    bf1_start_bins: Optional[int] = None
    bf1_dm: Optional[float] = None
    bf1_dm_stddev: Optional[float] = None
    bf1_reduced_chisq: Optional[float] = None
    bf1_pvalue: Optional[float] = None
    voltage_sb00: Optional[str] = None
    voltage_sb01: Optional[str] = None
    voltage_sb02: Optional[str] = None
    voltage_sb03: Optional[str] = None
    voltage_sb04: Optional[str] = None
    voltage_sb05: Optional[str] = None
    voltage_sb06: Optional[str] = None
    voltage_sb07: Optional[str] = None
    voltage_sb08: Optional[str] = None
    voltage_sb09: Optional[str] = None
    voltage_sb10: Optional[str] = None
    voltage_sb11: Optional[str] = None
    voltage_sb12: Optional[str] = None
    voltage_sb13: Optional[str] = None
    voltage_sb14: Optional[str] = None
    voltage_sb15: Optional[str] = None
    beamformer_weights: Optional[str] = None
    beamformer_weights_sb00: Optional[str] = None
    beamformer_weights_sb01: Optional[str] = None
    beamformer_weights_sb02: Optional[str] = None
    beamformer_weights_sb03: Optional[str] = None
    beamformer_weights_sb04: Optional[str] = None
    beamformer_weights_sb05: Optional[str] = None
    beamformer_weights_sb06: Optional[str] = None
    beamformer_weights_sb07: Optional[str] = None
    beamformer_weights_sb08: Optional[str] = None
    beamformer_weights_sb09: Optional[str] = None
    beamformer_weights_sb10: Optional[str] = None
    beamformer_weights_sb11: Optional[str] = None
    beamformer_weights_sb12: Optional[str] = None
    beamformer_weights_sb13: Optional[str] = None
    beamformer_weights_sb14: Optional[str] = None
    beamformer_weights_sb15: Optional[str] = None
    
    def tojson(self):
        """ Convert event dict to json string.
        """

        jj = json.dumps(asdict(self))
        return jj

    def update(self, other):
        """ Update fields of this dsaevent with another dsaevent or dict.
        """

        if isinstance(other, DSAEvent):
            other = asdict(other)

        assert isinstance(other, dict), "update method takes DSACand or dict as argument"

        for kk,vv in other.items():
            if kk in self.__dict__:
                if self.__dict__[kk] is None:
                    self.__dict__[kk] = vv
            else:
                print(f"key {kk} not in DSACand")

    def writejson(self, outpath=OUTPUT_PATH, lock=None):
        """ Writes event to JSON or updates JSON file that already exists.
        """

        fn = Path(outpath) / Path(f'{self.trigname}.json')

        if lock is not None:
            lock.acquire(timeout="5s")

        if not Path(fn).exists():
            with open(fn, 'w') as fp:
                json.dump(asdict(self), fp, ensure_ascii=False, indent=4)
        else:
            dsaevent0 = create_event(fn)
            dsaevent0.update(self)
            with open(fn, 'w') as fp:
                json.dump(asdict(self), fp, ensure_ascii=False, indent=4)

        if lock is not None:
            lock.release()


def create_event(fn):
    """ Create a DSAEvent from a json file
    """

    assert Path(fn).exists(), f"File {fn} not found"
    with open(fn) as fp:
        dd = json.load(fp)

    if len(dd) != 1:
        try:
            dsaevent = DSAEvent(**dd)
        except TypeError:
            dsaevent = None
            print('Error reading json file. It may have extra keys?')
    else:
        # obsolete format written by initial trigger
        print('Found old trigger json format')
        assert len(dd), "dictionary read from json is empty"
        trigname = list(dd.keys())[0]  
        dd2 = dd[trigname]
        dd2['trigname'] = trigname
        dsaevent = DSAEvent(**dd2)

    return dsaevent


def doit(triggerfile, remarks, notes=None, files=None, production=True, getdoi=True, version=0.1, propdate=None, send=True, repeater_of_objid=None, csvfile='events.csv'):
    """
    Automated release of event via its T2 json trigger file.
    remarks appear on tns entry and help associate to common name (e.g., "a.k.a. casey")
    notes appear on dsa-110 archive. Default append TNS name to remarks (e.g., "{remarks} or FRB 2024...").
    files should be a list of full path to files on disk to make public at caltech data and associate with event.
    propdate sets the tns public date (e.g., "2025-01-31").
    Outcome is: an entry at caltech-data, an entry at tns, an official name, and a csv file that can be pushed to github.
    """

    # ctd_send
    metadata = caltechdata.create_ctd(triggerfile=triggerfile, production=production, getdoi=getdoi, version=version)
    for Iddict in metadata['identifiers']:
        if Iddict['identifierType'] == 'DOI':
            doi = Iddict['identifier']
            print(f'Got doi {doi} from metadata')

    print(f'Created metadata from {triggerfile} with doi {doi}')

    metadata_json = f'metadata_{triggerfile}'
    print(f'Saving {metadata_json}')
    with open(metadata_json, 'w') as fp:
        json.dump(metadata, fp)

    caltechdata.edit_ctd(metadata, files=files, production=production)  # publishes by default

    # tns_create
    event_dict, phot_dict = {}, {}
    if repeater_of_objid is not None:
        event_dict['repeater_of_objid'] = repeater_of_objid
    if remarks is not None:
        event_dict['remarks'] = remarks
    if propdate is not None:
        assert propdate.count("-") == 2 and propdate.count(":") == 0 and propdate.count(" ") == 0
        event_dict['end_prop_period'] = propdate

    dd = caltechdata.set_metadata(triggerfile=triggerfile)
    ve = voevent.create_voevent(**dd)
    dd2 = voevent.set_tns_dict(ve, phot_dict=phot_dict, event_dict=event_dict)

    # tmp file to send
    fn = f'tns_report_{ve.Why.Name}.json'
    if os.path.exists(fn):
        print(f"Removing older version of {fn}")
        os.remove(fn)
    voevent.write_tns(dd2, fn)
    if send:
        report_id, objname = tns_api_bulk_report.send_report(fn, production)
        if len(objname) == 1:
            objname = objname[0]
        else:
            print(f"objname is longer than length 1: {objname}")
    else:
        objname = 'Unnamed'

    # archive_update
    with open(metadata_json, 'r') as fp:
        dd = json.load(fp)

    if notes is None:
        dd['notes'] = f"{remarks} or {objname}"

    for Iddict in dd['identifiers']:
        if Iddict['identifierType'] == 'DOI':
            doi = Iddict['identifier']
            dd['doi'] = doi
            print(f'Got doi {doi} from metadata')
    
    columns = ['internalname', 'mjds', 'dm', 'width', 'snr', 'ra', 'dec', 'radecerr', 'notes', 'version', 'doi']
    colheader = ['Internal Name', 'MJD', 'DM', 'Width', 'SNR', 'RA', 'Dec', 'RADecErr', 'Notes', 'Version', 'doi']

    # verify that columns are correct?

    row = [dd[column] for column in columns]
    if os.path.exists(csvfile):
        code = 'a'
    else:
        code = 'w'
    with open(csvfile, code) as fp:
        csvwriter = csv.writer(fp)
        if code == 'w':
            csvwriter.writerow(colheader)  # no need if appending
        csvwriter.writerow(row)

    # still need to commit and push to github
