import sys

# Make sure we are running python3.5+
if 10 * sys.version_info[0]  + sys.version_info[1] < 35:
    sys.exit("Sorry, only Python 3.5+ is supported.")

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'med2image',
      version          =   '0.6',
      description      =   '(Python) utility to convert medical images to jpg and png',
      long_description =   '(Python) utility to convert medical images to jpg and png',
      author           =   'FNNDSC',
      author_email     =   'dev@babymri.org',
      url              =   'https://github.com/FNNDSC/med2image',
      packages         =   ['med2image'],
      install_requires =   ['nibabel', 'pydicom', 'numpy', 'matplotlib', 'pillow'],
      #test_suite       =   'nose.collector',
      #tests_require    =   ['nose'],
      scripts          =   ['bin/med2image'],
      license          =   'MIT',
      zip_safe         =   False
)