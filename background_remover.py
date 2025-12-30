import argparse
import sys
import os
import time

# Lazy load heavy imports
def get_rembg_tools():
    print("⏳ this might take a moment...")
    try:
        from rembg import remove, new_session
        return remove, new_session
    except ImportError as e:
        print(f"❌ Error loading libraries: {e}")
        sys.exit(1)

def process_image(input_path, output_path, model_name="isnet-general-use"):
    """
    Removes the background from an image using a specific model.
    """
def process_image(img_path, output_path, model_name="u2net", alpha_matting=False):
    # Lazy load rembg
    try:
        from rembg import remove, new_session
    except ImportError:
        # If called from API, we expect deps to be there, or we catch this.
        # But for CLI we might want to install. 
        # For now, let's assume if imported, we want to just raise or return False
        if __name__ == "__main__":
             # install_dependencies() # This function is not defined, so we'll just raise
             raise ImportError("rembg not installed. Please install it using 'pip install rembg[gpu]' or 'pip install rembg'")
        else:
             raise ImportError("rembg not installed")

    # ... check deps ...

    try:
        print(f"Processing: {img_path}...")
        print(f"Using Model: {model_name}")
        
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"The file '{img_path}' was not found.")

        # Read image
        print("📖 Reading image...")
        with open(img_path, 'rb') as i:
            input_data = i.read()

        # ... (rest of processing)
        
        # Setup Session
        # We can cache sessions in the backend later, for now new session every time is safer for script reuse
        # but slower. backend optimization: global cache.
        print("🪄 Removing background...")
        providers = ['CUDAExecutionProvider', 'DirectMLExecutionProvider', 'CPUExecutionProvider']
        session = new_session(model_name, providers=providers)

        if alpha_matting:
             output_data = remove(input_data, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=10, alpha_matting_erode_size=10)
        else:
             output_data = remove(input_data, session=session)

        print("💾 Saving result...")
        with open(output_path, 'wb') as o:
            o.write(output_data)
            
        print(f"✅ Saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error: {e}")
        # Re-raise if called from API so we can handle it
        if __name__ != "__main__":
            raise e
        return None


def main():
    parser = argparse.ArgumentParser(description="Remove background from images using CPU or GPU.")
    parser.add_argument("-i", "--input", required=True, nargs='+', help="Path to input image(s)")
    parser.add_argument("-o", "--output", help="Path to output directory or file (optional). If multiple inputs, this should be a directory.")
    parser.add_argument("-m", "--model", default="u2net", help="Model to use (default: u2net). Options: u2net, isnet-general-use, u2net_human_seg")

    args = parser.parse_args()

    # Reconstruct paths that might have been split by spaces (if quotes were missing)
    def reconstruct_paths(raw_args):
        cleaned_paths = []
        current_path = []
        
        for arg in raw_args:
             # If arg is a flag or looks like one, we shouldn't be here (argparse handles it), 
             # but just in case, or if it's the start of a new file.
             
             # Heuristic:
             # 1. Add part to current_path.
             # 2. Check if current_path exists. 
             # 3. If exists, save it and reset current_path.
             # 4. If not, keep accumulating (unless we run out, then assume the user gave a bad path or a list of bad paths, 
             #    in which case we probably output the accumulated chunks as best effort).
             
             # Better Heuristic for "Nargs+" where some are split:
             # We want to greedily match the longest existing prefix? No, usually valid paths don't overlap.
             # We accumulate until we find a match?
             
             current_path.append(arg)
             candidate = " ".join(current_path)
             
             # Check if this candidate is a file or directory
             # Also check if we strip quotes (though arg usually has them stripped by shell)
             candidate_clean = candidate.strip('"').strip("'")
             
             if os.path.exists(candidate_clean):
                 cleaned_paths.append(candidate_clean)
                 current_path = []
        
        # If leftovers (e.g. file doesn't exist), we might have skipped it or it's a typo.
        # But we should probably add it to the list to let the main loop report "File not found" correctly
        # instead of failing silently.
        if current_path:
            cleaned_paths.append(" ".join(current_path).strip('"').strip("'"))
            
        return cleaned_paths

    # Process inputs
    input_list = reconstruct_paths(args.input)

    # Determine if output is a directory or file (or None)
    output_target = args.output
    
    # Check if multiple inputs
    multiple_inputs = len(input_list) > 1

    if multiple_inputs and output_target and not os.path.isdir(output_target):
        # If multiple inputs and output is specified but not a dir, we can't map 1:1 easily unless we auto-generate names in that "file" which is invalid.
        # So we assume if multiple inputs, output must be a dir or None.
        print("⚠️ Warning: Multiple inputs detected, but output is not a directory. Output will be saved in source directories.")
        output_target = None 

    for input_path in input_list:
        if not input_path: continue
        
        # Verify extension
        valid_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        ext = os.path.splitext(input_path)[1].lower()
        if ext not in valid_exts:
            print(f"⚠️ Skipping non-image file: {input_path}")
            continue

        if not output_target:
             # Generate output path in the same location
            base, ext = os.path.splitext(input_path)
            if not ext: ext = ".png"
            output_path = f"{base}_no_bg.png"
        elif os.path.isdir(output_target):
            # Output is a directory
            filename = os.path.basename(input_path)
            base, ext = os.path.splitext(filename)
            output_path = os.path.join(output_target, f"{base}_no_bg.png")
        else:
             # Single input, single output file
             output_path = output_target

        process_image(input_path, output_path, args.model)

if __name__ == "__main__":
    main()
