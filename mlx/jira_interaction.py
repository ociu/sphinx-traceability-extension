"""Functionality to interact with Jira"""
from re import search

from jira import JIRA, JIRAError

from mlx.traceability_exception import report_warning


def create_jira_issues(app):
    settings = app.config.traceability_jira_automation

    mandatory_keys = ('api_endpoint', 'username', 'password', 'item_to_issue_regex', 'issue_type')
    missing_keys = []
    for key in mandatory_keys:
        if not settings.get(key, None):
            missing_keys.append(key)
    if missing_keys:
        return report_warning("Configuration for automated ticket creation via Jira API is missing mandatory values "
                              "for keys {}".format(missing_keys))

    jira = JIRA({"server": settings['api_endpoint']}, basic_auth=(settings['username'], settings['password']))
    issue_type = settings['issue_type']

    general_fields = {}
    general_fields['issuetype'] = {'name': issue_type}
    components = []
    for comp in settings.get('components', '').split(','):
        if comp:
            components.append({'name': comp.strip()})
    if components:
        general_fields['components'] = components

    traceability_collection = app.builder.env.traceability_collection
    for item_id in traceability_collection.get_items(settings['item_to_issue_regex']):
        fields = {}
        item = traceability_collection.get_item(item_id)
        project_id_or_key = determine_jira_project(settings.get('project_key_regexp', ''),
                                                   settings.get('project_key_prefix', ''),
                                                   settings.get('default_project', ''),
                                                   item_id)
        if not project_id_or_key:
            report_warning("Could not determine a JIRA project key or id for item {!r}".format(item_id))
            continue

        assignee = item.get_attribute('assignee')
        summary = item.caption
        attendees = []
        if settings['relationship_to_parent']:
            parent_ids = item.iter_targets(settings['relationship_to_parent'])
            if parent_ids:
                parent_id = parent_ids[0]
                parent = traceability_collection.get_item(parent_id)
                summary = "{} {}".format(parent_id, summary)
                attendees = parent.get_attribute('attendees').split(',')

        matches = jira.search_issues("project={} and summary ~ {!r}".format(project_id_or_key, summary))
        if matches:
            if settings.get('warn_if_existent', False):
                report_warning("Won't create a {} for item {!r} because the Jira API query to check to prevent duplication "
                               "returned {}".format(issue_type, item_id, matches))
            continue

        fields['project'] = project_id_or_key
        fields['summary'] = summary
        fields['description'] = item.get_content()
        if assignee:
            fields['assignee'] = {'name': item.get_attribute('assignee')}

        create_jira_issue_for_item(jira, {**fields, **general_fields}, item, attendees)


def create_jira_issue_for_item(jira, fields, item, attendees):
    issue = jira.create_issue(**fields)

    effort = item.get_attribute('effort')
    if effort:
        try:
            issue.update(update={"timetracking": [{"edit": {"timeestimate": effort}}]}, notify=False)
        except JIRAError:
            issue.update(description="{}\n\nEffort estimation: {}".format(item.get_content(), effort), notify=False)

    for attendee in attendees:
        try:
            jira.add_watcher(issue, attendee.strip())
        except JIRAError as err:
            report_warning("Jira API returned error code {}: {}".format(err.status_code, err.response.text))

    return issue


def determine_jira_project(key_regexp, key_prefix, default_project, item_id):
    """ Determines the JIRA project key or id to use for give item ID.

    Args:
        key_regexp (str): Regular expression used to scan through the <<item_id>>. In case of a hit, the capture group
            with name 'project' will be used to build the project key.
        key_prefix (str): Prefix to use if <<key_regexp>> gets used to build the project key.
        default_project (str): Project key or id to use if a match for <<key_regexp>> doesn't get used.

    Returns:
        str: JIRA project key or id.
    """
    key_match = search(key_regexp, item_id)
    try:
        return key_prefix + key_match.group('project')
    except (AttributeError, IndexError):
        return default_project
