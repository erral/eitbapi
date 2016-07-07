import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'waitress',
    'youtube-dl',
    'requests',
    'cherrypy',
    'pastescript',
    'redis',
]

tests_requires = [
    'WebTest >= 1.3.1',
    'pytest',
    'pytest-cov',
]

setup(name='eitbapi',
      version='1.0',
      description='eitbapi',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Mikel Larreategi',
      author_email='larreategi@eibar.org',
      url='https://github.com/erral/eitbapi',
      license='GPLv2',
      keywords='web pyramid pylons eitb video api tv',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_requires,
      extras_require={'testing': tests_requires},
      test_suite="eitbapi",
      entry_points="""\
      [paste.app_factory]
      main = eitbapi:main
      """,
      )
