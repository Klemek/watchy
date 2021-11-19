from PIL import Image
import os.path

ROOT_DIR = f"{os.path.dirname(__file__)}/pokemon-src/main-sprites/yellow"
FRONT_DIR = f"{ROOT_DIR}/gray"
BACK_DIR = f"{ROOT_DIR}/back/gray"

COUNT = 151

OUT_DIR = f"{os.path.dirname(__file__)}/pokemon-out"

THRESHOLD = 127

for i in range(1, COUNT + 1):
    with Image.open(f"{FRONT_DIR}/{i}.png") as im_src:
        w0, h0 = im_src.size
        im = Image.new(im_src.mode, (56, 56), 'white')
        im.paste(im_src, ((56 - w0) // 2, (56 - h0) // 2))
        im = im.resize((68, 68))
        im = im.point(lambda p: 1 if p > THRESHOLD else 0, mode="1")
        im0, im = im, Image.new(im.mode, (80, 68), color=1)
        im.paste(im0, (0, 0))
        im = im.convert(mode="P")
        im.save(f"{OUT_DIR}/front_{i}.bmp")
    
    with Image.open(f"{BACK_DIR}/{i}.png") as im:
        w0, h0 = im.size
        im0, im = im, Image.new(im.mode, (28, 28), 'white')
        im.paste(im0, (0, 0))
        im = im.resize((68, 68))
        im = im.point(lambda p: 1 if p > THRESHOLD else 0, mode="1")
        im0, im = im, Image.new(im.mode, (80, 68), color=1)
        im.paste(im0, (0, 0))
        im = im.convert(mode="P")
        im.save(f"{OUT_DIR}/back_{i}.bmp")