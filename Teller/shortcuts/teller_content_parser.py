from Teller.models import UserTaleVariable
import lxml.html
from Teller.shortcuts.logic_evaluator import LogicEvaluator


class TellerContentParser:
    def __init__(self):
        pass

    def evaluate_algebra(self, algebra_expression, user):
        elements = algebra_expression.split()
        variable_id = int(elements[0].translate(None, "'"))
        value = int(elements[2])
        variable = UserTaleVariable.objects.get(user=user, tale_variable__id=variable_id)
        if elements[1] == ">=":
            return str(variable.value >= value)
        elif elements[1] == "<=":
            return str(variable.value <= value)
        elif elements[1] == "=":
            return str(variable.value == value)

    def evaluate_algebra_in_logic(self, logic_expression, user):
        i = 0
        while i < len(logic_expression):
            i = logic_expression.find('{', i)
            if i == -1:
                break
            j = logic_expression.find('}', i)
            algebra_expression = logic_expression[i + 1:j]
            evaluated_expression = self.evaluate_algebra(algebra_expression, user)
            logic_expression = logic_expression[:i] + evaluated_expression + logic_expression[j+1:]
            i += len(evaluated_expression)
        logic_expression = logic_expression.replace("(True)", "True")
        logic_expression = logic_expression.replace("(False)", "False")
        return logic_expression

    def prepare_conditional_content(self, tale_part, user):
        logic_evaluator = LogicEvaluator()
        content = lxml.html.fragment_fromstring(tale_part.content, create_parent='div')
        talelogic_outers = content.find_class('talelogic-outer')
        for talelogic_outer in talelogic_outers:
            data_talelogic = talelogic_outer.get("data-talelogic")
            result = logic_evaluator.nested_bool_eval(self.evaluate_algebra_in_logic(data_talelogic, user))
            talelogic_if = talelogic_outer.find_class('talelogic-if')[0]
            talelogic_if_condition = talelogic_if.find_class('talelogic-if-condition')[0]
            talelogic_if_condition.drop_tree()
            talelogic_if_text = talelogic_if.find_class('talelogic-if-text')[0]
            talelogic_else = talelogic_outer.find_class('talelogic-else')[0]
            talelogic_else_condition = talelogic_else.find_class('talelogic-else-condition')[0]
            talelogic_else_condition.drop_tree()
            talelogic_else_text = talelogic_else.find_class('talelogic-else-text')[0]
            if result:
                talelogic_if_text.drop_tag()
                talelogic_if.drop_tag()
                talelogic_else.drop_tree()
            else:
                talelogic_else_text.drop_tag()
                talelogic_else.drop_tag()
                talelogic_if.drop_tree()
            talelogic_outer.drop_tag()
        tale_part.content = lxml.html.tostring(content)
        return tale_part