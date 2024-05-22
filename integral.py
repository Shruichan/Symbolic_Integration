import re

class Term:
    def __init__(self, coefficient, base, exponent):
        self.coefficient = coefficient
        self.base = base
        self.exponent = exponent

    def __repr__(self):
        return f"{self.coefficient}*{self.base}^{self.exponent}"

    def integrate(self):
        if self.base == 'x':
            new_exponent = self.exponent + 1
            new_coefficient = self.coefficient / new_exponent
            return Term(new_coefficient, self.base, new_exponent)
        else:
            raise NotImplementedError("Integration for non-x bases is not implemented")

class Parser:
    @staticmethod
    def parse_term(term):
        match = re.match(r'(\d*\.?\d*)\*?(x)\^(\d*\.?\d*)', term)
        if match:
            coeff = float(match.group(1)) if match.group(1) else 1
            base = match.group(2)
            exp = float(match.group(3)) if match.group(3) else 1
            return Term(coeff, base, exp)
        else:
            raise ValueError(f"Unsupported term format: {term}")

    @staticmethod
    def parse(expression):
        expression = re.sub(r'\s+', '', expression)
        return Parser.parse_expression(expression)

    @staticmethod
    def parse_expression(expression):
        if '(' not in expression:
            return Parser.parse_simple_expression(expression)

        sub_expressions = []
        balance = 0
        start = 0

        for i, char in enumerate(expression):
            if char == '(':
                if balance == 0:
                    start = i
                balance += 1
            elif char == ')':
                balance -= 1
                if balance == 0:
                    sub_expressions.append((start, i))

        parsed_terms = []
        last_pos = 0

        for start, end in sub_expressions:
            before_sub_expr = expression[last_pos:start]
            if before_sub_expr:
                parsed_terms.extend(Parser.parse_simple_expression(before_sub_expr))

            sub_expr = expression[start+1:end]
            sub_expr_terms = Parser.parse_expression(sub_expr)

            if expression[end+1:end+2] == '^':
                end += 1
                power_match = re.match(r'\^(\d+)', expression[end+1:])
                if power_match:
                    power = int(power_match.group(1))
                    sub_expr_terms = [Term(term.coefficient, term.base, term.exponent * power) for term in sub_expr_terms]
                    end += len(power_match.group(0))

            parsed_terms.extend(sub_expr_terms)
            last_pos = end + 1

        after_last_sub_expr = expression[last_pos:]
        if after_last_sub_expr:
            parsed_terms.extend(Parser.parse_simple_expression(after_last_sub_expr))

        return parsed_terms

    @staticmethod
    def parse_simple_expression(expression):
        if not expression:
            return []

        terms = re.split(r'(\+|\-)', expression)
        parsed_terms = []
        current_sign = 1

        for term in terms:
            term = term.strip()
            if term == '+':
                current_sign = 1
            elif term == '-':
                current_sign = -1
            elif term:
                try:
                    parsed_term = Parser.parse_term(term)
                    parsed_term.coefficient *= current_sign
                    parsed_terms.append(parsed_term)
                except ValueError:
                    if '*' in term:
                        factors = term.split('*')
                        product_term = None
                        for factor in factors:
                            if 'x' in factor:
                                term = Parser.parse_term(factor)
                                if product_term is None:
                                    product_term = term
                                else:
                                    if product_term.base == term.base:
                                        new_coefficient = product_term.coefficient * term.coefficient
                                        new_exponent = product_term.exponent + term.exponent
                                        product_term = Term(new_coefficient, product_term.base, new_exponent)
                                    else:
                                        raise ValueError("Different bases in multiplication are not supported")
                        if product_term:
                            product_term.coefficient *= current_sign
                            parsed_terms.append(product_term)
                    elif '/' in term:
                        numerator, denominator = term.split('/')
                        try:
                            numerator_term = Parser.parse_term(numerator)
                        except ValueError:
                            numerator_term = Term(float(numerator), 'x', 0) if numerator.isdigit() else None
                        try:
                            denominator_term = Parser.parse_term(denominator)
                        except ValueError:
                            denominator_term = Term(float(denominator), 'x', 0) if denominator.isdigit() else None
                        if numerator_term and denominator_term:
                            # Simplify the division
                            if numerator_term.base == denominator_term.base:
                                new_coefficient = current_sign * numerator_term.coefficient / denominator_term.coefficient
                                new_exponent = numerator_term.exponent - denominator_term.exponent
                                parsed_terms.append(Term(new_coefficient, numerator_term.base, new_exponent))
                            else:
                                raise ValueError("Different bases in division are not supported")
                    else:
                        raise ValueError(f"Unsupported term format: {term}")

        return parsed_terms

def format_integrated_terms(terms):
    formatted_terms = []
    for term in terms:
        if term.exponent == 1:
            formatted_terms.append(f"{term.coefficient}*x")
        else:
            formatted_terms.append(f"{term.coefficient/term.exponent}*x^{term.exponent}")
    return ' + '.join(formatted_terms) + ' + C'

def indefinite_integral(expression):
    parsed_terms = Parser.parse(expression)
    integrated_terms = [term.integrate() for term in parsed_terms]
    return format_integrated_terms(integrated_terms)

if __name__ == "__main__":
    expression_str = input("Enter a mathematical expression to integrate (e.g., '3*x^2 + 2*x^1 + (3*x^2) / (2*x^5)'): ")
    result = indefinite_integral(expression_str)
    print(f"The indefinite integral of {expression_str} is:")
    print(result)
