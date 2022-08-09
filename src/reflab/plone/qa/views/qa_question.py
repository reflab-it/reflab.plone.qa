# -*- coding: utf-8 -*-

from plone.dexterity.browser.view import DefaultView
from reflab.plone.qa import _


class QAQuestionView(DefaultView):

    def __call__(self):
        return super(QAQuestionView, self).__call__()

    @property
    def title(self):
        return self.context.Title()

    def answers(self):
        return self.context.listFolderContents(
            contentFilter={"portal_type" : "qa Answer"}
        )        