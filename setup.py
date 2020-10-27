from setuptools import setup

setup(name='tuttest',
      version='0.1',
      description='Tutorial tester',
      url='http://github.com/antmicro/tuttest',
      author='Antmicro',
      author_email='mgielda@antmicro.com',
      install_requires=[
          'docutils', 'pygments', 'fire'
      ],
      license='MIT',
      scripts=['bin/tuttest'],
      packages=['tuttest'])
