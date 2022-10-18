from pathlib import Path
import json
from dataclasses import dataclass, asdict
from typing import Optional, Any

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

    try:
        dsaevent = DSAEvent(**dd)
    except TypeError:
        # obsolete format written by initial trigger
        print('Found old trigger json format')
        assert len(dd), "dictionary read from json is empty"
        trigname = list(dd.keys())[0]  
        dd2 = dd[trigname]
        dd2['trigname'] = trigname
        dsaevent = DSAEvent(**dd2)

    return dsaevent
