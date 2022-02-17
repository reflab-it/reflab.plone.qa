# -*- coding: utf-8 -*-
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles, TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from reflab.plone.qa.content.qa_question import IQaQuestion  # NOQA E501
from reflab.plone.qa.testing import REFLAB_PLONE_QA_INTEGRATION_TESTING  # noqa
from zope.component import createObject, queryUtility

import unittest


class QaQuestionIntegrationTest(unittest.TestCase):

    layer = REFLAB_PLONE_QA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'qa Folder',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_qa_question_schema(self):
        fti = queryUtility(IDexterityFTI, name='qa Question')
        schema = fti.lookupSchema()
        self.assertEqual(IQaQuestion, schema)

    def test_ct_qa_question_fti(self):
        fti = queryUtility(IDexterityFTI, name='qa Question')
        self.assertTrue(fti)

    def test_ct_qa_question_factory(self):
        fti = queryUtility(IDexterityFTI, name='qa Question')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IQaQuestion.providedBy(obj),
            u'IQaQuestion not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_qa_question_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='qa Question',
            id='qa_question',
        )

        self.assertTrue(
            IQaQuestion.providedBy(obj),
            u'IQaQuestion not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('qa_question', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('qa_question', parent.objectIds())

    def test_ct_qa_question_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Question')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_qa_question_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='qa Question')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'qa_question_id',
            title='qa Question container',
        )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
