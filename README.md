# Social-media   http://kashifakhtar.pythonanywhere.com/
It's a social media platform like facebook and instagram that's why name FaceGramClone 😁, it allows user to register themself with thier valid email id's and login. User can post pictures or thier thoughts using this app, user can also send friend request to other users that are using this app and they can like posts,comment on post , like comments on post and delete their own post and comment.It also allow users to message each other if they are both following each other which is the best thing i like about my web app. It's also allow users to update their profile like profile picture ,user name,bio and other things.

## How to run app
1. Either fork or download app.
2. Install all dependencies given in requirements.txt file in cmd using  pip install -r requirements.txt.
3. run create_db.py file to create database and create all the tables that will be required.
4. Now run app.py , you will get local host http://127.0.0.1:5000/ .
5. Now open the url in web browser.
 
## How to use app
1. You will get  login page where on bottom you will see register button,click on it.
2. You will be directed to register page where you can fill your credentials like username, email id , password and other info.
3. You will be directed to login page and a message will be flashed that a link has been send to your email id to verify your email.
4. Go to email , you would have received a link from a email id 'facegramclone', click on it(don't worry it's safe , if you are afraid to use just make a new gmail account and use that while registering 😉).
5. You will be directed to login page, fill in your email id and password that you set.
6. You will see home page, here you can post pictures and see posts of other users whom you are following.
7. There will also be option to see your profile by clicking on profile button, you can update profile by clicking update profile button under that image icon and update information about you like mobile number, profile picture,gender, e.t.c.


## Features
1. You can see other followers by going to explore section and clicking on users profile.
2. You can send friend request to other users by clicking on follow button on their profile page, a friend request will be sent to that user and when he accept your request you could see his posts on your home page.You can also unfollow him by clicking on unfollow button which will be visible only after you have started following him/her.
3. You can message a user if you both are following each other and can also delete your message,you can also see time duration of that message.
4. You can also comment on other user posts and also like other people comment on any posts.
5. You can delete your comments and posts that you posted and also messages that you sent to someone.
6. If someone send you friend request you will get notification in red symbol and it will be visisble in friend request section.
7. The most interesting part is that you can see any notifications that you get like if someone message you or send you friend request or liked and commented on your post and comments in the notification section.
8. Unread messages will also be marked red so that you can get to know if their are any unread messages.
9. You can also update your password if you forget by clicking on change password button on login page, you have to provide your email and link will be send to yout email id.

## Future fetaures
1. Notifications and message notification are kind of interlinked ,means if you click on message section the red symbol on notifcation button will go away and vice versa, maybe do some changes so that clicking on message section doesn't affect notification section red symbol.
2. When you are chatting with someone, others person's messages won't be updated in real time you have to come out of chat box to see other person's message , maybe some changes can be done here to make real time update
3. Again, i am not a web designer , so design formats are not so good ,maybe a little more designing make it near perfect.
4. When someone comment on a post you can't reply to that reply ,you have to make a new comment, maybe allow user to make reply on a reply.

## Dependencies(main)
1. Flask
2. sqlite
3. flask_mail
4. wtforms

## What the app looks like

# Login Page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/login_page.PNG)


# Registration page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/register_page.PNG)


# Home Page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/Home_page.PNG)



# Profile Page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/Profile_page.PNG)




# Profile Update Page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/update_profile.PNG)



# Explore Page
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/explore.PNG)



# POSTS
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/posts_img.PNG)



# Comment
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/comment_on_post.PNG)




# Friend request
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/accept_friend_req.PNG)


# Message 
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/show_unread_msg.PNG)

![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/msg_chat.PNG)




# Notifications
![alt text](https://github.com/kashif-flask/Social-media/blob/master/images/msg_notify.PNG)





