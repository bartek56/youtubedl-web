from youtubedl import app, logger, mailManager
from flask import render_template
from flask import flash, request


@app.route('/contact.html')
def contactHTML():
    if mailManager.initialize():
        return render_template('contact.html')
    else:
        return render_template('alert.html', alert="Mail is not supported")

@app.route('/mail', methods = ['POST', 'GET'])
def mail():
    if request.method == 'POST':
        sender = request.form['sender']
        message = request.form['message']
        if(len(sender)>2 and len(message)>2):
            fullMessage = "You received message from " + sender + ": " + message
            mailManager.sendMail("bartosz.brzozowski23@gmail.com", "MediaServer", fullMessage)
            flash("Successfull send mail",'success')
        else:
            flash("You have to fill in the fields", 'danger')

    return render_template('contact.html')