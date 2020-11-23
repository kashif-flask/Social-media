from flask import Flask,render_template,url_for,redirect,request,flash,session,jsonify,make_response
from threading import Lock
from passlib.hash import sha256_crypt
import datetime as dt
from datetime import timedelta,datetime
import os
import timeago
import time
from werkzeug.utils import secure_filename
from Forms import LoginForm,RegistrationForm,Verify,Change,Search
from sendmail import *
import sqlite3
conn=sqlite3.connect("insta.db",check_same_thread=False,detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
c=conn.cursor()

UPLOAD_FOLDER='static/uploads/'
ALLOWED_EXTENSIONS={'png','jpg','jpeg','mpg','mpeg','mp4','mov'}
app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['SECRET_KEY']=os.environ['Secret_key']

app.permanent_session_lifetime=timedelta(days=1)

def sdate(d):
    v=d.strftime("%d/%m/%Y %H:%M:%S")
    return v
def tim(date):
    d=timeago.format(date,datetime.now())
    return d
def isimage(file):
    ext=file.rsplit('.',1)[1].lower()
    if ext in ('png','jpg','jpeg','gif'):
        return True
    if ext in ('mpg','mpeg','mp4','mov'):
        return False
def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wraps

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS



def isfollowing(follower,followed):
    try:
        c.execute("""SELECT * FROM follower WHERE follower_id=? AND followed_id=?""",(follower,followed))
        if c.fetchone():
            return True
        else:
            return False
    except:
        pass
def pro(user_id):
    try:
        if user_id:
            c.execute("""SELECT * FROM user WHERE id=?""",(user_id,))
            val2=c.fetchone()
            return val2
        else:
            return None
    except:
        pass

def last_read_msg(from_id):
    try:
        c.execute("""SELECT count(*) FROM message WHERE timestamp> (SELECT timestamp FROM follower WHERE follower_id=? AND followed_id=? AND accept=1) AND from_id=? AND to_id=?""",
                      (session['id'],from_id,from_id,session['id']))
        val=c.fetchone()
        if val:
            return val[0]
        else:
            return None
    except:
        pass
@app.route("/last_read/")
def last_read():
    if "logged_in" in session:
        try:
            c.execute("""SELECT count(*) FROM message WHERE timestamp> (SELECT last_msg_read_time FROM user WHERE id=?) AND to_id=?""",(session['id'],session['id']))
            val=c.fetchone()
            if val:
                return jsonify({"result":val[0]})
            else:
                return None
        except:
            pass
    else:
       return redirect(url_for('login')) 
def last_like(post_id):
    try:
        c.execute("""SELECT * FROM liked WHERE timestamp> (SELECT last_visit FROM post WHERE user_id=? AND id=?) AND likedpost_id=? AND liker_id!=?""",
                  (session['id'],post_id,post_id,session['id']))
        val=c.fetchall()
        if val:
            
            return val
        else:
            return None
    except:
        pass
    
def last_comment(post_id):
    try:
    
        c.execute("""SELECT * FROM comment WHERE timestamp> (SELECT last_visit FROM post WHERE user_id=? AND id=?) AND post_id=?
                           AND user_id!=?""",(session['id'],post_id,post_id,session['id']))
        val=c.fetchall()
        if val:
            
            return val
        else:
            return None
    except:
        pass
def last_likecomment(post_id):
    try:
        c.execute("""SELECT notification_read_time FROM user WHERE id=?""",(session['id'],))
        v=c.fetchone()
        x=v[0]-dt.timedelta(minutes=1)
        c.execute("""SELECT * FROM liked_comment WHERE likedcomment_id IN (SELECT id FROM comment WHERE user_id=? AND post_id=?)
                    AND timestamp>(?) AND liker_id!=?""",(session['id'],post_id,x,session['id']))
        val=c.fetchall()
        if val:
            
            return val
        else:
            return None
    except:
        pass
@app.route("/last_request/")
def last_request():
    if "logged_in" in session:
        try:
            c.execute("""SELECT count(*) FROM follower WHERE timestamp> (SELECT last_request_seen FROM user WHERE id=?) AND followed_id=? AND accept=0""",
                      (session['id'],session['id']))
            val=c.fetchone()
            if val:
                return jsonify({"result":val[0]})
            else:
                return None
        except:
            pass
    else:
       return redirect(url_for('login')) 
@app.route("/accept/")
def accept():
    if 'logged_in' in session:
        follower_id=request.args.get('follower_id')
        followed_id=request.args.get('followed_id')
        c.execute("""UPDATE follower SET accept=1,timestamp=? WHERE follower_id=? AND followed_id=?""",(datetime.now(),follower_id,followed_id))
        conn.commit()
        v=pro(follower_id)[3]
        flash(f"Sarted following {v}",'info')
        return redirect(url_for('friendrequest'))
    else:
        return redirect(url_for('login'))
def followback(follower_id):
    print(follower_id)
    c.execute("""SELECT * FROM follower WHERE follower_id=? AND followed_id=?""",(session['id'],follower_id))
    val=c.fetchone()
    if val:
        return False
    else:
        return True
@app.route("/friendrequest/")
def friendrequest():
    
    if 'logged_in' in session:
        c.execute("""UPDATE user SET last_request_seen=? WHERE id=?""",(datetime.now(),session['id']))
        conn.commit()
        c.execute("""SELECT follower_id FROM follower WHERE accept=0  AND followed_id=? ORDER BY timestamp DESC""",(session['id'],))
        val=c.fetchall()
        c.execute("""SELECT follower_id FROM follower WHERE accept=1  AND followed_id=? ORDER BY timestamp DESC""",(session['id'],))
        val1=c.fetchall()
        return render_template("friendrequest.html",val=val,val1=val1,pro=pro,followback=followback,followed_id=session['id'])
        

    else:
        return redirect(url_for('login'))
    
@app.route("/last_notification/")
def last_notification():
    if "logged_in" in session:
        try:
            c.execute("""SELECT count(*) FROM (SELECT user_id,post_id,timestamp FROM comment WHERE timestamp>(
                      SELECT notification_read_time FROM user WHERE id=?) AND post_id IN (SELECT id FROM post WHERE user_id=?) AND user_id!=? UNION
                      SELECT liker_id as user_id,likedpost_id as post_id,timestamp FROM liked WHERE timestamp>(
                      SELECT notification_read_time FROM user WHERE id=?) AND likedpost_id IN (SELECT id FROM post WHERE user_id=?) AND liker_id!=?)""",
                      (session['id'],session['id'],session['id'],session['id'],session['id'],session['id']))
            val=c.fetchone()
            c.execute("""SELECT count(*) FROM liked_comment WHERE likedcomment_id IN (SELECT id FROM comment WHERE user_id=?)
                    AND timestamp>(SELECT notification_read_time FROM user WHERE id=?) AND liker_id!=?""",(session['id'],session['id'],session['id']))
            val1=c.fetchone()
            c.execute("""SELECT count(*) FROM follower WHERE timestamp> (SELECT notification_read_time FROM user WHERE id=?) AND follower_id=? AND accept=1""",
                      (session['id'],session['id']))
            val2=c.fetchone()
            if val:
                t1=val[0]
            else:
                t1=0
            if val1:
                t2=val1[0]
            else:
                t2=0
            if val2:
                t3=val2[0]
            else:
                t3=0
            t=t1+t2+t3
            return jsonify({"result":t})
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/notification/")
def notification():
    if 'logged_in' in session:
        
        def commentor(user_id):
            try:
                c.execute("""SELECT * FROM user WHERE id=?""",(user_id,))
                v=c.fetchone()
                return v[3]
            except:
                pass
        def commentid(comment_id):
            try:
                c.execute("""SELECT post_id FROM comment WHERE id=?""",(comment_id,))
                v=c.fetchone()
                return v[0]
            except:
                pass
        try:
            c.execute("""SELECT id FROM post WHERE user_id=?""",(session['id'],))
            val=c.fetchall()
            c.execute("""SELECT id FROM post""")
            val1=c.fetchall()
            c.execute("""SELECT notification_read_time FROM user WHERE id=?""",(session['id'],))
            vv=c.fetchone()
            tt=vv[0]-dt.timedelta(minutes=2)
            c.execute("""SELECT followed_id FROM follower WHERE timestamp> (?) AND follower_id=? AND accept=1""",
                      (tt,session['id']))
            val2=c.fetchall()
            c.execute("""UPDATE user SET notification_read_time=? WHERE id=?""",(datetime.now(),session['id']))
            conn.commit()
            return render_template("notification.html",val=val,val1=val1,val2=val2,last_comment=last_comment,last_like=last_like,commentid=commentid,
                                   last_likecomment=last_likecomment,commentor=commentor,pro=pro)
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/contact/")
def contact():
    if 'logged_in' in session:
        try:
            c.execute("""UPDATE user SET last_msg_read_time=? WHERE id=?""",(datetime.now(),session['id']))
            conn.commit()
        
            c.execute("""SELECT to_id  FROM message WHERE from_id=? UNION SELECT from_id FROM message WHERE to_id=?""",(session['id'],session['id']))
            val=c.fetchall()
        
            return render_template('contact.html',val=val,pro=pro,current_id=session['id'],last_read_msg=last_read_msg)
        except:
            pass
    else:
        return redirect(url_for('login'))
    
@app.route("/backgroundmessage/",methods=["POST"])
def backgroundmessage():
    try:
        from_id=request.form["from_id"]
        to_id=request.form["to_id"]
        msg=request.form["message"]
        print(from_id)
        print(msg)
        if from_id==session['id']:
            f=0
        else:
            f=1
        if msg:
            c.execute("""SELECT id FROM message ORDER BY timestamp DESC""")
            v=c.fetchall()
            val=pro(from_id)
            return jsonify({'image':'/static/uploads/'+val[6],'username':val[3],'message':msg,'isnotuser':f})
        else:
            return jsonify({'error':'Wrong'})
    except:
        pass
@app.route("/message/",methods=["GET","POST"])
def message():
    
    
    if "logged_in" in session:
        from_id=request.args.get('from_id')
        to_id=request.args.get('to_id')
        
        c.execute("""SELECT * FROM user WHERE id=?""",(to_id,))
        v=c.fetchone()
        c.execute("""UPDATE follower SET timestamp=? WHERE follower_id=? AND followed_id=? AND accept=1""",(datetime.now(),session['id'],to_id))
        
        conn.commit()

        if request.method=="POST":
            msg=request.form["ms"]
            if msg!="":
            
                
                c.execute("""INSERT INTO message(from_id,to_id,body,timestamp) VALUES(?,?,?,?)""",(from_id,to_id,msg,datetime.now()))
                
                conn.commit()
            
                
        
        c.execute("""SELECT * FROM message WHERE from_id=? AND to_id=? UNION SELECT * FROM message WHERE from_id=? AND to_id=?
                  ORDER BY timestamp DESC""",(from_id,to_id,to_id,from_id))
        val=c.fetchall()
        
        return render_template("message.html",from_id=from_id,to_id=to_id,name=v[3],val=val,current_id=session['id'],pro=pro,time=sdate)
    else:
        return redirect(url_for('login.html'))
    
@app.route("/comment/",methods=["GET","POST"])
def comment():
    if 'logged_in' in session:
        try:
            def tim(date):
                d=timeago.format(date,datetime.now())
                return d
            def likedchecker(id1,id2):
                try:
                    c.execute("""SELECT * FROM liked_comment WHERE liker_id=? AND likedcomment_id=?""",(id1,id2))
                    val1=c.fetchone()
                    if val1:
                        return True
                    else:
                        return False
                except:
                    pass
            def commentor(user_id):
                try:
                    c.execute("""SELECT * FROM user WHERE id=?""",(user_id,))
                    val=c.fetchone()
                    return val
                except:
                    pass

            
            post_id=request.args.get('post_id')
            x=datetime.now()-dt.timedelta(minutes=1)
            c.execute("""UPDATE post SET last_visit=? WHERE user_id=? AND id=?""",(x,session['id'],post_id))
            conn.commit()
            c.execute("""SELECT * FROM post WHERE id=?""",(post_id,))
            post=c.fetchone()
            if request.method=="POST":
                
                comment=request.form["tx"]
                if comment!="":
                    c.execute("""INSERT INTO comment(user_id,post_id,body,timestamp) VALUES(?,?,?,?)""",(session['id'],post_id,comment,datetime.now()))
                    conn.commit()
                else:
                    flash("First write something in comment box",'warning')
            c.execute("""SELECT * FROM comment WHERE post_id=? ORDER BY timestamp DESC;""",(post_id,))
            comments=c.fetchall()
            if comments:
                return render_template('comment.html',post=post,comments=comments,commentor=commentor,username=session['current_user'],user_id=session['id'],
                                       likedchecker=likedchecker,tim=tim,isimage=isimage)

            else:
                return render_template('comment.html',post=post,commentor=commentor,isimage=isimage,username=session['current_user'],
                                       user_id=session['id'],last_read=last_read,last_notification=last_notification)
        except:
            pass
    else:
        flash('You need to login first','warning')
        return redirect(url_for('login'))
@app.route("/likescomment/")
def likescomment():
    if 'logged_in' in session:
        try:
            commentid=request.args.get('commentid')
            c.execute("""INSERT INTO liked_comment VALUES(?,?,?)""",(session['id'],commentid,datetime.now()))
            conn.commit()
            c.execute("""SELECT * FROM comment WHERE id=(?)""",(commentid,))
            val=c.fetchone()
            if val[6] is None:
                nl=0
            else:
                nl=val[6]
            c.execute("""UPDATE comment SET likes=(?) WHERE id=?""",(nl+1,commentid))
            conn.commit()
            c.execute("""SELECT likes FROM comment WHERE id=(?)""",(commentid,))
            val=c.fetchone()
            if val[0]:
                likes=val[0]
            else:
                likes=0
            return jsonify({"result":"success","likes":likes})
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/likes/")
def likes():
    if 'logged_in' in session:
        try:
            postid=request.args.get('postid')
            c.execute("""INSERT INTO liked(liker_id,likedpost_id,timestamp) VALUES(?,?,?)""",(session['id'],postid,datetime.now()))
            conn.commit()
            c.execute("""SELECT likes FROM post WHERE id=(?)""",(postid,))
            val=c.fetchone()
            if val[0] is None:
                nl=0
            else:
                nl=val[0]
            c.execute("""UPDATE post SET likes=(?) WHERE id=?""",(nl+1,postid))
            conn.commit()
            c.execute("""SELECT likes FROM post WHERE id=(?)""",(postid,))
            val=c.fetchone()
            if val[0]:
                likes=val[0]
            else:
                likes=0
            return jsonify({"result":"success","likes":likes})
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/unlikescomment/")
def unlikescomment():
    if 'logged_in' in session:
        try:
            commentid=request.args.get('commentid')
            c.execute("""DELETE FROM liked_comment WHERE liker_id=? AND likedcomment_id=?""",(session['id'],commentid))
            conn.commit()
            c.execute("""SELECT * FROM comment WHERE id=(?)""",(commentid,))
            
            val=c.fetchone()
            if val[6] is None:
                nl=0
            else:
                nl=val[6]
            if nl<=0:
                nl=0
            else:
                nl=nl-1
            c.execute("""UPDATE comment SET likes=(?) WHERE id=?""",(nl,commentid))
            conn.commit()
            c.execute("""SELECT likes FROM comment WHERE id=(?)""",(commentid,))
            val=c.fetchone()
            if val[0]:
                likes=val[0]
            else:
                likes=0
            return jsonify({"result":"success","likes":likes})
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/unlikes/")
def unlikes():
    if 'logged_in' in session:
        try:
            postid=request.args.get('postid')
            c.execute("""DELETE FROM liked WHERE liker_id=? AND likedpost_id=?""",(session['id'],postid))
            conn.commit()
            c.execute("""SELECT likes FROM post WHERE id=(?)""",(postid,))
            
            val=c.fetchone()
            if val[0] is None:
                nl=0
            else:
                nl=val[0]
            c.execute("""UPDATE post SET likes=(?) WHERE id=?""",(nl-1,postid))
            conn.commit()
            c.execute("""SELECT likes FROM post WHERE id=(?)""",(postid,))
            val=c.fetchone()
            if val[0]:
                likes=val[0]
            else:
                likes=0
            return jsonify({"result":"success","likes":likes})
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/<username>/following/")
def following(username):
    if 'logged_in' in session:
        try:
            c.execute("""SELECT * FROM user WHERE username=?""",(username,))
            val=c.fetchone()
            if val[6]:
                filename=val[6]
            else:
                filename="default.jpeg"
            c.execute("""SELECT * FROM user WHERE id IN (SELECT followed_id FROM follower WHERE follower_id=? AND accept=1)""",(val[0],))
            val=c.fetchall()
            return render_template("following.html",f=val,current_user=session["current_user"],username=username,filename=filename)
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/<username>/follower/")
def follower(username):
    if 'logged_in' in session:
        try:
            c.execute("""SELECT * FROM user WHERE username=?""",(username,))
            val=c.fetchone()
            if val[6]:
                filename=val[6]
            else:
                filename="default.jpeg"
            c.execute("""SELECT * FROM user WHERE id IN (SELECT follower_id FROM follower WHERE followed_id=? AND accept=1)""",(val[0],))
            val=c.fetchall()
            return render_template("follower.html",f=val,current_user=session["current_user"],username=username,filename=filename)
        except:
            pass
    else:
        return redirect(url_for('login'))
    
@app.route("/deletemessage/")
def deletemessage():
    if 'logged_in' in session:
        try:
            from_id=request.args.get('from_id')
            to_id=request.args.get('to_id')
            msg_id=request.args.get('msg_id')
            try:
                c.execute("""DELETE FROM message WHERE id=?""",(msg_id,))
                conn.commit()
                
            except:
                pass
            return redirect(url_for('.message',from_id=from_id,to_id=to_id))
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/deletecomment/")
def deletecomment():
    if 'logged_in' in session:
        try:
            comment_id=request.args.get('comment_id')
            c.execute("""SELECT * FROM comment WHERE id=?""",(comment_id,))
            val=c.fetchone()
            
        
            
            c.execute("""DELETE FROM comment WHERE id=?""",(comment_id,))
            conn.commit()
            c.execute("""DELETE FROM liked_comment WHERE likedcomment_id=?""",(comment_id,))
            conn.commit()
            
            
            return redirect(url_for('.comment',post_id=val[2]))
        except:
            pass
    else:
        return redirect(url_for('login'))
    
@app.route("/delete/")
def delete():
    if 'logged_in' in session:
        try:
            postid=request.args.get('postid')
            c.execute("""SELECT path FROM post WHERE id=?""",(postid,))
            val1=c.fetchone()
            
            try:
                os.remove(f"C:\\Users\\Kashik\\Desktop\\instaclone\\static\\uploads\\{val1[0]}")
                c.execute("""DELETE FROM post WHERE id=?""",(postid,))
                conn.commit()
                c.execute("""DELETE FROM liked WHERE likedpost_id=?""",(postid,))
                conn.commit()
                c.execute("""DELETE FROM comment WHERE post_id=?""",(postid,))
                conn.commit()
            except:
                pass
            
            c.execute("""SELECT * FROM user WHERE id=?""",(session["id"],))
            val=c.fetchone()
            if val[10]:
                npost=val[10]-1
            else:
                npost=0
            c.execute("""UPDATE user SET nposts=? WHERE id=?""",(npost,session["id"]))
            conn.commit()
            flash("Deleted post",'info')
            
            return redirect(url_for('home'))
        except:
            pass
    else:
        return redirect(url_for('login'))
@app.route("/follow/")
def follow():
    if 'logged_in' in session:
        
        followed=request.args.get('username')
        follower=session["current_user"]
        c.execute("""SELECT id FROM user WHERE username=?""",(follower,))
        followerid=c.fetchone()
        c.execute("""SELECT * FROM user WHERE username=?""",(followed,))
        followedid=c.fetchone()
        c.execute("""INSERT INTO follower(follower_id,followed_id,timestamp) VALUES(?,?,?)""",(followerid[0],followedid[0],datetime.now()))
        conn.commit()
        flash(f"Friend request sent to {followedid[3]}",'info')
        return redirect(url_for('home'))
        
    else:
        return redirect(url_for('login'))
    
@app.route("/unfollow/")
def unfollow():
    if 'logged_in' in session:
        try:
            followed=request.args.get('username')
            follower=session["current_user"]
            c.execute("""SELECT id FROM user WHERE username=?""",(follower,))
            followerid=c.fetchone()
            c.execute("""SELECT * FROM user WHERE username=?""",(followed,))
            followedid=c.fetchone()
            c.execute("""DELETE FROM follower WHERE follower_id=? AND followed_id=?""",(followerid[0],followedid[0]))
            conn.commit()
            flash(f"unfollowed {followedid[3]}",'info')
            return redirect(url_for('home'))
        except:
            pass
    else:
        redirect(url_for('login'))
@app.route('/load')
def load():
    print('yo')
    time.sleep(0.2)
    if request.args:
        print(request.args.get("c"))
        counter=int(request.args.get("c"))
        if counter==0:
            print(f"returning 0 to {5}")
            c.execute("""SELECT * FROM user LIMIT 5""")
            val=c.fetchall()
            print(val)
            res=make_response(jsonify(val),200)
        elif counter==10:
            print('no more post')
            res=make_response(jsonify({}),200)
        else:
            print(f"returning {counter} to {counter+5}")
            c.execute("""SELECT * FROM user LIMIT ?,5""",(counter,))
            val=c.fetchall()
            res=make_response(jsonify(val),200)
    return res
@app.route("/explore/",methods=["GET","POST"])
def explore():
    if "logged_in" in session:
        form=Search()
        if form.validate_on_submit():
            search=form.search.data
            c.execute("""SELECT * FROM user WHERE username LIKE ('%' || ? || '%') OR name LIKE ('%' || ? || '%')""",(search,search))
            val=c.fetchall()
            return render_template("explore.html",users=val,form=form,flag=1,username=session["current_user"])
        return render_template("explore.html",form=form,flag=0,username=session["current_user"])
    else:
        return redirect(url_for('login'))
@app.route("/profile/<username>/update/",methods=["GET","POST"])
def update(username):
    if "logged_in" in session:
        try:
            flag=False
            if request.method=='POST':
                n=request.form['name9']
                b=request.form['tx9']
                ph=request.form['pn9']
                gen=request.form['gn9']
                c.execute("""SELECT path FROM user WHERE id=?""",(session['id'],))
                val=c.fetchone()
                try:
                    file=request.files['file']
                    
                    if file and allowed_file(file.filename):
                        filename=secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                        c.execute("""UPDATE user SET path=? WHERE id=?""",(filename,session['id']))
                        conn.commit()
                        flag=True
                except:
                    pass
                

                if not flag:
                    if n:
                        c.execute("""UPDATE user SET name=?,bio=?,phone_number=?,gender=? WHERE id=?""",(n,b,ph,gen,session["id"]))
                        conn.commit()
                        flash("profile updated succesfully","success")
                    else:
                        flash("Fill Name")
            c.execute("""SELECT * FROM user WHERE id=?""",(session['id'],))
            val=c.fetchone()
                
            if val[7] is None:
                bio=""
            else:
                bio=val[7]
                
            if val[8] is None:
                phone=""
            else:
                phone=val[8]
                
            if val[9] is None:
                gender=""
            else:
                gender=val[9]
            if val[6] is None:
                filename="default.jpeg"
            else:
                filename=val[6]
            return render_template("update.html",username=username,filename=filename,bio=bio,gender=gender,phone=phone,name=val[3])
        except:
            pass
    else:
        return redirect(url_for('login'))

@app.route("/profile/<username>/")
def profile(username):
    if "logged_in" in session:
        try:
            def friend(to_id,from_id):
                c.execute("""SELECT * FROM follower WHERE follower_id=? AND followed_id=? AND accept=1""",(to_id,from_id))
                if c.fetchone():
                    c.execute("""SELECT * FROM follower WHERE follower_id=? AND followed_id=? AND accept=1""",(from_id,to_id))
                    if c.fetchone():
                        return True

                return False
            current_user=session['current_user']
            c.execute("""SELECT * FROM user WHERE username=?""",(current_user,))
            followerid=c.fetchone()
            c.execute("""SELECT * FROM user WHERE username=?""",(username,))
            followedid=c.fetchone()
            c.execute("""SELECT * FROM post WHERE user_id=?""",(followedid[0],))
            posts=c.fetchall()
        
            isfollowings=isfollowing(followerid[0],followedid[0])
            path='default.jpeg'
            
            c.execute("""SELECT count(followed_id) FROM follower WHERE follower_id=? AND accept=1""",(followedid[0],))
            v=c.fetchone()
            if v:
                following=v[0]
            else:
                following=0
            c.execute("""SELECT count(follower_id) FROM follower WHERE followed_id=? AND accept=1""",(followedid[0],))
            v=c.fetchone()
            if v:
                follower=v[0]
            else:
                follower=0
            if followedid[6] is None:
                filename=path
            else:
                filename=followedid[6]
                
            if followedid[7] is None:
                bio=""
            else:
                bio=followedid[7]
                
            if followedid[8] is None:
                phone=""
            else:
                phone=followedid[8]
                
            if followedid[9] is None:
                gender=""
            else:
                gender=followedid[9]
            if followedid[10] is None:
                npost=""
            else:
                npost=followedid[10]
            
            return render_template("profile.html",posts=posts,npost=npost,bio=bio,phone=phone,gender=gender,follower=follower,following=following,filename=filename,
                                   username=username,nameus=followedid[3],namecr=followerid[3],current_user=current_user,isfollowings=isfollowings,current_id=session['id'],
                                   user_id=followedid[0],friend=friend,isimage=isimage,a1="",a2="active",a3="",a4="")
        except:
            pass
    return redirect(url_for('login'))
@app.route("/home/",methods=["GET","POST"])
def home():
    if "logged_in" in session:
        try:
            flag=False
            

            def likedchecker(id1,id2):
                c.execute("""SELECT * FROM liked WHERE liker_id=? AND likedpost_id=?""",(id1,id2))
                val1=c.fetchone()
                if val1:
                    return True
                else:
                    return False
            c.execute("""SELECT * FROM user WHERE id=?""",(session['id'],))
            val=c.fetchone()
            try:
                file=request.files['file']
            
                if file and allowed_file(file.filename):
                    filename=secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                    flag=True
                
            except:
                pass
            if request.method=="POST":
                k=False
                post=request.form["ps"]
                print(post)
                if flag and post=="":
                    c.execute("""INSERT INTO post(path,timestamp,user_id,last_visit) VALUES (?,?,?,?)""",(filename,datetime.now(),session["id"],datetime.now()))
                    conn.commit()
                    k=True
                elif post!="" and not flag:
                    c.execute("""INSERT INTO post(body,timestamp,user_id,last_visit) VALUES (?,?,?,?)""",(post,datetime.now(),session["id"],datetime.now()))
                    conn.commit()
                    k=True
                elif post!="" and flag:
                    c.execute("""INSERT INTO post(body,timestamp,user_id,path,last_visit) VALUES (?,?,?,?,?)""",(post,datetime.now(),session["id"],filename,datetime.now()))
                    conn.commit()
                    k=True
                    
                else:
                    pass
                if k:
                    if val[10]:
                        npost=val[10]+1
                    else:
                        npost=1
                    c.execute("""UPDATE user SET nposts=? WHERE id=?""",(npost,session["id"]))
                    conn.commit()
            query="""SELECT m.id,m.body,m.image,m.timestamp,m.user_id,m.path,m.likes,m.last_visit,u.id,u.username,u.email,u.name,u.image,u.password,u.path,u.bio,u.phone_number,u.gender,
                     u.nposts,u.confirmed,u.last_msg_read_time,u.notification_read_time,u.last_request_seen FROM(post p INNER JOIN follower f ON p.user_id = f.followed_id) m
                     LEFT JOIN (SELECT * FROM user) u ON m.followed_id=u.id WHERE m.follower_id=? AND m.accept=1
                     UNION SELECT * FROM post JOIN (SELECT * FROM user WHERE id=?) s ON post.user_id=s.id ORDER BY timestamp DESC"""
            c.execute(query,(session['id'],session["id"]))
            posts=c.fetchall()
            
            if posts:
                
                return render_template("home.html",likedchecker=likedchecker,current_userid=session['id'],time=tim,username=val[1],current_user=val[1],name=val[3],
                                       posts=posts,last_comment=last_comment,isimage=isimage,a1="active",a2="",a3="",a4="")
            else:
                return render_template("home.html",username=val[1],current_user=val[1],name=val[3],a1="active",a2="",a3="",a4="")
        except:
            pass
    else:
        return redirect(url_for('login'))
    
@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email=verify_token(token)
        email=email[2]
    except:
        flash("The confirmation link is invalid or expired,Please register again",'danger')
        try:
            c.execute("DELETE FROM user WHERE email=?",(email,))
            conn.commit()
        except:
            pass
        return redirect(url_for('register'))
    c.execute("""SELECT * FROM user WHERE email=?""",(email,))
    val=c.fetchone()
    if val[-1]:
        flash("Account already verified,Please login",'success')
    else:
        c.execute("""UPDATE user SET confirmed=1 WHERE email=?""",(email,))
        conn.commit()
        flash("Your account has been verified .Please Login")
    return redirect(url_for('login'))
@app.route("/register/",methods=["GET" ,"POST"])
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        username=form.username.data
        email=form.email.data
        password=form.password.data
        confirm_password=form.confirm_password.data
        name=form.name.data
        
        try:
            c.execute("""SELECT * FROM user WHERE username=?""",(username,))
            if c.fetchone() is None:
                pa=sha256_crypt.encrypt(password)
                c.execute("""SELECT * FROM user WHERE email=?""",(email,))
                val=c.fetchone()
                if val is None:
                    c.execute("""INSERT INTO user(username,email,password,name,last_msg_read_time,notification_read_time,last_request_seen) VALUES(?,?,?,?,?,?,?)""",
                              (username,email,pa,name,datetime.now(),datetime.now(),datetime.now()))
                    conn.commit()
                else:
                    if not val[-1]:
                        c.execute("""UPDATE user SET username=?,password=?,name=? WHERE email=?""",(username,pa,name,email))
                        conn.commit()
                    else:
                        flash("Email already exist",'warning')
                c.execute("""SELECT * FROM user WHERE email=?""",(email,))
                val=c.fetchone()
                send_email1(val)
                flash("An email has been send to your email,click the link within 4 min to verify your account",'success')
                return redirect(url_for("login"))
                
            else:
               flash("username already exist",'warning') 
        
        except Exception as e:
            flash(f"{e}")
    
    return render_template("register.html",form=form)
@app.route("/",methods=["GET","POST"])
@app.route("/login/",methods=["GET","POST"])
def login():
    
    
    if "logged_in" in session:
        flash("already logged in")
        return redirect(url_for("home"))
    else:
        form=LoginForm()
        if form.validate_on_submit():
            session.permanent=True
            email=form.email.data
            password=form.password.data
            remember=form.remember.data
            c.execute("""SELECT * FROM user WHERE email=?""",(email,))
            val2=c.fetchone()
            if val2 is not None:
                ap=val2[5]
                i=val2[0]
            
        
                if sha256_crypt.verify(password,ap):
                    if val2[-2]:
                        session["logged_in"]=True
                        session["id"]=i
                        session["current_user"]=val2[1]
                        return redirect(url_for("home"))
                    else:
                        flash("You didn't verified your account,Please confirm first by clicking the given link or registering again",'warning')
                    
                    
                else:
                    flash("wrong password!",'warning')
            
            else:
                flash("No such username","warning")
                
            
    return render_template("login.html",form=form)    
    
@app.route("/logout/")
def logout():
    if "logged_in" in session:
        flash("you have been logged out!")
        session.pop("logged_in",None)
        session.pop("id",None)
        session.pop("current_user",None)
         
    else:
        flash("you need to login first")

    
    
    session.clear()
    return redirect(url_for('login'))
        
    
@app.route("/verify/",methods=["GET","POST"])
def verify():
    if 'logged_in' in session:
        return redirect(url_for('home'))
    form=Verify()
    if form.validate_on_submit():
        email=form.email.data
        c.execute("""SELECT * FROM user WHERE email=?""",(email,))
        val=c.fetchone()
        if val is not None:
            send_email(val)
            flash('An email has been send to your email,click the link to reset password','info')
            return redirect(url_for('login'))
        else:
            flash("No such email","warning")
        
    return render_template("verify.html",form=form)
@app.route("/change/<token>",methods=["GET","POST"])
def change(token):
    if 'logged_in' in session:
        return redirect(url_for('home'))
    user=verify_token(token)
    if user is None:
        flash('Either it is invalid token or your it has expired','warning')
        return redirect(url_for('verify'))
    
    form=Change()
    
    if form.validate_on_submit():
        pas=form.password.data
        pa=sha256_crypt.encrypt(pas)
        try:
            c.execute("""UPDATE user SET password=? WHERE email=?""",(pa,user[2]))
            conn.commit()
            flash("password changed successfully","success")
            return redirect(url_for("login"))
        except:
            pass
        
        
    return render_template("change.html",form=form)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html",username=session["current_user"])

def getApp():
    return app
