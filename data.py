active = 'active'

import sqlite3

db_path = 'r4db2.db'

def connect_db(path):
    conn = sqlite3.connect(path)
    #converts tuples to dictionary
    conn.row_factory = sqlite3.Row
    #Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    return (conn, conn.cursor(),)

def inserted_id_grabber():
    conn, cur = connect_db(db_path)
    query = 'SELECT last_insert_rowid()'
    results = cur.execute(query,).fetchone()
    return results

def select_users():
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM users'
    results = cur.execute(query,).fetchall()
    return results

def select_users_specific(username):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM users WHERE username = ?'
    results = cur.execute(query, (username,)).fetchall()
    return results

def username_id_grab(user):
    conn, cur = connect_db(db_path)
    query = 'SELECT id FROM users WHERE username = ?'
    results = cur.execute(query, (user,)).fetchone()
    return results

def userid_username_grab(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT username FROM users WHERE id = ?'
    results = cur.execute(query, (user_id,)).fetchone()
    return results

def insert_users(register_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO users (email,username,password,privileges,avatar) VALUES (?,?,?,?,?)'
    values = (
        register_data['email'],
        register_data['username'],
        register_data['password'],
        register_data['privileges'],
        register_data['avatar']
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def update_users_privileges(user_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE users SET privileges=?, WHERE prime_key=?'
    values = (
        user_data['privileges'],
        user_data['prime_key'],
    )
    cur.execute(query,values)
    conn.commit()
    conn.close()

def delete_users(prime_key):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM users WHERE prime_key=?'
    cur.execute(query, (prime_key,))
    conn.commit()
    conn.close()

def select_tiangge():
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM tiangges'
    results = cur.execute(query,).fetchall()
    return results

def select_tiangge_with_id(tiangge_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM tiangges WHERE id = ?'
    results = cur.execute(query, (tiangge_id,)).fetchall()
    return results

def slct_sr_tngg(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_user_tiangge INNER JOIN tiangges ON pvt_user_tiangge.tiangge_id = tiangges.id\
             WHERE user_id=? '
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def confirm_pivot_user_tiangge(user_id, tiangge_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_user_tiangge where user_id=? and tiangge_id=?'
    results = cur.execute(query, (user_id, tiangge_id)).fetchall()
    return results

def tiangge_data_grab(name):
    conn, cur = connect_db(db_path)
    query = 'SELECT id, subscribers, date_created FROM tiangges WHERE name = ?'
    results = cur.execute(query, (name,))
    return results

def insert_tiangge(tiangge_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO tiangges (name, subscribers, date_created) VALUES (?, ?, ?)'
    values = (
        tiangge_data['name'],
        tiangge_data['subscribers'],
        tiangge_data['date_created'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_pivot_user_tiangge(pivot_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_user_tiangge (user_id, tiangge_id) VALUES (?, ?)'
    values = (
        pivot_data['user_id'],
        pivot_data['tiangge_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def update_tiangge_subscriber_count(tiangge_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE tiangges SET subscribers = ? WHERE id = ? AND date_created=?'
    values = (
        tiangge_data['subscribers'],
        tiangge_data['id'],
        tiangge_data['date_created'],
    )
    cur.execute(query,values)
    conn.commit()
    conn.close()

def delete_tiangge(id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM tiangges WHERE id=?'
    cur.execute(query, (id,))
    conn.commit()
    conn.close()

def delete_pivot_user_tiangge(id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM pvt_user_tiangge WHERE id = ?'
    cur.execute(query, (id,))
    conn.commit()
    conn.close()

def select_post():
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM posts'
    results = cur.execute(query,).fetchall()
    return results

def slct_pvt_hx_tngg_pst_w_sr(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_hex_tiangge_post WHERE pvt_hex_tiangge_post.user_id = ?'
    results = cur.execute(query, (user_id, )).fetchall()
    return results

def slct_pvt_pprvl_tngg_pst(tiangge_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_approval_tiangge_post WHERE pvt_approval_tiangge_post.tiangge_id = ?'
    results = cur.execute(query, (tiangge_id, )).fetchall()
    return results

def slct_pvt_pprvl_sr(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_approval_user WHERE user_id = ?'
    results = cur.execute(query, (user_id, )).fetchall()
    return results

def slct_spcfc_pvt_pprvl_sr(user_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_approval_user WHERE user_id = ? AND post_id = ?'
    results = cur.execute(query, (user_id, post_id, )).fetchall()
    return results

def confirm_post_user(user_id, user_name):
    conn, cur = connect_db(db_path)
    query = 'SELECT posts.id, posts.user_id, posts.title FROM posts INNER JOIN users\
             ON posts.user_id = users.id\
             WHERE user_id = ? AND username = ?'
    results = cur.execute(query, (user_id, user_name,)).fetchall()
    return results

def tiangge_id_grab(tiangge_name):
    conn, cur = connect_db(db_path)
    query = 'SELECT id FROM tiangges WHERE name = ?'
    results = cur.execute(query, (tiangge_name, )).fetchone()
    return results

def post_id_grab(title, user_id, date_created):
    conn, cur = connect_db(db_path)
    query = 'SELECT id FROM posts WHERE title = ? AND user_id = ? AND date_created = ?'
    results = cur.execute(query, (title, user_id, date_created)).fetchone()
    return results

def hex_id_grab(hex_cd, date_created):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM hex WHERE hex_cd = ? AND date_created = ?'
    results = cur.execute(query, (hex_cd, date_created)).fetchall()
    return results

def approval_id_grab(date_created):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM approvals WHERE date_created = ?'
    results = cur.execute(query, (date_created, )).fetchall()
    return results

def select_post_tiangge(name):
    conn, cur = connect_db(db_path)
    query = 'select posts.id, posts.title, posts.content, posts.date_created, posts.user_id,\
            posts.like, posts.dislike,\
            tiangges.name, users.username, hex.hex_cd FROM posts INNER JOIN tiangges INNER JOIN hex\
            INNER JOIN users INNER JOIN pvt_hex_tiangge_post ON pvt_hex_tiangge_post.tiangge_id = tiangges.id\
            AND pvt_hex_tiangge_post.user_id = users.id AND posts.id = pvt_hex_tiangge_post.post_id\
            AND hex.id = pvt_hex_tiangge_post.hex_id WHERE name = ?;'
    results = cur.execute(query, (name,)).fetchall()
    return results

def select_post_comment_with_post_id(post_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT comments.id, comments.comment, comments.date_created, comments.post_id,\
             users.username FROM comments INNER JOIN pvt_comment_tiangge_post INNER JOIN users\
             ON comments.id = pvt_comment_tiangge_post.comment_id AND pvt_comment_tiangge_post.user_id = users.id\
             WHERE post_id = ?'
    results = cur.execute(query, (post_id, )).fetchall()
    return results

def select_post_comment(tiangge_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT comments.id, comments.comment, comments.date_created, comments.post_id,\
             users.username FROM comments INNER JOIN pvt_comment_tiangge_post INNER JOIN users\
             ON comments.id = pvt_comment_tiangge_post.comment_id AND pvt_comment_tiangge_post.user_id = users.id\
             WHERE tiangge_id = ? AND post_id = ?'
    results = cur.execute(query, (tiangge_id, post_id, )).fetchall()
    return results

def post_comment_counter(tiangge_id,):
    conn, cur = connect_db(db_path)
    query = 'SELECT comments.id, comments.comment, comments.date_created, comments.post_id,\
             users.username FROM comments INNER JOIN pvt_comment_tiangge_post INNER JOIN users\
             ON comments.id = pvt_comment_tiangge_post.comment_id AND pvt_comment_tiangge_post.user_id = users.id\
             WHERE tiangge_id = ?'
    results = cur.execute(query, (tiangge_id, )).fetchall()
    return results

def check_users_approvals(user_id,):
    conn, cur = connect_db(db_path)
    query = 'SELECT DISTINCT approvals.id, pvt_approval_user.approval_type,\
            pvt_approval_user.user_id, pvt_approval_tiangge_post.post_id,\
            pvt_approval_tiangge_post.tiangge_id\
            FROM approvals\
            INNER JOIN pvt_approval_user INNER JOIN pvt_approval_tiangge_post\
            ON approvals.id = pvt_approval_user.approval_id AND\
            approvals.id = pvt_approval_tiangge_post.approval_id\
            WHERE\
            pvt_approval_user.user_id = ?'
    cur.execute(query, (user_id,))
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def select_post_approval_with_user_id(user_id,):
    conn, cur = connect_db(db_path)
    query = 'SELECT DISTINCT pvt_approval_user.user_id, pvt_approval_user.post_id,\
            pvt_approval_user.approval_type, posts.title, hex.hex_cd,\
            posts.date_created, users.username,\
            posts.like, posts.dislike, pvt_hex_tiangge_post.tiangge_id\
            FROM pvt_approval_user\
            INNER JOIN posts INNER JOIN pvt_hex_tiangge_post INNER JOIN tiangges INNER JOIN users\
            INNER JOIN hex\
            ON pvt_approval_user.post_id = posts.id AND posts.id = pvt_hex_tiangge_post.post_id AND\
            pvt_hex_tiangge_post.tiangge_id = tiangges.id AND pvt_hex_tiangge_post.user_id = users.id\
            AND pvt_hex_tiangge_post.hex_id = hex.id\
            WHERE\
            pvt_approval_user.user_id = ?'
    cur.execute(query, (user_id,))
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def select_post_with_user_id(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT DISTINCT posts.id, posts.title, posts.date_created, posts.user_id,\
            users.username, hex.hex_cd, pvt_hex_tiangge_post.tiangge_id,\
            posts.total, posts.like, posts.dislike, posts.content, posts.content_type\
            FROM posts\
            INNER JOIN pvt_hex_tiangge_post INNER JOIN hex INNER JOIN users \
            ON posts.id = pvt_hex_tiangge_post.post_id AND\
            pvt_hex_tiangge_post.hex_id = hex.id AND\
            pvt_hex_tiangge_post.user_id = users.id\
            WHERE pvt_hex_tiangge_post.user_id = ?'
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def select_post_with_tiangge(tiangge_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT DISTINCT posts.id, posts.title, posts.date_created, posts.user_id,\
            users.username, hex.hex_cd, pvt_hex_tiangge_post.tiangge_id,\
            posts.total, posts.like, posts.dislike, posts.content, posts.date_created\
            FROM posts\
            INNER JOIN pvt_hex_tiangge_post INNER JOIN hex INNER JOIN users \
            ON posts.id = pvt_hex_tiangge_post.post_id AND\
            pvt_hex_tiangge_post.hex_id = hex.id AND\
            pvt_hex_tiangge_post.user_id = users.id\
            WHERE pvt_hex_tiangge_post.tiangge_id = ?'
    results = cur.execute(query, (tiangge_id,)).fetchall()
    return results

def select_post_approval(name_id, title_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT approvals.id, approvals.like, approvals.dislike, approvals.total, approvals.ratio\
             FROM approvals INNER JOIN tiangges INNER JOIN posts\
             ON approvals.tiangge_id = tiangges.id AND approvals.post_id = posts.id\
             WHERE tiangge_id = ? AND post_id = ?'
    results = cur.execute(query, (name_id, title_id, )).fetchall()
    return results

def approval_type_grab(id):
    conn, cur = connect_db(db_path)
    query = 'SELECT approval_type FROM pvt_approval_user WHERE id = ?'
    results = cur.execute(query, (id,))
    return results

def insert_post(post_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO posts (title, content, content_type, date_created, user_id, like, dislike, total, ratio) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'
    values = (
        post_data['title'],
        post_data['content'],
        post_data['content_type'],
        post_data['date_created'],
        post_data['user_id'],
        post_data['like'],
        post_data['dislike'],
        post_data['total'],
        post_data['ratio'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def update_post(post_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE posts SET content = ? WHERE id = ?'
    values = (
        post_data['content'],
        post_data['id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def delete_post(id, date_created):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM posts WHERE id = ? AND date_created = ?'
    cur.execute(query, (id, date_created))
    conn.commit()
    conn.close()

def delete_hex(hex_cd, date_created):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM hex WHERE hex_cd = ? AND date_created = ?'
    cur.execute(query, (hex_cd, date_created))
    conn.commit()
    conn.close()

def delete_approval(approval_id, date_created):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM approvals WHERE id = ? AND date_created = ?'
    cur.execute(query, (approval_id, date_created))
    conn.commit()
    conn.close()

def select_car():
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM cars'
    results = cur.execute(query,).fetchall()
    return results

def select_model():
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM models'
    results = cur.execute(query,).fetchall()
    return results

def select_pivot_cm():
    conn, cur = connect_db(db_path)
    query = 'select pivot_car_model.id, pivot_car_model.car_id, cars.brand, pivot_car_model.model_id, models.type\
            from cars INNER JOIN pivot_car_model INNER JOIN models\
            ON pivot_car_model.car_id = cars.id AND pivot_car_model.model_id = models.id;'
    results = cur.execute(query,).fetchall()
    return results

def insert_pivot_cm(pivot_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pivot_car_model (car_id, model_id) VALUES (?, ?)'
    values = (
        pivot_data['car_id'],
        pivot_data['model_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def delete_pivot_car(car_id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM pivot_car_model WHERE car_id=?'
    values = 'car_id'
    cur.execute(query, (car_id,))
    conn.commit()
    conn.close()

def insert_pvt_hex_tiangge_post(pvt_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_hex_tiangge_post (hex_id, user_id, tiangge_id, post_id) VALUES (?, ?, ?, ?)'
    values = (
        pvt_data['hex_id'],
        pvt_data['user_id'],
        pvt_data['tiangge_id'],
        pvt_data['post_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def confirm_in_approval_user(id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_approval_user WHERE pvt_approval_user.user_id = ?'
    results = cur.execute(query, (id,)).fetchall()
    return results

def confirm_in_approval_user_specific(user_id, tiangge_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_approval_user WHERE pvt_approval_user.user_id = ? AND\
             pvt_approval_user.tiangge_id = ? AND pvt_approval_user.post_id = ?'
    results = cur.execute(query, (user_id, tiangge_id, post_id,)).fetchall()
    return results

def insert_approval(approval_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO approvals (like, dislike, total, ratio, date_created) VALUES (?, ?, ?, ?, ?)'
    values = (
        approval_data['like'],
        approval_data['dislike'],
        approval_data['total'],
        approval_data['ratio'],
        approval_data['date_created'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_pvt_approval_tiangge_post(pvt_approval_tiangge_post_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_approval_tiangge_post (approval_id, tiangge_id, post_id) VALUES (?, ?, ?)'
    values = (
        pvt_approval_tiangge_post_data['approval_id'],
        pvt_approval_tiangge_post_data['tiangge_id'],
        pvt_approval_tiangge_post_data['post_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_pvt_approval_user(pvt_approval_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_approval_user (user_id, post_id, approval_type) VALUES (?, ?, ?)'
    values = (
        pvt_approval_data['user_id'],
        pvt_approval_data['post_id'],
        pvt_approval_data['approval_type'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def delete_pvt_approval_user(user_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM pvt_approval_user WHERE user_id = ? and post_id = ?'
    cur.execute(query, (user_id, post_id, ))
    conn.commit()
    conn.close()

def update_post_approval(approval_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE posts SET like = ?, dislike = ?, total = ?, ratio = ? WHERE id = ?'
    values = (
        approval_data['like'],
        approval_data['dislike'],
        approval_data['total'],
        approval_data['ratio'],
        approval_data['id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def update_pvt_approval_user(pvt_approval_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE pvt_approval_user SET approval_type = ? WHERE user_id = ? AND post_id = ?'
    values = (
        pvt_approval_data['approval_type'],
        pvt_approval_data['user_id'],
        pvt_approval_data['post_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_hex(hex_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO hex (hex_cd, date_created) VALUES (?, ?)'
    values = (
        hex_data['hex_cd'],
        hex_data['date_created'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_comment(comment_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO comments (comment, date_created, post_id, tiangge_id) VALUES (?, ?, ?, ?)'
    values = (
        comment_data['comment'],
        comment_data['date_created'],
        comment_data['post_id'],
        comment_data['tiangge_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_pvt_comment_tiangge_post(pvt_comment_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_comment_tiangge_post (comment_id, user_id) VALUES (?, ?)'
    values = (
        pvt_comment_data['comment_id'],
        pvt_comment_data['user_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def update_comment(comment_data):
    conn, cur = connect_db(db_path)
    query = 'UPDATE comments SET comment = ? WHERE id = ? AND post_id = ? AND tiangge_id = ?'
    values = (
        comment_data['comment_id'],
        comment_data['post_id'],
        comment_data['tiangge_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def select_specific_comment(comment, date_created, post_id, tiangge_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM comments WHERE comment = ? AND date_created = ? AND post_id = ? AND tiangge_id = ?'
    results = cur.execute(query, (comment, date_created, post_id, tiangge_id)).fetchall()
    return results

def slct_sr_svd_pst(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_saved_post_user WHERE user_id = ?'
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def insert_pvt_saved_post_user(pvt_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_saved_post_user (tiangge_id, post_id, user_id) VALUES ( ?, ?, ?)'
    values = (
        pvt_data['tiangge_id'],
        pvt_data['post_id'],
        pvt_data['user_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def delete_pvt_saved_post_user(user_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM pvt_saved_post_user WHERE user_id = ? AND post_id = ? '
    cur.execute(query, (user_id, post_id,))
    conn.commit()
    conn.close()

def slct_sr_hddn_pst(user_id):
    conn, cur = connect_db(db_path)
    query = 'SELECT * FROM pvt_hidden_post_user WHERE user_id = ?'
    results = cur.execute(query, (user_id,)).fetchall()
    return results

def insert_pvt_hidden_post_user(pvt_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_hidden_post_user (tiangge_id, post_id, user_id) VALUES ( ?, ?, ?)'
    values = (
        pvt_data['tiangge_id'],
        pvt_data['post_id'],
        pvt_data['user_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def delete_pvt_hidden_post_user(user_id, post_id):
    conn, cur = connect_db(db_path)
    query = 'DELETE FROM pvt_hidden_post_user WHERE user_id = ? AND post_id = ? '
    cur.execute(query, (user_id, post_id,))
    conn.commit()
    conn.close()

def report_id_grab(report, date_created):
    conn, cur = connect_db(db_path)
    query = 'SELECT id FROM reports WHERE report = ? AND date_created = ?'
    results = cur.execute(query, (report, date_created)).fetchone()
    return results

def insert_report(report_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO reports (report, user_id, date_created) VALUES (?, ?, ?)'
    values = (
        report_data['report'],
        report_data['user_id'],
        report_data['date_created'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()

def insert_pvt_post_report(pvt_data):
    conn, cur = connect_db(db_path)
    query = 'INSERT INTO pvt_post_report (tiangge_id, post_id, report_id) VALUES (?, ?, ?)'
    values = (
        pvt_data['tiangge_id'],
        pvt_data['post_id'],
        pvt_data['report_id'],
    )
    cur.execute(query, values)
    conn.commit()
    conn.close()