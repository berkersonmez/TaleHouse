import lxml.html
import re
from lxml.html.clean import Cleaner
from django.conf import settings
from Teller.shortcuts.logic_evaluator import LogicEvaluator


class TellerContentParser:
    def __init__(self):
        self.whitespace_regex = re.compile('^\s+$', re.UNICODE)
        pass

    def evaluate_algebra(self, algebra_expression, user, tale_variables):
        elements = algebra_expression.split()
        variable_id = int(elements[0].translate(None, "'"))
        value = int(elements[2])
        variable = next((x for x in tale_variables if x.id == variable_id), None)
        if variable is None:
            return 'False'
        if elements[1] == ">=":
            return str(variable.value >= value)
        elif elements[1] == "<=":
            return str(variable.value <= value)
        elif elements[1] == "=":
            return str(variable.value == value)

    def evaluate_algebra_in_logic(self, logic_expression, user, tale_variables):
        i = 0
        while i < len(logic_expression):
            i = logic_expression.find('{', i)
            if i == -1:
                break
            j = logic_expression.find('}', i)
            algebra_expression = logic_expression[i + 1:j]
            evaluated_expression = self.evaluate_algebra(algebra_expression, user, tale_variables)
            logic_expression = logic_expression[:i] + evaluated_expression + logic_expression[j+1:]
            i += len(evaluated_expression)
        logic_expression = logic_expression.replace("(True)", "True")
        logic_expression = logic_expression.replace("(False)", "False")
        return logic_expression

    def prepare_conditional_content(self, tale_part, user, tale_variables):
        logic_evaluator = LogicEvaluator()
        content = lxml.html.fragment_fromstring(tale_part.content, create_parent='div')
        talelogic_outers = content.find_class('talelogic-outer')
        for talelogic_outer in talelogic_outers:
            data_talelogic = talelogic_outer.get("data-talelogic")
            result = logic_evaluator.nested_bool_eval(self.evaluate_algebra_in_logic(data_talelogic, user,
                                                                                     tale_variables))
            talelogic_if = talelogic_outer.find_class('talelogic-if')[0]
            talelogic_if_condition = talelogic_if.find_class('talelogic-if-condition')[0]
            talelogic_if_condition.drop_tree()
            talelogic_if_text = talelogic_if.find_class('talelogic-if-text')[0]
            talelogic_else = talelogic_outer.find_class('talelogic-else')[0]
            talelogic_else_condition = talelogic_else.find_class('talelogic-else-condition')[0]
            talelogic_else_condition.drop_tree()
            talelogic_else_text = talelogic_else.find_class('talelogic-else-text')[0]
            if result:
                if len(talelogic_if_text) == 1 and self.whitespace_regex.match(talelogic_if_text[0].text) is not None:
                    talelogic_if_text.drop_tree()
                else:
                    talelogic_if_text.drop_tag()
                talelogic_if.drop_tag()
                talelogic_else.drop_tree()
            else:
                if len(talelogic_else_text) == 1 and self.whitespace_regex.match(talelogic_else_text[0].text) is not None:
                    talelogic_else_text.drop_tree()
                else:
                    talelogic_else_text.drop_tag()
                talelogic_else.drop_tag()
                talelogic_if.drop_tree()
            talelogic_outer.drop_tag()
        talelogic_variable_values = content.find_class('talelogic-variable-value')
        for talelogic_variable_value in talelogic_variable_values:
            data_talelogic_variable = talelogic_variable_value.get("data-talelogic-variable")
            variable = next((x for x in tale_variables if x.id == int(data_talelogic_variable)), None)
            if variable is None:
                talelogic_variable_value.text = '-'
            else:
                talelogic_variable_value.text = str(variable.value)
            talelogic_variable_value.drop_tag()
        tale_part.content = lxml.html.tostring(content)
        return tale_part

    def clean_conditional_content(self, tale_part):
        content = lxml.html.fragment_fromstring(tale_part.content, create_parent='div')
        talelogic_outers = content.find_class('talelogic-outer')
        for talelogic_outer in talelogic_outers:
            talelogic_outer.drop_tree()
        talelogic_variable_values = content.find_class('talelogic-variable-value')
        for talelogic_variable_value in talelogic_variable_values:
            talelogic_variable_value.drop_tree()
        tale_part.content = lxml.html.tostring(content)
        return tale_part

    def clean_html(self, content):
        cleaner = Cleaner(host_whitelist=['www.youtube.com'], safe_attrs=settings.TELLER_CONTENT_SAFE_ATTRS)
        return cleaner.clean_html(content)