from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
import os, uuid, shutil
from PIL import Image
from app.core.config import settings
from app.core.dependencies import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    _: User = Depends(get_current_admin),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Tipo de imagen no permitido (jpeg/png/webp)")

    content = await file.read()
    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"Imagen demasiado grande (máx {settings.MAX_IMAGE_SIZE_MB}MB)")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    upload_dir = os.path.join(settings.UPLOAD_DIR, "products")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    # Resize to max 1200px width
    with Image.open(filepath) as img:
        if img.width > 1200:
            ratio = 1200 / img.width
            new_size = (1200, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            img.save(filepath, optimize=True, quality=85)

    return {"url": f"/uploads/products/{filename}", "filename": filename}


@router.delete("/image/{filename}", status_code=204)
async def delete_image(filename: str, _: User = Depends(get_current_admin)):
    filepath = os.path.join(settings.UPLOAD_DIR, "products", filename)
    if os.path.exists(filepath):
        os.remove(filepath)
