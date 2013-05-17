# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.PlonePAS.browser.search import PASSearchView
from rer.groupware.addressbook import groupwareAddressbookMessageFactory as _
from plone.registry.interfaces import IRegistry
from rer.groupware.room.interfaces import IRoomGroupsSettingsSchema
from zope.component import queryUtility


class SearchFormUsersView(PASSearchView):
    """
    """

    def __init__(self, context, request):
        """
        """
        super(SearchFormUsersView, self).__init__(context, request)

    def searchByRequest(self, request=None, sort_by='userid'):
        """
        Search users in groupware, and return only users in your groups.
        If you are an admin, groups filter doesn't work.
        """
        if not request:
            request = self.request
        pm = getToolByName(self.context, 'portal_membership')
        acl_users = getToolByName(self.context, "acl_users")
        users = self.searchUsersByRequest(request, sort_by)
        authenticated_member = pm.getAuthenticatedMember()
        #get the list of rooms where the user is enables
        available_rooms = self.getUserRoomGroups(authenticated_member)
        is_manager = pm.checkPermission('Manage portal', self.context)
        users_list = []
        for user in users:
            # userid = user.get('userid', '')
            # if userid in available_userids or is_manager:
            #     user['list_rooms'] = self.getUserRooms(userid)
            #     users_list.append(user)
            user_obj = acl_users.getUser(user.get('userid'))
            if user_obj:
                user_rooms = self.getUserRoomGroups(user_obj)
                if is_manager:
                    user['list_rooms'] = user_rooms
                    users_list.append(user)
                else:
                    if user_rooms.intersection(available_rooms):
                        user['list_rooms'] = user_rooms
                        users_list.append(user)
        return users_list

    def getRoomTitles(self):
        """
        """
        pc = getToolByName(self.context, 'portal_catalog')
        rooms = pc(portal_type="GroupRoom", sort_on="sortable_title")
        rooms_dict = {}
        for room in rooms:
            rooms_dict[room.getId] = room.Title
        return rooms_dict

    def getUserRoomGroups(self, user):
        user_groups = user.getGroups()
        list_rooms = set()
        registry = queryUtility(IRegistry)
        groups_settings = registry.forInterface(IRoomGroupsSettingsSchema, check=False)
        passive_groups = getattr(groups_settings, 'passive_groups', None)
        available_groups_ids = [x.group_id for x in passive_groups]
        available_groups_ids.append('users')
        for group in user_groups:
            for availabel_group_id in available_groups_ids:
                if group.endswith(".%s" % availabel_group_id):
                    list_rooms.add(group[:group.index('.')])
        return list_rooms

    # def getUserRooms(self, userid):
    #     """
    #     """
    #     acl_users = getToolByName(self.context, "acl_users")
    #     user = acl_users.getUser(userid)
    #     user_groups = user.getGroups()
    #     for group in user_groups:
    #         if group.endswith(".users"):


    def validateRequest(self, request=None):
        if not request:
            request = self.request
        errors = []

        if not self.request.get('fullname', False) \
                  and not self.request.get('email', False):
            errors.append(_('You must enter at least one search criteria'))
        return errors

    def searchUsersByRequest(self, request=None, sort_by='userid'):
        if not request:
            request = self.request
        criteria = {}
        if self.validateRequest():
            return tuple()
        else:
            if self.request.get('fullname', False):
                #startswith
                criteria['fullname'] = "%s" % self.request.fullname.strip()
            if self.request.get('email', False):
                #startswith
                criteria['email'] = "%s" % self.request.email.strip()
            if len(criteria) == 0:
                return tuple()
            # not empty
            return self.searchUsers(sort_by=sort_by, **criteria)

    def getPortrait(self, userid):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.getPersonalPortrait(userid)
