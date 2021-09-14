from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import *
from flask import url_for
import os
from flask_mail import Mail,Message
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']="facegramclone@gmail.com"
app.config['MAIL_PASSWORD']="xutmowmmbcmwtztl"
mail=Mail(app)
def get_token(user):
    s=Serializer(app.config["SECRET_KEY"],240)
    return s.dumps({'user_id':user[0]}).decode('utf=8')

def verify_token(token):
    s=Serializer(app.config["SECRET_KEY"])
    try:
        user_id=s.loads(token)['user_id']
    except:
        return None
    c.execute("""SELECT * FROM user WHERE id=?""",(user_id,))
    val=c.fetchone()
    return val
def send_email(user):
    token=get_token(user)
    msg=Message('Reset Instaclone Password',sender='instaclone@demo.com',recipients=[user[2]])
    msg.body=f'''To reset your InstaClone password ,visit following link:
{url_for('change',token=token,_external=True)}

If you did not make this request then just ignore.
'''
    mail.send(msg)

def send_email1(user):

    token=get_token(user)
    msg=Message('Verify InstaClone account',sender='instaclone@demo.com',recipients=[user[2]])
    msg.body=f'''To verify your InstaClone account,visit following link:
{url_for('confirm_email',token=token,_external=True)}

If you did not make this request then just ignore.
'''
    mail.send(msg)

