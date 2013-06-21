# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


class View(BrowserView):
    '''
    A view that return a dict of contents created by an user, splitted by Room
    '''
    def __call__(self, *args, **kw):
        '''
        '''
        portal_types = getToolByName(self.context, 'portal_types')
        portal_properties = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(portal_properties, 'site_properties')
        if site_properties.hasProperty('types_not_searched'):
            search_types = [x for x
                          in portal_types.keys()
                          if x not in site_properties.getProperty('types_not_searched')]
        if not kw.get('userid', ''):
            return {}
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc.searchResults(Creator=kw.get('userid', ''),
                                sort_on='created',
                                sort_order='reverse',
                                portal_type=search_types)
        res_dict = {}
        for brain in brains:
            item_room = brain.parentRoom
            if not item_room:
                portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
                item_room = portal_state.portal_title
            if item_room not in res_dict:
                res_dict[item_room] = [brain]
            else:
                limit = kw.get('limit', 0)
                if not limit or len(res_dict[item_room]) < limit:
                    res_dict[item_room].append(brain)
        return res_dict
