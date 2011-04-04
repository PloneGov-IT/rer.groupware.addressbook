from Products.LDAPUserFolder.LDAPDelegate import filter_format
from Products.LDAPUserFolder.utils import to_utf8,guid2string
STARTSWITH_FIELDS = ['sn','givenName','mail']
ENDSWITH_FIELDS = ['telephoneNumber',]
EXACT_FIELDS = ['employeeNumber',]
import logging
logger = logging.getLogger('event.LDAPUserFolder')
# Products.LDAPUserFolder-2.13
# LDAPUserFolder
def searchUsers(self, attrs=(), exact_match=False, **kw):
    """ Look up matching user records based on one or mmore attributes

    This method takes any passed-in search parameters and values as
    keyword arguments and will sort out invalid keys automatically. It
    accepts all three forms an attribute can be known as, its real
    ldap name, the name an attribute is mapped to explicitly, and the
    friendly name it is known by.
    """
    users  = []
    users_base = self.users_base
    search_scope = self.users_scope
    filt_list = []

    if not attrs:
        attrs = self.getSchemaConfig().keys()

    schema_translator = {}
    for ldap_key, info in self.getSchemaConfig().items():
        public_name = info.get('public_name', None)
        friendly_name = info.get('friendly_name', None)

        if friendly_name:
            schema_translator[friendly_name] = ldap_key

        if public_name:
            schema_translator[public_name] = ldap_key

        schema_translator[ldap_key] = ldap_key

    for (search_param, search_term) in kw.items():
        if search_param == 'dn':
            users_base = search_term
            search_scope = self._delegate.BASE

        elif search_param == 'objectGUID':
            # we can't escape the objectGUID query piece using filter_format
            # because it replaces backslashes, which we need as a result
            # of guid2string
            users_base = self.users_base
            guid = guid2string(search_term)

            if exact_match:
                filt_list.append('(objectGUID=%s)' % guid)
            else:
                filt_list.append('(objectGUID=*%s*)' % guid)

        else:
            # If the keyword arguments contain unknown items we will
            # simply ignore them and continue looking.
            ldap_param = schema_translator.get(search_param, None)
            if ldap_param is None:
                continue

            if search_term and exact_match:
                filt_list.append( filter_format( '(%s=%s)'
                                               , (ldap_param, search_term)
                                               ) )
            elif search_term:
                # monkey patch starts here
                if ldap_param in STARTSWITH_FIELDS:
                    filt_list.append( filter_format( '(%s=%s*)'
                                               , (ldap_param, search_term)
                                               ) )
                if ldap_param in ENDSWITH_FIELDS:
                    filt_list.append( filter_format( '(%s=*%s)'
                                               , (ldap_param, search_term)
                                               ) )
                elif ldap_param in EXACT_FIELDS:
                    filt_list.append( filter_format( '(%s=%s)'
                                               , (ldap_param, search_term)
                                               ) )
                else:
                    filt_list.append( filter_format( '(%s=*%s*)'
                                               , (ldap_param, search_term)
                                               ) )
                # monkey patch ends here
            else:
                filt_list.append('(%s=*)' % ldap_param)

    if len(filt_list) == 0 and search_param != 'dn':
        # We have no useful filter criteria, bail now before bringing the
        # site down with a search that is overly broad.
        res = { 'exception' : 'No useful filter criteria given' }
        res['size'] = 0
        search_str = ''

    else:
        search_str = self._getUserFilterString(filters=filt_list)
        res = self._delegate.search( base=users_base
                                   , scope=search_scope
                                   , filter=search_str
                                   , attrs=attrs
                # monkey patch starts here
                                   , convert_filter=False
                # monkey patch ends here
                                   )

    if res['exception']:
        logger.debug('findUser Exception (%s)' % res['exception'])
        msg = 'findUser search filter "%s"' % search_str
        logger.debug(msg)
        users = [{ 'dn' : res['exception']
                 , 'cn' : 'n/a'
                 , 'sn' : 'Error'
                 }]

    elif res['size'] > 0:
        res_dicts = res['results']
        for i in range(res['size']):
            dn = res_dicts[i].get('dn')
            rec_dict = {}
            rec_dict['sn'] = rec_dict['cn'] = ''

            for key, val in res_dicts[i].items():
                # monkey patch starts here
                if isinstance(val[0], basestring):
                    rec_dict[key] = to_utf8(val[0])
                else:
                    rec_dict[key] = val[0]
                # monkey patch ends here

            rec_dict['dn'] = dn

            users.append(rec_dict)

    return users

