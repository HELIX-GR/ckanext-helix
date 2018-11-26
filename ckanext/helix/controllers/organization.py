import logging

from ckan.lib.base import c, model, request, render, h
from ckan.common import _, config, OrderedDict
from ckan.lib.base import abort
import ckan.lib.maintain as maintain
import ckan.lib.search as search
import ckan.lib.plugins as lib_plugins
import ckan.plugins.toolkit as toolkit
import ckan.authz as authz

from ckan.controllers.organization import OrganizationController  as oController
from ckan.controllers.group import GroupController

lookup_group_controller = lib_plugins.lookup_group_controller
get_action = toolkit.get_action
from six import string_types

class Controller(GroupController):

    def read(self, id, limit=10):
        oc = oController()
        group_type = oc._ensure_controller_matches_group_type(
            id.split('@')[0])

        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'schema': oc._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        data_dict = {'id': id, 'type': group_type}

        # unicode format (decoded from utf8)
        c.q = request.params.get('q', '')

        try:
            # Do not query for the group datasets when dictizing, as they will
            # be ignored and get requested on the controller anyway
            data_dict['include_datasets'] = False
            c.group_dict = oc._action('group_show')(context, data_dict)
            c.group = context['group']
        except (NotFound, NotAuthorized):
            abort(404, _('Group not found'))

        self._read(id, limit, group_type)
        return render(oc._read_template(c.group_dict['type']),
                      extra_vars={'group_type': group_type})

    def _read(self, id, limit, group_type):
        oc = oController()
        ''' This is common code used by both read and bulk_process'''
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'schema': oc._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q = request.params.get('q', '')
        # Search within group
        if c.group_dict.get('is_organization'):
            fq = 'owner_org:"%s"' % c.group_dict.get('id')
        else:
            fq = 'groups:"%s"' % c.group_dict.get('name')

        c.description_formatted = \
            h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        page = h.get_page_number(request.params)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']
        sort_by = request.params.get('sort', None)

        def search_url(params):
            controller = lookup_group_controller(group_type)
            action = 'bulk_process' if c.action == 'bulk_process' else 'read'
            url = h.url_for(controller=controller, action=action, id=id)
            params = [(k, v.encode('utf-8') if isinstance(v, string_types)
                       else str(v)) for k, v in params]
            return url + u'?' + urlencode(params)

        def drill_down_url(**by):
            return h.add_url_param(alternative_url=None,
                                   controller='group', action='read',
                                   extras=dict(id=c.group_dict.get('name')),
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            controller = lookup_group_controller(group_type)
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller=controller, action='read',
                                      extras=dict(id=c.group_dict.get('name')))

        c.remove_field = remove_field

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))
            return search_url(params)

        try:
            c.fields = []
            c.fields_grouped = {}
            search_extras = {}
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        q += ' %s: "%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            facets = OrderedDict()

            default_facet_titles = {'organization': _('Organizations'),
                                    'groups': _('Groups'),
                                    'closed_tag': _('Subjects'),
                                    'tags': _('Tags'),
                                    'res_format': _('Formats'),
                                    'license_id': _('Licenses')}

            for facet in h.facets():
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Facet titles
            oc._update_facet_titles(facets, group_type)
            
            c.user_role = authz.users_role_for_group_or_org(id, c.user) or 'member'
           
            #if user is a member he shouldn't see all private datasets of organizations
            if (c.user_role == 'member'):
                include_private = False
            else:
                include_private = True
            data_dict = {
                'q': q,
                'fq': fq,
                'include_private': include_private,
                'facet.field': facets.keys(),
                'rows': limit,
                'sort': sort_by,
                'start': (page - 1) * limit,
                'extras': search_extras
            }

            context_ = dict((k, v) for (k, v) in context.items()
                            if k != 'schema')
            query = get_action('package_search')(context_, data_dict)

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )

            c.group_dict['package_count'] = query['count']

            c.search_facets = query['search_facets']
            c.search_facets_limits = {}
            for facet in c.search_facets.keys():
                limit = int(request.params.get('_%s_limit' % facet,
                            config.get('search.facets.default', 10)))
                c.search_facets_limits[facet] = limit
            c.page.items = query['results']

            c.sort_by_selected = sort_by

        except search.SearchError as se:
            log.error('Group search error: %r', se.args)
            c.query_error = True
            c.page = h.Page(collection=[])

        oc._setup_template_variables(context, {'id': id},
                                       group_type=group_type)
        

    def edit(self, id, data=None, errors=None, error_summary=None):
        oc = oController()
        group_type = oc._ensure_controller_matches_group_type(
            id.split('@')[0])

        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'save': 'save' in request.params,
                   'for_edit': True,
                   'parent': request.params.get('parent', None)
                   }
        data_dict = {'id': id, 'include_datasets': False}

        if context['save'] and not data:
            return oc._save_edit(id, context)

        try:
            data_dict['include_datasets'] = False
            old_data = oc._action('group_show')(context, data_dict)
            c.grouptitle = old_data.get('title')
            c.groupname = old_data.get('name')
            data = data or old_data
        except (NotFound, NotAuthorized):
            abort(404, _('Group not found'))

        group = context.get("group")
        c.group = group
        c.group_dict = oc._action('group_show')(context, data_dict)
        c.user_role = authz.users_role_for_group_or_org(id, c.user)
        if c.user_role == 'editor':
            context['ignore_auth'] = True
        try:
            oc._check_access('group_update', context)
        except NotAuthorized:
            abort(403, _('User %r not authorized to edit %s') % (c.user, id))

        errors = errors or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'edit',
                'group_type': group_type}

        oc._setup_template_variables(context, data, group_type=group_type)
        c.form = render(oc._group_form(group_type), extra_vars=vars)
        return render(oc._edit_template(c.group.type),
                      extra_vars={'group_type': group_type})