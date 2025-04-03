import os
import cv2

from core.detector import TextDetector
from core.text_translator import TextTranslator

# ==== CẤU HÌNH ====
INPUT_IMAGE = "D:\proxglobal\MangaTranslator\samples\image.png"
OUTPUT_IMAGE = "data/translated/translated_demo1.jpg"
FONT_PATH = "assets/font.ttf"

# ==== Load ảnh ====
image = cv2.imread(INPUT_IMAGE)
assert image is not None, "Không tìm thấy ảnh đầu vào."

# ==== Detect box ====
detector = TextDetector()
bboxes = detector.detect_text_from_image(image)

# ==== Dịch + ghi đè text ====
translator = TextTranslator(font_path=FONT_PATH)
output_img = translator.add_text_trans_to_image(bboxes, image)

# ==== Lưu ảnh đã dịch ====
os.makedirs(os.path.dirname(OUTPUT_IMAGE), exist_ok=True)
cv2.imwrite(OUTPUT_IMAGE, output_img)
print(f"✅ Ảnh đã dịch lưu tại: {OUTPUT_IMAGE}")
