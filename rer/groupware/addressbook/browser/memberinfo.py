# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

class MemberInfo(BrowserView):
    """Get user member info"""
    
    def getMemberInfo(self, userid=None):
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        if userid:
            member = mtool.getMemberById(userid)
        else:
            member = mtool.getAuthenticatedMember()
        if member:
            memberinfo = {
                           'description' : member.getProperty('description',''),
                           'location'    : member.getProperty('location',''),
                           'language'    : member.getProperty('language',''),
                           'home_page'   : member.getProperty('home_page',''),
                           'username'    : member.getUserName(),
                           'listed': member.getProperty('listed',''),
                           'givenName'   : member.getProperty('givenName',''),
                           'sn'          : member.getProperty('sn',''),
                           'postalAddress'   : member.getProperty('postalAddress',''),
                           'roomNumber'      : member.getProperty('roomNumber',''),
                           'telephoneNumber'    : member.getProperty('telephoneNumber',''),
                           'homePhone'    : member.getProperty('homePhone',''),
                           'mobile'    : member.getProperty('mobile',''),
                           'mail'    : member.getProperty('email',''),
                           'incarico'    : member.getProperty('incarico',''),
                           'employeeNumber'    : member.getProperty('employeeNumber',''),
                           'businessCategory'    : member.getProperty('businessCategory',''),
                           'destinationIndicator'    : member.getProperty('destinationIndicator',''),
                         }
            if memberinfo['givenName'] and memberinfo['sn']:
                memberinfo['fullname'] = "%s %s" % (memberinfo['givenName'], memberinfo['sn'])
            else:
                memberinfo['fullname']=member.getId()
        else:
            memberinfo = {}
        return memberinfo
