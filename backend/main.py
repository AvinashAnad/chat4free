from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os

app = FastAPI()

# Serve static frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def serve_homepage():
    with open("frontend/index.html", "r") as f:
        return f.read()

@app.post("/summarize/")
async def summarize(file: UploadFile = File(...)):
    # Save the uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Mock summary (replace with actual logic later)
    summary = f"This is a summary of {file.filename}."

    # Clean up
    os.remove(temp_path)

    return JSONResponse(content={"summary": summary})
