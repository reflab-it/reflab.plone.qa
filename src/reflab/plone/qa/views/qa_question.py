# -*- coding: utf-8 -*-

from plone.dexterity.browser.view import DefaultView
from reflab.plone.qa import _


class QAQuestionView(DefaultView):

    def __call__(self):
        return super(QAQuestionView, self).__call__()
