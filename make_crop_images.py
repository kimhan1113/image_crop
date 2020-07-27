import labelme
import cv2
import glob
import numpy as np
import json
from PIL import Image, ImageDraw
import os
import matplotlib.pyplot as plt
import math

# 각 crop된 종류별로 총 숫자 출력하기

rect = 0
circle = 0
poly = 0

def polygon_crop(points):

    shp = []
    for j in points:
        k = tuple(j)
        shp.append(k)
    # shapes = np.array(shapes)
    im = Image.open(os.path.join(img_folder, base + '.bmp')).convert("RGBA")
    # im = Image.open('Fov002_1.bmp').convert("RGBA")
    # convert to numpy (for convenience)
    imArray = np.asarray(im)
    # create mask
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(shp, outline=1, fill=1)
    mask = np.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = np.empty(imArray.shape, dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:, :, :3] = imArray[:, :, :3]

    # transparency (4th column)
    newImArray[:, :, 3] = mask * 255

    # back to Image from numpy
    newIm = Image.fromarray(newImArray, "RGBA")
    newIm.save(os.path.join('crop_pictures', base + '.png'))

def rect_crop(points):

    img = Image.open(os.path.join(img_folder, base + '.bmp'))
    po = sum(points, [])
    region = img.crop(po)
    region.save(os.path.join('crop_pictures', base + '.png'))

def circle_crop(points):


    po = sum(points, [])

    img = Image.open(os.path.join(img_folder, base + '.bmp')).convert("RGB")
    width, height = img.size

    x = (width - height) // 2
    # create grayscale image with white circle (255) on black background (0)
    mask = Image.new('L', img.size)
    mask_draw = ImageDraw.Draw(mask)
    # width, height = img_cropped.size

    # (cx, cy), (px, py) = po
    cx = po[0]
    cy = po[1]
    px = po[2]
    py = po[3]

    d = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
    # draw.ellipse([cx - d, cy - d, cx + d, cy + d], outline=1, fill=1)

    mask_draw.ellipse([cx - d, cy - d, cx + d, cy + d], fill=255)

    # add mask as alpha channel
    img.putalpha(mask)

    # mask.show()

    img = img.resize((width * 4, height *4))

    # save as png which keeps alpha channel
    img.save(os.path.join('crop_pictures', base + '.png'))

if __name__ == '__main__':

    img_folder = 'imgs' # folder name
    img_list = [img for img in os.listdir(img_folder) if not img.startswith('Anno')]
    # print(img_list)
    img_anno = os.path.join(img_folder,'Annotation') # Annotation folder
    anno_list = os.listdir(img_anno)

    for i in range(len(anno_list)):
        try:
            with open(os.path.join(img_anno, anno_list[i])) as json_file:
                json_data = json.load(json_file)
                shapes = json_data['shapes']

                base = os.path.splitext(anno_list[i])[0]

                for shp in shapes:
                    point = shp['points']
                    if shp['shape_type'] == 'rectangle':
                        rect_crop(point)
                        rect += 1

                    elif shp['shape_type'] == 'polygon':
                        polygon_crop(point)
                        poly += 1

                    elif shp['shape_type'] == 'circle':
                        circle_crop(point)
                        circle += 1

                    else:
                        print('This tool can\'t make crop images. please use polygon, circle and rectangle crop tool')
        except:
            continue

    print(f'Rectangle count = {rect}, Polygon count = {poly}, Circle count = {circle}')

