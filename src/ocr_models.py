"""OCR engines run locally on CPU. Each loader takes a language code and returns read(path) -> str.

Imports are lazy because PaddleOCR 2.9.1 lives in a separate environment (.venv-paddle) without torch.
TrOCR and PaddleOCR settings are copied from the authors' notebooks (run_ocr/trocr.ipynb, paddle.ipynb).
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tesseract(lang="pol"):
    import pytesseract
    from PIL import Image

    tess = ROOT / ".tools" / "tess"  # local micromamba install (see README); otherwise the system tesseract
    if (tess / "bin" / "tesseract").exists():
        pytesseract.pytesseract.tesseract_cmd = str(tess / "bin" / "tesseract")
        os.environ.setdefault("TESSDATA_PREFIX", str(tess / "share" / "tessdata"))
    # psm 7: the image holds a single text line (a word or a sentence)
    return lambda path: pytesseract.image_to_string(Image.open(path), lang=lang, config="--psm 7").strip()


def easyocr(lang="pl"):
    import easyocr as easy

    reader = easy.Reader([lang], gpu=False, verbose=False)
    return lambda path: " ".join(reader.readtext(str(path), detail=0))


def trocr(lang=None, model="microsoft/trocr-large-printed"):
    import torch
    from PIL import Image
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    processor = TrOCRProcessor.from_pretrained(model)
    net = VisionEncoderDecoderModel.from_pretrained(model).eval()
    # transformers 5 builds the model on the meta device; the sinusoidal position table is a plain attribute
    # (not a buffer), so it is never materialised and has to be recomputed
    for m in net.modules():
        if hasattr(m, "get_embedding") and getattr(m, "weights", None) is not None and m.weights.is_meta:
            m.weights = m.get_embedding(m.weights.size(0), m.embedding_dim, m.padding_idx)

    def read(path):
        pixels = processor(images=Image.open(path).convert("RGB"), return_tensors="pt").pixel_values
        with torch.inference_mode():
            # the checkpoint ships use_cache=False, which makes CPU decoding ~2.5x slower; greedy output is identical
            # max_length stays at the library default (21 tokens), as in the authors' runs, so long lines are cut
            ids = net.generate(pixels, use_cache=True)
        return processor.batch_decode(ids, skip_special_tokens=True)[0]

    return read


def paddle(lang="en"):
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=False, show_log=False)

    def read(path):
        result = ocr.ocr(str(path), cls=True)
        lines = [line[1][0] for block in (result or []) if block for line in block]
        return "\n".join(lines)  # as in the authors' notebook

    return read


QWEN_PROMPT = ("Extract the {language} text from the image exactly as it appears. Do not repeat, comment, translate, "
               "or add any text. Return only the raw text. If no text is detected, return an empty response.")


def qwen(lang="Polish", model=None):
    """Qwen2.5-VL with the authors' prompt (run_ocr/qwen.ipynb), the language name swapped in.

    The authors used the 7B model; it needs ~17 GB in bf16 (Colab L4/A100). The 3B model fits a T4 or 16 GB RAM.
    """
    import torch
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    gpu = torch.cuda.is_available()
    if model is None:
        big = gpu and torch.cuda.get_device_properties(0).total_memory > 20e9
        model = f"Qwen/Qwen2.5-VL-{'7B' if big else '3B'}-Instruct"
    print(f"loading {model} on {'cuda' if gpu else 'cpu'}", flush=True)
    net = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model, dtype=torch.bfloat16 if not gpu or torch.cuda.is_bf16_supported() else torch.float16,
    ).to("cuda" if gpu else "cpu").eval()
    processor = AutoProcessor.from_pretrained(model)
    prompt = QWEN_PROMPT.format(language=lang)

    def read(path):
        messages = [{"role": "user", "content": [{"type": "image", "image": f"file://{Path(path).resolve()}"},
                                                 {"type": "text", "text": prompt}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        images, videos = process_vision_info(messages)
        inputs = processor(text=[text], images=images, videos=videos, padding=True, return_tensors="pt").to(net.device)
        with torch.inference_mode():
            ids = net.generate(**inputs, max_new_tokens=128)
        return processor.batch_decode(ids[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0].strip()

    return read


MODELS = {"tesseract": tesseract, "easyocr": easyocr, "trocr": trocr, "paddle": paddle, "qwen": qwen}
