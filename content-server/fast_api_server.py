from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi import Request

app = FastAPI()
# Jinja2 template
templates = Jinja2Templates(directory="templates")
app.mount("/images", StaticFiles(directory="images"), name="images")

# Home route
@app.get("/")
async def index(request: Request):
    images = list(Path("images").glob("*"))
    return templates.TemplateResponse("index.html", {"request": request, "images": images})

# serve individual images when clicked
@app.get("/image/{image_name}")
async def get_image(image_name: str):
    image_path = Path("images") / image_name
    if image_path.exists() and image_path.is_file():
        return FileResponse(image_path)
    return {"error": "Image not found"}
