import argparse
import sys
import os
import numpy as np
from PIL import Image

def install_dependencies():
    print("\n⚠️ Missing required libraries for BiRefNet.")
    print("Attempting to install: transformers, timm, accelerate, torch, pillow, einops, kornia")
    import subprocess
    
    def pip_install(args):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + args)
            return True
        except subprocess.CalledProcessError:
            return False

    # Install essentials
    if pip_install(["transformers", "timm", "accelerate", "pillow", "einops", "kornia"]):
         # Torch check is covered by other scripts usually, but good to ensure
         pass
         
    print("\n✅ Installation complete! Please restart the tool.")
    sys.exit(0)

def get_birefnet_model():
    print("⏳ Loading BiRefNet Model (this may download weights first time)...")
    try:
        import torch
        from transformers import AutoModelForImageSegmentation
        from torchvision import transforms

        torch.set_float32_matmul_precision(['high', 'medium'][0])
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load Code from Hugging Face (trust_remote_code required for BiRefNet)
        model = AutoModelForImageSegmentation.from_pretrained(
            "ZhengPeng7/BiRefNet", 
            trust_remote_code=True
        )
        model.to(device)
        model.eval()
        return model, device, transforms
    except ImportError:
        if __name__ == "__main__":
             install_dependencies()
        else:
             raise ImportError("dependencies missing")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        if __name__ == "__main__":
            sys.exit(1)
        raise e

def process_birefnet(model_data, input_path, output_path):
    model, device, transforms = model_data
    import torch
    
    try:
        print(f"Processing (BiRefNet): {input_path}...")
        
        image = Image.open(input_path).convert("RGB")
        w, h = image.size
        
        # BiRefNet works best at specific resolutions (1024x1024)
        # We transform input
        transform_image = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform_image(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            # Inference
            preds = model(input_tensor)[-1].sigmoid().cpu()
        
        # Resize mask back to original size
        pred = preds[0].squeeze()
        
        # Convert to PIL Image
        from torchvision.transforms.functional import to_pil_image
        mask_pil = to_pil_image(pred)
        mask_pil = mask_pil.resize((w, h), Image.Resampling.LANCZOS)
        
        # Composite
        final_img = image.copy()
        final_img.putalpha(mask_pil)
        
        final_img.save(output_path)
        print(f"✅ Saved to: {output_path}")

    except Exception as e:
        print(f"❌ Failed to process {input_path}: {e}")
        import traceback
        traceback.print_exc()
        raise e

def main():
    parser = argparse.ArgumentParser(description="Remove background using BiRefNet.")
    parser.add_argument("-i", "--input", required=True, nargs='+', help="Path to input image(s)")
    parser.add_argument("-o", "--output", help="Optional output directory")

    args = parser.parse_args()
    
    # Reconstruct paths logic (Shared across our scripts)
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

    # Load model once
    model_data = get_birefnet_model()
    
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
            output_path = f"{base}_birefnet_rem.png"
        elif os.path.isdir(output_target):
            filename = os.path.basename(input_path)
            base, ext = os.path.splitext(filename)
            output_path = os.path.join(output_target, f"{base}_birefnet_rem.png")
        else:
            output_path = output_target

        process_birefnet(model_data, input_path, output_path)

if __name__ == "__main__":
    main()
