from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from __init__ import app
from ista import *
from flask_mail import Mail,Message
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='mohdkashif264@gmail.com'
app.config['MAIL_PASSWORD']='uisv frrq ytii aixy' 
mails=Mail(app)
def get_token(user):
    s=Serializer(app.config["SECRET_KEY"],90)
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
