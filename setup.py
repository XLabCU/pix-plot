from os.path import join
from setuptools import setup
import os
import sys

# validate python version
if sys.version_info < (3, 10):
  sys.exit('Sorry, this version of PixPlot requires Python 3.10 or later')

# populate list of all paths in `./pixplot/web`
web = []
dirs = [join('pixplot', 'web'), join('pixplot', 'models')]
for i in dirs:
  for root, subdirs, files in os.walk(i):
    if not files:
      continue
    for file in files:
      web.append(join(root.replace('pixplot/', '')
                          .replace('pixplot\\', ''), file))

setup(
  name='pixplot',
  version='0.0.113',
  packages=['pixplot'],
  package_data={
    'pixplot': web,
  },
  keywords=['computer-vision',
            'webgl',
            'three.js',
            'tensorflow',
            'machine-learning'],
  description='Visualize large image collections with WebGL',
  url='https://github.com/yaledhlab/pix-plot',
  author='Douglas Duhaime',
  author_email='douglas.duhaime@gmail.com',
  license='MIT',
  install_requires = [
  'cmake>=3.15.3',
  'glob2>=0.6',
  'h5py>=3.8.0',
  'iiif-downloader>=0.0.6',
  'numpy>=1.22.1',
  'Pillow>=10.0.0',
  'pointgrid>=0.0.2',
  'python-dateutil>=2.8.0',
  'scikit-learn>=1.3.0',
  'scipy>=1.11.0',
  'tensorflow',  # TF 2.12+ supports Python 3.11
  'tqdm>=4.66.0',
  'umap-learn>=0.5.3',
  'rasterfairy>=1.0.6',  # Check if this needs updating
  'matplotlib>=3.7.0'
],
  entry_points={
    'console_scripts': [
      'pixplot=pixplot:parse',
    ],
  },
)
