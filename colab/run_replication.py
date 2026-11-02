"""Run the authors' open models on the replication sample, one isolated environment per model.

The models need conflicting dependencies (GOT-OCR2 and DeepSeek torch 2.0, Pixtral torch 2.7 and vLLM), so each gets
its own uv environment, pinned to the state of the authors' runs (June-July 2025). A model that fails to install or
run is logged and skipped. Finished models are skipped on a re-run, and interrupted ones continue where they stopped.

Writes to --out:
    <name>.csv        predictions (file, prediction, seconds), same format as src/run_ocr.py
    logs/<name>.log   full output of the model's install and run
    envs/<name>.txt   exact package versions
    runs.json         per-model status and timings

Usage (Colab, see replication_colab.ipynb):
    python colab/run_replication.py --out /content/drive/MyDrive/ocr-benchmark/replication
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# name: run_ocr model, repo and revision (pinned: these models execute code from the repo), minimal GPU memory in GB,
# Python, (torch, torchvision, CUDA build), packages, and a date limit for everything not pinned here.
# Without a repo the model fetches its own weights; `libs` are package directories added to LD_LIBRARY_PATH.
SPECS = {
    "got": dict(loader="got", repo="stepfun-ai/GOT-OCR2_0", rev="979938bf89ccdc949c0131ddd3841e24578a4742",
                vram=6, python="3.11", torch=("2.0.1", "0.15.2", "cu118"),
                packages=["transformers==4.37.2", "tiktoken==0.6.0", "verovio==4.3.1", "accelerate==0.28.0",
                          "numpy==1.26.4"], date="2025-07-01"),
    "deepseek": dict(loader="deepseek", repo="deepseek-ai/deepseek-vl2-tiny",
                     rev="66c54660eae7e90c9ba259bfdf92d07d6e3ce8aa", vram=10, python="3.9",
                     torch=("2.0.1", "0.15.2", "cu118"),
                     packages=["deepseek_vl2 @ git+https://github.com/deepseek-ai/DeepSeek-VL2"
                               "@ef9f91e2b6426536b83294c11742c27be66361b1",
                               "xformers==0.0.21", "numpy==1.26.4"], date="2025-07-01"),
    "phi": dict(loader="phi", repo="microsoft/Phi-3.5-vision-instruct", rev="12b77fb40b63a2c73c68243d3f767aab688a1b2a",
                vram=12, python="3.11", torch=("2.6.0", "0.21.0", "cu124"),
                packages=["transformers==4.47.0", "accelerate", "pillow", "requests"], date="2025-07-01"),
    "qwen7b": dict(loader="qwen", repo="Qwen/Qwen2.5-VL-7B-Instruct", rev="cc594898137f460bfe9f0759e9844b3ce807cfb5",
                   vram=20, python="3.11", torch=("2.6.0", "0.21.0", "cu124"),
                   packages=["transformers==4.53.0", "accelerate", "qwen-vl-utils", "av==14.2.0", "pillow"], date="2025-06-28"),
    "internvl": dict(loader="internvl", repo="OpenGVLab/InternVL3-8B", rev="853e3a797a661694b1b8ece0cb72dc2b23e3dac9",
                     vram=20, python="3.11", torch=("2.6.0", "0.21.0", "cu124"),
                     packages=["transformers==4.52.4", "accelerate", "timm", "einops", "sentencepiece", "pillow"],
                     date="2025-07-01"),
    "pixtral": dict(loader="pixtral", repo="mistralai/Pixtral-12B-2409", rev="a5ca2b7a9421a35ea24411c46e970758b8d3c6a7",
                    vram=30, python="3.11", torch=("2.7.0", "0.22.0", "cu126"),
                    packages=["vllm==0.9.1", "mistral_common[image]", "pillow"], date="2025-07-06"),
    "trocr": dict(loader="trocr", repo="microsoft/trocr-large-printed", rev="9ff792d8e7c22061f2ee67e1ed2246b1f9ef1e98",
                  vram=4, python="3.11", torch=("2.6.0", "0.21.0", "cu124"), packages=["transformers", "pillow"],
                  date="2025-07-01"),
    # the PyPI wheel is built for CUDA 11.8 and cuDNN 8, and loads both from the system, so they come as packages
    "paddle": dict(loader="paddle", repo=None, rev=None, lang="en", vram=4, python="3.11", torch=None,
                   packages=["paddlepaddle-gpu==2.6.2", "paddleocr==2.9.1", "numpy==1.26.4", "setuptools<81",
                             "nvidia-cudnn-cu11==8.6.0.163", "nvidia-cublas-cu11==11.11.3.6"],
                   libs=["nvidia/cudnn/lib", "nvidia/cublas/lib"], date="2025-07-01"),
}


def run(cmd, log, **kwargs):
    """Run a command, echoing its output to the notebook and the model's log. Raises if it fails."""
    with subprocess.Popen([str(c) for c in cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          errors="replace", **kwargs) as p:
        for line in p.stdout:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
    if p.returncode:
        raise RuntimeError(f"{Path(str(cmd[0])).name} {cmd[1]} exited with code {p.returncode}")


def gpu_memory_gb():
    try:
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"])
        return float(out.split()[0]) / 1024
    except (OSError, subprocess.CalledProcessError, IndexError):
        return 0.0


def build_env(name, spec, work, torch_index, log):
    env = work / "envs" / name
    python = env / "bin" / "python"
    marker = env / ".complete"
    if marker.exists():
        return python
    run(["uv", "venv", "--clear", "--python", spec["python"], env], log)
    if spec["torch"]:
        torch_version, vision_version, cuda = spec["torch"]
        build = torch_index or cuda
        run(["uv", "pip", "install", "--python", python, f"torch=={torch_version}+{build}",
             f"torchvision=={vision_version}+{build}", "--index-url", f"https://download.pytorch.org/whl/{build}"], log)
    run(["uv", "pip", "install", "--python", python, "--exclude-newer", spec["date"], *spec["packages"],
         "editdistance", "jiwer"], log)
    marker.touch()
    return python


def csv_rows(path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def run_model(name, spec, args, n_images, log, record):
    from huggingface_hub import snapshot_download  # part of the Colab base image

    out = args.out / f"{name}.csv"
    t = time.time()
    python = build_env(name, spec, args.work, args.torch_index, log)
    record["install_s"] = round(time.time() - t)

    t = time.time()
    command = [python, ROOT / "src" / "run_ocr.py", "--model", spec["loader"], "--lang", spec.get("lang", "Turkish"),
               "--data", args.data, "--labels", args.labels, "--out", out]
    repo, rev = args.repo.get(name, (spec["repo"], spec["rev"]))
    if repo:
        weights = snapshot_download(repo, revision=rev, cache_dir=args.work / "hf",
                                    ignore_patterns=["*.bin", "*.pth", "*.h5", "*.msgpack", "*.onnx"])
        record["download_s"] = round(time.time() - t)
        record["checkpoint"] = f"{repo}@{rev}"
        command += ["--checkpoint", weights]
    environment = {**os.environ, "HF_HOME": str(args.work / "hf"), "HF_HUB_OFFLINE": "1"}
    if spec["torch"] and spec["torch"][0] != "2.0.1":  # torch 2.0 refuses to start with this option
        environment["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    if spec.get("libs"):
        packages = python.parent.parent / "lib" / f"python{spec['python']}" / "site-packages"
        # keep the existing value: on Colab it points to the NVIDIA driver (libcuda.so.1)
        paths = [str(packages / d) for d in spec["libs"]] + [os.environ.get("LD_LIBRARY_PATH", "")]
        environment["LD_LIBRARY_PATH"] = ":".join(filter(None, paths))

    # a few images first: a broken model should fail in a minute, not leave empty predictions for the whole sample
    t = time.time()
    run([*command, "--limit", args.smoke], log, env=environment)
    rows = csv_rows(out)
    if not any(r["prediction"].strip() for r in rows):
        out.unlink(missing_ok=True)
        raise RuntimeError(f"no text in the first {args.smoke} predictions")
    print(f"--- {name}, first predictions:", *[repr(r["prediction"][:70]) for r in rows[:3]], sep="\n    ", flush=True)
    if not args.smoke_only:
        run(command, log, env=environment)
    record["run_s"] = round(time.time() - t)

    rows = csv_rows(out)
    seconds = [float(r["seconds"]) for r in rows[1:]]  # the first image includes lazy initialisation
    record.update(images=len(rows), empty=sum(not r["prediction"].strip() for r in rows),
                  sec_per_image=round(sum(seconds) / max(1, len(seconds)), 2))
    freeze = subprocess.run(["uv", "pip", "freeze", "--python", str(python)], capture_output=True, text=True).stdout
    (args.out / "envs" / f"{name}.txt").write_text(freeze, encoding="utf-8")
    if not args.smoke_only and len(rows) < n_images:
        raise RuntimeError(f"only {len(rows)}/{n_images} images finished")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--models", nargs="*", default=list(SPECS), choices=list(SPECS))
    ap.add_argument("--data", type=Path, default=ROOT / "replication" / "data")
    ap.add_argument("--labels", default="sample.csv")
    ap.add_argument("--work", type=Path, default=Path("/content/work"), help="environments and model weights")
    ap.add_argument("--smoke", type=int, default=3, help="images in the initial check of each model")
    ap.add_argument("--smoke-only", action="store_true", help="stop after the initial check")
    ap.add_argument("--keep-files", action="store_true", help="keep a model's weights and environment after its run")
    ap.add_argument("--torch-index", help="override the torch build, e.g. cpu for a test without a GPU")
    ap.add_argument("--no-vram-check", action="store_true")
    ap.add_argument("--repo", nargs="*", default=[], metavar="NAME=REPO@REV", help="use another checkpoint (tests)")
    args = ap.parse_args()
    args.repo = {k: tuple(v.split("@")) for k, v in (item.split("=") for item in args.repo)}
    args.out = args.out.resolve()
    args.data = args.data.resolve()
    (args.out / "logs").mkdir(parents=True, exist_ok=True)
    (args.out / "envs").mkdir(exist_ok=True)

    with open(args.data / args.labels, encoding="utf-8") as f:
        n_images = sum(1 for _ in csv.DictReader(f))
    memory = gpu_memory_gb()
    print(f"GPU memory: {memory:.0f} GB, {n_images} images, models: {' '.join(args.models)}", flush=True)
    summary_path = args.out / "runs.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    for name in args.models:
        spec = SPECS[name]
        print(f"\n===== {name} =====", flush=True)
        if len(csv_rows(args.out / f"{name}.csv")) >= n_images:
            print("already finished", flush=True)
            continue
        if memory < spec["vram"] and not args.no_vram_check:
            print(f"skipped: needs {spec['vram']} GB of GPU memory", flush=True)
            summary[name] = dict(status="skipped", reason=f"needs {spec['vram']} GB, have {memory:.0f} GB")
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
            continue
        record = dict(status="ok", gpu_memory_gb=round(memory))
        t = time.time()
        with open(args.out / "logs" / f"{name}.log", "a", encoding="utf-8") as log:
            try:
                run_model(name, spec, args, n_images, log, record)
            except Exception as e:  # one model must not cost the others their turn on the GPU
                record.update(status="failed", reason=str(e))
                print(f"FAILED {name}: {e}", file=sys.stderr, flush=True)
        record["total_s"] = round(time.time() - t)
        summary[name] = record
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        if not args.keep_files:  # 74 GB of weights for all six, about 7 GB per environment
            shutil.rmtree(args.work / "hf", ignore_errors=True)
            if record["status"] == "ok":
                shutil.rmtree(args.work / "envs" / name, ignore_errors=True)

    print("\n===== summary =====")
    for name in args.models:
        print(f"{name:9s} {json.dumps(summary.get(name, dict(status='finished earlier')))}")


if __name__ == "__main__":
    main()
