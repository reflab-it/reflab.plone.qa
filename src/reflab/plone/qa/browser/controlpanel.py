# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper,
    RegistryEditForm,
)
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IQAControlPanel(Interface):

    supervisor_email = schema.TextLine(
        title=u'Supervisor email',
        description=u'',
        default='',
        required=False,
    )


class QAControlPanelForm(RegistryEditForm):
    schema = IQAControlPanel
    schema_prefix = "reflab.plone.qa"
    label = u'Q&A Settings'


QAControlPanelView = layout.wrap_form(
    QAControlPanelForm, ControlPanelFormWrapper)
