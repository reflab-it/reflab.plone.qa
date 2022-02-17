# -*- coding: utf-8 -*-

from plone.dexterity.browser.view import DefaultView
from reflab.plone.qa import _


class QAAnswerView(DefaultView):

    def __call__(self):
        return super(QAAnswerView, self).__call__()
