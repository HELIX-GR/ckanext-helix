import logging
import json
import time
import datetime

from pylons import g
from pylons.i18n import _

from ckan.lib.base import (BaseController, c, request, response, abort, redirect)
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic

import ckanext.publicamundi
from ckanext.publicamundi.lib.util import to_json
from ckanext.publicamundi.lib.metadata import vocabularies
from ckanext.publicamundi.controllers import helpers

from ckanext.publicamundi.lib.metadata.xml_serializers import *
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import *

log1 = logging.getLogger(__name__)

content_types = {
    'json': 'application/json; charset=utf8',
    'xml': 'text/xml'
}

class Controller(BaseController):

    # Autocomplete helpers
    
    def mimetype_autocomplete(self):
        q = request.params.get('incomplete', '')
        limit  = request.params.get('limit', 10)

        context = { 'model': model, 'session': model.Session }
        data_dict = { 'q': q, 'limit': limit }

        r = logic.get_action('mimetype_autocomplete')(context, data_dict)

        result_set = {
            'ResultSet': {
                'Result': [{'name': t } for t in r]
            }
        }

        response.headers['Content-Type'] = content_types['json']
        return [to_json(result_set)]

    # Vocabularies

    # Note: The 1st thought was to rely on CKAN's vocabulary/tag functionality.
    # But because (e.g. for INSPIRE-related thesauri) we need to distinguish 
    # between the human and the machine-friendly view of a term, we had to use
    # our own vocabularies. So, provided that we had some way to solve this,
    # the following api calls should not be needed any more.

    def vocabularies_list(self):
        response.headers['Content-Type'] = content_types['json']
        return [json.dumps(vocabularies.get_names())]

    def vocabulary_get(self, name):
        name = str(name)
        r = None
        
        vocab = vocabularies.get_by_name(name)
        if vocab:
            terms = vocab['vocabulary'].by_value
            r = {
                'date_type': vocab.get('date_type'),
                'reference_date': vocab.get('reference_date'),
                'title': vocab.get('title'),
                'name': vocab.get('name'),
                'terms': [{ 'value': k, 'title': terms[k].title } for k in terms],
            }
                
        response.headers['Content-Type'] = content_types['json']
        return [to_json(r)]

    # Export to XML/Json
    def export_to_type(self, id):
        rtype = request.params.get('type')
        if rtype:
            output = request.params.get('type')
        else:
            output = 'json'
        #file_output='json', name_or_id=None):
        dataset = self._show(id)
        dataset_type = dataset.get('dataset_type')
        obj = dataset.get(dataset_type)

        if output == 'xml':
            response.headers['Content-Type'] = content_types['xml']
            ser = xml_serializer_for_object(obj)
            return [ser.dumps()]
        else:
            response.headers['Content-Type'] = content_types['json']
            data = obj.to_json()
            return [data]

    # Helpers

    @classmethod
    def _get_action_context(cls):
        return {
            'model': model, 
            'session': model.Session, 
            'ignore_auth':True, 
            'api_version': 3,
        }

    def _prepare_inspire_draft(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data
        pkg_data['state'] = 'draft'

        pkg = self._create_or_update(pkg_data)
        return pkg


    def _prepare_inspire(self, insp):
        data = insp.to_dict(flat=1, opts={'serialize-keys': True})

        pkg_data = {}
        pkg_data['title'] = data.get('title')
        pkg_data['name'] = json_loader.munge(unidecode(data.get('title')))
        pkg_data['dataset_type'] = 'inspire'
        pkg_data['inspire'] = data

        pkg = self._create_or_update(pkg_data)
        return pkg

    def _create_or_update(self, data):
        context = self._get_action_context()
        # Purposefully skip validation at this stage
        context.update({ 'skip_validation': True })
        if self._package_exists(data.get('name')):
            # Not supporting package upload from xml
            pass
        else:
            pkg = toolkit.get_action ('package_create')(context, data_dict=data)
            log1.info('Created package %s' % pkg['name'])
        return pkg


    def _show(self, name_or_id):
        return toolkit.get_action ('package_show') (self._get_action_context(), data_dict = {'id': name_or_id})

    def _package_exists(self, name_or_id):
        return  name_or_id in toolkit.get_action ('package_list')(self._get_action_context(), data_dict={})

    def _check_result_for_read(self, data, result):
        pass
