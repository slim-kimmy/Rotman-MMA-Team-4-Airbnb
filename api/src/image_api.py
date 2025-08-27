
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
import asyncio
from PIL import Image
import io
import base64

app = FastAPI()

sys.path.append("..")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')

executor = ThreadPoolExecutor()

def process_image(image_path, n, m, format):
    img = Image.open(image_path)
    # Resize the image to n x m pixels
    resized_img = img.resize((n, m))
    buf = io.BytesIO()
    resized_img.save(buf, format=format.upper())
    buf.seek(0)
    return buf



@app.get("/images/ads/{ad_id}")
async def get_image(ad_id: int, n: int = 200, m: int = 200, format: str = "png"):
    """
    Returns the image with the given number, resized to n x m pixels.
    """
    image_path = os.path.join(IMAGES_DIR, f"ads/{ad_id}.{format}")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=403, detail="Image not found")

    loop = asyncio.get_event_loop()
    buf = await loop.run_in_executor(executor, process_image, image_path, n, m, format)
    return StreamingResponse(buf, media_type=f"image/ads/{format}")



@app.get("/image/{image_number}")
async def get_image(image_number: int, n: int = 100, m: int = 100, format: str = "png"):
    """
    Returns the image with the given number, resized to n x m pixels.
    """
    image_path = os.path.join(IMAGES_DIR, f"{image_number}.{format}")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    loop = asyncio.get_event_loop()
    buf = await loop.run_in_executor(executor, process_image, image_path, n, m, format)
    return StreamingResponse(buf, media_type=f"image/{format}")



@app.get("/images/{folder_number}")
async def get_images(folder_number: int, n: int = 200, m: int = 200):
    """
    Return all PNGs in IMAGES_DIR/<folder_number>/ resized to n x m and
    packaged in JSON as data URI strings.
    """

    folder_path = os.path.join(IMAGES_DIR, str(folder_number))
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail="Folder not found")

    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".png")])
    if not files:
        return {"folder": folder_number, "images": []}

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(executor, process_image, os.path.join(folder_path, f), n, m, "png")
        for f in files
    ]
    bufs = await asyncio.gather(*tasks)

    images_out = []
    for fname, buf in zip(files, bufs):
        data = buf.getvalue()
        b64 = base64.b64encode(data).decode("ascii")
        images_out.append({"filename": fname, "data_uri": f"data:image/png;base64,{b64}"})

    return {"folder": folder_number, "images": images_out}
