from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Note
from . import db
from .helper import csv_df_to_html, make_facies_log_plot, predict, combine_result
import json
import os
from keras.models import load_model


views = Blueprint('views', __name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
ALLOWED_EXTENSIONS = {'csv'}
model = load_model(os.path.join(APP_ROOT, 'static/model.h5'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/about')
def about():
    return render_template('about.html', user=current_user)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file was uploaded!', category='error')
            return redirect(request.url)

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected files', category='error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            flash('File was uploaded!', category='success')

            tables = csv_df_to_html(file=file_path, describe=False)
            describe_tables = csv_df_to_html(file=file_path, describe=True)

            # visualize
            logs_img = make_facies_log_plot(file_path)

            # prediction
            predict_cols = predict(file_path, model)
            # combine result in one DataFrame
            result_table = combine_result(file_path, predict_cols)
            result_table = result_table.to_html()

            return render_template('visual.html', user=current_user, tables=[tables], describe_tables=[describe_tables], logs_img=logs_img, predicted_table=[result_table])

    return render_template('home.html', user=current_user)


@views.route('delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    note_id = note['noteId']
    note = Note.query.get(note_id)

    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()


    return jsonify({})