#!/usr/bin/python3 -B

import re

def tokenize(program):
    # \s* -> Matches any number of blanks [ \t\n\r\f\v].
    # (?:...) -> A non-capturing version of regular parentheses.
    # \b -> Matches the empty string, but only at the beginning or end of a word.
    # \w -> Matches [a-zA-Z0-9_]
    reg = "\s*(?:(and|or|not|\(|\))|(\"[ \.\w_\-\&]+\")|([\.\w_\-\&]+))"
    for operator, q_string, string in re.findall(reg, program):
        # print 'Tokenize >> Program -> "' + program + \
        #       '", String -> "' + string + '", Operator -> "' + operator + '"\n';
        if string:
            yield 'Literal "{}"'.format(string)
        elif q_string:
            if q_string[0] == '"': q_string = q_string[1:]
            if q_string[-1] == '"': q_string = q_string[:-1]
            yield 'Literal quoted "{}"'.format(q_string)
        elif operator == "and":
            yield 'Operator AND'
        elif operator == "or":
            yield 'Operator OR'
        elif operator == "not":
            yield 'Operator NOT'
        elif operator == "(":
            yield 'Operator ('
        elif operator == ")":
            yield 'Operator )'
        else:
            raise SyntaxError("Unknown operator: %r".format(operator))
    yield 'END Token'

# --- main code ---
# t_str = '"Ball & Paddle" or "Whac A Mole" or Climbing or Driving or Fighter or Platform or Puzzle or Shooter or Sports'
t_str = 'contains(Konami)'
print("String '{}'".format(t_str))
for i, token in enumerate(tokenize(t_str)):
    print("Token {:02d} '{}'".format(i, token))
