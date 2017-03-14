from flask import current_app, flash, url_for
from werkzeug.utils import secure_filename

import os

ALLOWED_EXTENSIONS = set(['txt' 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'JPG'])

def validName(filename):
    try:
        if filename != '':
            return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        return True
    except:
        return False


def delete(path):

    try:
        os.remove(path)
    except:
        pass



def save(image, item):
    try:
        if image.filename != '':
            filename = '%s_%s' % (item.id, secure_filename(image.filename))

            path = os.path.join(current_app.root_path,
                                current_app.config['UPLOAD_FOLDER'], filename)

            delete(path)
            image.save(path)
            return filename
        else:
            return None
    except Exception as e:
        # flash('The picture was invalid')
        flash(e)
        flash(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename))
        return None

