from distutils.core import setup

import version


setup(name='nested_structures',
      version=version.getVersion(),
      description='Nested structures based on Python standard containers.',
      keywords='python nested structures',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/nested_structures.git',
      license='GPL',
      packages=['nested_structures'])
