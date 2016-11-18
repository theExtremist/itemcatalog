import os
from flask import current_app, flash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['txt' 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def validName(filename):
    try:
        if filename != '':
            return filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
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
            path = os.path.join(current_app.root_path,
                                current_app.config['UPLOAD_FOLDER'],'%s_%s'
                                % (item.id, image.filename))
            delete(path)
            delete(item.image)
            image.save(path)
            return path
        else:
            return None
    except:
        flash('The picture was invalid')
        return None