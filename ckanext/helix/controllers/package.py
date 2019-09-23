import datetime
import os
import cgi
import logging
import copy
import uuid

from pylons import g, config, session

from ckan.lib.base import (
    c, request, response, render, abort, BaseController)
import ckan.model as model
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
import ckanext.helix.lib.template_helpers as ext_h
import cStringIO
import ckan.logic as logic
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.controllers.package import PackageController  as pController

from ckanext.helix.lib import uploader
from ckanext.helix.lib import actions as ext_actions
from ckanext.helix.lib import metadata as ext_metadata


from ._helpers import authenticated

log = logging.getLogger(__name__)

CACHE_PARAMETERS = ['__cache', '__no_cache__']
_ = toolkit._
_url = toolkit.url_for
_get_action = toolkit.get_action
_check_access = toolkit.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
flatten_to_string_key = logic.flatten_to_string_key
lookup_package_plugin = lib_plugins.lookup_package_plugin

class Controller(BaseController):

    def __after__(self):
        session.save()
        return

    def _import_metadata(self, post):
        '''Handle a submitted import_metadata form.
        Return a redirection URL.
        '''

        redirect_url = None

        #
        # Read and validate post parameters
        #

        # Note Authorization is enforced by the underlying action.
        owner_org = post.get('owner_org')
        if not owner_org:
            abort(400, 'The owner organization is not given')

        uv = {'group': owner_org}
        uv.update(request.urlvars)
        redirect_url = _url(**uv)

        dtype = post.get('dataset_type')
        log.debug('post %s', post)
        log.debug('dtype: %s, dataset_types %s ', dtype, ext_h.get_dataset_types())
        if not dtype in ext_h.get_dataset_types():
            abort(400, 'Unknown metadata schema')

        rename_if_conflict = post.get('rename', '') == 'y'
        continue_on_errors = post.get('force_create', '') == 'y'

        # Examine source (an upload or a link)
        # Todo Remember orig_metadata_source (as source_url)

        source_url = None
        source = post.get('source')
        source_upload = post.get('source-upload')

        if source:
            # Assume source is provided as a URL
            source_url = source
        elif isinstance(source_upload, cgi.FieldStorage):
            # Assume source is an uploaded file
            up = uploader.MetadataUpload(source_upload.filename)
            up.update_data_dict(dict(post), 'source-upload')

            try:
                up.upload(max_size=1)
            except Exception as ex:
                log.error('Failed to save uploaded file %r: %s',
                          source_upload.filename, ex.message)
                abort(400, 'Failed to upload file')
            source_url = _url(
                controller='ckanext.helix.controllers.files:Controller',
                action='download_file',
                object_type=up.object_type,
                name_or_id=up.filename,
                filename=source_upload.filename)
            source = source_upload.file
            source.seek(0, 0)
            # Provide a file-like object as source
            #source = source_upload.file
            #log.debug('\n\n source:  %s ,type: %s, up is %s , source url is %s, source_upload is %s  \n\n', source, type(source),up, source_url, source_upload)
            #log.debug('\n source_upload:  %s ,  value is %s\n\n', source_upload, source.getvalue())
            # for attr in dir(source_upload):
            #				       		log.info(" source upload.%s = %r" % (attr, getattr(source_upload, attr)))

            # for attr in dir(source):
            # 	log.info("source.%s = %r" % (attr, getattr(source, attr)))
            #source.seek(0, 0)
        else:
            # No source given
            session['error_summary'] = _(
                'No source specified: Upload or link to an XML file.')
            return redirect_url

        #
        # Invoke dataset_import action
        #

        context = {
            'model': model,
            'session': model.Session,
            'api_version': 3
        }

        data_dict = {
            'source': source,
            'owner_org': owner_org,
            'dtype': dtype,
            'rename_if_conflict': rename_if_conflict,
            'continue_on_errors': continue_on_errors,
        }

        try:
            result = _get_action('dataset_import')(context, data_dict)
        except ext_actions.Invalid as ex:
            log.error('Cannot import package (invalid input): %r' %
                      (ex.error_dict))
            if len(ex.error_dict) > 1:
                session['error_summary'] = _('Received invalid input (%s)' % (
                    ','.join(ex.error_dict.keys())))
                session['errors'] = ex.error_dict
            else:
                session['error_summary'] = next(ex.error_dict.itervalues())
        except (ext_actions.IdentifierConflict, ext_actions.NameConflict) as ex:
            log.error('Cannot import package (name/id conflict): %r' %
                      (ex.error_dict))
            session['error_summary'] = ex.error_summary
        except toolkit.ValidationError as ex:
            # The input is valid, but results in an invalid package
            log.error('Cannot import package (metadata are invalid): %r' %
                      (ex.error_dict))
            session['error_summary'] = _('The given metadata are invalid.')
            session['errors'] = ex.error_dict
        except AssertionError as ex:
            raise
        except Exception as ex:
            log.error('Cannot import package (unexpected error): %s' % (ex))
            abort(400, 'Cannot import package')
        else:
            # Success: save result and redirect to success page
            session['result'] = result

        # Done
        return redirect_url

    @authenticated
    def import_metadata(self, **kwargs):
        if request.method == 'POST':
            redirect_url = self._import_metadata(request.params)
            h.redirect_to(redirect_url)
        else:
            c.group_id = request.params.get('group')
            c.error_summary = session.pop('error_summary', None)
            c.errors = session.pop('errors', None)
            c.result = session.pop('result', None)
            return render('package/import_metadata.html')

    @authenticated
    def translate_metadata(self, name_or_id, **kwargs):

        from ckanext.helix.lib.metadata import widgets

        context = {
            'model': model,
            'session': model.Session,
            'api_version': 3,
            'translate': False
        }

        pkg = _get_action('package_show')(context, {'id': name_or_id})

        # Check authorization

        _check_access(
            'package_translation_update', context, {'org': pkg['owner_org']})

        # Render

        c.pkg_dict = pkg

        return render('package/translate_metadata.html')

    def _package_form(self, package_type=None):
        return lookup_package_plugin(package_type).package_form()

    def _setup_template_variables(self, context, data_dict, package_type=None):
        return lookup_package_plugin(package_type).\
            setup_template_variables(context, data_dict)



    def _new_template(self, package_type):
        return lookup_package_plugin(package_type).new_template()

    def _guess_package_type(self, expecting_name=False):
        """
            Guess the type of package from the URL handling the case
            where there is a prefix on the URL (such as /data/package)
        """

        # Special case: if the rot URL '/' has been redirected to the package
        # controller (e.g. by an IRoutes extension) then there's nothing to do
        # here.
        if request.path == '/':
            return 'dataset'

        parts = [x for x in request.path.split('/') if x]

        idx = -1
        if expecting_name:
            idx = -2

        pt = parts[idx]
        if pt == 'package':
            pt = 'dataset'

        return pt

    def _get_package_type(self, id):
        """
        Given the id of a package this method will return the type of the
        package, or 'dataset' if no type is currently set
        """
        pkg = model.Package.get(id)
        if pkg:
            return pkg.type or 'dataset'
        return None    


    def new_resource(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']
            resource_id = data['id']
            del data['id']

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}

            # see if we have any data that we are trying to save
            data_provided = False
            for key, value in data.iteritems():
                if ((value or isinstance(value, cgi.FieldStorage))
                        and key != 'resource_type'):
                    data_provided = True
                    break

            if not data_provided and save_action != "go-dataset-complete":
                if save_action == 'go-dataset':
                    # go to final stage of adddataset
                    h.redirect_to(h.url_for(controller='package',
                                            action='edit', id=id))
                # see if we have added any resources
                try:
                    data_dict = _get_action('package_show')(context, {'id': id})
                except NotAuthorized:
                    abort(401, _('Unauthorized to update dataset'))
                except NotFound:
                    abort(404,
                          _('The dataset {id} could not be found.').format(id=id))
                if not len(data_dict['resources']):
                    # no data so keep on page
                    msg = _('You must add at least one data resource')
                    # On new templates do not use flash message
                    if g.legacy_templates:
                        h.flash_error(msg)
                        h.redirect_to(h.url_for(controller='ckanext.helix.controllers.package:Controller',
                                                action='new_resource', id=id))
                    else:
                        errors = {}
                        error_summary = {_('Error'): msg}
                        # made resource adding optional
                        h.redirect_to(controller='ckanext.helix.controllers.package:Controller',
                              action='new_metadata', id=id, data=data)
                        #return self.new_resource(id, data, errors, error_summary)
                    
                # we have a resource so let them add metadata
                h.redirect_to(controller='ckanext.helix.controllers.package:Controller',
                              action='new_metadata', id=id, data=data)

            data['package_id'] = id
            '''if 'size' not in data:
                if hasattr(data['upload'], 'filesize'):
                    data['size'] = data['upload'].filesize'''

            try:
                pkg_dict = _get_action('package_show')(context, {'id': id})
            except NotFound:
                abort(
                    404, _('The dataset {id} could not be found.').format(id=id))
            if 'size' not in data:
                if hasattr(data['upload'], 'filesize'):
                    pkg_dict['size'] = data['upload'].filesize
            log.debug('pkg dict resources are: %s', pkg_dict['resources'])

            try:
                if resource_id:
                    data['id'] = resource_id
                    _get_action('resource_update')(context, data)
                else:
                    _get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_resource(id, data, errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to create a resource'))
            except NotFound:
                abort(404,
                      _('The dataset {id} could not be found.').format(id=id))
            if save_action == 'go-metadata':
                # go to final stage of add dataset
                h.redirect_to(h.url_for(controller='ckanext.helix.controllers.package:Controller',
                                        action='new_metadata', id=id, data=data))
            elif save_action == 'go-dataset':
                # go to first stage of add dataset
                h.redirect_to(h.url_for(controller='package',
                                        action='edit', id=id))
            elif save_action == 'go-dataset-complete':
                # go to first stage of add dataset
                h.redirect_to(h.url_for(controller='package',
                                        action='read', id=id))
            else:
                # add more resources
                h.redirect_to(h.url_for(controller='ckanext.helix.controllers.package:Controller',
                                        action='new_resource', id=id))
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new'}
        vars['pkg_name'] = id
        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = _get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        try:
            _check_access('resource_create', context, {
                         "package_id": pkg_dict["id"]})
        except NotAuthorized:
            abort(401, _('Unauthorized to create a resource for this package'))

        # required for nav menu (stages)
        vars['pkg_dict'] = pkg_dict
        template = 'package/new_resource_not_draft.html'
        if pkg_dict['state'] == 'draft':
            vars['stage'] = ['complete', 'active']
            template = 'package/new_resource.html'
        elif pkg_dict['state'] == 'draft-complete':
            vars['stage'] = ['complete', 'active', 'complete']
            template = 'package/new_resource.html'
        elif pkg_dict['state'] == 'active':
            vars['stage'] = ['complete', 'active', 'complete']
            template = 'package/new_resource.html'

        return render(template, extra_vars=vars)

    def new_metadata(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']

            data_dict = _get_action('package_show')(context, {'id': id})

            data_dict['id'] = id
            
            # update the state
            if save_action == 'finish':
                # we want this to go live when saved
                data_dict['state'] = 'active'
            elif save_action in ['go-resources', 'go-dataset']:
                data_dict['state'] = 'draft-complete'
            # allow the state to be changed
            context['allow_state_change'] = True
            data_dict.update(data)
            try:
                _get_action('package_update')(context, data_dict)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_metadata(id, data, errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to update dataset'))
            if save_action == 'go-resources':
                # we want to go back to the add resources form stage
                h.redirect_to(h.url_for(controller='ckanext.helix.controllers.package:Controller',
                                        action='new_resource', id=id))
            elif save_action == 'go-dataset':
                # we want to go back to the add dataset stage
                h.redirect_to(h.url_for(controller='package',
                                        action='edit', id=id))

            h.redirect_to(
                h.url_for(controller='package', action='read', id=id))

        if not data:
            data = _get_action('package_show')(context, {'id': id})
        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'error_summary': error_summary}
        vars['pkg_name'] = id

        package_type = self._get_package_type(id)
        self._setup_template_variables(context, {},
                                       package_type=package_type)

        # changed to 2-stage creation 25-4
        # return render('package/new_package_metadata.html', extra_vars=vars)
        return render('package/new_package_finish.html', extra_vars=vars)

    def choose_schema(self, data=None, errors=None, error_summary=None):
        
        return render(u'snippets/choose_dtype.html')

    def new(self, data=None, errors=None, error_summary=None):

        schema_type = request.params.get('schema_type')

        if data and 'type' in data:
            package_type = data['type']
        else:
            package_type = self._guess_package_type(True)

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj,
                   'save': 'save' in request.params}

        # Package needs to have a organization group in the call to
        # check_access and also to save it
        try:
            _check_access('package_create', context)
        except NotAuthorized:
            abort(403, _('Unauthorized to create a package'))

        if context['save'] and not data:
            pc = pController()
            return pController._save_new(pc, context, package_type=package_type)

        data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
            request.params, ignore_keys=CACHE_PARAMETERS))))
        c.resources_json = h.json.dumps(data.get('resources', []))
        # convert tags if not supplied in data
        if data and not data.get('tag_string'):
            data['tag_string'] = ', '.join(
                h.dict_list_reduce(data.get('tags', {}), 'name'))

        errors = errors or {}
        error_summary = error_summary or {}
        # in the phased add dataset we need to know that
        # we have already completed stage 1
        stage = ['active']
        if data.get('state', '').startswith('draft'):
            stage = ['active', 'complete']

        # if we are creating from a group then this allows the group to be
        # set automatically
        data['group_id'] = request.params.get('group') or \
            request.params.get('groups__0__id')

        # add custom id for ckan name so we can have duplicate titles
        new_uuid = uuid.uuid4()
        data['name'] = new_uuid
        # set default visibility to private before admin/editor changes it to public
        data['private'] = 'True'
        # if not h.organizations_available('create_dataset'):

        # add to helix org as default
        #data['owner_org'] = 'helix'

        form_snippet = self._package_form(package_type=package_type)
        form_vars = {'data': data, 'errors': errors,
                     'error_summary': error_summary,
                     'action': 'new', 'stage': stage,
                     'dataset_type': package_type,
                     'schema_type': schema_type,
                     }
        c.errors_json = h.json.dumps(errors)

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        new_template = self._new_template(package_type)
        return render(new_template,
                      extra_vars={'form_vars': form_vars,
                                  'form_snippet': form_snippet,
                                  'dataset_type': package_type,
                                  })
