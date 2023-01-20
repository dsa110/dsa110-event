# dsa110-event

Handling candidate alerts and metadata for DSA-110. Uses Caltech Data, Transient Name Server, and VOEvent protocols to publish/share/distribute discoveries.

# Dependencies

- [voevent-parse](https://github.com/caseyjlaw/voevent-parse)
- [caltechdata_api](https://github.com/caltechlibrary/caltechdata_api)
- [datacite](https://github.com/inveniosoftware/datacite)
- [requests](https://requests.readthedocs.io/en/latest)

# Installation

```
<git clone dsa110-event and cd into directory>
pip install -r requirements.txt
python setup.py install
```

# Use Cases

## ASAP distribution of detection for triggering by all-sky monitors (e.g., OVRO-LWA)

Start with T2 json with initial (search beam) localization:
- `create_voevent` -- creates standard VOEvent file.
- `send_voevent` (in development) -- sends VOEvent to a broker or partner.

## Sub-arcminute localization distribution for triggering of repoint by telescope (e.g., Swift/GUANO)

Start with T3 json with rough, real-time calibration and localization:
- `create_voevent` -- creates standard VOEvent file.
- `send_voevent` (in development) -- sends VOEvent to a broker or partner.
- optionally:
-- Use T2 data as input to publication of event (`ctd_send`, `tns_create`, and `archive_update`, as below).
-- Important to save Caltech Data metadata file, in case updates are required. Keep it in the candidates data area.

## Arcsecond localization distribution for publication of complete analysis

Start with T3 json with full calibration and localization:
- `ctd_send` -- get DOI and upload discovery plot. Creates metadata needed for updates and making archive update.
- `tns_create` -- use T3 json to get official name and broadcast to public (with prop period, if needed).
- `archive_update` -- adds line to DSA-110 event archive with link to data DOI, nickname, and official name.

Or if sub-arcmin localization already published, then modify the Caltech Data metadata and pass to `ctd_update` and `archive_update`.