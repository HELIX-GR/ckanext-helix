# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import datetime
import json
import weberror
import logging
import string
import urllib
import pylons

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckan.lib.search as search

import ckanext.helix.model as ext_model
import ckanext.helix.lib.metadata as ext_metadata
import ckanext.helix.lib.metadata.validators as ext_validators
import ckanext.helix.lib.actions as ext_actions
import ckanext.helix.lib.template_helpers as ext_template_helpers
import ckanext.helix.lib.helpers as ext_helpers
import ckanext.helix.lib.languages as ext_languages
import ckanext.helix.reference_data as ext_reference_data 
#import ckanext.helix.lib.pycsw_sync as ext_pycsw_sync
from ckan.lib.base import BaseController
import ckan.lib.plugins
from ckan.common import _,OrderedDict, config, json, request, c, g, response
import ckan.lib.base as base
from ckanext.helix.lib.helpers import min_title_length


import cgi
import ckan.lib.helpers as h

from ckanext.helix.lib.metadata import class_for_metadata
from ckanext.helix.lib.util import (to_json, random_name)
from six import string_types
from urllib import urlencode

NotFound = logic.NotFound
get_action = toolkit.get_action
_ = toolkit._
asbool = toolkit.asbool
aslist = toolkit.aslist
url_for = toolkit.url_for

log1 = logging.getLogger(__name__)

render = base.render
abort = base.abort



class DatasetForm(p.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''Override the default dataset form.
    '''
    
    p.implements(p.ITemplateHelpers)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IDatasetForm, inherit=True)
    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IActions, inherit=True)
    p.implements(p.IAuthFunctions, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    p.implements(p.IResourceController, inherit=True)
    p.implements(p.IFacets, inherit=True)

    _debug = False

    _dataset_types = None

    _extra_fields = None
    
    RESOURCE_TYPES = ['Audiovisual', 'Collection', 'DataPaper', 'Dataset', 'Event', 'Image', 'InteractiveResource', 'Model', 'PhysicalObject', 'Service', 'Software', 'Sound', 'Text', 'Workflow', 'Other']
    
    TITLE_TYPES = ['Alternative Title', 'Subtitle', 'Translated Title', 'Other']
    
    #CLOSED_TAGS = ['Alaska', 'California', 'Nevada','Oregon', 'Arizona', 'Colorado', 'Idaho', 'Utah', 'Delaware', 'Florida', 'Georgia', 'Indiana', 'Maryland' ] 

    ## Define helper methods ## 
    
    @classmethod
    def create_resource_types(cls):
        '''Create resource type vocabulary and tags, if they don't exist already.
        Note that you could also create the vocab and tags using CKAN's api,
        and once they are created you can edit them (add or remove items) using the api.
        '''
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}
        try:
            data = {'id': 'resource_types'}
            toolkit.get_action ('vocabulary_show') (context, data)
            log1.info("The resource-types vocabulary already exists. Skipping.")
        except toolkit.ObjectNotFound:
            log1.info("Creating vocab 'resource_types'")
            data = {'name': 'resource_types'}
            vocab = toolkit.get_action ('vocabulary_create') (context, data)
            for tag in cls.RESOURCE_TYPES:
                log1.info("Adding tag {0} to vocab 'resource_types'".format(tag))
                data = {'name': tag, 'vocabulary_id': vocab['id']}
                toolkit.get_action ('tag_create') (context, data)
    
    @classmethod
    def resource_types(cls):
        '''Return the list of all existing types from the resource_types vocabulary.'''
        cls.create_resource_types()
        try:
            resource_types = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'resource_types'})
            return resource_types
        except toolkit.ObjectNotFound:
            return None
    
    @classmethod
    def resource_types_options(cls):
        ''' This generator method is only useful for creating select boxes.'''
        for name in cls.resource_types():
            yield { 'value': name, 'text': name }
    
    
    @classmethod
    def create_closed_tags(cls):
        '''Create closed tag vocabulary and tags, if they don't exist already.
        Note that you could also create the vocab and tags using CKAN's api,
        and once they are created you can edit them (add or remove items) using the api.
        '''
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}
        
        try:
            data = {'id': 'closed_tags'}
            toolkit.get_action ('vocabulary_show') (context, data)
            log1.info("The closed tag vocabulary already exists. Skipping.")
        except toolkit.ObjectNotFound:
            log1.info("Creating vocabulary closed tags")
            data = {'name': 'closed_tags'}
            vocab = toolkit.get_action ('vocabulary_create') (context, data)
        data = {'id': 'closed_tags'}
        vocab = toolkit.get_action ('vocabulary_show') (context, data)
        closed_tags = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'closed_tags'})
        with open(ext_reference_data.get_path('closed-subject.txt')) as f: 
            closed_subjects = f.read().splitlines()
        for tag in closed_subjects:
            if tag not in closed_tags:
                log1.info("Adding tag {0} to vocab 'closed_tags'".format(tag))
                data = {'name': tag, 'vocabulary_id': vocab['id']}
                toolkit.get_action ('tag_create') (context, data)
    
    @classmethod
    def closed_tags(cls):
        '''Return the list of all existing types from the closed tags vocabulary.'''
        cls.create_closed_tags()
        try:
            closed_tags = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'closed_tags'})
            return closed_tags
        except toolkit.ObjectNotFound:
            return None
    
    @classmethod
    def create_languages(cls):
        '''Create languages vocabulary and tags, if they don't exist already.
        Note that you could also create the vocab and tags using CKAN's api,
        and once they are created you can edit them (add or remove items) using the api.
        '''
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}
        
        data = {'id': 'languages'}
        vocab = toolkit.get_action ('vocabulary_show') (context, data)
        languages = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'languages'})
        more_languages = None 
        with open(ext_reference_data.get_path('languages.txt')) as f: 
            more_languages = f.read().splitlines()
        for tag in more_languages:
            if tag not in languages:
                log1.info("Adding tag {0} to vocab 'languages'".format(tag))
                data = {'name': tag, 'vocabulary_id': vocab['id']}
                toolkit.get_action ('tag_create') (context, data)
    
    @classmethod
    def languages(cls):
        '''Return the list of all existing types from the closed tags vocabulary.'''
        cls.create_languages()
        try:
            languages = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'languages'})
            return languages
        except toolkit.ObjectNotFound:
            return None
    
    DATASET_CATEGORIES = ['BIO','GEO','STAT']
    @classmethod
    def create_dataset_categories(cls):
        '''Create dataset category vocabulary and tags, if they don't exist already.
        Note that you could also create the vocab and tags using CKAN's api,
        and once they are created you can edit them (add or remove items) using the api.
        '''
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}
        try:
            data = {'id': 'dataset_categories'}
            toolkit.get_action ('vocabulary_show') (context, data)
            log1.info("The dataset categories vocabulary already exists. Skipping.")
        except toolkit.ObjectNotFound:
            log1.info("Creating vocabulary dataset categories")
            data = {'name': 'dataset_categories'}
            vocab = toolkit.get_action ('vocabulary_create') (context, data)
        data = {'id': 'dataset_categories'}
        vocab = toolkit.get_action ('vocabulary_show') (context, data)
        categories = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'dataset_categories'})
        for tag in cls.DATASET_CATEGORIES:
            if tag not in categories:
                log1.info("Adding tag {0} to vocab 'dataset categories'".format(tag))
                data = {'name': tag, 'vocabulary_id': vocab['id']}
                toolkit.get_action ('tag_create') (context, data)  
    
    @classmethod
    def dataset_categories(cls):
        '''Return the list of all existing types from the dataset_categories vocabulary.'''
        cls.create_dataset_categories()
        try:
            dataset_categories = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'dataset_categories'})
            return dataset_categories
        except toolkit.ObjectNotFound:
            return None
    
    @classmethod
    def create_title_types(cls):
        '''Create title type vocabulary and tags, if they don't exist already.
        Note that you could also create the vocab and tags using CKAN's api,
        and once they are created you can edit them (add or remove items) using the api.
        '''
        user = toolkit.get_action('get_site_user')({'ignore_auth': True}, {})
        context = {'user': user['name']}
        try:
            data = {'id': 'title_types'}
            toolkit.get_action ('vocabulary_show') (context, data)
            log1.info("The title-types vocabulary already exists. Skipping.")
        except toolkit.ObjectNotFound:
            log1.info("Creating vocab 'title_types'")
            data = {'name': 'title_types'}
            vocab = toolkit.get_action ('vocabulary_create') (context, data)
            for tag in cls.TITLE_TYPES:
                log1.info("Adding tag {0} to vocab 'title_types'".format(tag))
                data = {'name': tag, 'vocabulary_id': vocab['id']}
                toolkit.get_action ('tag_create') (context, data)
    
    @classmethod
    def title_types(cls):
        '''Return the list of all existing types from the title_types vocabulary.'''
        cls.create_title_types()
        try:
            title_types = toolkit.get_action ('tag_list') (data_dict={ 'vocabulary_id': 'title_types'})
            return title_types
        except toolkit.ObjectNotFound:
            return None

    @classmethod
    def title_types_options(cls):
        ''' This generator method is only useful for creating select boxes.'''
        for name in cls.title_types():
            yield { 'value': name, 'text': name }

    @classmethod
    def organization_list_objects(cls, org_names = []):
        ''' Make a action-api call to fetch the a list of full dict objects (for each organization) '''
        context = {
            'model': model,
            'session': model.Session,
            'user': toolkit.c.user,
        }

        options = { 'all_fields': True }
        if org_names and len(org_names):
            t = type(org_names[0])
            if   t is str:
                options['organizations'] = org_names
            elif t is dict:
                options['organizations'] = map(lambda org: org.get('name'), org_names)

        return logic.get_action('organization_list') (context, options)

    @classmethod
    def organization_dict_objects(cls, org_names = []):
        ''' Similar to organization_list_objects but returns a dict keyed to the organization name. '''
        results = {}
        for org in cls.organization_list_objects(org_names):
            results[org['name']] = org
        return results
    
    @classmethod
    def dataset_types(cls):
        '''Provide a dict of supported dataset types'''
        return cls._dataset_types

    @classmethod
    def dataset_type_options(cls):
        '''Provide options for dataset-type (needed for selects)'''
        for name in cls._dataset_types:
            yield {'value': name, 'text': name.upper()}

    ## ITemplateHelpers interface ##

    def get_helpers(self):
        '''Return a dict of named helper functions (ITemplateHelpers interface).
        These helpers will be available under the 'h' thread-local global object.
        '''

        return {
            'debug': lambda: self._debug,
            'is_multilingual_dataset': False,
            'random_name': random_name,
            'filtered_list': ext_template_helpers.filtered_list,
            'dataset_types': self.dataset_types,
            'dataset_type_options': self.dataset_type_options,
            'organization_objects': ext_template_helpers.get_organization_objects,
            'make_metadata': ext_metadata.make_metadata,
            'markup_for_field': ext_metadata.markup_for_field,
            'markup_for_object': ext_metadata.markup_for_object,
            'markup_for': ext_metadata.markup_for,
            'resource_ingestion_result': ext_template_helpers.resource_ingestion_result,
            'get_primary_metadata_url': ext_template_helpers.get_primary_metadata_url,
            'get_ingested_raster': ext_template_helpers.get_ingested_raster,
            'get_ingested_vector': ext_template_helpers.get_ingested_vector,
            'transform_to_iso_639_2': ext_template_helpers.transform_to_iso_639_2,
            'resource_types': self.resource_types,
            'resource_types_options': self.resource_types_options,
            'closed_tags': self.closed_tags,
            'dataset_categories': self.dataset_categories,
            'languages': self.languages,
            'title_types': self.title_types,
            'title_types_options': self.title_types_options,
            'organization_list_objects': self.organization_list_objects,
            'organization_dict_objects': self.organization_dict_objects,
            'update_facets': self.update_facets,
            'dataset_facets': self.dataset_facets
        }

    ## IConfigurer interface ##

    def update_config(self, config):
        '''Configure CKAN (Pylons) environment'''

        # Setup static resources

        p.toolkit.add_public_directory(config, 'public')
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_template_directory(config, 'templates_legacy')
        p.toolkit.add_resource('public', 'ckanext-helix')
        
        #override default pager helper function
        h.Page.pager = ext_template_helpers.pager
        
        return

    ## IConfigurable interface ##

    def configure(self, config):
        '''Pass configuration to plugins and extensions'''
        
        cls = type(self)

        # Are we in debug mode?

        cls._debug = asbool(config['global_conf']['debug'])
        
        # Set supported dataset types
        
        known_dtypes = set(aslist(config['ckanext.helix.dataset_types']))
        
        # Todo Load external schemata/classes if provided
        
        ext_metadata.setup()
        registered_dtypes = ext_metadata.dataset_types

        cls._dataset_types = known_dtypes & registered_dtypes

        # Set extra (not included in supported schemata) fields

        cls._extra_fields = aslist(config.get('ckanext.helix.extra_fields', ''))

        # Modify the pattern for valid names for {package, groups, organizations}
        
        if asbool(config.get('ckanext.helix.validation.relax_name_pattern')):
            logic.validators.name_match = re.compile('[a-z0-9~_\-]*$')
            log1.debug('Using pattern for valid names: %r', 
                logic.validators.name_match.pattern)
        # Setup extension-wide cache manager

        from ckanext.helix import cache_manager
        cache_manager.setup(config)
    
        return

    ## IRoutes interface ##

    def before_map(self, mapper):
        '''Setup routes before CKAN defines core routes.'''

        from routes.mapper import SubMapper
        
        api_controller = 'ckanext.helix.controllers.api:Controller'
  
        with SubMapper(mapper, controller=api_controller) as m:
        
            m.connect(
                '/api/helix/util/resource/mimetype_autocomplete',
                action='resource_mimetype_autocomplete')
        
            m.connect(
                '/api/helix/util/resource/format_autocomplete',
                action='resource_format_autocomplete')

            m.connect(
                '/api/helix/vocabularies',
                action='vocabularies_list')
         
            m.connect(
                '/api/helix/vocabularies/{name}',
                action='vocabulary_get')
        
            m.connect(
                '/api/helix/dataset/export/{name_or_id}', 
                action='dataset_export')

            m.connect(
                '/api/helix/dataset/export_dcat/{name_or_id}',
                action='dataset_export_dcat')
        
            m.connect(
                '/api/helix/dataset/import', 
                action='dataset_import',
                conditions=dict(method=['POST']))

           

        user_controller = 'ckanext.helix.controllers.user:UserController'

        with SubMapper(mapper, controller=user_controller) as m:

            m.connect(
                'user_dashboard_resources',
                '/dashboard/resources',
                action='show_dashboard_resources')

            m.connect(
                'admin_page_resources',
                '/user/resources',
                 action='show_admin_page_resources')

            m.connect(
                'reject_resource',
                '/{parent}/resources/reject/{resource_id}',
                action='reject_resource')
            
            m.connect(
                'identify_vector_resource', # Fixme: adapt
                '/{parent}/resources/identify_vector/{resource_id}',
                action='identify_resource',
                storer_type='vector')
            
            m.connect(
                'render_ingestion',
                '/{parent}/resources/ingest/{resource_id}',
                action='render_ingestion_template')

            m.connect(
                'datasets',
                '/dashboard/datasets',
                action='datasets')
            
      
        files_controller = 'ckanext.helix.controllers.files:Controller'
        
        with SubMapper(mapper, controller=files_controller) as m:
        
            m.connect(
                '/helix/files/{object_type}/{name_or_id}/download/{filename:.*?}',
                action='download_file')
        
            m.connect(
                '/helix/files/{object_type}', 
                action='upload_file',
                conditions=dict(method=['POST']))
        
        package_controller = 'ckanext.helix.controllers.package:Controller'

        mapper.connect(
            '/dataset/import_metadata',
            controller=package_controller,
            action='import_metadata')
        
        mapper.connect('dataset_new', '/dataset/new', 
            controller=package_controller, action='new')
        mapper.connect('new_resource', '/dataset/new_resource/{id}',
            controller=package_controller, action='new_resource') 
        mapper.connect('new_metadata', '/dataset/new_metadata/{id}',
            controller=package_controller, action='new_metadata') 
        
        organization_controller = 'ckanext.helix.controllers.organization:Controller'

        #added because organization_read overrided default new org
        mapper.connect('organization_new', '/organization/new',controller='organization', action='new')
        #override organization read to restrict private dataset reading for members
        mapper.connect('organization_read', '/organization/{id}',controller=organization_controller, action='read')
        mapper.connect('organization_edit', '/organization/edit/{id}',controller=organization_controller, action='edit',
                  ckan_icon='pencil-square-o')     
        
        tests_controller = 'ckanext.helix.controllers.tests:Controller'

        mapper.connect(
            'helix-tests', 
            '/testing/helix/{action}/{id}',
            controller=tests_controller)
        
        mapper.connect(
            'helix-tests', 
            '/testing/helix/{action}',
            controller=tests_controller)
  

        return mapper

    def after_map(self, mapper):
        
        #added in after map to override default controller names ()
        mapper.connect('organization_new', '/organization/new',controller='organization', action='new')

        organization_controller = 'ckanext.helix.controllers.organization:Controller'
        #override organization read to restrict private dataset reading for members
        mapper.connect('organization_read', '/organization/{id}',controller=organization_controller, action='read')
        mapper.connect('organization_edit', '/organization/edit/{id}',controller=organization_controller, action='edit',
                  ckan_icon='pencil-square-o')
    
        return mapper

    ## IActions interface ##

    def get_actions(self):
        return {
            'mimetype_autocomplete': ext_actions.autocomplete.mimetype_autocomplete,
            'dataset_export': ext_actions.package.dataset_export,
            'dataset_import': ext_actions.package.dataset_import,
            'dataset_export_dcat': ext_actions.package.dataset_export_dcat,
            #'group_list_authz': ext_actions.group.group_list_authz,
            'favorite': ext_actions.package.favorite,
        }
    
    ## IAuthFunctions interface ##
    
    def get_auth_functions(self):
        '''Define new authorization checks or replace existing ones
        '''
        funcs = {
            # Relax the required conditions for adding to (thematic) groups    
            'member_create': ext_actions.group.member_create_check_authorized,
            'member_delete': ext_actions.group.member_delete_check_authorized,
        }
        return funcs

    ## IDatasetForm interface ##

    def is_fallback(self):
        '''
        Return True to register this plugin as the default handler for
        package types not handled by any other IDatasetForm plugin.
        '''
        return True

    def package_types(self):
        '''
        This plugin doesn't handle any special package types, it just
        registers itself as the default (above).
        '''
        return []


    def __modify_package_schema(self, schema):
        '''Define modify schema for both create/update operations.
        '''
        check_not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        default = toolkit.get_validator('default')
        from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid        
    
        def identifier_validator(value):
            ''' Demo of a typical behaviour inside a validator/converter '''

            if not value.isdigit():
                 raise Invalid("must include numbers only")
            return value
            pass

        def check_empty(value):
            ''' Check empty validator '''

            if not value:
                 raise Invalid("Field is required")
            return value
            pass
  
        
        # Add dataset-type, the field that distinguishes metadata formats
        is_dataset_type = ext_validators.is_dataset_type
        schema['dataset_type'] = [
            default('datacite'), convert_to_extras, 
            is_dataset_type,
        ]
       
        # Add package field-level validators/converters
        
        # Note We provide a union of fields for all supported schemata.
        # Of course, not all of them will be present in a specific dataset,
        # so any "required" constraint cannot be applied here.
        get_field_processor = ext_validators.get_field_edit_processor
        
        for dtype in self._dataset_types:
            cls1 = ext_metadata.class_for_metadata(dtype)  
            opts1 = {'serialize-keys': True, 'key-prefix': dtype}
            for field_name, field in cls1.get_flattened_fields(opts=opts1).items():
                # Build chain of processors for field
                schema[field_name] = [
                    ignore_missing, get_field_processor(field)]
        # Add before/after package-level processors

        preprocess_dataset = ext_validators.preprocess_dataset_for_edit
        postprocess_dataset = ext_validators.postprocess_dataset_for_edit
        
        schema['__before'].insert(-1, preprocess_dataset)

        if not '__after' in schema:
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset)
        
        # Add extra top-level fields (i.e. not bound to a schema)
        
        for field_name in self._extra_fields:
            schema[field_name] = [ignore_empty, convert_to_extras]
        
        # Add or replace resource field-level validators/converters

        #guess_resource_type = ext_validators.guess_resource_type_if_empty

        #schema['resources'].update({
         #   'resource_type': [
         #       guess_resource_type, string.lower, unicode],
          #  'format': [
          #      check_not_empty, string.lower, unicode],
        #})

        # Done, return updated schema

        # Update default validation schema (inherited from DefaultDatasetForm)

        schema.update({
            # Make organisation field optional
            #'owner_org': [
            #    toolkit.get_validator('ignore_missing'),
            #],
            'notes': [ 
                toolkit.get_validator('not_empty') 
            ],
            'title': [

                min_title_length,
                toolkit.get_validator('not_empty'),
            ],
            'notes_optional': [ 
                toolkit.get_validator('ignore_missing') ,
                toolkit.get_converter('convert_to_extras')
            ],
            'title_optional': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'dataset_category': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('dataset_categories')
            ],
            'closed_tag': [
                toolkit.get_validator('not_empty'),
                toolkit.get_converter('convert_to_tags')('closed_tags')
            ],
            'language_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('languages')
            ],
            'featured': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'title_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'identifier_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_name_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_family_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_given_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_name_identifier': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_name_identifier_scheme': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'creator_name_identifier_scheme_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            #'creator_affiliation': [
            #    toolkit.get_validator('ignore_missing'),
            #    toolkit.get_converter('convert_to_extras')
            #],
            #'publisher': [
                #check_empty,
            #    toolkit.get_converter('convert_to_extras')
            #],
            #'publication_year': [
            #    toolkit.get_validator('ignore_missing'),
            #    toolkit.get_converter('convert_to_extras')
            #],
            'subject': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'subject_scheme': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'subject_scheme_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')                
            ],
            'subject_value_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_family_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_given_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_name_identifier': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_name_identifier_scheme': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_name_identifier_scheme_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'contributor_affiliation': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'date': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            #'date_type': [
             #   toolkit.get_converter('convert_to_tags')('resource_types'),
              #  toolkit.get_validator('ignore_missing')
            #],
            'date_information': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'language': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'resource_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'resource_type_general': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_tags')('resource_types')
            ],
            'alternate_identifier': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'alternate_identifier_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'related_identifier': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'related_identifier_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'relation_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'related_metadata_scheme': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'related_metadata_scheme_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'related_metadata_scheme_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'license_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'funding_reference': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'funder_name': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'funder_identifier': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'funder_identifier_type': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'award_number': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'award_uri': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
            'award_title': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ],
        })   

        return schema

    def create_package_schema(self):
        schema = super(DatasetForm, self).create_package_schema()
        schema = self.__modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(DatasetForm, self).update_package_schema()
        schema = self.__modify_package_schema(schema)
        return schema

    def show_package_schema(self):


        schema = super(DatasetForm, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))
        
        check_not_empty = toolkit.get_validator('not_empty')
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')
        
        schema['dataset_type'] = [convert_from_extras, check_not_empty]
       
        # Add package field-level converters
        
        get_field_processor = ext_validators.get_field_read_processor

        for dtype in self._dataset_types:
            cls1 = ext_metadata.class_for_metadata(dtype)  
            opts1 = {'serialize-keys': True, 'key-prefix': dtype}
            for field_name, field in cls1.get_flattened_fields(opts=opts1).items():
                schema[field_name] = [
                    convert_from_extras, ignore_missing, get_field_processor(field)]
          
        # Add before/after package-level processors
        
        preprocess_dataset = ext_validators.preprocess_dataset_for_read
        postprocess_dataset = ext_validators.postprocess_dataset_for_read

        schema['__before'].insert(-1, preprocess_dataset)
        
        if not '__after' in schema:
            schema['__after'] = []
        schema['__after'].append(postprocess_dataset)
        
        # Add extra top-level fields (i.e. not under a schema)
        
        for field_name in self._extra_fields:
            schema[field_name] = [convert_from_extras, ignore_missing]

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(toolkit.get_converter('free_tags_only'))

        schema.update({
           
            # Make organisation field optional
            #'owner_org': [
            #    toolkit.get_validator('ignore_missing'),
            #],
            'notes': [
                toolkit.get_validator('not_empty')
            ],
            'closed_tag': [
                toolkit.get_converter('convert_from_tags')('closed_tags'),
                toolkit.get_validator('not_empty')
            ],
            'dataset_category': [
                toolkit.get_converter('convert_from_tags')('dataset_categories'),
                toolkit.get_validator('ignore_missing')
            ],
            'language_name': [
                toolkit.get_converter('convert_from_tags')('languages'),
                toolkit.get_validator('ignore_missing')
            ],
            'featured': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'title': [
                min_title_length,
                toolkit.get_validator('not_empty')
            ],
            'title_optional': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'notes_optional': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            # Add our extra field to the dataset schema.
            'title_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            #'identifier': [
            #    toolkit.get_converter('convert_from_extras'),
                #check_empty
            #],
            'identifier_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_name_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_family_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_given_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_name_identifier': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_name_identifier_scheme': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_name_identifier_scheme_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'creator_affiliation': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            #'publisher': [
            #    toolkit.get_converter('convert_from_extras'),
                #check_empty,
            #],
            #'publication_year': [
            #    toolkit.get_converter('convert_from_extras'),
            #    toolkit.get_validator('ignore_missing'),
            #],
            'subject': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'subject_scheme': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'subject_scheme_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'subject_value_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_family_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_given_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_name_identifier': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_name_identifier_scheme': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_name_identifier_scheme_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'contributor_affiliation': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'date': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing'),
            ],
            'date_information': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing'),
            ],
            'language': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'resource_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing'),
            ],
            'resource_type_general': [
                toolkit.get_converter('convert_from_tags')('resource_types'),
                toolkit.get_validator('ignore_missing')
            ],
            'alternate_identifier': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'alternate_identifier_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'related_identifier': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'related_identifier_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'relation_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'related_metadata_scheme': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'related_metadata_scheme_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'related_metadata_scheme_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'license_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'funding_reference': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'funder_name': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'funder_identifier': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'funder_identifier_type': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'award_number': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'award_uri': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
            'award_title': [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ],
        })
        
        # Done, return updated schema

        return schema

    def setup_template_variables(self, context, data_dict):
        ''' Setup (add/modify/hide) variables to feed the template engine.
        This is done through through toolkit.c (template thread-local context object).
        '''
        
        super(DatasetForm, self).setup_template_variables(context, data_dict)
        
        c = toolkit.c
        if c.search_facets:
            # Provide label functions for certain facets
            if not c.facet_labels:
                c.facet_labels = {
                    'res_format': lambda t: t['display_name'].upper()
                }

    # Note for all *_template hooks: 
    # We choose not to modify the path for each template (so we simply call super()). 
    # If a specific template's behaviour needs to be overriden, this can be done by 
    # means of template inheritance (e.g. Jinja2 `extends' or CKAN `ckan_extends')

    def new_template(self):
        return super(DatasetForm, self).new_template()

    def read_template(self):
        return super(DatasetForm, self).read_template()

    def edit_template(self):
        return super(DatasetForm, self).edit_template()

    def comments_template(self):
        return super(DatasetForm, self).comments_template()

    def search_template(self):
        return super(DatasetForm, self).search_template()

    def history_template(self):
        return super(DatasetForm, self).history_template()

    ## IPackageController interface ##
    
    def after_create(self, context, pkg_dict):
        log1.debug('after_create: Package %s is created', pkg_dict.get('name'))
        pass

    def after_update(self, context, pkg_dict):
        log1.debug('after_update: Package %s is updated', pkg_dict.get('name'))
        pass

    def after_show(self, context, pkg_dict, view=None):
    
        '''Hook into the validated data dict after the package is ready for display. 
        
        The main tasks here are:
         * Convert dataset_type-related parts of pkg_dict to a nested dict or an object.

        This hook is for reading purposes only, i.e for template variables, api results, 
        form initial values etc. It should *not* affect the way the read schema is used: 
        schema items declared at read_package_schema() should not be removed (though their 
        values can be changed!).
        ''' 
        c = toolkit.c
        #rr = c.environ['pylons.routes_dict'] if hasattr(c, 'environ') else {}
        if hasattr(c, 'environ') and c.environ:
            rr = c.environ['pylons.routes_dict']
        else:
            rr = {}

        is_validated = context.get('validate', True)
        if not is_validated:
            return # noop: extras are not yet promoted to 1st-level fields
    
        for_view = context.get('for_view', False)
        for_edit = ( # is this package prepared for edit ?
            (rr.get('controller') == 'package' and rr.get('action') == 'edit') or
            (rr.get('controller') in DatasetForm.after_show._api_controllers and 
                rr.get('action') == 'action' and
                rr.get('logic_function') in DatasetForm.after_show._api_edit_actions))
        return_json = ( # do we need to return a json-friendly result ?
            context.get('return_json', False) or
            (rr.get('controller') in DatasetForm.after_show._api_controllers and 
                rr.get('action') == 'action' and
                rr.get('logic_function') in DatasetForm.after_show._api_actions))

        log1.info(
            'Package %s is shown: for-view=%s for-edit=%s return-json=%s api=%s', 
            pkg_dict.get('name'), for_view, for_edit, return_json, context.get('api_version'))

        # Determine dataset_type-related parameters for this package
        
        key_prefix = dtype = pkg_dict.get('dataset_type')
        public_doi = pkg_dict.get('datacite.public_doi')
        if not dtype:
            return # noop: unknown dataset-type (pkg_dict has raw extras?)

        notes_optional=pkg_dict.get('notes_optional')
        title_optional=pkg_dict.get('title_optional')
        # Note Do not attempt to pop() flat keys here (e.g. to replace them by a 
        # nested structure), because resource forms will clear all extra fields !!

        # Turn to an object
        if dtype=='foo':
            return pkg_dict
        
        md = class_for_metadata(dtype).from_converted_data(pkg_dict)

        # Provide a different view, if not editing
        
        if (not for_edit) and view and callable(view):
            try:
                md = view(md)
            except Exception as ex:
                log1.warn('Cannot build view %r for package %r: %s',
                    view, pkg_dict.get('name'), str(ex))
                pass # noop: keep the original view
        
        pkg_dict[key_prefix] = md
        
        # Fix for json-friendly results (so json.dumps can handle them)
        
        # temporary fix for api actions (package_show) not containing c.environ

        if return_json or rr=={}:
            # Remove flat field values (won't be needed anymore)
            key_prefix_1 = key_prefix + '.'
            for k in (y for y in pkg_dict.keys() if y.startswith(key_prefix_1)):
                pkg_dict.pop(k)
            pkg_dict[key_prefix] = md.to_json(return_string=False)
            
        return pkg_dict
        
    
    after_show._api_show_actions = {
        'package_show', 'dataset_show', 'user_show'
    }
    after_show._api_edit_actions = {
        'package_create', 'package_update', 'dataset_create', 'dataset_update',
    }
    after_show._api_actions = {
        'package_create', 'package_update', 'dataset_create', 'dataset_update',
        'package_show', 'dataset_show', 'user_show' 
    }
    after_show._api_controllers = { 
        'api', 
        'ckanext.googleanalytics.controller:GAApiController' # intercepts API calls to record requests
    }

    def before_search(self, search_params):
        '''Return a modified (or not) version of the query parameters.
        '''
        #search_params['q'] = 'extras_boo:*';
        #search_params['extras'] = { 'ext_boo': 'far' }
        return search_params
   
    def after_search(self, search_results, search_params):
        '''Receive the search results, as well as the search parameters, and
        return a modified (or not) result with the same structure.
        '''
        #raise Exception('Breakpoint')
        return search_results

    def before_index(self, pkg_dict):
        '''Receive what will be given to SOLR for indexing.
        
        This is essentially a flattened dict (except for multi-valued fields 
        such as tags) of all the terms sent to the indexer.
        '''
        log1.debug('before_index: Package %s is indexed', pkg_dict.get('name'))
        if 'vocab_closed_tags' in pkg_dict:
            subjects= pkg_dict['vocab_closed_tags']
            
            #Add subjects for solr indexing/facet use

            pkg_dict['closed_tags'] = []
            for subject in subjects:
                pkg_dict['closed_tags'].append(subject)

        #Add resource size for solr indexing, get it from package show because resources are flattened
        context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            temp_pkg_dict = get_action('package_show')(context, {'id': pkg_dict.get('id')})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=pkg_dict.get('id')))        
        if temp_pkg_dict["resources"]:
            pkg_dict['res_size'] = []
            for resource in temp_pkg_dict["resources"]:
                pkg_dict['res_size'].append(resource['size'])


        return pkg_dict

    def before_view(self, pkg_dict):
        '''Receive the validated package dict before it is sent to the template. 
        '''

        log1.debug('before_view: Package %s is prepared for view', pkg_dict.get('name'))
        
        dtype = pkg_dict.get('dataset_type')
        pkg_name, pkg_id = pkg_dict['name'], pkg_dict['id']
        
        # Provide alternative download links for dataset's metadata 
        
        if dtype:
            download_links = pkg_dict.get('download_links', []) 
            if not download_links:
                pkg_dict['download_links'] = download_links
            download_links.extend([
                {
                    'title': dtype.upper(),
                    'url': url_for('/api/action/dataset_show', id=pkg_name),
                    'weight': 0,
                    'format': 'json',
                },
                {
                    'title': dtype.upper(),
                    'url': url_for(
                        controller='ckanext.helix.controllers.api:Controller',
                        action='dataset_export',
                        name_or_id=pkg_name),
                    'weight': 5,
                    'format': 'xml',
                },
                {
                    'title': 'GeoDCAT',
                    'url': url_for(
                        controller='ckanext.helix.controllers.api:Controller',
                        action='dataset_export_dcat',
                        name_or_id=pkg_name),
                    'weight': 7,
                    'format': 'xml',
                },
            ])
        
        return pkg_dict

    ## IResourceController interface ##

    def before_show(self, resource_dict):
        '''Receive the validated data dict before the resource is ready for display.
        '''
        
        # Normalize resource format (#66)
        # Note ckan.lib.dictization.model_dictize:resource_dictize converts only
        # some of the formats to uppercase (?), which leads to mixed cases.
        resource_dict['format'] = resource_dict['format'].lower()
        
        return resource_dict

    ## IFacets interface ##

    def dataset_facets(self, facets_dict=None, package_type=None):
        '''Update the facets_dict and return it.
        '''
        facets_dict['closed_tags'] = p.toolkit._('Subject') #add facet for Subject
        facets_dict['res_size'] = p.toolkit._('Resource size') #add facet for Res size
        if (package_type !="harvest"):
            if facets_dict['groups']:
                del facets_dict['groups']
            myorder = ['organization', 'closed_tags', 'tags', 'res_format', 'res_size',  'license_id']
            facets_dict = OrderedDict((k, facets_dict[k]) for k in myorder)
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        '''Update the facets_dict and return it.
        '''
        facets_dict['closed_tags'] = p.toolkit._('Subject') #add facet for Subject
        facets_dict['res_size'] = p.toolkit._('Resource size') #add facet for Subject
        if (package_type !="harvest"):
            if facets_dict['groups']:
                del facets_dict['groups']
            myorder = ['organization', 'closed_tags', 'tags', 'res_format', 'res_size',  'license_id']
            facets_dict = OrderedDict((k, facets_dict[k]) for k in myorder)
        c.facet_titles = facets_dict
        return facets_dict    

    def group_facets(self, facets_dict, group_type, package_type):
        '''Update the facets_dict and return it.
        '''
        facets_dict['closed_tags'] = p.toolkit._('Subject') #add facet for Subject
        facets_dict['res_size'] = p.toolkit._('Resource size') #add facet for Subject
        if (package_type !="harvest"):
            if facets_dict['groups']:
                del facets_dict['groups']
            myorder = ['organization', 'closed_tags', 'tags', 'res_format', 'res_size',  'license_id']
            facets_dict = OrderedDict((k, facets_dict[k]) for k in myorder)
        c.facet_titles = facets_dict
        #log1.debug('myorder: %s, c.facet_titles: %s', myorder, c.facet_titles)
        return facets_dict    

    def update_facets(self):

        #Update facets for advanced search
        
        facets = OrderedDict()

        default_facet_titles = {
                'organization': _('Organizations'),
                'closed_tag_facets': _('Subject'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'res_size': _('Resource size'),
                'license_id': _('Licenses'),
            }

        for facet in h.facets():
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet
        # Facet titles
        facets = self.dataset_facets(facets)

        c.facet_titles = facets
        
        data_dict = {
                'facet.field': facets.keys(),
                'rows': 0,
        }
        
        context = {'model': model, 'session': model.Session,
                       'user': c.user, 'for_view': True,
                       'auth_user_obj': c.userobj}
        query = get_action('package_search')(context, data_dict)
        #c.sort_by_selected = query['sort']
        c.search_facets = query['search_facets']

class PackageController(p.SingletonPlugin):
    '''Hook into the package controller
    '''

    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IPackageController, inherit=True)
    
    csw_output_schemata = {
        'dc': 'http://www.opengis.net/cat/csw/2.0.2',
        'iso-19115': 'http://www.isotc211.org/2005/gmd',
        'fgdc': 'http://www.opengis.net/cat/csw/csdgm',
        'atom': 'http://www.w3.org/2005/Atom',
        'nasa-dif': 'http://gcmd.gsfc.nasa.gov/Aboutus/xml/dif/',
    }
   
    _pycsw_config_file = None
    _pycsw_service_endpoint = None

    ## IConfigurable interface ##

    def configure(self, config):
        '''Apply configuration settings to this plugin
        '''
        
        cls = type(self)

        site_url = config['ckan.site_url']
        cls._pycsw_config_file = config.get(
            'ckanext.helix.pycsw.config', 
            'pycsw.ini')
        cls._pycsw_service_endpoint = config.get(
            'ckanext.helix.pycsw.service_endpoint', 
            '%s/csw' % (site_url.rstrip('/')))
        
        #ext_pycsw_sync.setup(site_url, self._pycsw_config_file)

        return

    ## IPackageController interface ##

    def after_create(self, context, pkg_dict):
        '''Extensions will receive the validated data dict after the package has been created
       
        Note that the create method will return a package domain object, which may not 
        include all fields. Also the newly created package id will be added to the dict.
        At this point, the package is possibly in 'draft' state so most Action-API 
        (targeting on the package itself) calls will fail.
        '''
        
        log1.debug('A package was created: %s', pkg_dict['id'])
        #self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_update(self, context, pkg_dict):
        '''Extensions will receive the validated data dict after the package has been updated
        
        Note that the edit method will return a package domain object, which may not include 
        all fields.
        '''
        
        log1.debug('A package was updated: %s', pkg_dict['id'])
        #self._create_or_update_csw_record(context['session'], pkg_dict)
        pass

    def after_delete(self, context, pkg_dict):
        '''Extensions will receive the data dict (typically containing just the package id)
        after the package has been deleted.
        '''

        log1.debug('A package was deleted: %s', pkg_dict['id'])
        #self._delete_csw_record(context['session'], pkg_dict)
        pass

    def after_show(self, context, pkg_dict):
        '''Receive the validated data dict after the package is ready for display. 
        
        Note that the read method will return a package domain object (which may 
        not include all fields).
        '''
        
        #log1.info('A package is shown: %s', pkg_dict)
        pass

    def before_search(self, search_params):
        '''Extensions will receive a dictionary with the query parameters just before are
        sent to SOLR backend, and should return a modified (or not) version of it.
        
        Parameter search_params will include an "extras" dictionary with all values from 
        fields starting with "ext_", so extensions can receive user input from specific fields.
        This "extras" dictionary will not affect SOLR results, but can be later be used by the
        after_search callback.
        '''
        # add resource size for solr indexing
        extras = search_params.get('extras')
        if not extras:
            # There are no extras in the search params, so do nothing.
            return search_params
        min_size= extras.get('ext_minsize')
        max_size = extras.get('ext_maxsize')
        fq = search_params['fq']
        fq = '{fq} +res_size:[{min_size} TO {max_size}]'.format(
            fq=fq, min_size=min_size, max_size=max_size)
        search_params['fq'] = fq

        return search_params

    def after_search(self, search_results, search_params):
        '''Extensions will receive the search results, as well as the search parameters,
        and should return a modified (or not) object with the same structure:
            {"count": "", "results": "", "facets": ""}
        
        Note that count and facets may need to be adjusted if the extension changed the results
        for some reason. Parameter search_params will include an extras dictionary with all 
        values from fields starting with "ext_", so extensions can receive user input from 
        specific fields. For example, the ckanext-spatial extension recognizes the "ext_bbox"
        parameter (inside "extras" dict) and handles it appropriately by filtering the results on one
        more condition (filters out those not contained in the specified bounding box)
        '''
        
        #raise Exception('Breakpoint')
        return search_results

    def before_index(self, pkg_dict):
        '''Extensions will receive what will be given to SOLR for indexing. This is essentially
        a flattened dict (except for multli-valued fields such as tags) of all the terms sent
        to the indexer. The extension can modify this by returning an altered version.
        '''
        
        
        
        return pkg_dict

    def before_view(self, pkg_dict):
        '''Extensions will recieve this before the dataset gets displayed.
        
        The dictionary returned will be the one sent to the template.
        '''
        
        dtype = pkg_dict.get('dataset_type')
        pkg_name, pkg_id = pkg_dict['name'], pkg_dict['id']

        # Provide CSW-backed download links for dataset's metadata 
       
        if dtype:
            download_links = pkg_dict.get('download_links', []) 
            if not download_links:
                pkg_dict['download_links'] = download_links
            download_links.extend([
                {
                    'title': 'DC',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='dc', output_format='application/xml'),
                    'weight': 10,
                    'format': 'xml',
                },
                {
                    'title': 'DC',
                    'generator': 'CSW',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='dc', output_format='application/json'),
                    'weight': 15,
                    'format': 'json',
                },
                {
                    'title': 'ISO-19115',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='iso-19115', output_format='application/xml'),
                    'weight': 15,
                    'format': 'xml',
                },
                {
                    'title': 'ISO-19115',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='iso-19115', output_format='application/json'),
                    'weight': 20,
                    'format': 'json',
                },
                {
                    'title': 'FGDC',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='fgdc', output_format='application/xml'),
                    'weight': 25,
                    'format': 'xml',
                },
                {
                    'title': 'Atom',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='atom', output_format='application/xml'),
                    'weight': 30,
                    'format': 'xml',
                },
                {
                    'title': 'NASA-DIF',
                    'generator': 'CSW',
                    'url': self._build_csw_request_url(
                        pkg_id, output_schema='nasa-dif', output_format='application/xml'),
                    'weight': 35,
                    'format': 'xml',
                },
            ])
        
        return pkg_dict

    ## Helpers ##
    
    def _build_csw_request_url(self, pkg_id, output_schema='dc', output_format=None):
        '''Build a GetRecordById request to a CSW endpoint
        '''
        
        qs_params = {
            'service': 'CSW',
            'version': '2.0.2',
            'request': 'GetRecordById',
            'ElementSetName': 'full',
            'OutputSchema': self.csw_output_schemata.get(output_schema, ''),
            'Id': pkg_id,
        }
        
        if output_format:
            qs_params['OutputFormat'] = output_format
 
        return self._pycsw_service_endpoint + '?' + urllib.urlencode(qs_params)

    def _create_or_update_csw_record(self, session, pkg_dict):
        '''Sync dataset with CSW record'''
        
        pkg_id = pkg_dict['id']

        if pkg_dict.get('state', 'active') != 'active':
            log1.info(
                'Skipped sync of non-active dataset %s to CSW record' % (pkg_id))
            return

        #record = ext_pycsw_sync.create_or_update_record(session, pkg_dict)
        #if record: 
        #    log1.info('Saved CswRecord %s (%s)', record.identifier, record.title)
        #else:
            log1.warning('Failed to save CswRecord for dataset %s' %(pkg_id))
        
        return

    def _delete_csw_record(self, session, pkg_dict):
        '''Delete CSW record'''
        #record = ext_pycsw_sync.delete_record(session, pkg_dict)
        #if record:
        #    log1.info('Deleted CswRecord for dataset %s', pkg_dict['id'])  
        return

class ErrorHandler(p.SingletonPlugin):
    '''Fix CKAN's buggy errorware configuration'''
    p.implements(p.IConfigurer, inherit=True)

    @staticmethod
    def _exception_as_mime_message(exc_data, to_addresses, from_address, prefix):
        from weberror.reporter  import as_str
        from weberror.formatter import format_text

        msg = weberror.reporter.MIMEText(format_text(exc_data)[0])
        msg['Subject'] = as_str(prefix + exc_data.exception_value)
        msg['From'] = as_str(from_address)
        msg['Reply-To'] = as_str(from_address)
        msg['To'] = as_str(", ".join(to_addresses))
        msg.set_type('text/plain')
        msg.set_param('charset', 'UTF-8')
        return msg

    def update_config(self, config):
        from weberror.reporter import EmailReporter as error_reporter
        
        # Override default config options for pylons errorware
        error_config = config['pylons.errorware']
        error_config.update({
            'error_subject_prefix' : config.get('ckan.site_title') + ': ',
            'from_address' : config.get('error_email_from'),
            'smtp_server'  : config.get('smtp.server'),
            'smtp_username': config.get('smtp.user'),
            'smtp_password': config.get('smtp.password'),
            'smtp_use_tls' : config.get('smtp.starttls'),
        })
        
        # Monkey-patch email error reporter 
        error_reporter.assemble_email = lambda t, exc: self._exception_as_mime_message(
            exc, 
            to_addresses=t.to_addresses, 
            from_address=t.from_address,
            prefix=t.subject_prefix)

class MultilingualDatasetForm(DatasetForm):
    '''Extend our basic dataset-form functionality to support multilingual datasets.
    
    This plugin is part of multilingual support in order to be able to:
      * tag fields of your schemata as translatable
      * translate field names (i.e key paths) for a schema
      * translate vocabularies referenced from a schema
      * translate user-supplied values for a certain dataset (web-based)
    
    '''

    ## IDatasetForm interface ## 

    def setup_template_variables(self, context, data_dict):
        super(MultilingualDatasetForm, self).setup_template_variables(context, data_dict)
        c = toolkit.c
        c.target_language = self.target_language()

    def create_package_schema(self):
        schema = super(MultilingualDatasetForm, self).create_package_schema()
        return self.__modify_package_schema(schema)

    def update_package_schema(self):
        schema = super(MultilingualDatasetForm, self).update_package_schema()
        return self.__modify_package_schema(schema)
    
    def show_package_schema(self):
        schema = super(MultilingualDatasetForm, self).show_package_schema()
        
        ignore_missing = toolkit.get_validator('ignore_missing')
        convert_from_extras = toolkit.get_converter('convert_from_extras')
        default = toolkit.get_validator('default')

        schema['language'] = [
            convert_from_extras, default(pylons.config['ckan.locale_default'])]
        return schema

    def __modify_package_schema(self, schema):
        
        ignore_empty = toolkit.get_validator('ignore_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        
        schema['language'] = [ignore_empty, convert_to_extras]
        schema['__after'].append(ext_validators.guess_language)
        return schema

    ## IPackageController interface ##

    def after_search(self, search_results, search_params):
        '''Try to replace displayed fields with their translations (if any).
        '''
        
        from ckanext.helix.lib.metadata import fields, bound_field
        from ckanext.helix.lib.metadata import class_for_metadata, translator_for
        
        uf = fields.TextField()
        lang = self.target_language()

        for pkg in search_results['results']:
            source_lang = pkg.get('language')
            if not source_lang or (source_lang == lang):
                continue # no need to translate
            dtype = pkg['dataset_type']
            md = class_for_metadata(dtype)(identifier=pkg['id']) 
            translator = translator_for(md, source_lang)
            # Lookup translations in the context of this package
            translated = False
            for k in ('title', 'notes'):
                tr = translator.get_field_translator(bound_field(uf, (k,), pkg[k]))
                yf = tr.get(lang) if tr else None
                if yf:
                    pkg[k] = yf.context.value
                    translated = True  
            # If at least one translation was found, mark as translated
            if translated:
                pkg['translated_to_language'] = lang
        
        return search_results

    def after_update(self, context, pkg_dict):
        log1.info('Discard translations for modified keys of package %s', pkg_dict['name'])
        # Todo: Discard translations for modified keys 
        pass
    
    def after_delete(self, context, pkg_dict):
        log1.info('Cleaning up translations for package %s', pkg_dict['id'])
        # Todo: Cleanup translations
        pass

    def after_show(self, context, pkg_dict):
        '''Hook into the validated data dict after the package is ready for display.
        '''
        
        from ckanext.helix.lib.metadata import fields, bound_field
        
        try:
            req_params = toolkit.request.params
        except:
            req_params = {} # not a web request

        dtype = pkg_dict.get('dataset_type')
        
        # Determine language context

        source_language = pkg_dict.get('language')
        language = self.target_language()
        
        # Decide if a translation must take place

        should_translate = None
        if 'translate' in context:
            should_translate = asbool(context['translate'])
        elif 'translate' in req_params:
            should_translate = asbool(req_params['translate'])
        else:
            should_translate = bool(source_language)

        # Build metadata object, translate if needed

        translated = None    
        if should_translate and (source_language != language):
            translated = self.TranslatedView(source_language, language)

        parent = super(MultilingualDatasetForm, self)
        pkg_dict = parent.after_show(context, pkg_dict, view=translated)
        if not pkg_dict:
            return # noop: super method returned prematurely
        md = pkg_dict[dtype]

        if not translated or not translated.translator:
            # Nothing more to do (either translation not needed or not working)
            return pkg_dict
 
        pkg_dict['translated_to_language'] = language

        # Apart from structured package metadata, try to translate:
        #  * core (CKAN) package metadata
        #  * core (CKAN) resource metadata
        
        uf = fields.TextField()
        field_translator = translated.translator.get_field_translator
        
        # Translate core package metadata
        for k in ('title', 'notes'):
            v = pkg_dict.get(k)
            if not v:
                continue # nothing to translate
            tr = field_translator(bound_field(uf, (k,), v))
            yf = tr.get(language) if tr else None
            if yf:
                pkg_dict[k] = yf.context.value
        
        # Translate core resource metadata
        # Todo
        
        return pkg_dict
    
    ## ITemplateHelpers interface ##
    
    def get_helpers(self):
        helpers = super(MultilingualDatasetForm, self).get_helpers()
        
        helpers.update({
            'is_multilingual_dataset': True,
            'target_language': self.target_language,
            'language_name': 
                lambda code: ext_languages.by_code(code).name,
            'markup_for_translatable_text': 
                ext_template_helpers.markup_for_translatable_text,
        })
        
        return helpers
    
    ## IAuthFunctions interface ##
    
    def get_auth_functions(self):
        funcs = super(MultilingualDatasetForm, self).get_auth_functions()
        funcs.update({
            'dataset_translation_update': 
                ext_actions.package.dataset_translation_check_authorized,
        })
        return funcs
    
    ## IActions interface ##

    def get_actions(self):
        actions = super(MultilingualDatasetForm, self).get_actions()
        actions.update({
            'dataset_translation_update': 
                ext_actions.package.dataset_translation_update,
            'dataset_translation_update_field':
                ext_actions.package.dataset_translation_update_field,
        })
        return actions
    
    ## IRoutes interface ##

    def before_map(self, mapper):
        mapper = super(MultilingualDatasetForm, self).before_map(mapper)
        
        mapper.connect(
            'dataset_translate',
            '/dataset/translate/{name_or_id}',
            controller = 'ckanext.helix.controllers.package:Controller',
            action = 'translate_metadata')

        return mapper

    ## Helpers ##
    
    class TranslatedView(object):
        
        def __init__(self, source_language, language):
            self.source_language = source_language
            self.language = language
            self.translator = None
            
        def __call__(self, md):
            assert self.translator is None, 'Expected to be called once!'
            self.translator = ext_metadata.translator_for(md, self.source_language)
            try:
                result = self.translator.get(self.language)
            except Exception as ex:
                self.translator = False # is unusable
                raise
            return result
    
    def target_language(self):
        '''Determine the target language for metadata.
        '''
        
        # A GET/POST request parameter always comes first
        try:
            params = toolkit.request.params
        except:
            params = None
        language = params.get('lang') if params else None
        
        # If absent, pick active language
        if not language:
            language = pylons.i18n.get_lang()
            language = language[0] if language else 'en'

        return language


