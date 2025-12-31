import argparse
import sys
import os
import time

# Import local modules
# We wrap imports in try-except block in case dependencies are not installed, 
# though we will check them before running.
try:
    import background_remover
    import birefnet_remover
    import rmbg2_remover
    import sam2_remover
except ImportError:
    pass # Will be handled if execution fails or we can check explicitly

def validate_input_paths(input_paths):
    """
    Validates input paths and expands them if they were split by shell arguments.
    """
    cleaned_paths = []
    current_path = []
    
    for arg in input_paths:
        current_path.append(arg)
        candidate = " ".join(current_path)
        candidate_clean = candidate.strip('"').strip("'")
        
        if os.path.exists(candidate_clean):
            cleaned_paths.append(candidate_clean)
            current_path = []
            
    if current_path:
        # Fallback for last item
        cleaned_paths.append(" ".join(current_path).strip('"').strip("'"))
        
    return cleaned_paths

def process_removal(args):
    """
    Handles the background removal logic dispatch.
    """
    input_list = validate_input_paths(args.input)
    if not input_list:
        print("❌ Error: No valid input files found.")
        return

    output_dir = args.output
    # If multiple inputs and output is a file path (not dir), warn user
    if len(input_list) > 1 and output_dir and not os.path.isdir(output_dir) and not output_dir.endswith(os.sep):
         # It's ambiguous if the user meant a file or a dir that doesn't exist.
         # For safety, if multiple inputs, we treat output as a directory.
         pass

    print(f"🚀 Starting Background Removal using model: {args.model}")
    print(f"   Inputs: {len(input_list)} files")

    # Load Model (Lazy Loading)
    model_data = None
    
    if args.model == "birefnet":
        try:
            model_data = birefnet_remover.get_birefnet_model()
        except Exception as e:
            print(f"❌ Failed to load BiRefNet: {e}")
            sys.exit(1)
            
    elif args.model == "rmbg2":
        try:
            model_data = rmbg2_remover.get_rmbg2_model()
        except Exception as e:
            print(f"❌ Failed to load RMBG-2.0: {e}")
            sys.exit(1)
            
    elif args.model == "sam2":
        try:
            model_data = sam2_remover.get_sam_model()
        except Exception as e:
            print(f"❌ Failed to load SAM 2: {e}")
            sys.exit(1)

    # Process Loop
    start_time = time.time()
    success_count = 0
    
    for str_path in input_list:
        if not os.path.exists(str_path):
             print(f"⚠️ File not found: {str_path}")
             continue
             
        # Determine Output Path
        filename = os.path.basename(str_path)
        base, ext = os.path.splitext(filename)
        
        if output_dir:
            # If output_dir doesn't exist, create it?
            # Or if it looks like a file (has extension), use it (only if single input)
            if len(input_list) == 1 and os.path.splitext(output_dir)[1]:
                final_output_path = output_dir
                # Ensure parent dir exists
                os.makedirs(os.path.dirname(os.path.abspath(final_output_path)), exist_ok=True)
            else:
                os.makedirs(output_dir, exist_ok=True)
                final_output_path = os.path.join(output_dir, f"{base}_no_bg.png")
        else:
            final_output_path = f"{base}_no_bg.png"

        # Dispatch
        try:
            if args.model == "u2net" or args.model == "isnet":
                # Using general background_remover (rembg)
                # It handles its own session loading usually, or we can look at its code.
                # background_remover.process_image loads 'u2net' by default or passed arg.
                background_remover.process_image(str_path, final_output_path, model_name=args.model)
                
            elif args.model == "birefnet":
                birefnet_remover.process_birefnet(model_data, str_path, final_output_path)
                
            elif args.model == "rmbg2":
                rmbg2_remover.process_rmbg2(model_data, str_path, final_output_path)
                
            elif args.model == "sam2":
                sam2_remover.process_sam2(model_data, str_path, final_output_path)
            
            success_count += 1
            
        except Exception as e:
             print(f"❌ Failed to process {filename}: {e}")

    total_time = time.time() - start_time
    print(f"\n✨ Completed {success_count}/{len(input_list)} images in {total_time:.2f}s")


def main():
    parser = argparse.ArgumentParser(
        description="Professional Background Removal Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Remove Command
    remove_parser = subparsers.add_parser("remove", help="Remove background from images")
    remove_parser.add_argument("-i", "--input", required=True, nargs='+', help="Input image path(s)")
    remove_parser.add_argument("-o", "--output", help="Output path or directory")
    remove_parser.add_argument(
        "-m", "--model", 
        default="u2net", 
        choices=["u2net", "isnet", "birefnet", "rmbg2", "sam2"], 
        help=(
            "Select AI Model:\n"
            "  u2net    : Balanced (Default, uses rembg)\n"
            "  isnet    : High accuracy for general use (uses rembg)\n"
            "  birefnet : State-of-the-art segmentation\n"
            "  rmbg2    : RMBG v2.0 (High accuracy)\n"
            "  sam2     : Segment Anything Model 2 (Subject detection)"
        )
    )

    args = parser.parse_args()

    if args.command == "remove":
        process_removal(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
