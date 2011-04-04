from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.PlonePAS.browser.search import PASSearchView
from Products.statusmessages.interfaces import IStatusMessage
from rer.groupware.addressbook import groupwareAddressbookMessageFactory as _

class SearchFormUsersView(PASSearchView):
    """"""
    def searchByRequest(self, request=None, sort_by='userid'):
        if not request:
            request = self.request
        users=self.searchUsersByRequest(request, sort_by)
        authenticated_member=self.context.portal_membership.getAuthenticatedMember()
        #get the list of rooms where the user is enables
        list_authenticated_rooms=self.getUserRooms(authenticated_member)
        users_list=[]
        acl_users=getToolByName(self.context,"acl_users")
        for user in users:
            user_obj=acl_users.getUser(user.get('userid'))
            if user_obj:
                user_rooms=self.getUserRooms(user_obj)
                if user_rooms.intersection(list_authenticated_rooms):
                    user['list_rooms']=user_rooms
                    users_list.append(user)
        return users_list

    def getUserRooms(self,user):
        user_groups=user.getGroups()
        list_rooms=set()
        for group in user_groups:
            if group.endswith('.coordinators') or group.endswith('.members') or group.endswith('.membersAdv') or group.endswith('.hosts'):
                list_rooms.add(group[:group.index('.')])
        return list_rooms

    def validateRequest(self, request=None):
        if not request:
            request = self.request
        errors = []
    
        if not self.request.get('searchName', False) \
                  and not self.request.get('searchSurname', False) \
                  and not self.request.get('searchEmail', False) \
                  and not self.request.get('searchPhone', False) \
                  and not self.request.get('searchOffice', False):
            errors.append(_('You must enter at least one search criteria'))
        return errors

    def searchUsersByRequest(self, request=None, sort_by='userid'):
        if not request:
            request = self.request
        criteria = {}
        if self.validateRequest():
            return tuple()
        else:
            if self.request.get('searchName', False):
                #startswith
                criteria['givenName']= "%s" % self.request.searchName.strip()
            if self.request.get('searchSurname', False):
                #startswith
                criteria['sn'] = "%s" % self.request.searchSurname.strip()
            if self.request.get('searchEmail', False):
                #startswith
                criteria['mail'] = "%s" % self.request.searchEmail.strip()
            if self.request.get('searchPhone', False):
                #contains
                criteria['telephoneNumber']= "%s" % self.request.searchPhone.strip()
            if self.request.get('searchOffice', False):
                #contains
                criteria['destinationIndicator']= "%s" % self.request.searchOffice.strip()
            if len(criteria) == 0:
                return tuple()
            # not empty
            return self.searchUsers(sort_by=sort_by,**criteria)

    def getPortrait(self,userid):
        pm = getToolByName(self.context, 'portal_membership')
        return pm.getPersonalPortrait(userid)
        
