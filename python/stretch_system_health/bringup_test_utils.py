
from stretch_production_tools.production_test_utils import  Production_Test, Production_TestResult, Production_TestSuite, Production_TestRunner
from stretch_body.robot_params import RobotParams
class Bringup_Test(Production_Test):
    def __init__(self, test_name):
        Production_Test.__init__(self, test_name)
        self.robot_tool = RobotParams.get_params()[1]['robot']['tool']

class Bringup_TestResult(Production_TestResult):
    def __init__(self):
        Production_TestResult.__init__(self)

class BRI_TestSuite(Production_TestSuite):
    def __init__(self,bringup_test=None, failfast=False):
        Production_TestSuite.__init__(self,bringup_test, failfast)

class BRI_TestRunner(Production_TestRunner):
    def __init__(self,suite, doc_verify_fail=False):
        Production_TestRunner.__init__(self,suite, doc_verify_fail)
