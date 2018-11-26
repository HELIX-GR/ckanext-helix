from setuptools import setup, find_packages
import sys, os

version = '1.4dev'

setup(
    name='ckanext-helix',
    version=version,
    description="A collection of CKAN plugins developed for helix project",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='ckan catalog open-data',
    author='Michail Alexakis',
    author_email='alexakis@imis.athena-innovation.gr',
    url='https://github.com/helix/ckanext-helix',
    license='GPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    paster_plugins=['pylons', 'ckan'],
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        # Note: Moved under requirements.txt
    ],
    entry_points=\
    """
        [ckan.plugins]

        helix_dataset = ckanext.helix.plugins:DatasetForm
        
        helix_multilingual_dataset = ckanext.helix.plugins:MultilingualDatasetForm
        
        helix_package = ckanext.helix.plugins:PackageController

        helix_errorware = ckanext.helix.plugins:ErrorHandler

        helix_vector = ckanext.helix.storers.vector.plugin:VectorStorer

        helix_raster = ckanext.helix.storers.raster.plugin:RasterStorer
       
        helix_analytics = ckanext.helix.analytics.plugin:AnalyticsPlugin

        [paste.paster_command]
        
        helix = ckanext.helix.commands:Command
        
        #helix-example1 = ckanext.helix.commands:Example1

        [babel.extractors]
        
        helix_extract_json = ckanext.helix.lib.vocabularies.babel_extractors:extract_json
        
        [fanstatic.libraries]
        
        [ckan.celery_task]
        
        vector_tasks = ckanext.helix.storers.vector.celery_import:task_imports
    
        raster_taks = ckanext.helix.storers.raster.celery_import:task_imports
        
    """,
    # The following only stands as an example. The actual message_extractors should be defined into 
    # ckan's setup.py (from where message extraction is invoked).
    message_extractors = {
        'ckanext/helix': [
            #('reference_data/inspire-vocabularies.json', 'helix_extract_json', None),
            ('reference_data/language-codes.json', 'helix_extract_json', None),
            ('**.py', 'python', None),
            ('**.html', 'ckan', None),
            #('multilingual/solr/*.txt', 'ignore', None),
            #('**.txt', 'genshi', {
            #    'template_class': 'genshi.template:TextTemplate'
            #}),
        ]
    }
)
