from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.PlonePAS.browser.search import PASSearchView
from Products.statusmessages.interfaces import IStatusMessage
from rer.groupware.addressbook import groupwareAddressbookMessageFactory as _

class SearchFormUsersView(PASSearchView):
    """ """

    def searchByRequest(self, request=None, sort_by='userid'):
        if not request:
            request = self.request
        users=self.searchUsersByRequest(request, sort_by)
        user_groups=self.context.portal_membership.getAuthenticatedMember().getGroups()
        if not user_groups:
            return []
        list_rooms=set()
        for group in user_groups:
            if group.endswith('.coordinators') or group.endswith('.members') or group.endswith('.membersAdv') or group.endswith('.hosts'):
                list_rooms.add(group[:group.index('.')])
        
        users_list=[]
        acl_users=getToolByName(self.context,"acl_users")
        for user in users:
            user_obj=acl_users.getUser(user.get('userid'))
            try:
                user_groups=user_obj.getGroups()
            except:
                continue
            user_flag=False
            for group in user_groups:
                for room in list_rooms:
                    if group.startswith(room):
                        user_flag=True
            if user_flag:
                users_list.append(user)
        return users_list

    def validateRequest(self, request=None):
        if not request:
            request = self.request
        errors = []
    
        if not self.request.get('searchName', False) \
                  and not self.request.get('searchSurname', False) \
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
            if self.request.get('searchPhone', False):
                #contains
                criteria['phone']= "%s" % self.request.searchPhone.strip()
            if self.request.get('searchOffice', False):
                #contains
                criteria['destinationIndicator']= "%s" % self.request.searchOffice.strip()
            if len(criteria) == 0:
                return tuple()
            # not empty
            return self.searchUsers(sort_by=sort_by)


