""" Module for the directive for declaring checklist items. """
from mlx.directives.item_directive import ItemDirective
from mlx.traceability_exception import report_warning, TraceabilityException


class ChecklistItemDirective(ItemDirective):
    """
    Directive to declare checklist items and their traceability relationships. The behavior is the same as
    ItemDirective except that an extra attribute is added when the item ID is found in the queried checklist.
    The checklist has been queried using the ``traceability_checklist`` configuration variable.
    """
    query_results = {}

    def run(self):
        """ Processes the contents of the directive. """
        env = self.state.document.settings.env
        app = env.app


        [target_node, item_node] = super().run()
        target_id = self.arguments[0]

        try:
            item = env.traceability_collection.get_item(target_id)
            item.add_attribute(app.config.traceability_checklist['attribute_name'], self.query_results[target_id])
        except TraceabilityException as err:
            report_warning(env, err, env.docname, self.lineno)
        except KeyError as err:
            report_warning(env,
                           "Could not find item {} in a checklist; only {}."
                           .format(err, list(self.query_results.keys())),
                           env.docname,
                           self.lineno)

        return [target_node, item_node]
