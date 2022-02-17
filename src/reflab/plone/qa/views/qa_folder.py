# -*- coding: utf-8 -*-

from plone.dexterity.browser.view import DefaultView
from reflab.plone.qa import _


class QAFolderView(DefaultView):

    def __call__(self):
        return super(QAFolderView, self).__call__()
