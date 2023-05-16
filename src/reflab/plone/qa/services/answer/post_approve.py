from plone.restapi.services import Service
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify
from datetime import datetime

from ...helpers import can_user_approve
from ...content.qa_question import IQaQuestion

class Approve(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        response = {"status": "", "msg": ""}
        answer = self.context

        if not can_user_approve(answer):
            response['status'] = "failed"
        else:
            question = answer.aq_parent

            intids = getUtility(IIntIds)
            uuid = intids.getId(answer)
            relation = RelationValue(uuid)

            # TODO REVISIONE QUI!!
            setattr(question, "approved_answer", relation)
            setattr(question, "approved_date", datetime.now().date())
            question.reindexObject(idxs=['approved_date'])
            question.reindexObject(idxs=['has_approved_answer'])

            # Reindex where required
            for answer in question.listFolderContents(contentFilter={"portal_type": ["qa Answer"]}):
                answer.reindexObject(idxs=['approved_date'])
                answer.reindexObject(idxs=['is_approved_answer'])

            response['status'] = "ok"
            response["msg"] = "approved"

        return response

