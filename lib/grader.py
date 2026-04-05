"""Answer grading: compare predicted answer to ground truth.

Supports numeric comparison, symbolic math equivalence, and string matching.
"""

import re
import logging
from math import isclose

logger = logging.getLogger(__name__)


def normalize_latex(s: str) -> str:
    """Normalize a LaTeX string for comparison."""
    s = s.strip()
    # Remove \left \right
    s = s.replace("\\left", "").replace("\\right", "")
    # Remove \, spacing
    s = s.replace("\\,", "")
    # Remove \text{} wrapper
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    # Remove \mathrm{} wrapper
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    # Remove dollar signs
    s = s.replace("$", "")
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def try_parse_number(s: str) -> float | None:
    """Try to parse a string as a number (int or float)."""
    s = normalize_latex(s)
    # Remove commas in numbers
    s = s.replace(",", "")
    # Handle fractions like \frac{a}{b}
    frac_match = re.match(r"\\frac\{(-?\d+)\}\{(-?\d+)\}", s)
    if frac_match:
        num, den = int(frac_match.group(1)), int(frac_match.group(2))
        return num / den if den != 0 else None
    # Handle simple fractions like a/b
    frac_match = re.match(r"^(-?\d+(?:\.\d+)?)\s*/\s*(-?\d+(?:\.\d+)?)$", s)
    if frac_match:
        num, den = float(frac_match.group(1)), float(frac_match.group(2))
        return num / den if den != 0 else None
    try:
        return float(s)
    except ValueError:
        return None


def grade_integer(predicted: str, gold: str) -> bool:
    """Grade integer answers (AIME-style)."""
    pred_num = try_parse_number(predicted)
    gold_num = try_parse_number(gold)
    if pred_num is not None and gold_num is not None:
        return isclose(pred_num, gold_num, abs_tol=1e-6)
    # Fallback: string comparison after normalization
    return normalize_latex(predicted) == normalize_latex(gold)


def grade_expression(predicted: str, gold: str) -> bool:
    """Grade mathematical expression answers.

    Uses multiple strategies:
    1. Numeric comparison (if both parse to numbers)
    2. Sympy symbolic comparison (if available)
    3. Normalized string comparison (fallback)
    """
    pred_norm = normalize_latex(predicted)
    gold_norm = normalize_latex(gold)

    # Direct string match after normalization
    if pred_norm == gold_norm:
        return True

    # Numeric comparison
    pred_num = try_parse_number(predicted)
    gold_num = try_parse_number(gold)
    if pred_num is not None and gold_num is not None:
        # Use relative tolerance for large numbers, absolute for small
        return isclose(pred_num, gold_num, rel_tol=1e-6, abs_tol=1e-9)

    # Sympy symbolic comparison
    try:
        from sympy.parsing.latex import parse_latex
        from sympy import simplify, nsimplify

        pred_expr = parse_latex(predicted)
        gold_expr = parse_latex(gold)
        diff = simplify(pred_expr - gold_expr)
        if diff == 0:
            return True
        # Try numeric evaluation
        diff_val = complex(diff.evalf())
        if abs(diff_val) < 1e-6:
            return True
    except Exception:
        pass

    # More aggressive normalization for string comparison
    def strip_all(s):
        return re.sub(r"[\\{}\s]", "", s).lower()

    return strip_all(pred_norm) == strip_all(gold_norm)


def grade_choice(predicted: str, gold: str) -> bool:
    """Grade multiple-choice answers."""
    return predicted.strip().upper() == gold.strip().upper()


def grade(predicted: str, gold: str, answer_type: str) -> bool:
    """Grade a predicted answer against the gold answer.

    Args:
        predicted: Extracted predicted answer.
        gold: Ground truth answer.
        answer_type: One of "integer", "expression", "choice".

    Returns:
        True if correct, False otherwise.
    """
    if not predicted:
        return False

    if answer_type == "integer":
        return grade_integer(predicted, gold)
    elif answer_type == "expression":
        return grade_expression(predicted, gold)
    elif answer_type == "choice":
        return grade_choice(predicted, gold)
    else:
        raise ValueError(f"Unknown answer type: {answer_type}")
