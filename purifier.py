from io import BytesIO

from PIL.Image import Image as PImage
from PIL import Image, ImageEnhance, ImageOps, ImageFilter


def check_ratio(image: PImage, ratio):
    from math import floor
    width, height = image.size
    return floor(width * 10 / height) == floor(ratio * 10)

def is_close_color(c1: tuple, c2: tuple, tolerance=30):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def post_processing(image: PImage, image_name) -> PImage:

    yaxis = [7.08, 1.58]
    xaxis = [4.17, 1.36]

    width, height = image.size
    yaxis_grid = [round(height / y, 0) for y in yaxis]
    xaxis_grid = [round(width / x, 0) for x in xaxis]

    # split image
    title_level_button_image = image.crop((0, 0, xaxis_grid[1], yaxis_grid[0]))
    judge_detail_image = image.crop((0, yaxis_grid[0], xaxis_grid[0], yaxis_grid[1]))
    score_image = image.crop((xaxis_grid[0], yaxis_grid[1], xaxis_grid[1], height))

    # post processing judge detail image
    post_processing_judge_detail(judge_detail_image, xaxis_grid=xaxis_grid, yaxis_grid=yaxis_grid)

    # merge image
    new_width = title_level_button_image.width
    new_height = title_level_button_image.height + judge_detail_image.height

    new_image = Image.new("RGB", (new_width, new_height))
    new_image.paste(title_level_button_image, (0, 0))
    new_image.paste(judge_detail_image, (0, title_level_button_image.height))
    new_image.paste(score_image, (judge_detail_image.width, title_level_button_image.height))
    new_image.save(f"after/after_{image_name}")
    print(f"after_{image_name}")
    return new_image


def post_processing_judge_detail(image: PImage, xaxis_grid: list, yaxis_grid: list) -> PImage:
    pixels = image.load()
    width, height = image.size

    target_colors = [
        (191, 191, 191),
        (247, 190, 5),
        (219, 169, 29),
        (246, 174, 24),
        (251, 160, 40),
        (227, 134, 65),
        (231, 117, 85),
        (243, 101, 108),
        (215, 83, 120),
        (220, 69, 137),
        (222, 60, 149),
        (221, 60, 149),
        (180, 7, 7)
    ]

    for y in range(height):
        for x in range(width):
            if xaxis_grid[0]//2 > x and y > height/4.7:
                pixels[x, y] = (0, 0, 0)
            else:
                r, g, b = pixels[x, y]
                if not any(is_close_color((r, g, b), tc) for tc in target_colors):
                    # 대상 색상이 아니면 투명 처리
                    pixels[x, y] = (0, 0, 0)
                else:
                    pixels[x, y] = (255, 255, 255)
    
    return image

def post_processing_title(image: PImage, xaxis_grid: list, yaxis_grid: list) -> PImage:
    return image

def post_processing_button(image: PImage, xaxis_grid: list, yaxis_grid: list) -> PImage:
    return image

def post_processing_score(image: PImage, xaxis_grid: list, yaxis_grid: list) -> PImage:
    return image


def convert_base64_image(image: PImage) -> str:
    import base64
    import io

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode("utf-8")


def purifier(image_path: str, image_name: str) -> str:
    try:
        image = Image.open(f"{image_path}/{image_name}")
    except Exception as e:
        raise ValueError(f"이미지를 불러올 수 없습니다. {e}")
    if check_ratio(image, 16/9) is False:
        raise ValueError("이미지의 비율이 16:9가 아닙니다.")

    image = post_processing(image, image_name)
    return convert_base64_image(image)


def convert_thumbnail(image_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(image_bytes))

    # RGB로 변환 (JPG는 RGBA 지원 안 함)
    image = image.convert("RGB")

    # 80x80으로 리사이즈
    image = image.resize((80, 80))

    # 다시 바이트로 변환 (JPG로 저장)
    output_buffer = BytesIO()
    image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)
    resized_bytes = output_buffer.read()
    return resized_bytes


if __name__ == "__main__":
    import os

    for name in os.listdir("before"):
        print(name, end=" > ")
        purifier("before", name)