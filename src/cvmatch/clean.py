"""Clean and tokenise text from CVs and job descriptions.

Cleaning is deliberately light: lower-case, collapse whitespace,
strip punctuation that does not carry meaning, and drop a small
stop-word list. The cleaned text feeds TF-IDF and skill matching.
"""

import re

STOP_WORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with",
    "by", "at", "from", "as", "is", "are", "was", "were", "be", "been",
    "we", "our", "you", "your", "will", "shall", "should", "must", "can",
    "this", "that", "these", "those", "it", "its", "i", "me", "my", "he",
    "she", "they", "them", "their", "his", "her", "not", "no", "do", "does",
    "did", "have", "has", "had", "than", "then", "so", "such", "into",
    "about", "over", "under", "between", "through", "per", "via",
}

_WORD_RE = re.compile(r"[a-z][a-z0-9+#.]*")


def clean_text(text):
    """Lower-case text, collapse whitespace and strip stray characters."""
    if not text:
        return ""
    text = text.lower()
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenise(text, remove_stop_words=True):
    """Split cleaned text into word tokens.

    Keeps tokens like ``c++`` and ``.net``; drops pure numbers and,
    by default, stop words.
    """
    cleaned = clean_text(text)
    tokens = _WORD_RE.findall(cleaned)
    tokens = [t.strip(".") for t in tokens]
    tokens = [t for t in tokens if t and not t.isdigit()]
    if remove_stop_words:
        tokens = [t for t in tokens if t not in STOP_WORDS]
    return tokens


def keywords(text, top_n=20):
    """Return the most frequent meaningful words in the text."""
    from collections import Counter

    counts = Counter(tokenise(text))
    return [word for word, _ in counts.most_common(top_n)]
