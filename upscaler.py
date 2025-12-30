import argparse
import sys
import os
from PIL import Image

def install_dependencies():
    print("\n⚠️ Missing required libraries for Upscaler.")
    print("Attempting to install: diffusers, transformers, accelerate, torch")
    import subprocess
    
    # helper to run pip
    def pip_install(args, description):
        print(f"📦 Attempting to install: {description}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + args)
            return True
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {description}.")
            return False

    # 1. Try Stable CUDA (Works for Py 3.10-3.12 usually)
    # Using cu124 as it is newer, might support 3.13 sooner
    if pip_install(["torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu124"], "PyTorch (Stable CUDA 12.4)"):
        pass
    
    # 2. Try Nightly CUDA (Recommended for Python 3.13+)
    elif pip_install(["--pre", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/nightly/cu124"], "PyTorch (Nightly CUDA 12.4 - for Py3.13)"):
        pass
        
    # 3. NO CPU Fallback requested.
    # elif pip_install(["torch", "torchvision", "torchaudio"], "PyTorch (Standard/CPU Fallback)"):
    #     print("⚠️ Warning: Installed Standard/CPU version. Upscaling will be slow.")
    
    else:
        print("\n❌ Failed to install a GPU-supported version of PyTorch.")
        print("Please check your internet connection or try installing PyTorch manually.")
        sys.exit(1)

    # Install the rest
    if pip_install(["diffusers", "transformers", "accelerate", "scipy"], "Diffusers & Libraries"):
        print("\n✅ Installation complete! Please restart the tool.")
        sys.exit(0)
    else:
        sys.exit(1)

def get_upscaler_pipe():
    print("⏳ Loading Stable Diffusion Upscaler (this may download the model ~10GB first time)...")
    try:
        import torch
        from diffusers import StableDiffusionUpscalePipeline
        
        model_id = "stabilityai/stable-diffusion-x4-upscaler"
        
        if not torch.cuda.is_available():
             print("❌ ERROR: GPU (CUDA) not detected. This tool is configured to run ONLY on GPU.")
             sys.exit(1)

        print("🚀 Running on GPU (CUDA) - Enabling Low VRAM Mode")
        
        # Optimize memory allocation to reduce fragmentation
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        
        device = "cuda"
        dtype = torch.float16

        pipeline = StableDiffusionUpscalePipeline.from_pretrained(
            model_id, torch_dtype=dtype
        )
        
        # ---------------------------------------------------------
        # LOW VRAM OPTIMIZATIONS
        # ---------------------------------------------------------
        # 1. Attention Slicing: Processes attention in chunks.
        pipeline.enable_attention_slicing()
        
        # 2. Sequential CPU Offload:
        # Crucial for 4GB VRAM cards. Moves entire models to CPU when not processing.
        # This makes inference slower but possible on small GPUs.
        pipeline.enable_sequential_cpu_offload()
        
        # 3. VAE Tiling:
        # Reduces memory usage during the final image decoding step (often the heaviest part).
        try:
             pipeline.vae.enable_tiling()
        except AttributeError:
             print("⚠️ VAE Tiling not available, skipping.")
        
        return pipeline
    except ImportError:
        install_dependencies()
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        sys.exit(1)

def upscale_tiled(pipeline, image, tile_size=512, overlap=32):
    """
    Splits image into tiles, upscales them, and stitches them back.
    Simple stitching (cropling overlap) to fit in memory.
    """
    import torch
    w, h = image.size
    
    # Grid calculation
    # We step by (tile_size - overlap) to ensure coverage
    step = tile_size - overlap
    
    new_w = w * 4
    new_h = h * 4
    
    final_img = Image.new("RGB", (new_w, new_h))
    
    print(f"   -> Tiling enabled: Input {w}x{h} -> Output {new_w}x{new_h}")
    print(f"   -> Tile size: {tile_size}x{tile_size}")
    
    # Loop through tiles
    for y in range(0, h, step):
        for x in range(0, w, step):
            # Define box
            box = (x, y, min(x + tile_size, w), min(y + tile_size, h))
            tile = image.crop(box)
            
            # Pad tile if it's smaller than tile_size (at edges)
            # SD Upscaler usually likes 128x128 or 256x256 minimums. 
            # We keep it simple: processed tile will be 4x the input size.
            
            # Run inference on tile
            # Using a simplified prompt for tiles to avoid context confusion
            prompt = "high resolution, high quality, sharp details"
            
            # Clear cache before each tile
            torch.cuda.empty_cache()
            
            upscaled_tile = pipeline(prompt=prompt, image=tile, num_inference_steps=20).images[0]
            
            # Calculate where to paste
            paste_x = x * 4
            paste_y = y * 4
            
            # If we are not at the first column/row, we might need to account for overlap?
            # Actually with a simple crop/stitch, we just paste.
            # Ideally: we crop the center of the upscaled tile to avoid edge artifacts.
            # MVP: Just paste.
            
            final_img.paste(upscaled_tile, (paste_x, paste_y))
            print(f"      Processed tile at ({x}, {y})", end="\r")

    print("") # Newline
    return final_img

def upscale_image(pipeline, input_path, output_path, scale_factor=4):
    try:
        print(f"Processing: {input_path}...")
        image = Image.open(input_path).convert("RGB")
        w, h = image.size
        print(f"   Input Resolution: {w}x{h}")
        
        # Decide process based on size
        # 4GB VRAM safety limit: ~512x512 input (which becomes 2048x2048 output)
        if w > 512 or h > 512:
            print("⚠️ Image is large for 4GB VRAM. Using Tiled Mode...")
            upscaled_image = upscale_tiled(pipeline, image)
        else:
            # The pipeline always upscales 4x
            prompt = "high resolution, high quality, clear image, sharp details"
            upscaled_image = pipeline(prompt=prompt, image=image).images[0]
        
        # If user wanted 1x (just enhancement) or 2x, we resize the 4x result down
        # This keeps the "generated details" but at a lower resolution
        if scale_factor == 1:
            target_size = image.size
            print(f"Target 1x: Resizing back to {target_size}")
            upscaled_image = upscaled_image.resize(target_size, Image.Resampling.LANCZOS)
        elif scale_factor == 2:
            target_size = (image.size[0] * 2, image.size[1] * 2)
            print(f"Target 2x: Resizing to {target_size}")
            upscaled_image = upscaled_image.resize(target_size, Image.Resampling.LANCZOS)
        
        upscaled_image.save(output_path)
        print(f"✅ Saved to: {output_path}")

    except Exception as e:
        print(f"❌ Failed to process {input_path}: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Upscale images using Stable Diffusion.")
    parser.add_argument("-i", "--input", required=True, nargs='+', help="Path to input image(s)")
    parser.add_argument("-o", "--output", help="Optional output directory")
    parser.add_argument("-s", "--scale", type=int, choices=[1, 2, 4], default=4, help="Scale factor (1, 2, or 4)")

    args = parser.parse_args()
    
    # Reconstruct paths logic
    def reconstruct_paths(raw_args):
        cleaned_paths = []
        current_path = []
        for arg in raw_args:
             current_path.append(arg)
             candidate = " ".join(current_path)
             candidate_clean = candidate.strip('"').strip("'")
             if os.path.exists(candidate_clean):
                 cleaned_paths.append(candidate_clean)
                 current_path = []
        if current_path:
            cleaned_paths.append(" ".join(current_path).strip('"').strip("'"))
        return cleaned_paths

    input_list = reconstruct_paths(args.input)
    
    # Load pipeline once
    pipeline = get_upscaler_pipe()
    
    output_target = args.output
    
    for input_path in input_list:
        if not input_path: continue
        
        # Verify extension
        valid_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        ext = os.path.splitext(input_path)[1].lower()
        if ext not in valid_exts:
            print(f"⚠️ Skipping non-image file: {input_path}")
            continue
            
        if not output_target:
            base, ext = os.path.splitext(input_path)
            if not ext: ext = ".png"
            output_path = f"{base}_upscaled_{args.scale}x.png"
        elif os.path.isdir(output_target):
            filename = os.path.basename(input_path)
            base, ext = os.path.splitext(filename)
            output_path = os.path.join(output_target, f"{base}_upscaled_{args.scale}x.png")
        else:
            output_path = output_target

        upscale_image(pipeline, input_path, output_path, args.scale)

if __name__ == "__main__":
    main()
