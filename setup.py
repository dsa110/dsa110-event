from setuptools import setup
from version import get_git_version

setup(name='dsa110-event',
      version=get_git_version(),
      url='http://github.com/dsa110/dsa110-event',
      packages=['event'],
      zip_safe=False)
