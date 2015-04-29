from setuptools import setup, find_packages

version = '0.1.0'

setup(name='ucmclient',
      version=version,
      description="A python client for communicating with Oracle UCM 11g Content Server",
      long_description="""\
This package provides a simple client for calling the services on Oracle Content Server 11g via the standard web interface. It can be used in conjunction with any of the services provided by Content Server  defined here http://download.oracle.com/docs/cd/E14571_01/doc.1111/e11011/toc.htm  
""",
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Natural Language :: English',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP'
      ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='oracle ucm services client',
      author='stuart robinson',
      author_email='webmasterwords+pypi@gmail.com',
      url='http://www.webmasterwords.com/python-ucm-client',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "MultipartPostHandler==0.1.0",
          "simplejson==2.1.2"
      ],
)
