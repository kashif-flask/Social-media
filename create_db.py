import sqlite3
path="insta.db"
conn=sqlite3.connect(path)
conn.execute("""CREATE TABLE "user" (
	"id"	INTEGER,
	"username"	VARCHAR(40) NOT NULL,
	"email"	VARCHAR NOT NULL UNIQUE,
	"name"	TEXT NOT NULL,
	"image"	BLOB,
	"password"	VARCHAR,
	"path"	VARCHAR,
	"bio"	TEXT,
	"phone_number"	TEXT(12),
	"gender"	TEXT,
	"nposts"	INTEGER,
	"confirmed"	INTEGER DEFAULT 0,
	"last_msg_read_time"	TIMESTAMP,
	"notification_read_time"	TIMESTAMP,
	"last_request_seen"	TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT)
)""")
conn.execute("""CREATE TABLE "post" (
	"id"	INTEGER,
	"body"	VARCHAR(140),
	"image"	BLOB,
	"timestamp"	TIMESTAMP,
	"user_id"	INTEGER,
	"path"	VARCHAR,
	"likes"	INTEGER,
	"last_visit"	TIMESTAMP,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""")

conn.execute("""CREATE TABLE "message" (
	"id"	INTEGER,
	"from_id"	INTEGER,
	"to_id"	INTEGER,
	"body"	VARCHAR,
	"timestamp"	TIMESTAMP,
	FOREIGN KEY("to_id") REFERENCES "user"("id"),
	FOREIGN KEY("from_id") REFERENCES "user"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""")
conn.execute("""CREATE TABLE "liked_comment" (
	"liker_id"	INTEGER,
	"likedcomment_id"	INTEGER,
	"timestamp"	TIMESTAMP,
	FOREIGN KEY("likedcomment_id") REFERENCES "comment"("id"),
	FOREIGN KEY("liker_id") REFERENCES "user"("id")
)""")
conn.execute("""CREATE TABLE "liked" (
	"liker_id"	INTEGER,
	"likedpost_id"	INTEGER,
	"timestamp"	TIMESTAMP,
	"read_like"	TIMESTAMP,
	FOREIGN KEY("liker_id") REFERENCES "user"("id"),
	FOREIGN KEY("likedpost_id") REFERENCES "post"("id")
)""")
conn.execute("""CREATE TABLE "follower" (
	"follower_id"	INTEGER,
	"followed_id"	INTEGER,
	"timestamp"	TIMESTAMP,
	"accept"	INTEGER DEFAULT 0,
	FOREIGN KEY("follower_id") REFERENCES "user"("id"),
	FOREIGN KEY("followed_id") REFERENCES "user"("id")
)""")
conn.execute("""CREATE TABLE "comment" (
	"id"	INTEGER,
	"user_id"	INTEGER,
	"post_id"	INTEGER,
	"body"	VARCHAR,
	"timestamp"	TIMESTAMP,
	"track_id"	INTEGER,
	"likes"	INTEGER,
	FOREIGN KEY("post_id") REFERENCES "post"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
)""")