from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import requests

app = FastAPI(title="Pro 3D Asset Generator", description="Powered by Tripo3D AI")

# Task aur API key track karne ke liye database
asset_database = {}

@app.get("/")
def home():
    return {"message": "Tripo 3D API is Live! 🚀", "instruction": "Go to /docs to use the App Dashboard"}

@app.post("/api/upload-and-generate")
async def create_3d_task(
    api_key: str = Form(..., description="Tripo3D se copy ki hui API Key yahan paste karein"),
    asset_category: str = Form("Character", description="Jaise: Gun, Character, etc."),
    file: UploadFile = File(...)
):
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key is required!")

    try:
        # Tripo3D ke liye VIP Pass (Headers)
        headers = {
            "Authorization": f"Bearer {api_key}"
        }

        # Step 1: Photo ko Tripo ke server par upload karna
        upload_url = "https://api.tripo3d.ai/v2/openapi/upload"
        file_bytes = await file.read()
        files = {"file": (file.filename, file_bytes, file.content_type)}
        
        upload_res = requests.post(upload_url, headers=headers, files=files)
        if upload_res.status_code != 200:
            raise HTTPException(status_code=upload_res.status_code, detail=f"Upload Error: {upload_res.text}")
        
        image_token = upload_res.json()["data"]["image_token"]

        # Step 2: Tripo ko 3D model banane ka order dena (Task Create)
        task_url = "https://api.tripo3d.ai/v2/openapi/task"
        payload = {
            "type": "image_to_model",
            "file": {
                "type": "jpg",
                "file_token": image_token
            }
        }
        
        task_res = requests.post(task_url, headers=headers, json=payload)
        if task_res.status_code != 200:
            raise HTTPException(status_code=task_res.status_code, detail=f"Task Error: {task_res.text}")

        task_id = task_res.json()["data"]["task_id"]

        # task_id aur key save karna taaki baad mein status check kar sakein
        asset_database[task_id] = {
            "category": asset_category,
            "filename": file.filename,
            "api_key": api_key
        }

        return {
            "status": "Task Started 🚀",
            "task_id": task_id,
            "asset_type": asset_category,
            "message": "Tripo AI ne model banana shuru kar diya hai! Niche 'check-status' wale endpoint mein yeh task_id daalkar progress check karein."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/check-status/{task_id}")
def check_model_status(task_id: str):
    task_info = asset_database.get(task_id)
    if not task_info:
        raise HTTPException(status_code=404, detail="Task ID server par nahi mili. Kripya naya task shuru karein.")

    api_key = task_info.get("api_key")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Tripo se task ka status poochna
    task_url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    response = requests.get(task_url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Status check failed")

    data = response.json().get("data", {})
    status = data.get("status")
    
    if status == "success":
        model_url = data.get("result", {}).get("model", {}).get("url")
        return {
            "task_id": task_id,
            "status": "READY! 🎉",
            "download_link_glb": model_url,
            "message": "Mubarak ho! Aapka 3D file ready hai. Link copy karke browser mein paste karein aur model download karein."
        }
    elif status in ["failed", "cancelled"]:
        return {"task_id": task_id, "status": "FAILED ❌", "error": "Model nahi ban paya."}
    else:
        progress = data.get("progress", 0)
        return {"task_id": task_id, "status": f"PROCESSING ⏳ ({progress}%)"}
