# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from reflab.plone.qa.testing import REFLAB_PLONE_QA_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that reflab.plone.qa is properly installed."""

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if reflab.plone.qa is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'reflab.plone.qa'))

    def test_browserlayer(self):
        """Test that IReflabPloneQaLayer is registered."""
        from reflab.plone.qa.interfaces import (
            IReflabPloneQaLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IReflabPloneQaLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['reflab.plone.qa'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if reflab.plone.qa is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'reflab.plone.qa'))

    def test_browserlayer_removed(self):
        """Test that IReflabPloneQaLayer is removed."""
        from reflab.plone.qa.interfaces import \
            IReflabPloneQaLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IReflabPloneQaLayer,
            utils.registered_layers())
