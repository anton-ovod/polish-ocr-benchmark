"""OCR engines: each loader returns read(path) -> str."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tesseract(lang="pol"):
    import pytesseract
    from PIL import Image

    tess = ROOT / ".tools" / "tess"
    if (tess / "bin" / "tesseract").exists():
        pytesseract.pytesseract.tesseract_cmd = str(tess / "bin" / "tesseract")
        os.environ.setdefault("TESSDATA_PREFIX", str(tess / "share" / "tessdata"))
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
    device = "cuda" if torch.cuda.is_available() else "cpu"
    net = VisionEncoderDecoderModel.from_pretrained(model).eval()
    for m in net.modules():
        if hasattr(m, "get_embedding") and getattr(m, "weights", None) is not None and m.weights.is_meta:
            m.weights = m.get_embedding(m.weights.size(0), m.embedding_dim, m.padding_idx)
    net.to(device)

    def read(path):
        pixels = processor(images=Image.open(path).convert("RGB"), return_tensors="pt").pixel_values.to(device)
        with torch.inference_mode():
            ids = net.generate(pixels, use_cache=True)
        return processor.batch_decode(ids, skip_special_tokens=True)[0]

    return read


def paddle(lang="en"):
    import paddle as framework
    from paddleocr import PaddleOCR

    use_gpu = framework.device.is_compiled_with_cuda()
    if use_gpu and not framework.device.cuda.device_count():
        raise RuntimeError("GPU build of Paddle, but it sees no GPU")
    ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu, show_log=False)
    print(f"PaddleOCR device: {framework.device.get_device()}", flush=True)

    def read(path):
        result = ocr.ocr(str(path), cls=True)
        lines = [line[1][0] for block in (result or []) if block for line in block]
        return "\n".join(lines)

    return read


QWEN_PROMPT = ("Extract the {language} text from the image exactly as it appears. Do not repeat, comment, translate, "
               "or add any text. Return only the raw text. If no text is detected, return an empty response.")


def qwen(lang="Polish", model=None):
    import torch
    import transformers
    from qwen_vl_utils import process_vision_info
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    gpu = torch.cuda.is_available()
    if model is None:
        big = gpu and torch.cuda.get_device_properties(0).total_memory > 20e9
        model = f"Qwen/Qwen2.5-VL-{'7B' if big else '3B'}-Instruct"
    print(f"loading {model} on {'cuda' if gpu else 'cpu'}", flush=True)
    dtype = torch.bfloat16 if not gpu or torch.cuda.is_bf16_supported() else torch.float16
    dtype_arg = "dtype" if tuple(int(x) for x in transformers.__version__.split(".")[:2]) >= (4, 56) else "torch_dtype"
    net = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        model, **{dtype_arg: dtype},
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


INTERNVL_PROMPT = ("<image>\nExtract the {language} text from the image exactly as it appears. Do not repeat any text, "
                   "do not add any comments, and do not generate additional text. Only return the raw text found in "
                   "the image, without any formatting or repetition. If the text or image is not clear to extract "
                   "text or doing ocr process, just give me blank(empty) output.")
DEEPSEEK_PROMPT = "<image>\n<|ref|>Extract the {language} text exactly.<|/ref|>."


def _internvl_tiles(image, image_size=448, max_num=12):
    width, height = image.size
    ratios = sorted({(i, j) for i in range(1, max_num + 1) for j in range(1, max_num + 1) if i * j <= max_num},
                    key=lambda r: r[0] * r[1])
    best, best_diff = (1, 1), float("inf")
    for r in ratios:
        diff = abs(width / height - r[0] / r[1])
        if diff < best_diff:
            best, best_diff = r, diff
        elif diff == best_diff and width * height > 0.5 * image_size * image_size * r[0] * r[1]:
            best = r
    columns, rows = best
    resized = image.resize((image_size * columns, image_size * rows))
    tiles = [resized.crop((c * image_size, r * image_size, (c + 1) * image_size, (r + 1) * image_size))
             for r in range(rows) for c in range(columns)]
    if len(tiles) != 1:
        tiles.append(image.resize((image_size, image_size)))
    return tiles


def internvl(lang="Turkish", model="OpenGVLab/InternVL3-8B"):
    import torch
    import torchvision.transforms as T
    from PIL import Image
    from torchvision.transforms.functional import InterpolationMode
    from transformers import AutoModel, AutoTokenizer

    gpu = torch.cuda.is_available()
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True, use_fast=False)
    net = AutoModel.from_pretrained(model, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True, use_flash_attn=False,
                                    trust_remote_code=True).eval()
    net = net.cuda() if gpu else net
    transform = T.Compose([T.Resize((448, 448), interpolation=InterpolationMode.BICUBIC), T.ToTensor(),
                           T.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225))])
    prompt = INTERNVL_PROMPT.format(language=lang)
    config = dict(max_new_tokens=512, do_sample=False, temperature=0.0)

    def read(path):
        tiles = _internvl_tiles(Image.open(path).convert("RGB"))
        pixels = torch.stack([transform(t) for t in tiles]).to(torch.bfloat16).to(net.device)
        with torch.inference_mode():
            return net.chat(tokenizer, pixels, prompt, config)

    return read


def deepseek(lang="Turkish", model="deepseek-ai/deepseek-vl2-tiny"):
    import torch
    from deepseek_vl2.models import DeepseekVLV2Processor
    from deepseek_vl2.utils.io import load_pil_images
    from transformers import AutoModelForCausalLM

    processor = DeepseekVLV2Processor.from_pretrained(model)
    net = AutoModelForCausalLM.from_pretrained(model, trust_remote_code=True)
    net = net.to(torch.bfloat16).to("cuda" if torch.cuda.is_available() else "cpu").eval()
    prompt = DEEPSEEK_PROMPT.format(language=lang)

    def read(path):
        conversation = [{"role": "<|User|>", "content": prompt, "images": [str(path)]},
                        {"role": "<|Assistant|>", "content": ""}]
        inputs = processor(conversations=conversation, images=load_pil_images(conversation), force_batchify=True,
                           system_prompt="").to(net.device)
        tok = processor.tokenizer
        with torch.inference_mode():
            ids = net.generate(inputs_embeds=net.prepare_inputs_embeds(**inputs), attention_mask=inputs.attention_mask,
                               pad_token_id=tok.eos_token_id, bos_token_id=tok.bos_token_id,
                               eos_token_id=tok.eos_token_id, max_new_tokens=512, do_sample=False, use_cache=True)
        return tok.decode(ids[0].cpu().tolist(), skip_special_tokens=True)

    return read


def phi(lang="Turkish", model="microsoft/Phi-3.5-vision-instruct"):
    import torch
    from PIL import Image
    from transformers import AutoModelForCausalLM, AutoProcessor

    processor = AutoProcessor.from_pretrained(model, trust_remote_code=True, num_crops=16)
    net = AutoModelForCausalLM.from_pretrained(model, device_map="auto", trust_remote_code=True, torch_dtype="auto",
                                               _attn_implementation="eager").eval()
    messages = [{"role": "user", "content": "<|image_1|>\n" + QWEN_PROMPT.format(language=lang)}]
    prompt = processor.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def read(path):
        inputs = processor(prompt, [Image.open(path).convert("RGB")], return_tensors="pt").to(net.device)
        with torch.inference_mode():
            ids = net.generate(**inputs, max_new_tokens=512, temperature=0.0, do_sample=False,
                               eos_token_id=processor.tokenizer.eos_token_id)
        ids = ids[:, inputs["input_ids"].shape[1]:]
        return processor.batch_decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

    return read


def pixtral(lang="Turkish", model="mistralai/Pixtral-12B-2409"):
    import base64
    from io import BytesIO

    from PIL import Image
    from vllm import LLM
    from vllm.sampling_params import SamplingParams

    llm = LLM(model=model, tokenizer_mode="mistral", max_model_len=8192, trust_remote_code=True)
    sampling = SamplingParams(max_tokens=8192)
    prompt = QWEN_PROMPT.format(language=lang)

    def read(path):
        buffer = BytesIO()
        Image.open(path).convert("RGB").save(buffer, format="PNG")
        url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("utf-8")
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt},
                                                 {"type": "image_url", "image_url": {"url": url}}]}]
        return llm.chat(messages, sampling_params=sampling, use_tqdm=False)[0].outputs[0].text.strip()

    return read


def got(lang=None, model="stepfun-ai/GOT-OCR2_0"):
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
    net = AutoModel.from_pretrained(model, trust_remote_code=True, low_cpu_mem_usage=True, use_safetensors=True,
                                    device_map="cuda" if torch.cuda.is_available() else "cpu",
                                    pad_token_id=tokenizer.eos_token_id).eval()
    return lambda path: net.chat(tokenizer, str(path), ocr_type="ocr")


MODELS = {"tesseract": tesseract, "easyocr": easyocr, "trocr": trocr, "paddle": paddle, "qwen": qwen,
          "internvl": internvl, "deepseek": deepseek, "phi": phi, "pixtral": pixtral, "got": got}
