from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from rer.groupware.addressbook import groupwareAddressbookMessageFactory as _
from zope.component import getMultiAdapter
from zope.interface import implements

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
    
    def getUser(self):
        pm = getToolByName(self.context, 'portal_membership')
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        
        user = pm.getAuthenticatedMember()
        user_portrait = pm.getPersonalPortrait(user.getId())
        postalAddress = user.getProperty('postalAddress', '')
        name = user.getProperty('fullname', user.getId())
        gn = user.getProperty('givenName', '')
        sn = user.getProperty('sn', '')
        role_in_room=self.getRoleInRoom(user)
        if gn and sn:
            name = "%s %s " % (gn, sn)
        if not name or name == " ":
            name = str(user.getId())
            
        return {'id':str(user.getId()),
                'name':name,
                'role_in_room':_(role_in_room),
                'portrait':user_portrait}
    
    def getRoleInRoom(self,user):
        room=None
        user_groups=user.getGroups()
        for parent in self.context.aq_inner.aq_chain:
            if getattr(parent,'portal_type','') == 'GroupRoom':
                room=parent
        if not room:
            return ''
        room_id = room.getId()
        for group in user_groups:
            if group.startswith(room_id) and not (group.endswith('notifyBig') or group.endswith('notifySmall')):
                return group[group.index('.')+1:]
        return ''
        
    def getRoomMembers(self):
        room=None
        for parent in self.context.aq_inner.aq_chain:
            if getattr(parent,'portal_type','') == 'GroupRoom':
                room=parent
        if not room:
            return []
        room_id = room.getId()
        groups_list=[]
        group_types=['coordinators','membersAdv','members','hosts']
        acl_users=getToolByName(self.context,'acl_users')
        for group_type in group_types:
            group_id="%s.%s" %(room_id,group_type)
            group=acl_users.getGroup(group_id)
            if not group:
                continue
            group_members=group.getMemberIds()
            if not group_members:
                continue
            list_members=[]
            for member_id in group_members:
                member=acl_users.getUser(member_id)
                if not member:
                    continue
                list_members.append({'userid':member.getId(),
                                    'sn':member.getProperty('sn',''),
                                    'givenName':member.getProperty('givenName',''),
                                    'fullname':member.getProperty('fullname',''),
                                    'email':member.getProperty('email','')})
            groups_list.append({'group':_(group_type),
                                'members':list_members})
        groups_dict={'room_title':room.Title(),
                     'groups_list':groups_list}
        return groups_dict
            
class AddForm(base.NullAddForm):
    """Portlet add form.
     """
    def create(self):
        return Assignment()

