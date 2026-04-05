"""Robust answer extraction from model responses.

Strategy (ordered by priority):
1. Extract from \\boxed{...} (handle nested braces)
2. Extract from "the answer is ..." / "answer: ..." patterns
3. For integer-type: extract the last standalone number
"""

import re
import logging

logger = logging.getLogger(__name__)


def extract_boxed(text: str) -> str | None:
    """Extract content from the LAST \\boxed{...}, handling nested braces.

    Also handles truncated responses where \\boxed{ has no closing brace.
    """
    pattern = r"\\boxed\s*\{"
    matches = list(re.finditer(pattern, text))
    if not matches:
        return None

    last_match = matches[-1]
    start = last_match.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1

    if depth == 0:
        content = text[start : i - 1].strip()
        return content

    # Handle truncated \boxed{... (no closing brace, e.g. max_tokens cutoff)
    # Take whatever is inside, stripping trailing incomplete tokens
    content = text[start:].strip()
    # Remove trailing incomplete LaTeX commands or words
    content = re.sub(r"[\\a-zA-Z{(]*$", "", content).strip()
    if content:
        return content
    return None


def extract_answer_pattern(text: str) -> str | None:
    """Extract from common answer declaration patterns."""
    patterns = [
        r"[Tt]he\s+(?:final\s+)?answer\s+is[:\s]*\$?([^\$\n.]+)\$?",
        r"[Aa]nswer[:\s]+\$?([^\$\n.]+)\$?",
        r"[Tt]herefore[,\s]+(?:the\s+answer\s+is\s+)?\$?([^\$\n.]+)\$?",
        r"=\s*\\boxed\{([^}]+)\}",
    ]
    for pat in patterns:
        matches = list(re.finditer(pat, text))
        if matches:
            return matches[-1].group(1).strip()
    return None


def extract_last_number(text: str) -> str | None:
    """Extract the last standalone integer from the text."""
    matches = re.findall(r"(?<!\w)(-?\d+)(?!\w)", text)
    return matches[-1] if matches else None


def extract_answer(response: str, answer_type: str) -> str:
    """Extract the predicted answer from a model response.

    Args:
        response: Full model response text.
        answer_type: One of "integer", "expression", "choice".

    Returns:
        Extracted answer string, or empty string if extraction fails.
    """
    if not response:
        return ""

    # Strategy 1: \\boxed{...}
    boxed = extract_boxed(response)
    if boxed is not None:
        # Clean up: remove trailing punctuation, \text wrappers
        boxed = re.sub(r"\\text\{([^}]*)\}", r"\1", boxed)
        boxed = boxed.strip().rstrip(".")
        return boxed

    # Strategy 2: for integer type, try to find number near answer keywords first
    if answer_type == "integer":
        # Look for "answer is <number>" pattern specifically
        int_patterns = [
            r"[Aa]nswer\s+is\s+\$?\s*(\d+)\s*\$?",
            r"\\boxed\s*\{?\s*(\d+)",
            r"=\s*(\d+)\s*$",
        ]
        for pat in int_patterns:
            matches = list(re.finditer(pat, response))
            if matches:
                return matches[-1].group(1)

    # Strategy 3: "the answer is ..." patterns (general)
    pattern_match = extract_answer_pattern(response)
    if pattern_match is not None:
        extracted = pattern_match.strip().rstrip(".")
        # Validate: for integer type, must be a number
        if answer_type == "integer":
            if re.match(r"^-?\d+$", extracted):
                return extracted
        else:
            return extracted

    # Strategy 4: type-specific fallbacks
    if answer_type == "integer":
        num = extract_last_number(response)
        if num is not None:
            return num

    if answer_type == "choice":
        # Look for standalone letter (A-E) near the end
        matches = re.findall(r"\b([A-E])\b", response[-200:])
        if matches:
            return matches[-1]

    logger.warning(f"Could not extract answer from response (length={len(response)})")
    return ""
