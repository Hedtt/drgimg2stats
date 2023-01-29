from PIL import Image, ImageFilter
from pytesseract import pytesseract
from typing import List

from imageareas import *
import imageareas
import os
import cv2
import numpy as np
import imutils
from imutils.object_detection import non_max_suppression
import argparse
import re

from game import Game

import sys

# sys.path.append('/usr/local/programs/python/python39/lib/site-packages')

# Define path to tessaract.exe
path_to_tesseract = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Define path to image
path_to_image = 'images/20221124221038_1.jpg'
template = ['images/templates/xp_small.jpg']
path_to_template = 'images/templates/minerals/enor_pearl.jpg'
threshold = .8
# Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract


# Open image with PIL
def crop_image(img_path: str, crop_area: List[int]):
    image = cv2.imread(img_path)
    cropped = image[crop_area[1]: crop_area[3], crop_area[0]: crop_area[2]]
    cv2.imwrite('asdf.jpg', cropped)
    return cropped


def remove_template(image: Image, template_path: str):
    pick = get_area_of_template(image, template_path)
    print("[INFO] {} matched locations *after* NMS".format(len(pick)))
    # loop over the final bounding boxes
    for (startX, startY, endX, endY) in pick:
        # draw the bounding box on the image
        cv2.rectangle(image, (startX, startY), (endX, endY),
                      (255, 0, 0), -3)
    # show the output image
    # cv2.imshow("After NMS", image)
    # cv2.waitKey(0)
    return image


def get_text(image, config: str = 'normal') -> str:
    single_line = '--psm 7'
    single_word = '--psm 8'
    digits = '--psm 6 digits'
    normal = " --psm 11 -c tessedict_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHJIJKLMNOPQRSTUVWXYZ"
    config_used = normal
    if config == 'single_line':
        config_used = single_line
    elif config == 'single_word':
        config_used = single_word
    elif config == 'digits':
        config_used = digits
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(img_gray, lang='eng', config=config_used)
    return text


def get_area_of_template(image, template_path):
    template = cv2.imread(template_path)
    (tH, tW) = template.shape[:2]

    # convert to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # perform matching template
    result = cv2.matchTemplate(imageGray, templateGray, cv2.TM_CCOEFF_NORMED)

    # find all locations in the result map where the matched value is
    # greater than the threshold, then clone our original image, so we
    # can draw on it
    (yCoords, xCoords) = np.where(result >= threshold)
    clone = image.copy()
    print("[INFO] {} matched locations *before* NMS".format(len(yCoords)))
    # loop over our starting (x, y)-coordinates
    # only for viewing purposes
    # for (x, y) in zip(xCoords, yCoords):
    #     # draw the bounding box on the image
    #     cv2.rectangle(clone, (x, y), (x + tW, y + tH),
    #                   (0, 0, 255), 2)
    # show our output image *before* applying non-maxima suppression

    # initialize our list of rectangles
    rects = []
    # loop over the starting (x, y)-coordinates again
    for (x, y) in zip(xCoords, yCoords):
        # update our list of rectangles
        rects.append((x, y, x + tW, y + tH))
    # apply non-maxima suppression to the rectangles
    return non_max_suppression(np.array(rects))


def get_text_from_area(path_to_img, area, rmv_tmpl: bool = True):
    """
    compares text before and after removal of templates and if none returns the text
    :param path_to_img:
    :param area:
    :param rmv_tmpl: should the template be removed
    :return: string
    """
    crop_area = crop_image(path_to_img, area)
    text_wo_rmv_tmpl = get_text(crop_area)
    if rmv_tmpl:
        for temp in os.listdir('images/templates'):
            if temp == 'character' or temp == 'minerals':
                continue
            crop_area = remove_template(crop_area, 'images/templates/' + temp)
    text_w_rmv_tmpl = get_text(crop_area)
    if text_w_rmv_tmpl == text_wo_rmv_tmpl:
        # cv2.imshow('asdf', crop_area)
        # cv2.waitKey(0)
        return text_w_rmv_tmpl, "Same"
    else:
    #     cv2.imshow('asdf', crop_area)
    #     cv2.waitKey(0)
        return text_w_rmv_tmpl, text_wo_rmv_tmpl, "Different"


def get_credits_area(path, game):
    text = get_text_from_area(path, credits_area)
    text = text[0].split('\n')
    text = list(filter(lambda a: a != '', text))
    game.credits.all_credits = text[0].replace('¢','')
    game.credits.primary_objective = text[2]
    game.credits.secondary_objective = text[4]

    regex_survial = re.compile('[01234]x Survival Bonus')
    game.credits.survial_bonus_quan = text[text.index(list(filter(regex_survial.match, text))[0])][0]
    game.credits.survival_bonus = text[text.index(list(filter(regex_survial.match, text))[0])+1]

    regex_gold_mined = re.compile('\d+ x Gold mined')
    game.credits.gold_mined_quan = text[text.index(list(filter(regex_gold_mined.match, text))[0])].replace(' x Gold mined','')
    game.credits.gold_mined = text[text.index(list(filter(regex_gold_mined.match, text))[0])+1]

    regex_tyrant = re.compile('\d+ x Tyrant Shard')
    try:
        game.credits.tyrant_shard_quan = text[text.index(list(filter(regex_tyrant.match, text))[0])].replace(
            ' x Tyrant Shard', '')
        game.credits.tyrant_shard = text[text.index(list(filter(regex_tyrant.match, text))[0]) + 1]
    except:
        pass

    regex_bittergem = re.compile('\d+ x Bittergem')
    try:
        game.credits.bittergem_quan = text[text.index(list(filter(regex_bittergem.match, text))[0])].replace(
            ' x Tyrant Shard', '')
        game.credits.bittergem = text[text.index(list(filter(regex_bittergem.match, text))[0]) + 1]
    except:
        pass

    if 'OMEN Modular Exterminator' in text:
        game.credits.omen = text[text.index('OMEN Modular Exterminator')+1]
    if 'Ebonite Mutation' in text:
        game.credits.ebonite_mutation = text[text.index('Ebonite Mutation')+1]
    if 'Tritilyte Shard' in text:
        game.credits.ebonite_mutation = text[text.index('Tritilyte Shard')+1]
    if '1 x Data Cell' in text:
        game.credits.data_cell = text[text.index('1 x Data Cell')+1]
    if 'Kursite Infection' in text:
        game.credits.kursite_infection = text[text.index('Kursite Infection')+1]


if __name__ == '__main__':
    game = Game()
    get_credits_area(path_to_image, game)
