
class LogicEvaluator:
    def __init__(self):
        pass

    str_to_token = {'True': True,
                    'False': False,
                    'and': lambda left, right: left and right,
                    'or': lambda left, right: left or right,
                    '(': '(',
                    ')': ')'}

    empty_res = True

    def create_token_lst(self, s, str_to_token=str_to_token):
        """create token list:
        'True or False' -> [True, lambda..., False]"""
        s = s.replace('(', ' ( ')
        s = s.replace(')', ' ) ')

        return [str_to_token[it] for it in s.split()]

    def find(self, lst, what, start=0):
        return [i for i, it in enumerate(lst) if it == what and i >= start]

    def parens(self, token_lst):
        """returns:
            (bool)parens_exist, left_paren_pos, right_paren_pos
        """
        left_lst = self.find(token_lst, '(')

        if not left_lst:
            return False, -1, -1

        left = left_lst[-1]

        #can not occur earlier, hence there are args and op.
        right = self.find(token_lst, ')', left + 4)[0]

        return True, left, right

    def bool_eval(self, token_lst):
        """token_lst has length 3 and format: [left_arg, operator, right_arg]
        operator(left_arg, right_arg) is returned"""
        return token_lst[1](token_lst[0], token_lst[2])

    def formatted_bool_eval(self, token_lst, empty_res=empty_res):
        """eval a formatted (i.e. of the form 'ToFa(ToF)') string"""
        if not token_lst:
            return empty_res

        if len(token_lst) == 1:
            return token_lst[0]

        has_parens, l_paren, r_paren = self.parens(token_lst)

        if not has_parens:
            return self.bool_eval(token_lst)

        token_lst[l_paren:r_paren + 1] = [self.bool_eval(token_lst[l_paren+1:r_paren])]

        return self.formatted_bool_eval(token_lst, self.bool_eval)

    def nested_bool_eval(self, s):
        """The actual 'eval' routine,
        if 's' is empty, 'True' is returned,
        otherwise 's' is evaluated according to parentheses nesting.
        The format assumed:
            [1] 'LEFT OPERATOR RIGHT',
            where LEFT and RIGHT are either:
                    True or False or '(' [1] ')' (subexpression in parentheses)
        """
        return self.formatted_bool_eval(self.create_token_lst(s))