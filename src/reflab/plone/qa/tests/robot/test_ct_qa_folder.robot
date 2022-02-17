# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s reflab.plone.qa -t test_qa_folder.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src reflab.plone.qa.testing.REFLAB_PLONE_QA_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/reflab/plone/qa/tests/robot/test_qa_folder.robot
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

Scenario: As a site administrator I can add a qa Folder
  Given a logged-in site administrator
    and an add qa Folder form
   When I type 'My qa Folder' into the title field
    and I submit the form
   Then a qa Folder with the title 'My qa Folder' has been created

Scenario: As a site administrator I can view a qa Folder
  Given a logged-in site administrator
    and a qa Folder 'My qa Folder'
   When I go to the qa Folder view
   Then I can see the qa Folder title 'My qa Folder'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add qa Folder form
  Go To  ${PLONE_URL}/++add++qa Folder

a qa Folder 'My qa Folder'
  Create content  type=qa Folder  id=my-qa_folder  title=My qa Folder

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the qa Folder view
  Go To  ${PLONE_URL}/my-qa_folder
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a qa Folder with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the qa Folder title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
