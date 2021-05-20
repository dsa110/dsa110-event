from setuptools import setup, find_packages
from version import get_git_version
import glob

setup(name='dsa110-event',
      version=get_git_version(),
      url='http://github.com/dsa110/dsa110-event',
      packages=find_packages(),
      requirements=['caltechdata_api', 'requests', 'voevent-parse'],
      include_package_data=True,
#      package_data={'event': ['data/*.json']},
      data_files=[('event/data', glob.glob('data/*.json'))],
      entry_points='''
        [console_scripts]
        dsaevent=event.cli:cli
      ''',
      zip_safe=False)
