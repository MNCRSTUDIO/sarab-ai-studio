import os, subprocess, sys

def run(cmd, timeout=None):
    print("\n>>>", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True, timeout=timeout)

print("========== SARAB GPU CHECK ==========", flush=True)
run([sys.executable, "-c", "import torch; print('Torch:',torch.__version__); print('CUDA:',torch.cuda.is_available()); print('GPU:',torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')"])

run([sys.executable, "-m", "pip", "install", "-q", "uv"])
run(["uv", "python", "install", "3.11"])

run(["git", "clone", "https://github.com/deepbeepmeep/Wan2GP.git", "/kaggle/working/Wan2GP"])

run(["uv", "venv", "--python", "3.11", "/kaggle/working/wanenv"])
py = "/kaggle/working/wanenv/bin/python"

run(["uv", "pip", "install", "--python", py, "torch==2.10.0", "torchvision", "--index-url", "https://download.pytorch.org/whl/cu130"])
run(["uv", "pip", "install", "--python", py, "-r", "/kaggle/working/Wan2GP/requirements.txt", "--no-deps"])

run(["uv", "pip", "install", "--python", py, "packaging"])

run(["uv", "pip", "install", "--python", py, "requests", "huggingface-hub", "filelock", "regex", "importlib_metadata", "tqdm", "safetensors"])

run(["uv", "pip", "install", "--python", py, "gradio_client"])

print("========== IMPORT TEST ==========", flush=True)
run(["uv", "pip", "install", "--python", py, "gradio"])
run([py, "-c", "import torch; print('Torch:',torch.__version__); print('CUDA:',torch.cuda.is_available()); import diffusers,gradio; print('Diffusers:',diffusers.__version__); print('Gradio:',gradio.__version__)"])

run([py, "-c", "import os; p=\x27/kaggle/working/Wan2GP\x27; print(\x27Wan2GP folder:\x27, os.path.isdir(p)); print(\x27Launcher:\x27, os.path.isfile(p+\x27/wgp.py\x27)); print(\x27Files:\x27, os.listdir(p)[:30] if os.path.isdir(p) else \x27NOT FOUND\x27)"])
run(["uv", "pip", "install", "--python", py, "setuptools"])
run([py, "/kaggle/working/Wan2GP/wgp.py", "--help"], timeout=120)
print("========== SARAB SETUP COMPLETE ==========", flush=True)
