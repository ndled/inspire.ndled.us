#!/usr/bin/env python3

import logging
import os
import random
import math

from yt_dlp import YoutubeDL
import cv2

logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def remove_old(dir):
    for file in os.listdir(dir):
        os.remove(f"{dir}/{file}")


def random_image(img_dir="./static/imgs"):
    """
    Return a random image from the ones in the static/ directory
    """
    img_list = [f for f in os.listdir(img_dir) if f.endswith(".jpg")]
    img_path = random.choice(img_list)
    return img_path


def download(url, path="static/single"):
    ydl_opts = {
        "outtmpl": f"{path}/{'%(title)s-%(id)s.%(ext)s'}",
        "overwrites": True,
        "format": "135",  # Fun fact, has to be string
        "max_filesize": 300000000,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def video_cut(src, destination):
    for file in os.listdir(src):
        logger.info(f"started {src}")
        video_path = f"{src}/{file}"
        image_name = os.path.basename(video_path)
        cap = cv2.VideoCapture(video_path)
        frame_rate = cap.get(5)
        count = 0
        while cap.isOpened():
            frame_id = cap.get(1)
            ret, frame = cap.read()
            if ret != True:
                break
            if frame_id % math.floor(frame_rate) * 60 == 0:
                name = image_name + str(count).zfill(5) + ".jpg"
                count += 1
                cv2.imwrite(f"{destination}/{name}", frame)
    cap.release()


def youtube_url_handler(url):
    if len(url.split("=v")[-1]) == 11:
        url_id = url.split("=v")[-1]
    elif len(url) == 11:
        url_id = url
        url = f"https://www.youtube.com/watch?v={url_id}"
    elif len(url.split("/")[-1]) == 11:
        url_id = url.split("/")[-1]
        url = f"https://www.youtube.com/watch?v={url_id}"
    else:
        return url, "url_id_not_found"
    return url, url_id
