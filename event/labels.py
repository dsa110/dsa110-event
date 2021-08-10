import json
import os.path

_allowed = ['astrophysical', 'instrumental', 'unsure/noise', 'rfi', 'archive']

def readfile(filename):
    """ Read candidate json trigger file and return dict
    TODO: add file lock?
    """

    with open(filename, 'r') as fp:
        dd = json.load(fp)

    return dd


def writefile(dd, filename):
    """ Write candidate json trigger file with dict
    """

    with open(filename, 'w') as fp:
        json.dump(dd, fp)


def list_cands_labels(filename):
    """ read json file and list all candidates and labels.
    TODO: decide if more than one allowed
    """
    
    dd = readfile(filename)
    candnames = list(dd.keys())
    for candname in candnames:
        labels = [kk for kk in dd[candname].keys() if kk in _allowed]
        if len(labels):
            labelstr = ', '.join(labels)
        else:
            labelstr = 'no labels'
        print(f'{candname}: {labelstr}')


def set_label(candname, label, filename=None):
    """ Read, add label, and write candidate json file.
    Can optionally provide full path to file.
    Default assumes name of <candname>.json in cwd.
    TODO: decide if file can have more than one candname.
    """

    assert label in _allowed, f'label must be in {_allowed}'

    if filename is None:
        filename = f'{candname}.json'

    assert os.path.exists(filename), f'candidate json file {filename} not found'

    dd = readfile(filename)

    if candname in dd.keys():
        if label == 'archive':
            dd[candname][label] = True
        else:
            dd[candname]['label'] = label
        writefile(dd, filename)
    else:
        print(f'candname {candname} not found in {filename}. no label applied.')
        
        

