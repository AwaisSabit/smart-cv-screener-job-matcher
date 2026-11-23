"""Turn CV and job text into TF-IDF vectors for matching.

One shared vectoriser is fitted on the CVs and the job together, so
their vectors live in the same space and can be compared directly.
"""

from sklearn.feature_extraction.text import TfidfVectorizer

from cvmatch.clean import clean_text


def build_vectoriser(documents, max_features=5000):
    """Fit a TF-IDF vectoriser on the given documents.

    Uses word n-grams of length 1–2 so "machine learning" counts as
    one feature, and English stop words are removed.
    """
    vectoriser = TfidfVectorizer(
        preprocessor=clean_text,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=max_features,
        min_df=1,
    )
    vectoriser.fit(documents)
    return vectoriser


def vectorise(vectoriser, documents):
    """Transform documents into TF-IDF vectors with a fitted vectoriser."""
    return vectoriser.transform(documents)


def vectorise_pair(cv_text, job_text):
    """Vectorise one CV and one job in the same space.

    Returns ``(cv_vector, job_vector, vectoriser)``.
    """
    vectoriser = build_vectoriser([cv_text, job_text])
    vectors = vectoriser.transform([cv_text, job_text])
    return vectors[0], vectors[1], vectoriser


def vectorise_many(cv_texts, job_text):
    """Vectorise many CVs and one job in the same space.

    Returns ``(cv_vectors, job_vector, vectoriser)``.
    """
    documents = list(cv_texts) + [job_text]
    vectoriser = build_vectoriser(documents)
    vectors = vectoriser.transform(documents)
    return vectors[:-1], vectors[-1], vectoriser
