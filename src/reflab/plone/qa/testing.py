# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import reflab.plone.qa


class ReflabPloneQaLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=reflab.plone.qa)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'reflab.plone.qa:default')


REFLAB_PLONE_QA_FIXTURE = ReflabPloneQaLayer()


REFLAB_PLONE_QA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(REFLAB_PLONE_QA_FIXTURE,),
    name='ReflabPloneQaLayer:IntegrationTesting',
)


REFLAB_PLONE_QA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(REFLAB_PLONE_QA_FIXTURE,),
    name='ReflabPloneQaLayer:FunctionalTesting',
)


REFLAB_PLONE_QA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        REFLAB_PLONE_QA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ReflabPloneQaLayer:AcceptanceTesting',
)
