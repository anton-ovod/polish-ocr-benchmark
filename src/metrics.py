"""CER and WER: ours and the two variants found in the authors' code."""
import re
import string
import unicodedata

import editdistance
import jiwer


def normalize(text):
    text = unicodedata.normalize("NFC", str(text or "")).lower()
    return re.sub(r"\s+", " ", text).strip()


def cer(truth, pred):
    t, p = normalize(truth), normalize(pred)
    return min(editdistance.eval(t, p) / max(1, len(t)), 1.0)


def wer(truth, pred):
    t, p = normalize(truth), normalize(pred)
    if not t:
        return float(bool(p))
    return min(jiwer.wer(t, p) if p else 1.0, 1.0)


def cer_authors(truth, pred, lowercase=False):
    t, p = str(truth or "").strip(), str(pred or "").strip()
    if not t or not p:
        return 1.0
    if lowercase:
        t, p = t.lower(), p.lower()
    return min(editdistance.eval(t, p) / max(1, len(p)), 1.0)


_STRIP = str.maketrans("", "", string.whitespace + string.punctuation)


def cer_authors_nospace(truth, pred):
    t, p = str(truth or "").strip().lower(), str(pred or "").strip().lower()
    if not t or not p:
        return 1.0
    t, p = t.translate(_STRIP), p.translate(_STRIP)
    if not t:
        return 1.0
    return min(editdistance.eval(t, p) / len(t), 1.0)
