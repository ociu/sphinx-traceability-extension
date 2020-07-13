"""Functionality to interact with Jira"""
from re import search

from jira import JIRA, JIRAError

from mlx.traceability_exception import report_warning


def create_jira_issues(settings, traceability_collection):
    """ Creates Jira issues using configuration variable ``traceability_jira_automation``.

    Args:
        settings (dict): Settings relevant to this feature
        traceability_collection (TraceableCollection): Collection of all traceability items
    """
    mandatory_keys = ('api_endpoint', 'username', 'password', 'jira_field_id', 'item_to_ticket_regex', 'issue_type')
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

    relevant_item_ids = traceability_collection.get_items(settings['item_to_ticket_regex'])
    create_unique_issues(relevant_item_ids, jira, general_fields, settings, traceability_collection)


def create_unique_issues(item_ids, jira, general_fields, settings, traceability_collection):
    """ Creates a Jira ticket for each item matching the configured regex.

    Duplication is avoided by first querying Jira issues filtering on project and summary.

    Args:
        item_ids (list): List of item IDs
        jira (jira.JIRA): Jira interface object
        general_fields (dict): Dictionary containing fields that are not item-specific
        settings (dict): Configuration for this feature
        traceability_collection (TraceableCollection): Collection of all traceability items
    """
    for item_id in item_ids:
        fields = {}
        item = traceability_collection.get_item(item_id)
        project_id_or_key = determine_jira_project(settings.get('project_key_regex', ''),
                                                   settings.get('project_key_prefix', ''),
                                                   settings.get('default_project', ''),
                                                   item_id)
        if not project_id_or_key:
            report_warning("Could not determine a JIRA project key or id for item {!r}".format(item_id))
            continue

        assignee = item.get_attribute('assignee')
        jira_field = item.caption
        attendees = []
        if settings['relationship_to_parent']:
            parent_ids = item.iter_targets(settings['relationship_to_parent'])
            if parent_ids:
                parent_id = parent_ids[0]
                parent = traceability_collection.get_item(parent_id)
                jira_field = "{id} {field}".format(id=parent_id, field=jira_field)  # prepend item ID of parent
                attendees = parent.get_attribute('attendees').split(',')

        jira_field_id = settings['jira_field_id']
        matches = jira.search_issues("project={} and {} ~ {!r}".format(project_id_or_key,
                                                                       jira_field_id,
                                                                       jira_field))
        if matches:
            if settings.get('warn_if_exists', False):
                report_warning("Won't create a {} for item {!r} because the Jira API query to check to prevent "
                               "duplication returned {}".format(general_fields['issuetype']['name'], item_id, matches))
            continue

        fields['project'] = project_id_or_key
        fields[jira_field_id] = jira_field
        fields['description'] = item.get_content()
        if assignee:
            fields['assignee'] = {'name': item.get_attribute('assignee')}

        push_item_to_jira(jira, {**fields, **general_fields}, item, attendees)


def push_item_to_jira(jira, fields, item, attendees):
    """ Pushes the request to create a ticket on Jira for the given item.

    The value of the effort option gets added to the Estimated field of the time tracking section. On failure, it gets
    appended to the description instead.
    The attendees are added to the watchers field. A warning is raised for each error returned by Jira.

    Args:
        jira (jira.JIRA): Jira interface object
        general_fields (dict): Dictionary containing all fields to include in the initial creation of the Jira ticket
        item (TraceableItem): Traceable item to create the Jira ticket for
        attendees (list): List of attendees that should get added to the watchers field
    """
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


def determine_jira_project(key_regex, key_prefix, default_project, item_id):
    """ Determines the JIRA project key or id to use for give item ID.

    Args:
        key_regex (str): Regular expression used to scan through the <<item_id>>. In case of a hit, the capture group
            with name 'project' will be used to build the project key.
        key_prefix (str): Prefix to use if <<key_regex>> gets used to build the project key.
        default_project (str): Project key or id to use if a match for <<key_regex>> doesn't get used.

    Returns:
        str: JIRA project key or id.
    """
    key_match = search(key_regex, item_id)
    try:
        return key_prefix + key_match.group('project')
    except (AttributeError, IndexError):
        return default_project
