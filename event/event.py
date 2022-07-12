import os.path
import json
import dataclasses


@dataclasses.dataclass
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
        jj = json.dumps(dataclasses.asdict(self))
        return jj

    def writejson(self):
        fn = outpath + dd['trigname'] + '.json'

        if not os.path.exists(fn):
            with open(fn, 'w') as f:
                json.dump(self.tojson(), f, ensure_ascii=False, indent=4)
        else:
            with open(fn, 'r') as f:
                # implement T3Cand load
                # implement T3Cand update
                with open(fn, 'w') as f:
                    json.dump(self.tojson(), f, ensure_ascii=False, indent=4)
