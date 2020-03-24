import datetime
import os
import cgi
import logging

from paste import fileapp
from pylons import url

from ckan.lib.base import (
    c, request, response, render, abort, BaseController,)
import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.helix.cache_manager import get_cache
from ckanext.helix.lib.util import to_json
import ckanext.helix.lib.uploader as uploader
import ckanext.restricted.model as ext_model

from ckan.logic import get_action

log1 = logging.getLogger(__name__)

class Controller(BaseController):
    
    def download_file(self, object_type, name_or_id, filename=None):
        '''Download file from CKAN's filestore, grouped under `object_type` and
        identified by `name_or_id` inside this group.
        '''
        
        filepath = None
        if object_type == 'resources':
            up = uploader.ResourceUpload(resource={})
            filepath = up.get_path(name_or_id)
            app = fileapp.FileApp(filepath)
        elif object_type == 'source-metadata':
            up = uploader.MetadataUpload()
            filepath = up.get_path(name_or_id)
            app = fileapp.FileApp(filepath)
        elif object_type == 'metadata':
            val = get_cache('metadata').get(name_or_id)
            app = fileapp.DataApp(val, content_type='application/xml; charset=utf-8') 
        elif object_type== 'restricted_resources':
            resource_id = self._get_resource_id(name_or_id)
            context = {'model': model, 'session': model.Session, 
                      'user': c.user, 'auth_user_obj': c.userobj, 'ignore_auth': True}
            rsc = get_action('resource_show')(context, {'id': resource_id})
            filename = rsc['name']
            upload = uploader.ResourceUpload(resource=rsc)
            filepath = upload.get_path(rsc['id'])
            log1.info("Downloading restricted resource: %s" % (filepath))
            headers =  [
                ('Content-Disposition', 'attachment; filename=%s' % (str(filename))),
                ('Content-Type', str(rsc['mimetype']))
            ]
            app = fileapp.FileApp(filepath, headers=headers)
        else:
            abort(404, 'Unknown object-type')
        
        # Retreive file
        try:
            status, headers, app_it = request.call_application(app)
        except:
            abort(404, 'Not Found')
        response.headers.update(dict(headers))
        response.status = status
        # Dump
        return app_it

    def describe_file(self, object_type, name_or_id):
        # Todo
        pass
        
    def upload_file(self, object_type):
        
        name = request.params.get('name', '') # prefix
        upload_name = name + '-upload' if name else 'upload'

        upload = request.params.get(upload_name)
        if not isinstance(upload, cgi.FieldStorage):
            abort(400, 'Expected a file upload')
        
        result = None
        if object_type == 'resources':
            abort(400, 'Cannot handle uploading of resources here')
        elif object_type == 'source-metadata':
            up = uploader.MetadataUpload(upload.filename)
            up.update_data_dict(dict(request.params), upload_name)
            up.upload(max_size=1)
        
            link = toolkit.url_for(
                controller='ckanext.helix.controllers.files:Controller',
                action='download_file', 
                object_type=up.object_type,
                name_or_id=up.filename,
                filename=upload.filename)

            size = os.stat(u.filepath).st_size

            result = dict(name=u.filename, url=link, size=size)
        else:
            abort(404, 'Unknown object-type')

        response.headers['Content-Type'] = 'application/json'
        return [to_json(result)]

    def _get_resource_id(self, download_id):
        try:
            request = model.Session.query(ext_model.RestrictedRequest).filter_by(
                download_id=download_id, rejected_at=None).one_or_none()
            return request.resource_id
        except:
            abort(404, 'Not Found')
        
