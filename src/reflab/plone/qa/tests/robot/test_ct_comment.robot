# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s reflab.plone.qa -t test_comment.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src reflab.plone.qa.testing.REFLAB_PLONE_QA_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/reflab/plone/qa/tests/robot/test_comment.robot
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

Scenario: As a site administrator I can add a Comment
  Given a logged-in site administrator
    and an add Comment form
   When I type 'My Comment' into the title field
    and I submit the form
   Then a Comment with the title 'My Comment' has been created

Scenario: As a site administrator I can view a Comment
  Given a logged-in site administrator
    and a Comment 'My Comment'
   When I go to the Comment view
   Then I can see the Comment title 'My Comment'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Comment form
  Go To  ${PLONE_URL}/++add++Comment

a Comment 'My Comment'
  Create content  type=Comment  id=my-comment  title=My Comment

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Comment view
  Go To  ${PLONE_URL}/my-comment
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Comment with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Comment title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
