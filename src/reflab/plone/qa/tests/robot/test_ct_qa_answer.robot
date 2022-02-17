# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s reflab.plone.qa -t test_qa_answer.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src reflab.plone.qa.testing.REFLAB_PLONE_QA_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/reflab/plone/qa/tests/robot/test_qa_answer.robot
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

Scenario: As a site administrator I can add a qa Answer
  Given a logged-in site administrator
    and an add qa Question form
   When I type 'My qa Answer' into the title field
    and I submit the form
   Then a qa Answer with the title 'My qa Answer' has been created

Scenario: As a site administrator I can view a qa Answer
  Given a logged-in site administrator
    and a qa Answer 'My qa Answer'
   When I go to the qa Answer view
   Then I can see the qa Answer title 'My qa Answer'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add qa Question form
  Go To  ${PLONE_URL}/++add++qa Question

a qa Answer 'My qa Answer'
  Create content  type=qa Question  id=my-qa_answer  title=My qa Answer

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the qa Answer view
  Go To  ${PLONE_URL}/my-qa_answer
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a qa Answer with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the qa Answer title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
