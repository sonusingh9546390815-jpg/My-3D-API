from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import requests
import os

app = FastAPI(title="Advanced 3D Asset Pipeline", description="Powered by Meshy API")

# Render par 'MESHY_API_KEY' environment variable zaroori hai
MESHY_API_KEY = os.getenv("MESHY_API_KEY")
MESHY_API_URL = "https://api.meshy.ai/v1/image-to-3d"

# Ek chhota sa temporary database task track karne ke liye
asset_database = {}

@app.get("/")
def home():
    return {
        "message": "Pro 3D Asset Generator Live! 🎮", 
        "instruction": "Go to /docs to use the App Dashboard"
    }

@app.post("/api/upload-and-generate")
async def create_3d_task(
    asset_category: str = Form(..., description="Daalein: Gun, Character, Building, Tree, etc."),
    file: UploadFile = File(...)
):
    """
    Step 1: Photo upload karein aur Asset ka type batayein.
    """
    if not MESHY_API_KEY:
        raise HTTPException(status_code=400, detail="Meshy API Key missing!")

    try:
        image_bytes = await file.read()
        headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
        files = {"image_file": (file.filename, image_bytes, file.content_type)}
        data = {"ai_model": "v2", "topology": "quad", "target_polycount": 30000}

        # Meshy ko photo bhejna
        response = requests.post(MESHY_API_URL, headers=headers, files=files, data=data)
        
        if response.status_code not in [200, 202]:
            raise HTTPException(status_code=response.status_code, detail=f"Meshy Error: {response.text}")

        result = response.json()
        task_id = result.get("result")

        # Apne server ke database mein record save karna
        asset_database[task_id] = {
            "category": asset_category,
            "filename": file.filename
        }

        return {
            "status": "Task Started 🚀",
            "task_id": task_id,
            "asset_type": asset_category,
            "message": "AI ne model banana shuru kar diya hai! Niche 'check-status' wale endpoint mein yeh task_id daalkar progress check karein."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/check-status/{task_id}")
def check_model_status(task_id: str):
    """
    Step 2: task_id daalkar check karein ki model ready hua ya nahi.
    """
    if not MESHY_API_KEY:
        raise HTTPException(status_code=400, detail="Meshy API Key missing!")

    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
    response = requests.get(f"{MESHY_API_URL}/{task_id}", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Status check failed")

    data = response.json()
    status = data.get("status")
    
    if status == "SUCCEEDED":
        model_urls = data.get("model_urls", {})
        return {
            "task_id": task_id,
            "status": "READY! 🎉",
            "asset_details": asset_database.get(task_id, "Unknown"),
            "download_link_glb": model_urls.get("glb"),
            "message": "Mubarak ho! Aapka 3D file ready hai. Link copy karke browser mein paste karein aur model download karein."
        }
    elif status == "FAILED":
        return {
            "task_id": task_id, 
            "status": "FAILED ❌", 
            "error": data.get("task_error")
        }
    else:
        progress = data.get("progress", 0)
        return {
            "task_id": task_id,
            "status": f"PROCESSING ⏳ ({progress}%)",
            "message": "Meshy AI abhi model bana raha hai. Thodi der baad is endpoint ko dobara execute karein."
        }
