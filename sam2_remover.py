import argparse
import sys
import os
import numpy as np
from PIL import Image

def install_dependencies():
    print("\n⚠️ Missing required libraries for SAM 2.")
    print("Attempting to install: ultralytics")
    import subprocess
    try:
        # Install Ultralytics (includes torch etc)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
        
        print("\n✅ Installation complete! Please restart the tool.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

def get_sam_model():
    print("⏳ Loading SAM 2.1 Model (this may download weights first time)...")
    try:
        from ultralytics import SAM
        # Using SAM 2.1 Base model (balance of speed/accuracy)
        model = SAM("sam2.1_b.pt")
        return model
    except ImportError:
        # If called from API, checkingdeps should be handled or we assume installed
        if __name__ == "__main__":
             install_dependencies()
        else:
             raise ImportError("ultralytics not installed")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        if __name__ == "__main__":
            sys.exit(1)
        raise e

def process_sam2(model, input_path, output_path):
    try:
        print(f"Processing (SAM 2): {input_path}...")
        
        # Open image to get dimensions
        img = Image.open(input_path).convert("RGB")
        w, h = img.size
        
        # Heuristic: The subject is usually in the center.
        # We provide a single point prompt at the precise center of the image.
        # SAM 2 is very good at propagating from a single point.
        center_point = [w/2, h/2]
        
        # Run inference
        # bboxes=None, points=[center_point], labels=[1] (1 = foreground)
        results = model(input_path, points=[center_point], labels=[1], retina_masks=True, verbose=False)
        
        if not results or not results[0].masks:
            print(f"⚠️ No mask detected for {input_path}")
            return

        # Get the mask (take the first one, usually the best for single object)
        # Masks are returned as (N, H, W) tensors. We take the first mask [0].
        # It comes out as a float tensor, need to convert to binary.
        mask_data = results[0].masks.data[0].cpu().numpy()
        
        # Resize mask to match original image if needed (retina_masks=True should handle this mostly, but safety check)
        mask_img = Image.fromarray((mask_data * 255).astype(np.uint8))
        if mask_img.size != img.size:
            mask_img = mask_img.resize(img.size, Image.Resampling.LANCZOS)
            
        # Compose final image
        # Create an empty RGBA image
        final_img = img.copy()
        final_img.putalpha(mask_img)
        
        final_img.save(output_path)
        print(f"✅ Saved to: {output_path}")

    except Exception as e:
        print(f"❌ Failed to process {input_path}: {e}")
        raise e

def main():
    parser = argparse.ArgumentParser(description="Remove background using SAM 2.")
    parser.add_argument("-i", "--input", required=True, nargs='+', help="Path to input image(s)")
    parser.add_argument("-o", "--output", help="Optional output directory")

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

    # Load model once
    model = get_sam_model()
    
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
            output_path = f"{base}_sam2_rem.png"
        elif os.path.isdir(output_target):
            filename = os.path.basename(input_path)
            base, ext = os.path.splitext(filename)
            output_path = os.path.join(output_target, f"{base}_sam2_rem.png")
        else:
            output_path = output_target

        process_sam2(model, input_path, output_path)

if __name__ == "__main__":
    main()
