from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from rer.groupware.addressbook import groupwareAddressbookMessageFactory as _
from zope.component import getMultiAdapter
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from zope.component import queryUtility


class IGroupwareUserPortlet(IPortletDataProvider):
    """
    """


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGroupwareUserPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Groupware portlet user"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('groupware_portlet_user.pt')

    @property
    def available(self):
        return not getToolByName(self.context, 'portal_membership').isAnonymousUser()

    def getUserAction(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        user_actions = context_state.actions().get('user', None)
        return user_actions

    def getUserInfos(self):
        pm = getToolByName(self.context, 'portal_membership')
        user = pm.getAuthenticatedMember()
        user_portrait = pm.getPersonalPortrait(user.getId())
        name = user.getProperty('fullname', user.getId())
        gn = user.getProperty('givenName', '')
        sn = user.getProperty('sn', '')
        userinfo = {'id': str(user.getId()),
                    'name': name,
                    'portrait': user_portrait}
        #get some room infos
        room = None
        for parent in self.context.aq_inner.aq_chain:
            if getattr(parent, 'portal_type', '') == 'GroupRoom':
                room = parent
        if room:
            userinfo['role_in_room'] = self.getRoleInRoom(user, room)
            userinfo['room_members'] = self.getRoomMembers(room)
        if gn and sn:
            name = "%s %s " % (gn, sn)
        if not name or name == " ":
            name = str(user.getId())
        return userinfo

    def getDefaultRoomGroups(self):
        """
        """
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        active_groups = getattr(groups_settings, 'active_groups', None)
        passive_groups = getattr(groups_settings, 'passive_groups', None)
        return passive_groups + active_groups

    def getRoleInRoom(self, user, room):
        room_id = room.getId()
        user_groups = user.getGroups()
        room_groups = self.getDefaultRoomGroups()
        for group_id in user_groups:
            for default_group in room_groups:
                if group_id == "%s.%s" % (room_id, default_group.group_id):
                    return default_group.group_title
        return ''

    def getRoomMembers(self, room):
        room_id = room.getId()
        groups_list = []
        room_groups = self.getDefaultRoomGroups()
        acl_users = getToolByName(self.context, 'acl_users')
        for group_type in room_groups:
            default_group_id = group_type.group_id
            default_group_title = group_type.group_title
            group_id = "%s.%s" % (room_id, default_group_id)
            group = acl_users.getGroup(group_id)
            if not group:
                continue
            group_members = group.getMemberIds()
            if not group_members:
                continue
            list_members = []
            for member_id in group_members:
                member = acl_users.getUser(member_id)
                if not member:
                    continue
                list_members.append({'userid': member.getId(),
                                    'fullname': member.getProperty('fullname', ''),
                                    'email': member.getProperty('email', '')})
            list_members.sort(lambda x, y: cmp(x.get('fullname', ''), y.get('fullname', '')))
            groups_list.append({'group': default_group_title,
                                'members': list_members})
        return {'room_title': room.Title(),
                'groups_list': groups_list}


class AddForm(base.NullAddForm):
    """Portlet add form.
     """
    def create(self):
        return Assignment()
