# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from reflab.plone.qa.content.qa_comment import IQaComment  # NOQA E501
from reflab.plone.qa.testing import REFLAB_PLONE_QA_INTEGRATION_TESTING  # noqa
from zope.component import createObject, queryUtility

import unittest


class QaCommentIntegrationTest(unittest.TestCase):

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_qa_comment_schema(self):
        fti = queryUtility(IDexterityFTI, name='qa Comment')
        schema = fti.lookupSchema()
        self.assertEqual(IQaComment, schema)

    def test_ct_qa_comment_fti(self):
        fti = queryUtility(IDexterityFTI, name='qa Comment')
        self.assertTrue(fti)

    def test_ct_qa_comment_factory(self):
        fti = queryUtility(IDexterityFTI, name='qa Comment')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IQaComment.providedBy(obj),
            u'IQaComment not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_qa_comment_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='qa Comment',
            id='qa_comment',
        )

        self.assertTrue(
            IQaComment.providedBy(obj),
            u'IQaComment not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('qa_comment', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('qa_comment', parent.objectIds())

    def test_ct_qa_comment_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Comment')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_qa_comment_filter_content_type_false(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Comment')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'qa_comment_id',
            title='qa Comment container',
        )
        self.parent = self.portal[parent_id]
        obj = api.content.create(
            container=self.parent,
            type='Document',
            title='My Content',
        )
        self.assertTrue(
            obj,
            u'Cannot add {0} to {1} container!'.format(obj.id, fti.id)
        )
