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

 * `helix_dataset`: Provides validation logic, storage logic and ui controls for schema-following metadata (e.g. DATACITE).
 * `helix_package`: Provides synchronization of package metadata to other databases (e.g. to the integrated CSW service, through pycsw).
Configure
---------

Here we cover some of the basic configuration settings for `ckanext-helix`.

The most common settings are:



    # Specify which dataset types are enabled
    ckanext.helix.dataset_types = datacite

    # Add extra top-level (i.e not contained in schema) metadata fields. This is usually needed to provide 
    # a bridge to 3rd-party plugins that expect certain fields to be present (e.g. `spatial` from `spatial_metadata`).
    ckanext.helix.extra_fields = spatial
    ckanext.helix.validation.relax_name_pattern = true
    ckanext.helix.api_resource_formats = wms wcs wfs csw


Configuration for other plugins:

    #ckanext_scheming configuration:

    scheming.organization_schemas = ckanext.scheming:helix_organization_schema.json
    scheming.group_schemas = ckanext.scheming:helix_group_schema.json


    #ckanext-userautoadd configuration:

    # The organization to which new users are added
    ckan.userautoadd.organization_name = helix

    # The role the new users will have
    ckan.userautoadd.organization_role = member

    #ckanext.spatial configuration:

    ckan.spatial.srid = 4326
    ckanext.spatial.common_map.type = custom
    ckanext.spatial.common_map.custom.url = http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png
    ckanext.spatial.common_map.attribution = &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a> 


Manage
------

The `helix` command suite provides several subcommands to help managing the extension. Retreive a full list of available subcommands (along with their help):

    paster helix --config /path/to/development.ini

To get help on a particular subcommand (e.g. `widget-info`):

    paster helix --config /path/to/development.ini widget-info --help
    
Uninstall
---------

    paster helix --config /path/to/development.ini cleanup

