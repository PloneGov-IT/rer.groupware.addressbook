from Products.CMFCore.utils import getToolByName

# Properties are defined here, because if they are defined in propertiestool.xml,
# all properties are re-set the their initial state if you reinstall product
# in the quickinstaller.

def import_various(context):
    if context.readDataFile('groupwareaddressbook-various.txt') is None:
        return
