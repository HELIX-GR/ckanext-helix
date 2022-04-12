import ckan.authz as authz
import ckan.plugins.toolkit as toolkit
_ = toolkit._


def organization_create_auth(context, data_dict=None):
    user = context['user']
    user = authz.get_user_id_for_username(user, allow_none=True)
    orgs = toolkit.get_action(u'organization_list_for_user')(
                {u'user': user}, {u'permission': u'admin'})
    if user and orgs:
        return {'success': True}
    else:
        return {'success': False,
            'msg': _('User %s not authorized to create organizations') % user}
    