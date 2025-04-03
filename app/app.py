import streamlit as st
from PIL import Image
import os
import cv2
import numpy as np
import tempfile
import fitz  # PyMuPDF
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "font.ttf"))

from core.manga_translator import MangaTranslator

translator = MangaTranslator(scale_width=1.3, font_path=font_path)

st.set_page_config(page_title="Manga Translator", layout="wide")
st.title("📖 Dịch Manga sang Tiếng Việt")

st.markdown("Chọn ảnh hoặc file PDF chứa truyện tranh để dịch sang tiếng Việt.")

uploaded_files = st.file_uploader(
    "📤 Upload ảnh hoặc file PDF",
    type=["png", "jpg", "jpeg", "pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    process_button = st.button("🚀 Bắt đầu dịch")

    if process_button:
        st.markdown("## ⏳ Đang xử lý... vui lòng chờ")

        result_images = []

        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            suffix = filename.split(".")[-1].lower()

            if suffix == "pdf":
                # Đọc ảnh từ từng trang PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                    tmp_pdf.write(uploaded_file.read())
                    doc = fitz.open(tmp_pdf.name)
                    for i in range(len(doc)):
                        page = doc.load_page(i)
                        pix = page.get_pixmap(dpi=200)
                        img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                        if pix.n == 4:
                            img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2RGB)
                        result = translator.get_result(img_data)
                        result_images.append(Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)))
            else:
                # Đọc ảnh thường
                image = Image.open(uploaded_file).convert("RGB")
                img_np = np.array(image)
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                result = translator.get_result(img_bgr)
                result_images.append(Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)))

        st.success("✅ Dịch hoàn tất!")

        for idx, res_img in enumerate(result_images):
            st.image(res_img, caption=f"Kết quả trang {idx+1}", use_column_width=True)
