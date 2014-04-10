from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class TdftemplateuploadcenterLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import tdf.templateuploadcenter
        xmlconfig.file(
            'configure.zcml',
            tdf.templateuploadcenter,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'tdf.templateuploadcenter:default')

TDF_TEMPLATEUPLOADCENTER_FIXTURE = TdftemplateuploadcenterLayer()
TDF_TEMPLATEUPLOADCENTER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TDF_TEMPLATEUPLOADCENTER_FIXTURE,),
    name="TdftemplateuploadcenterLayer:Integration"
)
TDF_TEMPLATEUPLOADCENTER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TDF_TEMPLATEUPLOADCENTER_FIXTURE, z2.ZSERVER_FIXTURE),
    name="TdftemplateuploadcenterLayer:Functional"
)
