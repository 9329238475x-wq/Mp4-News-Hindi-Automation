"""
Master Watermark & Burned-in Text Blurring Engine (DLS Broadcast Standard)
-------------------------------------------------------------------------
1. Detects and applies smooth Gaussian blur to channel logos & watermarks (ABP, Bhaskar, Aaj Tak, NDTV, Zee).
2. Applies sleek broadcast frosted feather blur to bottom tickers, straps, and third-party Hindi headline banners.
3. Leaves the central 75% scene and human faces 100% crisp, sharp, and high-definition.
"""

import os
from PIL import Image, ImageFilter, ImageDraw
import numpy as np


def clean_watermarks_and_text(img: Image.Image) -> Image.Image:
    """
    तस्वीर से वॉटरमार्क, चैनल लोगो और बॉटम टिकर/टेक्स्ट को गॉसियन ब्लर से स्मूथ हटाना।
    """
    if img is None:
        return img

    w, h = img.size
    if w < 100 or h < 100:
        return img

    if img.mode != "RGB":
        img = img.convert("RGB")

    arr = np.array(img)
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    # 1. बॉटम बैनर / टिकर / टेक्स्ट स्ट्रैप ज़ोन (निचला 18-20% हिस्सा)
    bottom_start_y = int(h * 0.82)
    draw.rectangle([0, bottom_start_y, w, h], fill=255)

    # यदि टेक्स्ट थोड़ा ऊपर तक फैला हो (68% से 82% के बीच टेक्स्ट-एज डिटेक्शन)
    try:
        gray = np.mean(arr, axis=2)
        for y_chk in range(int(h * 0.68), bottom_start_y):
            row_diff = np.abs(np.diff(gray[y_chk, :]))
            edge_density = np.mean(row_diff > 35)
            if edge_density > 0.15:
                draw.rectangle([0, max(0, y_chk - 4), w, bottom_start_y], fill=255)
                break
    except Exception:
        pass

    # 2. कॉर्नर वॉटरमार्क / चैनल लोगो बग्स (Top-Right, Top-Left, Bottom Corners)
    try:
        # Top-Right corner (सबसे आम: ABP Live, Aaj Tak, NDTV, Bhaskar)
        tr_slice = arr[: int(h * 0.22), int(w * 0.74) :]
        tr_gray = gray[: int(h * 0.22), int(w * 0.74) :]
        tr_edge = np.mean(np.abs(np.diff(tr_gray, axis=1)) > 30)
        tr_has_badge = (
            (tr_slice[:, :, 0] > 160)
            & (tr_slice[:, :, 1] < 80)
            & (tr_slice[:, :, 2] < 80)
        ).sum() > 40
        tr_has_white_box = (
            (tr_slice[:, :, 0] > 230)
            & (tr_slice[:, :, 1] > 230)
            & (tr_slice[:, :, 2] > 230)
        ).sum() > 200

        if tr_edge > 0.07 or tr_has_badge or tr_has_white_box:
            draw.rectangle([int(w * 0.74), 0, w, int(h * 0.20)], fill=255)

        # Top-Left corner
        tl_slice = arr[: int(h * 0.22), : int(w * 0.26)]
        tl_gray = gray[: int(h * 0.22), : int(w * 0.26)]
        tl_edge = np.mean(np.abs(np.diff(tl_gray, axis=1)) > 30)
        tl_has_badge = (
            (tl_slice[:, :, 0] > 160)
            & (tl_slice[:, :, 1] < 80)
            & (tl_slice[:, :, 2] < 80)
        ).sum() > 40
        if tl_edge > 0.08 or tl_has_badge:
            draw.rectangle([0, 0, int(w * 0.26), int(h * 0.20)], fill=255)

        # Bottom-Right corner watermark bug
        br_slice = arr[int(h * 0.78) :, int(w * 0.74) :]
        br_gray = gray[int(h * 0.78) :, int(w * 0.74) :]
        br_edge = np.mean(np.abs(np.diff(br_gray, axis=1)) > 30)
        if br_edge > 0.08:
            draw.rectangle([int(w * 0.74), int(h * 0.78), w, h], fill=255)
    except Exception:
        pass

    # स्मूथ फेदरिंग ताकि ब्लर और ओरिजिनल फोटो के बीच कोई हार्श लाइन न दिखे
    mask = mask.filter(ImageFilter.GaussianBlur(radius=14))

    # स्ट्रॉन्ग गॉसियन ब्लर (रेडियस 26 - जिससे टेक्स्ट 100% अपठनीय व आकर्षक फ्रॉस्टेड बन जाए)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=26))
    return Image.composite(blurred, img, mask)


def blur_burned_in_text_and_watermarks(image_path: str) -> bool:
    """
    फाइल पाथ पर मौजूद तस्वीर को ब्लर करके उसी स्थान पर सुरक्षित ओवरराइट करता है।
    """
    if not image_path or not os.path.exists(image_path):
        return False
    if image_path.lower().endswith((".mp4", ".webm", ".gif")):
        # वीडियो या एनिमेटेड मीडिया को स्किप करें
        return True

    try:
        with Image.open(image_path) as im:
            cleaned = clean_watermarks_and_text(im)
            # Temporary file write then replace for atomic update
            temp_path = f"{image_path}.clean.jpg"
            cleaned.save(temp_path, "JPEG", quality=95)

        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
            os.replace(temp_path, image_path)
            return True
    except Exception as e:
        print(f"    ⚠️ [Blur Helper] Error processing {image_path}: {e}")
    return False
