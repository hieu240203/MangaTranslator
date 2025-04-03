from PIL import Image, ImageDraw, ImageFont

class ImageEditor:
    def __init__(self, font_path='assets/font.ttf', font_size=28):
        self.font = ImageFont.truetype(font_path, font_size)

    def _wrap_text(self, text, box_width):
        words = text.split()
        lines = []
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            width = self.font.getlength(test_line)
            if width <= box_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def draw_translations(self, image_path, results, output_path):
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        for (x1, y1, x2, y2, text_vi) in results:
            draw.rectangle([x1, y1, x2, y2], fill="white")
            box_width = x2 - x1
            box_height = y2 - y1
            lines = self._wrap_text(text_vi, box_width)

            total_text_height = sum([self.font.getbbox(line)[3] - self.font.getbbox(line)[1] for line in lines])
            y_text = y1 + (box_height - total_text_height) // 2

            for line in lines:
                bbox = self.font.getbbox(line)
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                x_text = x1 + (box_width - w) // 2
                draw.text((x_text, y_text), line, fill="black", font=self.font)
                y_text += h

        image.save(output_path)
