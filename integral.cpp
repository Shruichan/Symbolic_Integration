#include <iostream>
#include <string>
#include <regex>
#include <vector>
#include <sstream>
#include <stdexcept>

class Term {
public:
    float coefficient;
    std::string base;
    float exponent;

    Term(float coeff, const std::string &base, float exp) : coefficient(coeff), base(base), exponent(exp) {}

    std::string to_string() const {
        std::ostringstream oss;
        oss << coefficient << "*" << base << "^" << exponent;
        return oss.str();
    }

    Term integrate() const {
        if (base == "x") {
            float new_exponent = exponent + 1;
            float new_coefficient = coefficient / new_exponent;
            return Term(new_coefficient, base, new_exponent);
        } else {
            throw std::runtime_error("Integration for non-x bases is not implemented");
        }
    }
};

class Parser {
public:
    static Term parse_term(const std::string &term) {
        std::regex pattern(R"((\d*\.?\d*)\*?(x)\^(\d*\.?\d*))");
        std::smatch matches;
        if (std::regex_match(term, matches, pattern)) {
            float coeff = matches[1].str().empty() ? 1 : std::stof(matches[1].str());
            std::string base = matches[2].str();
            float exp = matches[3].str().empty() ? 1 : std::stof(matches[3].str());
            return Term(coeff, base, exp);
        } else {
            throw std::runtime_error("Unsupported term format: " + term);
        }
    }

    static std::vector<Term> parse_expression(const std::string &expression) {
        std::vector<Term> terms;
        std::regex term_pattern(R"((\+|\-)?(\d*\.?\d*)\*?(x)\^(\d*\.?\d*))");
        auto begin = std::sregex_iterator(expression.begin(), expression.end(), term_pattern);
        auto end = std::sregex_iterator();
        bool is_positive = true;

        for (std::sregex_iterator i = begin; i != end; ++i) {
            std::smatch match = *i;
            float coeff = match[2].str().empty() ? 1 : std::stof(match[2].str());
            if (match[1].matched && match[1].str() == "-")
                coeff = -coeff;

            terms.push_back(Term(coeff, match[3].str(), std::stof(match[4].str())));
        }
        return terms;
    }

    static std::vector<Term> parse(const std::string &expression) {
        return parse_expression(expression);
    }
};

std::string format_integrated_terms(const std::vector<Term>& terms) {
    std::ostringstream oss;
    bool first = true;
    for (const auto &term : terms) {
        if (!first)
            oss << " + ";
        first = false;
        oss << term.integrate().to_string();
    }
    oss << " + C";
    return oss.str();
}

std::string indefinite_integral(const std::string &expression) {
    auto terms = Parser::parse(expression);
    return format_integrated_terms(terms);
}

int main() {
    std::string expression;
    std::cout << "Enter a mathematical expression to integrate (e.g., '3*x^2 + 2*x^1'): ";
    std::getline(std::cin, expression);

    try {
        std::string result = indefinite_integral(expression);
        std::cout << "The indefinite integral of " << expression << " is:\n";
        std::cout << result << std::endl;
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
