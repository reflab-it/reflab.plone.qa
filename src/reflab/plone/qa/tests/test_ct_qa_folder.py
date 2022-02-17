# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from reflab.plone.qa.content.qa_folder import IQaFolder  # NOQA E501
from reflab.plone.qa.testing import REFLAB_PLONE_QA_INTEGRATION_TESTING  # noqa
from zope.component import createObject, queryUtility

import unittest


class QaFolderIntegrationTest(unittest.TestCase):

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_qa_folder_schema(self):
        fti = queryUtility(IDexterityFTI, name='qa Folder')
        schema = fti.lookupSchema()
        self.assertEqual(IQaFolder, schema)

    def test_ct_qa_folder_fti(self):
        fti = queryUtility(IDexterityFTI, name='qa Folder')
        self.assertTrue(fti)

    def test_ct_qa_folder_factory(self):
        fti = queryUtility(IDexterityFTI, name='qa Folder')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IQaFolder.providedBy(obj),
            u'IQaFolder not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_qa_folder_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='qa Folder',
            id='qa_folder',
        )

        self.assertTrue(
            IQaFolder.providedBy(obj),
            u'IQaFolder not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('qa_folder', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('qa_folder', parent.objectIds())

    def test_ct_qa_folder_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Folder')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_qa_folder_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Folder')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'qa_folder_id',
            title='qa Folder container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
