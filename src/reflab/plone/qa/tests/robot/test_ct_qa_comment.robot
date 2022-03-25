# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s reflab.plone.qa -t test_qa_comment.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src reflab.plone.qa.testing.REFLAB_PLONE_QA_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/reflab/plone/qa/tests/robot/test_qa_comment.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a qa Comment
  Given a logged-in site administrator
    and an add qa Comment form
   When I type 'My qa Comment' into the title field
    and I submit the form
   Then a qa Comment with the title 'My qa Comment' has been created

Scenario: As a site administrator I can view a qa Comment
  Given a logged-in site administrator
    and a qa Comment 'My qa Comment'
   When I go to the qa Comment view
   Then I can see the qa Comment title 'My qa Comment'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add qa Comment form
  Go To  ${PLONE_URL}/++add++qa Comment

a qa Comment 'My qa Comment'
  Create content  type=qa Comment  id=my-qa_comment  title=My qa Comment

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the qa Comment view
  Go To  ${PLONE_URL}/my-qa_comment
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a qa Comment with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the qa Comment title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
