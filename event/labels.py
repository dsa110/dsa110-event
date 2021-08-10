import json


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


def set_label(candname, label, path=None):
    """ 
    """

    assert label in ['astrophysical', 'instrumental', 'unsure/noise', 'rfi', 'archive']

    filename = f'{candname}.json'
    if path is not None:
        filename = os.path.join(path, filename)

    dd = readfile(filename)
    
    if label == 'archive':
        dd[candname][label] = True
    else:
        dd[candname]['label'] = label

    writefile(dd, filename)
