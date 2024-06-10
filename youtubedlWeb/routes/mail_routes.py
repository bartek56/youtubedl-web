from flask import Blueprint, render_template, flash, request
from flask import current_app as app

mail_bp = Blueprint('mail', __name__)

@mail_bp.route('/contact.html')
def contactHTML():
    if app.mailManager.initialize():
        return render_template('contact.html')
    else:
        return render_template('alert.html', alert="Mail is not supported")

@mail_bp.route('/mail', methods = ['POST', 'GET'])
def mail():
    if request.method == 'POST':
        sender = request.form['sender']
        message = request.form['message']
        if(len(sender)>2 and len(message)>2):
            fullMessage = "You received message from " + sender + ": " + message
            app.mailManager.sendMail("bartosz.brzozowski23@gmail.com", "MediaServer", fullMessage)
            flash("Successfull send mail",'success')
        else:
            flash("You have to fill in the fields", 'danger')

    return render_template('contact.html')