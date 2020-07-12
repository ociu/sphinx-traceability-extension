from logging import WARNING
from unittest import TestCase, mock

from mlx.traceable_attribute import TraceableAttribute
from mlx.traceable_collection import TraceableCollection
from mlx.traceable_item import TraceableItem
import mlx.jira_interaction as dut


@mock.patch('mlx.jira_interaction.JIRA')
class TestJiraInteraction(TestCase):

    def setUp(self):
        self.settings = {
            'api_endpoint': 'https://jira.atlassian.com/rest/api/latest/',
            'username': 'my_username',
            'password': 'my_password',
            'project_key_regexp': r'ACTION-(?P<project>\d{5})_',
            'project_key_prefix': 'MLX',
            'default_project': 'SWCC',
            'issue_type': 'Task',
            'item_to_issue_regex': r'ACTION-12345_ACTION_\d+',
            'warn_if_existent': True,
            'relationship_to_parent': 'depends_on',
            'components': '[SW],[HW]',
        }
        self.coll = TraceableCollection()
        parent = TraceableItem('MEETING-12345_2')
        action1 = TraceableItem('ACTION-12345_ACTION_1')
        action2 = TraceableItem('ACTION-12345_ACTION_2')
        action3 = TraceableItem('ACTION-98765_ACTION_55')
        item1 = TraceableItem('ITEM-12345_1')

        effort_attr = TraceableAttribute('effort', r'^([\d\.]+(mo|[wdhm]) ?)+$')
        assignee_attr = TraceableAttribute('assignee', '^.*$')
        attendees_attr = TraceableAttribute('attendees', '^([A-Z]{3}[, ]*)+$')
        TraceableItem.define_attribute(effort_attr)
        TraceableItem.define_attribute(assignee_attr)
        TraceableItem.define_attribute(attendees_attr)

        parent.add_attribute('attendees', 'ABC, ZZZ')
        action1.add_attribute('effort', '1mo 2w 3d 4h 55m')
        action1.add_attribute('assignee', 'ABC')
        action2.add_attribute('assignee', 'ABC')
        action3.add_attribute('assignee', 'ZZZ')

        for item in (parent, action1, action2, action3, item1):
            self.coll.add_item(item)

        self.coll.add_relation_pair('depends_on', 'impacts_on')
        self.coll.add_relation(action1.id, 'impacts_on', item1.id)
        self.coll.add_relation(action1.id, 'depends_on', parent.id)
        self.coll.add_relation(action2.id, 'depends_on', parent.id)

    def test_missing_endpoint(self, *_):
        self.settings = self.settings
        self.settings.pop('api_endpoint')
        with self.assertLogs(level=WARNING) as cm:
            dut.create_jira_issues(self.settings, None)
        self.assertEqual(
            cm.output,
            ["WARNING:sphinx.mlx.traceability_exception:Configuration for automated ticket creation via Jira API is "
             "missing mandatory values for keys ['api_endpoint']"]
        )

    def test_missing_username(self, *_):
        self.settings.pop('username')
        with self.assertLogs(level=WARNING) as cm:
            dut.create_jira_issues(self.settings, None)
        self.assertEqual(
            cm.output,
            ["WARNING:sphinx.mlx.traceability_exception:Configuration for automated ticket creation via Jira API is "
             "missing mandatory values for keys ['username']"]
        )

    def test_missing_all_mandatory(self, *_):
        mandatory_keys = ['api_endpoint', 'username', 'password', 'item_to_issue_regex', 'issue_type']
        for key in mandatory_keys:
            self.settings.pop(key)
        with self.assertLogs(level=WARNING) as cm:
            dut.create_jira_issues(self.settings, None)
        self.assertEqual(
            cm.output,
            ["WARNING:sphinx.mlx.traceability_exception:Configuration for automated ticket creation via Jira API is "
             "missing mandatory values for keys {}".format(mandatory_keys)]
        )

    def test_missing_all_optional_one_mandatory(self, *_):
        mandatory_keys = ['components', 'project_key_prefix', 'project_key_regexp', 'default_project',
                          'relationship_to_parent', 'warn_if_existent', 'password']
        for key in mandatory_keys:
            self.settings.pop(key)
        with self.assertLogs(level=WARNING) as cm:
            dut.create_jira_issues(self.settings, None)
        self.assertEqual(
            cm.output,
            ["WARNING:sphinx.mlx.traceability_exception:Configuration for automated ticket creation via Jira API is "
             "missing mandatory values for keys ['password']"]
        )

    def test_create_jira_issues(self, jira):
        dut.create_jira_issues(self.settings, self.coll)
        self.assertEqual(jira.call_args,
                         mock.call({'server': 'https://jira.atlassian.com/rest/api/latest/'},
                                   basic_auth=('my_username', 'my_password')))
