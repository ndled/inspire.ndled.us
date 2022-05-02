from flask import render_template
from flask import request
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import url_for
from flask import redirect

import os
from youtube_screen_grab import celery
from youtube_screen_grab.util import download, remove_old, video_cut, random_image

bp = Blueprint("/new", __name__)

@celery.task
def new_video(url):
    print("test")
    if os.path.exists("./youtube_screen_grab/static/temp/"):
        remove_old("./youtube_screen_grab/static/temp/")
    else:
        os.makedirs("./youtube_screen_grab/static/temp/")
    download(url, "./youtube_screen_grab/static/temp")
    video_path = "./youtube_screen_grab/static/temp/"
    video_cut(video_path, "./youtube_screen_grab/static/temp")
    image_path = random_image("./youtube_screen_grab/static/temp")
    return image_path

# @bp.route("/new", methods=["GET", "POST"])
# def new():
#     if request.method == "POST":
#         if request.form.get("submit"):
#             form_data = request.form
#             url = form_data["new_video"]
#             flash(f'Getting {url}')
#             new_video.delay(url)
#             return render_template("new.html", image=f"static/temp/{image_path}")
#         if request.form["random_image"]:
#             image_path = random_image(img_dir="./youtube_screen_grab/static/temp")
#             return render_template("new.html", image=f"static/temp/{image_path}")
#     else:
#         return render_template("new.html")


@bp.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        if request.form.get("submit"):
            form_data = request.form
            url = form_data["new_video"]
            flash(f'Getting {url}')
            task = new_video.delay(url)
            return redirect(url_for('/new.taskstatus',task_id=task.id))       
        if request.form["random_image"]:
            image_path = random_image(img_dir="./youtube_screen_grab/static/temp")
            return render_template("new.html", image=f"static/temp/{image_path}")
    else:
        return render_template("new.html")

@bp.route('/taskstatus/<task_id>')
def taskstatus(task_id):
    task = new_video.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'video': task.info,
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)