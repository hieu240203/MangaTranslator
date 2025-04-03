from deep_translator import GoogleTranslator
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import wordninja
import re
import os
from core import utlis

class TextTranslator:
    def __init__(self, font_path=None):
        if font_path is None:
            # Dự phòng nếu không truyền font_path từ bên ngoài
            possible_font_paths = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'font.ttf'))
            ]
            for path in possible_font_paths:
                if os.path.exists(path):
                    font_path = path
                    break

            if font_path is None:
                raise FileNotFoundError("No usable font found. Please provide a valid font_path.")

        self.font_path = font_path
        print(f"Using font: {self.font_path}")

        self.image = None
        self.bboxes_cluster = None
        self.translator = GoogleTranslator(source='auto', target='vi')

    def correction_text(self):
        for bbox in self.bboxes_cluster:
            text = utlis.apply_corrections(bbox[4]).lower()
            if len(text) < 5:
                final_text = text
            else:
                sentences = re.split(r'([!?.,])', text)
                processed_sentences = [
                    " ".join(wordninja.split(sentences[i].strip())) + (sentences[i + 1] if i + 1 < len(sentences) else '')
                    for i in range(0, len(sentences), 2)
                ]
                final_text = " ".join(processed_sentences)
            bbox[4] = final_text

    def translation(self, text):
        try:
            if not text.strip():
                return ""
            return self.translator.translate(text=text)
        except:
            return text

    def fit_text_to_bbox(self, image, font_path):
        result_image = image.copy()
        image_pil = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil, 'RGBA')

        try:
            test_font = ImageFont.truetype(font_path, 12)
        except Exception as e:
            print(f"Error loading font: {e}")
            font_path = None

        for bbox in self.bboxes_cluster:
            x1, y1, x2, y2, src_text = bbox
            trans_text = self.translation(src_text)

            padding = 4
            x1, y1, x2, y2 = x1 + padding, y1 + padding, x2 - padding, y2 - padding
            bbox_width = int(x2 - x1)
            bbox_height = int(y2 - y1)

            if bbox_width < 30 or bbox_height < 20:
                continue

            try:
                if font_path:
                    optimal_font_size = utlis.find_optimal_font_size([x1, y1, x2, y2], trans_text, font_path)
                    font = ImageFont.truetype(font_path, optimal_font_size)
                else:
                    font = ImageFont.load_default()

                lines = utlis.wrap_text(trans_text, font, bbox_width)
                text_width, text_height = utlis.calculate_text_dimensions('\n'.join(lines), font)

                x0 = x1 + max(0, (bbox_width - text_width) // 2)
                y0 = y1 + max(0, (bbox_height - text_height) // 2)

                draw.rectangle([x1 - padding, y1 - padding, x2 + padding, y2 + padding], fill=(255, 255, 255, 220))

                line_spacing = 4
                for line in lines:
                    draw.text((x0, y0), line, font=font, fill=(0, 0, 0))
                    y0 += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing
            except Exception as e:
                print(f"Error processing text box: {e}")
                continue

        return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    def add_text_trans_to_image(self, bboxes, image):
        self.bboxes_cluster = bboxes
        self.image = image
        return self.process()

    def process(self):
        self.correction_text()
        image_with_text = self.fit_text_to_bbox(self.image, self.font_path)
        return image_with_text

# from deep_translator import GoogleTranslator
# from PIL import Image, ImageDraw, ImageFont
# import numpy as np
# import cv2
# import wordninja
# import re
# import os
# from core import utlis

# class TextTranslator:
#     def __init__(self, font_path=None):
#         if font_path is None:
#             possible_font_paths = [
#                 os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'font.ttf'))
#             ]
#             for path in possible_font_paths:
#                 if os.path.exists(path):
#                     font_path = path
#                     break

#             if font_path is None:
#                 raise FileNotFoundError("No usable font found. Please provide a valid font_path.")

#         self.font_path = font_path
#         print(f"Using font: {self.font_path}")

#         self.image = None
#         self.bboxes_cluster = None
#         self.translator = GoogleTranslator(source='auto', target='vi')

#     def correction_text(self):
#         for bbox in self.bboxes_cluster:
#             text = utlis.apply_corrections(bbox[4]).lower()
#             if len(text) < 5:
#                 final_text = text
#             else:
#                 sentences = re.split(r'([!?.,])', text)
#                 processed_sentences = [
#                     " ".join(wordninja.split(sentences[i].strip())) + (sentences[i + 1] if i + 1 < len(sentences) else '')
#                     for i in range(0, len(sentences), 2)
#                 ]
#                 final_text = " ".join(processed_sentences)
#             bbox[4] = final_text

#     def translation(self, text):
#         try:
#             if not text.strip():
#                 return ""
#             return self.translator.translate(text=text)
#         except:
#             return text

#     def is_speech_bubble(self, bbox, image):
#         x1, y1, x2, y2 = bbox
#         region = image[y1:y2, x1:x2]
#         if region.size == 0:
#             return False
#         avg_color = np.mean(region)
#         return avg_color > 210  # giả định khung thoại có nền sáng

#     def fit_text_to_bbox(self, image, font_path):
#         result_image = image.copy()
#         image_pil = Image.fromarray(cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB))
#         draw = ImageDraw.Draw(image_pil, 'RGBA')

#         try:
#             test_font = ImageFont.truetype(font_path, 12)
#         except Exception as e:
#             print(f"Error loading font: {e}")
#             font_path = None

#         for bbox in self.bboxes_cluster:
#             x1, y1, x2, y2, src_text = bbox
#             trans_text = self.translation(src_text)

#             padding = 4
#             x1, y1, x2, y2 = x1 + padding, y1 + padding, x2 - padding, y2 - padding
#             bbox_width = int(x2 - x1)
#             bbox_height = int(y2 - y1)

#             if bbox_width < 30 or bbox_height < 20:
#                 continue

#             try:
#                 if font_path:
#                     optimal_font_size = utlis.find_optimal_font_size([x1, y1, x2, y2], trans_text, font_path)
#                     font = ImageFont.truetype(font_path, optimal_font_size)
#                 else:
#                     font = ImageFont.load_default()

#                 lines = utlis.wrap_text(trans_text, font, bbox_width)
#                 text_width, text_height = utlis.calculate_text_dimensions('\n'.join(lines), font)

#                 x0 = x1 + max(0, (bbox_width - text_width) // 2)
#                 y0 = y1 + max(0, (bbox_height - text_height) // 2)

#                 if self.is_speech_bubble([x1, y1, x2, y2], image):
#                     draw.rectangle([x1 - padding, y1 - padding, x2 + padding, y2 + padding], fill=(255, 255, 255, 220))
#                 # else: không vẽ nền nếu không phải khung thoại

#                 line_spacing = 4
#                 for line in lines:
#                     draw.text((x0, y0), line, font=font, fill=(0, 0, 0))
#                     y0 += font.getbbox(line)[3] - font.getbbox(line)[1] + line_spacing
#             except Exception as e:
#                 print(f"Error processing text box: {e}")
#                 continue

#         return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

#     def add_text_trans_to_image(self, bboxes, image):
#         self.bboxes_cluster = bboxes
#         self.image = image
#         return self.process()

#     def process(self):
#         self.correction_text()
#         image_with_text = self.fit_text_to_bbox(self.image, self.font_path)
#         return image_with_text
