helix Vector Plugin
==========================


Overview
--------

The `helix_vector` plugin allows users to upload vector geospatial data, and store and publish through OGC services.


Installation
------------

**1.  Install required Debian packages**

Install compression-related libraries

    sudo apt-get install unzip unrar p7zip-full

Install GDAL libraries and Python bindings (at system-level):

    sudo apt-get install python-gdal   

**2.  Install plugin's requirements**

    pip install -r vectorstorer-requirements.txt

**2.1.  Install backend-specific requirements**

Depending on the publishing backend you choose (i.e. `geoserver` or `mapserver`), a set of additional
requirements must be met. So, according to your choice, run:

    pip install -r vectorstorer-geoserver-requirements.txt

or 

    pip install -r vectorstorer-mapserver-requirements.txt


Configuration
-------------

**1.  Enable**

  This plugin requires `helix_dataset` to be also enabled. To enable the plugin add this under `ckan.plugins` in the configuration file:
 
        ckan.plugins = ... helix_dataset helix_vector ...

    
**2.  Configure**

  The following should be set in the CKAN config:

        ckanext.helix.vectorstorer.temp_dir = %(cache_dir)s/vectorstorer
        ckanext.helix.vectorstorer.gdal_folder = (e.g. /usr/lib/python2.7/dist-packages)

Geoserver-specific configuration

        ckanext.helix.vectorstorer.geoserver.url = (e.g. http://www.example.com/geoserver)
        ckanext.helix.vectorstorer.geoserver.api_url = (e.g. http://geoserver.localdomain:8080/geoserver)
        ckanext.helix.vectorstorer.geoserver.workspace = (e.g. CKAN)
        ckanext.helix.vectorstorer.geoserver.username = (e.g. admin)
        ckanext.helix.vectorstorer.geoserver.password = (e.g. geoserver)
        ckanext.helix.vectorstorer.geoserver.datastore = (e.g. ckan_datastore_default)
        ckanext.helix.vectorstorer.geoserver.reload_url = (optional e.g. http://geoserver.localdomain:5005/reload)

Geoserver workspace and datastore have to be created in advance. The datastore must be the same as the CKAN datastore database.

Mapserver-specific configuration

        ckanext.helix.vectorstorer.mapserver.url = (e.g. http://ckan_services_server/cgi-bin/mapserv)
        ckanext.helix.vectorstorer.mapserver.mapfile_folder = (e.g. /var/www/mapserv/mapfiles)
        ckanext.helix.vectorstorer.mapserver.templates_folder = (e.g. /var/www/mapserv/templates)
    
If both mapserver and geoserver are both configured, default publishing server has to be specified:

        ckanext.helix.vectorstorer.default_publishing_server= (e.g. mapserver)
    
If not set, `geoserver` will be used as the default publishing server.

**3.  Prepare Datastore**

  Enable the PostGis extension in the datastore database.

