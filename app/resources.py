import base64
import os.path

from flask_restful import Resource
from flask import request, url_for
from werkzeug.utils import secure_filename
import app


class Selfie(Resource):

    def post(self):
        image = request.files.get("image")
        data = request.form.to_dict()
        caption = data["caption"]
        # description = data["description"]
        id = data["id"]
        upload_folder = "static/uploads"
        file_name = secure_filename(image.filename)
        img_dir = os.path.join(upload_folder, file_name)
        image.save(img_dir)

        url = url_for('static', filename=f'uploads/{file_name}')
        img_full_url = f'http://localhost:6160{url}'
        return {
            "image": url,
            "caption": caption,
            # "description": description,
            "id": id
        }, 200
