""" Module for the directive used to set the checklist attribute. """
from re import match

from mlx.traceable_base_directive import TraceableBaseDirective
from mlx.traceability_exception import report_warning, TraceabilityException


class CheckboxResultDirective(TraceableBaseDirective):
    """
    Directive to set value of the checklist attribute for a checklist-item.

    Syntax::
      .. checkbox-result:: item_id attribute_value

    When run, no nodes will be returned.
    """
    # Required argument: id + attribute_value (separated by a whitespace)
    required_arguments = 2

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app

        target_id = self.arguments[0]
        attribute_value = self.arguments[1]
        checklist_item = env.traceability_collection.get_item(target_id)
        if not checklist_item:
            report_warning("Could not find item ID {!r}".format(target_id), env.docname, self.lineno)
            return []

        if not app.config.traceability_checklist.get('configured'):
            raise TraceabilityException("The checklist attribute in 'traceability_checklist' is not configured "
                                        "properly. See documentation for more details.")

        checklist_attribute_name = app.config.traceability_checklist['attribute_name']
        regexp = app.config.traceability_attributes[checklist_attribute_name]
        if match(regexp, attribute_value):
            checklist_item.add_attribute(checklist_attribute_name, attribute_value, overwrite=True)
        else:
            report_warning("Checkbox value invalid: {!r} does not match regex {}".format(attribute_value, regexp),
                           env.docname, self.lineno)

        return []
