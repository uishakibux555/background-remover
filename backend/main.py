from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import sys

# Add parent dir to path so we can import our scripts
sys.path.append("..") 

# Import our tools
# Note: We need to make sure these scripts are refactored to be importable
# (I refactored background_remover.py, others might need it too or we handle it here)
import background_remover
import sam2_remover
import birefnet_remover
import rmbg2_remover
# import upscaler # disabled for now

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
PROCESSED_DIR = os.path.join(os.getcwd(), "processed")

print(f"DEBUG: Upload Dir: {UPLOAD_DIR}")
print(f"DEBUG: Processed Dir: {PROCESSED_DIR}")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Mount processed dir to serve images
app.mount("/processed", StaticFiles(directory=PROCESSED_DIR), name="processed")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    model_id: str = Form(...)
):
    try:
        # Save uploaded file
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_filename = f"processed_{file.filename}"
        if not output_filename.endswith(".png"):
             output_filename = os.path.splitext(output_filename)[0] + ".png"
             
        output_location = f"{PROCESSED_DIR}/{output_filename}"
        
        abs_input = os.path.abspath(file_location)
        abs_output = os.path.abspath(output_location)

        # Route to correct model
        if model_id == "u2net":
             background_remover.process_image(abs_input, abs_output, model_name="u2net", alpha_matting=True)
        
        elif model_id == "sam2":
             # We need to load model first? 
             # For API efficiency, ideally we load models globally.
             # But for now let's use the script's functions which might load internally.
             # We should probably refactor scripts to allow passing a loaded model, 
             # OR just accept the hit of reloading (or let the script handle global lazy loading)
             
             # sam2_remover.get_sam_model() caches? 
             # Let's check sam2_remover.py... it uses get_sam_model() inside main.
             # We should probably reuse the loading logic.
             # For MVP, let's just make sure the script functions are accessible.
             # I need to refactor other scripts to expose a 'process' function that takes string paths.
             
             # Assuming I will refactor them in next steps, here is the call:
             model = sam2_remover.get_sam_model() # This should be cached globally ideally
             sam2_remover.process_sam2(model, abs_input, abs_output)

        elif model_id == "birefnet":
             model_data = birefnet_remover.get_birefnet_model()
             birefnet_remover.process_birefnet(model_data, abs_input, abs_output)

        elif model_id == "rmbg2":
             model_data = rmbg2_remover.get_rmbg2_model()
             rmbg2_remover.process_rmbg2(model_data, abs_input, abs_output)
             
        # elif model_id == "upscaler":
        #      pipeline = upscaler.get_upscaler_pipe()
        #      upscaler.upscale_image(pipeline, abs_input, abs_output)

        else:
             raise HTTPException(status_code=400, detail="Invalid model_id")

        if not os.path.exists(abs_output) or os.path.getsize(abs_output) == 0:
            raise HTTPException(status_code=500, detail="Processing failed: Output file not created.")

        # Encode filename for URL
        from urllib.parse import quote
        safe_filename = quote(output_filename)

        return {
            "status": "success",
            "original_url": f"/uploads/{file.filename}", 
            "processed_url": f"http://localhost:8000/processed/{safe_filename}"
        }

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
