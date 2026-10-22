"""CER and WER.

Two variants:
  * `cer` -- ours, matching the protocol described in the paper: NFC, lowercase, collapsed whitespace,
    Levenshtein distance / ground-truth length, clipped to 1.0.
  * `cer_authors` -- exactly what the authors' code computes (src/preprocessing/cer_wer_calculation.py):
    no normalisation, and because of swapped arguments it divides by the PREDICTION length.
"""
import re
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
        return 1.0  # the authors store None and later fillna(1.0)
    if lowercase:
        t, p = t.lower(), p.lower()
    return min(editdistance.eval(t, p) / max(1, len(p)), 1.0)
