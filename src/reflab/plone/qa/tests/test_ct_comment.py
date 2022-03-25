# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from reflab.plone.qa.content.comment import IComment  # NOQA E501
from reflab.plone.qa.testing import REFLAB_PLONE_QA_INTEGRATION_TESTING  # noqa
from zope.component import createObject, queryUtility

import unittest


class CommentIntegrationTest(unittest.TestCase):

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_comment_schema(self):
        fti = queryUtility(IDexterityFTI, name='Comment')
        schema = fti.lookupSchema()
        self.assertEqual(IComment, schema)

    def test_ct_comment_fti(self):
        fti = queryUtility(IDexterityFTI, name='Comment')
        self.assertTrue(fti)

    def test_ct_comment_factory(self):
        fti = queryUtility(IDexterityFTI, name='Comment')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IComment.providedBy(obj),
            u'IComment not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_comment_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Comment',
            id='comment',
        )

        self.assertTrue(
            IComment.providedBy(obj),
            u'IComment not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('comment', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('comment', parent.objectIds())

    def test_ct_comment_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Comment')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_comment_filter_content_type_false(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Comment')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'comment_id',
            title='Comment container',
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
