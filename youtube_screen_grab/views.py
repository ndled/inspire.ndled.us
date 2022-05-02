from flask import render_template
from flask import request
from flask import Blueprint
from flask import url_for
from flask import redirect

import os
from youtube_screen_grab import celery
from youtube_screen_grab.util import download, remove_old, video_cut, random_image

bp = Blueprint("/", __name__)


@celery.task
def new_video(url):
    url_id = url.split("v=")[-1]
    if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
        remove_old(f"./youtube_screen_grab/static/temp/{url_id}")
    else:
        os.makedirs(f"./youtube_screen_grab/static/temp/{url_id}")
    download(url, f"./youtube_screen_grab/static/temp/{url_id}")
    video_path = f"./youtube_screen_grab/static/temp/{url_id}"
    video_cut(video_path, f"./youtube_screen_grab/static/temp/{url_id}")
    return url


@bp.route("/", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        if request.form.get("submit"):
            form_data = request.form
            url = form_data["new_video"]
            url_id = url.split("v=")[-1]
            if url_id in os.listdir("./youtube_screen_grab/static/temp/"):
                return redirect(url_for("/.newurl", url_id=url_id))
            else: 
                task = new_video.delay(url)
                return redirect(url_for("/.taskstatus", task_id=task.id))
    else:
        results = [f for f in os.listdir("./youtube_screen_grab/static/temp/") if os.path.isdir(f"./youtube_screen_grab/static/temp/{f}")]
        print(results)
        return render_template("new.html", results = results)


@bp.route("/taskstatus/<task_id>", methods=["GET", "POST"])
def taskstatus(task_id):
    task = new_video.AsyncResult(task_id)
    if task.state != "SUCCESS":
        return render_template("task.html", video_name = "In Progress, this can take a while. Press random image to see if it's done", status = task.state)
    else:
        print(task.result.split('v=')[-1])
        return redirect(url_for("/.newurl", url_id=task.result.split('v=')[-1]))

@bp.route("/<url_id>", methods=["GET", "POST"])
def newurl(url_id):
    if os.path.exists(f"./youtube_screen_grab/static/temp/{url_id}"):
        image_path = random_image(img_dir=f"./youtube_screen_grab/static/temp/{url_id}")
        return render_template("task.html", image=f"./static/temp/{url_id}/{image_path}", video_name = image_path.split('.mp4')[0])
    else:
        return redirect(url_for("/.new"))