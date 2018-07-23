#!/usr/bin/env python3

import unittest
from unittest.mock import patch

from deploy import *

class GetPriorityTest(unittest.TestCase):
    def test_1(self):
        """Simple test to get next priority"""
        rules = json.loads('[{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/2cc6c973c4d32f55","Priority":"1","Conditions":[{"Field":"host-header","Values":["host1.asdf.com"]},{"Field":"path-pattern","Values":["/path2"]}],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":false},{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/f9994e3e3a55d6dd","Priority":"2","Conditions":[{"Field":"path-pattern","Values":["/path1"]}],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":false},{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/74a74e7da03f7ddb","Priority":"default","Conditions":[],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":true}]')
        priority = get_priority(rules)
        self.assertEqual(priority, 3)

    def test_2(self):
        """Test with gap in list of priorities"""
        rules = json.loads('[{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/5cdf34d5cf48fabc","Priority":"1","Conditions":[{"Field":"path-pattern","Values":["/asdffdas"]}],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":false},{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/2cc6c973c4d32f55","Priority":"2","Conditions":[{"Field":"host-header","Values":["host1.asdf.com"]},{"Field":"path-pattern","Values":["/path2"]}],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":false},{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/284a6e35adc73d71","Priority":"5","Conditions":[{"Field":"path-pattern","Values":["/32452345"]}],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":false},{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/74a74e7da03f7ddb","Priority":"default","Conditions":[],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":true}]')
        priority = get_priority(rules)
        self.assertEqual(priority, 3)

    def test_3(self):
        """Test with no rules except default"""
        rules = json.loads('[{"RuleArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:listener-rule/app/asdfasdfasdf/ba564ec55606a717/9c431593f1c78965/74a74e7da03f7ddb","Priority":"default","Conditions":[],"Actions":[{"Type":"forward","TargetGroupArn":"arn:aws:elasticloadbalancing:ap-southeast-2:12345678987:targetgroup/ecs-c-ALBDe-2TD7HNS9J92H/134e396d75ebd3a6"}],"IsDefault":true}]')
        priority = get_priority(rules)
        self.assertEqual(priority, 1)


class GenerateEnvironmentObjectTest(unittest.TestCase):
    @patch('builtins.open', unittest.mock.mock_open(read_data="ENV\nREALM\nECS_APP_NAME\nAWS_SECRET_ACCESS_KEY"))
    @patch.dict('os.environ', {'ENV': 'Dev', 'REALM': 'NonProd', 'AWS_SECRET_ACCESS_KEY': "I should not be present"})
    def test_1(self):
        """Test with variables present in .env and in working environment"""
        expected_environment = [
            {
                "name": "ENV",
                "value": "Dev"
            },
            {
                "name": "REALM",
                "value": "NonProd"
            }
        ]
        environment = generate_environment_object()
        self.assertEqual(environment, expected_environment)

    @patch('builtins.open', unittest.mock.mock_open(read_data="ENV\n\n\nREALM\n#asdfasdf\nECS_APP_NAME\nAWS_SECRET_ACCESS_KEY"))
    @patch.dict('os.environ', {'ENV': 'asdfsa!!asdfasdf#asdf', 'REALM': '""asdf\'asdfdfas{"asdf":"asdfa\'sd"}', 'AWS_SECRET_ACCESS_KEY': "I should not be present #          "})
    def test_2(self):
        """Test with weird formatting and characters in .env"""
        expected_environment = [
            {
                "name": "ENV",
                "value": "asdfsa!!asdfasdf#asdf"
            },
            {
                "name": "REALM",
                "value": '""asdf\'asdfdfas{"asdf":"asdfa\'sd"}'
            }
        ]
        environment = generate_environment_object()
        self.assertEqual(environment, expected_environment)

    @patch('builtins.open', unittest.mock.mock_open(read_data='ENV=\sdfsa!!asdfasdf#asdfn\n\nREALM=""asdf\'asdfdfas{"asdf":"asdfa\'sd"}\n#asdfasdf\nECS_APP_NAME=dddddd # comment\nAWS_SECRET_ACCESS_KEY'))
    @patch.dict('os.environ', {'ENV': 'asdfsa!!asdfasdf', 'REALM': '""asdf\'asdfdfas{"asdf":"asdfa\'sd"}', 'ECS_APP_NAME': 'dddddd', 'AWS_SECRET_ACCESS_KEY': "I should not be present #          "})
    def test_3(self):
        """Test with environment variable values set in file"""
        expected_environment = [
            {
                "name": "ENV",
                "value": "asdfsa!!asdfasdf"
            },
            {
                "name": "REALM",
                "value": '""asdf\'asdfdfas{"asdf":"asdfa\'sd"}'
            },
            {
                "name": "ECS_APP_NAME",
                "value": "dddddd"
            }
        ]
        environment = generate_environment_object()
        self.assertEqual(environment, expected_environment)

    @patch('builtins.open', unittest.mock.mock_open(read_data='ENV=Dev\nREGION'))
    @patch.dict('os.environ', {'ENV': 'Dev'})
    def test_4(self):
        """Test with environment variable values set in file"""
        expected_environment = [
            {
                "name": "ENV",
                "value": "Dev"
            }        
        ]
        environment = generate_environment_object()
        self.assertEqual(environment, expected_environment)


def main():
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
