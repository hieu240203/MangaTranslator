# core/ocr_engine.py
import os
import easyocr
from PIL import Image

class OCREngine:
    def __init__(self):
        os.environ['EASYOCR_MODULE_PATH'] = './models'  # Cache model lại
        self.reader = easyocr.Reader(['en'], gpu=False)

    def crop_and_read(self, image, box):
        """
        Cắt vùng box từ ảnh gốc rồi dùng OCR để đọc chữ trong box đó
        """
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        cropped = image[y_min:y_max, x_min:x_max]
        result = self.reader.readtext(cropped)
        if result:
            return result[0][1]  # Trả về text
        return ""
