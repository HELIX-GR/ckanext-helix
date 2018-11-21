ckanext-helix
====================

This is a CKAN extension that hosts various plugins needed for helix project!

Install
-------

    pip install -r requirements.txt
    python setup.py develop
    paster helix --config /path/to/development.ini setup


Update CKAN configuration
-------------------------

Edit your CKAN .ini configuration file (e.g. your `development.ini`) and activate the
plugins as usual. For now, the supported plugins are:

 * `helix_dataset`: Provides validation logic, storage logic and ui controls for schema-following metadata (e.g. INSPIRE).
 * `helix_multilingual_dataset`: Extend `helix_dataset` to support multilingual metadata.
 * `helix_package`: Provides synchronization of package metadata to other databases (e.g. to the integrated CSW service, through pycsw).
 * `helix_vector`: Provide processing and services for vector-based spatial resources. See more at README-vector.md
 * `helix_raster`: Provide processing and services for raster-based spatial resources. See more at README-raster.md 
 * `helix_analytics`: Process backend logs to extract information on user requests. See more at README-analytics.md 


Configure
---------

Here we cover some of the configuration settings for only basic plugins of `ckanext-helix`. Settings which are specific to a _storer_ plugin (either 
`helix_vector` or `helix_raster`) are documented in their dedicated README file.

The most common settings are:

    # Specify which dataset types are enabled
    ckanext.helix.dataset_types = ckan inspire datacite
    ckanext.helix.extra_fields = spatial
    
    # Indicate whether a more relaxed name pattern can be used for dataset names
    ckanext.helix.validation.relax_name_pattern = true 
    
    # Specify a list of formats which should be considered as services (APIs)
    ckanext.helix.api_resource_formats = wms wcs wfs csw

    # Add extra top-level (i.e not contained in schema) metadata fields. This is usually needed to provide 
    # a bridge to 3rd-party plugins that expect certain fields to be present (e.g. `spatial` from `spatial_metadata`).
    ckanext.helix.extra_fields = spatial

    # Specify a list of pre-existing resource formats to be used as autocomplete suggestions
    ckanext.helix.resource_formats = 
    # raster file formats 
        geotiff bitmap png jpeg
    # vector file formats
        shapefile sqlite gml kml
    # services, apis
       %(ckanext.helix.api_resource_formats)s

    # Specify the path to pycsw configuration 
    ckanext.helix.pycsw.config = %(here)s/pycsw.ini

    # Specify the endpoint under which CSW service is running (if it exists)
    ckanext.helix.pycsw.service_endpoint = %(ckan.site_url)s/csw

Manage
------

The `helix` command suite provides several subcommands to help managing the extension. Retreive a full list of available subcommands (along with their help):

    paster helix --config /path/to/development.ini

To get help on a particular subcommand (e.g. `widget-info`):

    paster helix --config /path/to/development.ini widget-info --help
    
Uninstall
---------

    paster helix --config /path/to/development.ini cleanup

Copying and License
-------------------

This material is copyright (c) 2013-2016 of the helix development team.

It is Free Software and Open Source Software, licensed under the GNU Affero General Public License (AGPL) v3.0
whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html

More details at `LICENSE <https://github.com/helix/ckanext-helix/blob/master/LICENSE.txt`
