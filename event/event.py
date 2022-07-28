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
    filfile: Optional[str] = None
    candplot: Optional[str] = None
    save: Optional[bool] = False
    label: Optional[str] = None
    corr03_data: Optional[Any] = None
    corr03_header: Optional[Any] = None
    corr04_data: Optional[Any] = None
    corr04_header: Optional[Any] = None
    corr05_data: Optional[Any] = None
    corr05_header: Optional[Any] = None
    corr06_data: Optional[Any] = None
    corr06_header: Optional[Any] = None
    corr07_data: Optional[Any] = None
    corr07_header: Optional[Any] = None
    corr08_data: Optional[Any] = None
    corr08_header: Optional[Any] = None
    corr19_header: Optional[Any] = None
    corr21_data: Optional[Any] = None
    corr21_header: Optional[Any] = None
    corr22_data: Optional[Any] = None
    corr22_header: Optional[Any] = None
    injected: Optional[bool] = None
    probability: Optional[float] = None
    real: Optional[bool] = None
                                        
    def tojson(self):
        """ Convert event dict to json string.
        """

        jj = json.dumps(asdict(self))
        return jj

    def update(self, dsaevent):
        """ Update fields of this dsaevent with another dsaevent.
        """

        return self.__dict__.update(dsaevent.__dict__)
    
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
            self.update(dsaevent0)
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
        trigname = list(dd.keys())[0]  
        dd2 = dd[trigname]
        dd2['trigname'] = trigname
        dsaevent = DSAEvent(**dd2)

    return dsaevent
