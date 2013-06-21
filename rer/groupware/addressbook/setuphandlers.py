# -*- coding: utf-8 -*-

from rer.groupware.addressbook import logger

_PROPERTIES = [
    dict(name='contact_author_enabled', type_='boolean', value=True),
]

def registerProperties(portal):
    ptool = portal.portal_properties
    props = ptool.groupware_properties

    for prop in _PROPERTIES:
        if not props.hasProperty(prop['name']):
            props.manage_addProperty(prop['name'], prop['value'], prop['type_'])
            logger.info("Added missing %s property" % prop['name'])

def importVarious(context):
    """Miscellanous steps import handle
    """
    
    if context.readDataFile('groupwareaddressbook-various.txt') is None:
        return
    
    portal = context.getSite()
    registerProperties(portal)
