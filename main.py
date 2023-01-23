import random
import string
import os
from flask import Flask, render_template, request, redirect, url_for, session, abort, Markup, jsonify, flash
from datetime import datetime
from collections import defaultdict
from string import hexdigits
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
from wtforms.validators import DataRequired

from data import *
from classes import *

upload_folder = 'static/images/uploads'
legal_extensions = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'avi', 'wmv', 'mov', 'flv', 'webm']
legal_extensions_img = ['.png', '.jpg', '.jpeg', '.gif']
legal_extensions_vid = ['.mp4', '.avi', '.wmv', '.mov', '.webm']

app = Flask(__name__, )
app.secret_key = 'ew34ERv3570'
app.config['upload_folder'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 200 * 1000 * 1000
csrf = CSRFProtect(app)

def username_to_id(user_name):
    user_data = username_id_grab(user_name)
    for id in user_data:
        id = id
    return id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in legal_extensions

def user_log():
    if "user" in session:
        return True
    else:
        return False

def rand_mask():
    rand_str = string.ascii_letters
    rand_int = string.digits
    rand_code_1 = ''.join(random.choice(rand_str) for i in range(2)).join(random.choice(rand_int) for i in range(2))
    rand_code_2 = ''.join(random.choice(rand_str) for i in range(2)).join(random.choice(rand_int) for i in range(2))
    rand_mask = rand_code_1 + rand_code_2
    return rand_mask

def comment_counter(tiangge_name):
    # returns a dict of posts' comment count
    # specific to a tiangge

    i = 0
    comment_count_dict = defaultdict(dict)

    sub_id = tiangge_id_grab(tiangge_name)
    posts_in_sub = select_post_tiangge(tiangge_name)

    for id in sub_id:
        tiangge_id = id
        for k in posts_in_sub:
            comment_count_dict[k['id']] = 0

    for post_ids, counter in comment_count_dict.items():
        post_comments = select_post_comment(tiangge_id, post_ids)
        for values in post_comments:
            counter = counter + 1
            comment_count_dict[post_ids] = counter

    return comment_count_dict

def users_approvals(user_id, tiangge_name):
    # returns a dictionary of a user's liked and disliked posts
    # returns data specific to a subtiangge
    # primarily used to track current user's liked and disliked posts

    user_approval_dict = defaultdict(dict)
    current_user_approval = slct_pvt_pprvl_sr(user_id)
    tiangge_post = select_post_tiangge(tiangge_name)

    for post in tiangge_post:

        user_approval_dict[post['id']] = 3

        for user_data in current_user_approval:
            if user_data['post_id'] == post['id']:
                user_approval_dict[user_data['post_id']] = user_data['approval_type']

    return user_approval_dict


def users_saved(user_id, tiangge_name):
    # returns a dictionary of a user's saved posts
    # returns data specific to a subtiangge
    # primarily used to track current user's saved posts

    tiangge_posts_ids = defaultdict(dict)
    current_user_saved_post = slct_pvt_svd_pst_sr(user_id)
    tiangge_post = select_post_tiangge(tiangge_name)

    for post in tiangge_post:

        tiangge_posts_ids[post['id']] = 'Unsaved'

        for user_data in current_user_saved_post:
            if user_data['post_id'] == post['id']:
                tiangge_posts_ids[user_data['post_id']] = 'Saved'

    return tiangge_posts_ids


def users_privileges(user_id):
    user_submitted = defaultdict(dict)
    id_data = userid_username_grab(user_id)
    for id_user in id_data:
        id_user = id_user

    current_user_approval = slct_pvt_pprvl_sr(user_id)
    posts_submitted = slct_pvt_pprvl_sr(user_id)

    for post in posts_submitted:

        user_submitted[post['id']] = 3

        for user_data in current_user_approval:
            if user_data['post_id'] == post['post_id']:
                user_submitted[user_data['post_id']] = 'Allowed'
            else:
                user_submitted[user_data['post_id']] = 'Not allowed'

    return "I", user_data['post_id']


def mask_post_id_(tiangge_name):
    post_id_mask = defaultdict(dict)
    sub_id = tiangge_id_grab(tiangge_name)
    posts_in_sub = select_post_tiangge(tiangge_name)

    for id in sub_id:
        tiangge_id = id
        for k in posts_in_sub:
            post_id_mask[k['id']] = 0

    for post in posts_in_sub:
        post_id_mask[post['id']] = rand_mask()

    return post_id_mask


@app.route('/')
def index():
    algo = 'FALSE'
    if algo != 'FALSE':
        login_block = ["login_block.html", "in_session_block.html"]
        tiangges = select_tiangge()
        return render_template('base.html', login_block=login_block, tiangges=tiangges, )
    else:
        if 'user' in session:
            return redirect(url_for('tiangge_list'))
        else:
            return redirect(url_for('login'))


@app.route('/test_process', methods=['POST'])
def test_process():
    pivot_data = {
        'car_id': request.form['brand_id'],
        'model_id': request.form['type_id'],
    }

    insert_pivot_cm(pivot_data)
    return redirect(url_for('index', ))


def profile_name_to_id(profile_name):
    user_data = username_id_grab(profile_name)
    for user_id in user_data:
        return user_id


@app.route('/u/<profile_name>/')
def profile_submitted(profile_name):
    user_logged = user_log()

    # main content
    profile_data = Profile_Data(profile_name)
    posts_submitted = select_post_with_user_id(username_id_grab(profile_name)['id'])
    user_mask = profile_data.mask_post_id_profile()

    if not user_logged:
        return render_template('/profiles/submitted.html', profile_data=profile_data, posts_submitted=posts_submitted,
                               user_logged=user_logged, profile_name=profile_name,
                               legal_extensions_img=legal_extensions_img,
                               legal_extensions_vid=legal_extensions_vid, user_mask=user_mask)

    else:
        currentuser_data = CurrentUser_Data(session["user"])
        return render_template('/profiles/submitted.html', profile_data=profile_data, posts_submitted=posts_submitted,
                               user_logged=user_logged, profile_name=profile_name, currentuser_data=currentuser_data,
                                legal_extensions_img=legal_extensions_img,
                               legal_extensions_vid=legal_extensions_vid, user_mask=user_mask)


@app.route('/u/<profile_name>/liked')
def profile_liked(profile_name):
    user_logged = user_log()
    if user_logged and session['user'] == profile_name:
        # main content
        profile_data = Profile_Data(profile_name)
        currentuser_data = CurrentUser_Data(session["user"])
        posts_liked = select_post_approval_with_user_id(username_id_grab(profile_name)['id'], "approved")
        user_mask = profile_data.mask_post_id_approvals()

        return render_template('/profiles/liked.html', profile_data=profile_data, user_logged=user_logged,
                               posts_liked=posts_liked, legal_extensions_img=legal_extensions_img, profile_name=profile_name,
                               legal_extensions_vid=legal_extensions_vid, user_mask=user_mask, currentuser_data=currentuser_data)
    else:
        return redirect(url_for('profile_submitted', profile_name=profile_name))


@app.route('/u/<profile_name>/disliked')
def profile_disliked(profile_name):
    user_logged = user_log()
    if user_logged and session['user'] == profile_name:
        # main content
        profile_data = Profile_Data(profile_name)
        currentuser_data = CurrentUser_Data(session["user"])
        posts_disliked = select_post_approval_with_user_id(username_id_grab(profile_name)['id'], "disapproved")
        user_mask = profile_data.mask_post_id_approvals()

        return render_template('/profiles/disliked.html', profile_data=profile_data, user_logged=user_logged,
                               posts_disliked=posts_disliked, legal_extensions_img=legal_extensions_img, profile_name=profile_name,
                               legal_extensions_vid=legal_extensions_vid, user_mask=user_mask,  currentuser_data=currentuser_data,)
    else:
        return redirect(url_for('profile_submitted', profile_name=profile_name))


@app.route('/u/<profile_name>/saved')
def profile_saved(profile_name):
    user_logged = user_log()
    if user_logged and session['user'] == profile_name:
        profile_data = Profile_Data(profile_name)
        currentuser_data = CurrentUser_Data(session["user"])
        posts_saved = select_post_saved_with_user_id(username_id_grab(profile_name)['id'])
        user_mask = profile_data.users_approval_in_others()['masked_saved_posts_ids']

        return render_template('/profiles/saved.html', profile_data=profile_data, user_logged=user_logged,
                               posts_saved=posts_saved, currentuser_data=currentuser_data,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask, )
    else:
        return redirect(url_for('profile_submitted', profile_name=profile_name))


@app.route('/u/<profile_name>/hidden')
def profile_hidden(profile_name):
    user_logged = user_log()
    if user_logged and session['user'] == profile_name:
        profile_data = Profile_Data(profile_name)
        currentuser_data = CurrentUser_Data(session["user"])
        posts_hidden = select_hidden_post_with_user_id(username_id_grab(profile_name)['id'])
        user_mask = profile_data.users_approval_in_others()['masked_hidden_posts_ids']

        return render_template('/profiles/hidden.html', profile_data=profile_data, user_logged=user_logged,
                               posts_hidden=posts_hidden, currentuser_data=currentuser_data,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask, )
    else:
        return redirect(url_for('profile_submitted', profile_name=profile_name))


@app.route('/login')
def login():
    return render_template('login.html', )


@app.route('/login_process', methods=['POST'])
def login_process():
    users = select_users()

    for users_data in users:
        if request.form['username'] in users_data['username']:
            if request.form['username'] == users_data['username'] and request.form['password'] == users_data[
                'password']:
                session_user = request.form['username']
                session['user'] = session_user
                if 'user' in session:
                    if 'referrer' not in session:
                        return redirect(url_for('index', ))
                    else:
                        return redirect(request.form['referrer'])
                else:
                    return redirect(url_for('login', ))
    else:
        return redirect(url_for('register', ))


@app.route('/logout_process', methods=['POST'])
def logout_process():
    for key in list(session.keys()):
        session.pop(key)
    session.clear()
    return redirect(request.referrer)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_process', methods=['POST'])
def register_process():
    users = select_users()

    register_data = {
        'email': request.form['email'],
        'username': request.form['username'],
        'password': request.form['password'],
        'privileges': 'user_standard',
        'avatar': os.path.join(app.config['upload_folder'], 'default.png')
    }

    if request.form['password'] == request.form['confirm_password']:
        if bool(users) == False:
            session['user'] = request.form['username']

            insert_users(register_data)
            return redirect(url_for('index'))

        elif bool(users) == True:
            for user in users:
                if register_data['username'] not in user['username'] and register_data['email'] not in user['email']:
                    session['user'] = request.form['username']

                    insert_users(register_data)
                    return redirect(url_for('index'))

                elif register_data['username'] in user['username']:
                    return redirect(url_for('login', ))
                elif register_data['email'] in user['email']:
                    return redirect(url_for('login', ))
    else:
        return redirect(url_for('register'))


@app.route('/t/<name>/')
def tiangge(name):

    tiangge_data = Tiangge_Data(name)
    tiangge_name = name
    tiangge_posts = select_post_with_tiangge(tiangge_data.tiangge_name_to_id()['id'])
    user_logged = user_log()
    post_mask = tiangge_data.post_data_in_tiangge()

    if user_logged:
        currentuser_data = CurrentUser_Data(session["user"])
        profile_data = Profile_Data(session['user'])
        user_ids = username_id_grab(session['user'])

        for user_id in user_ids:
            user_id = user_id

        user_saved = users_saved(user_id, name)
        approvals_again = users_approvals(user_id, name)
        approval_list = slct_pvt_pprvl_sr(user_id)

        return render_template('tiangge.html', tiangge_name=tiangge_name, user_id=user_id,
                               tiangge_data=tiangge_data, user_logged=user_logged, profile_data=profile_data,
                               approval_list=approval_list, post_mask=post_mask,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               tiangge_posts=tiangge_posts, currentuser_data=currentuser_data,
                               approvals_again=approvals_again, user_saved=user_saved)

    else:
        return render_template('tiangge.html', tiangge_name=tiangge_name, tiangge_data=tiangge_data,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_logged=user_logged, tiangge_posts=tiangge_posts, post_mask=post_mask)


@app.route('/tiangge_list')
def tiangge_list():
    tiangges = select_tiangge()

    return render_template('tiangge_list.html', tiangges=tiangges, )


@app.route('/tiangge_register')
def tiangge_register():
    return render_template('tiangge_register.html', )


@app.route('/t/<name>/subscribe_process', methods=['POST'])
def subscribe_process(name):
    user_ids = username_id_grab(session['user'])
    for user_id in user_ids:
        user_id = user_id

    tiangge_data = tiangge_data_grab(request.form['name'])

    for tiangge_datum in tiangge_data:
        tiangge_id = tiangge_datum['id']
        tiangge_subscriber = tiangge_datum['subscribers']
        date_created = tiangge_datum['date_created']

    pivot_data = {
        'user_id': user_id,
        'tiangge_id': tiangge_id,
        'is_subscriber': True,
        'is_moderator': False,
    }

    pvt_ids = confirm_pivot_user_tiangge(user_id, tiangge_id)
    for pvt_id in pvt_ids:
        pvt_id = pvt_id['id']

    if request.form['subscribe_process'] == 'subscribe':

        insert_pivot_user_tiangge(pivot_data)

        tiangge_data = {
            'subscribers': tiangge_subscriber + 1,
            'id': tiangge_id,
            'date_created': date_created,
        }

        update_tiangge_subscriber_count(tiangge_data)

        return redirect(url_for('tiangge', name=request.form['name']))

    elif request.form['subscribe_process'] == 'unsubscribe':

        tiangge_data = {
            'subscribers': tiangge_subscriber - 1,
            'id': tiangge_id,
            'date_created': date_created,
        }

        update_tiangge_subscriber_count(tiangge_data)
        delete_pivot_user_tiangge(pvt_id)

        return redirect(url_for('tiangge', name=request.form['name']))

@app.route('/approve_post_process', methods=['POST'])
def approve_post_process():
    user_data = Data_to_Id(request.form)
    user_id = user_data.current_user_id()
    post_id = user_data.post_id_new(request.form['post_title'], user_data.uploader_user_id(), request.form['post_date_created'])
    date = datetime.now().strftime('%a %b %d %Y %X')

    approval_data = {
        'id': post_id,
        'like': int(request.form['approval_like']),
        'dislike': int(request.form['approval_dislike']),
        'total': int(request.form['approval_total']),
    }
    pvt_approval_data = {
        'user_id': user_id,
        'post_id': post_id,
        'date_approval': date,
    }
    if "approval_type" in request.form:
        if request.form['approval_type'] == "approved":
            if request.form['approval'] == "approved":
                approval_data["like"] = approval_data["like"] - 1
                approval_data["total"] = approval_data["total"] - 1
                delete_pvt_approval_user(user_id, post_id)
            elif request.form['approval'] == "disapproved":
                approval_data["like"] = approval_data["like"] - 1
                approval_data["dislike"] = approval_data["dislike"] + 1
                pvt_approval_data["approval_type"] = request.form['approval']
                update_pvt_approval_user(pvt_approval_data)

            if approval_data["dislike"] > approval_data["like"] or approval_data["total"] == 0:
                approval_data["ratio"] = "0%"
            else:
                approval_data["ratio"] = f"{(approval_data['like'] / approval_data['total']):.0%}"
            update_post_approval(approval_data)
        elif request.form['approval_type'] == "disapproved":
            if request.form['approval'] == "approved":
                approval_data["like"] = approval_data["like"] + 1
                approval_data["dislike"] = approval_data["dislike"] - 1
                pvt_approval_data["approval_type"] = request.form['approval']
                update_pvt_approval_user(pvt_approval_data)
            elif request.form['approval'] == "disapproved":
                approval_data["dislike"] = approval_data["dislike"] - 1
                approval_data["total"] = approval_data["total"] - 1
                delete_pvt_approval_user(user_id, post_id)

            if approval_data["dislike"] > approval_data["like"] or approval_data["total"] == 0:
                approval_data["ratio"] = "0%"
            else:
                approval_data["ratio"] = f"{(approval_data['like'] / approval_data['total']):.0%}"
            update_post_approval(approval_data)
    else:
        approval_data["total"] = approval_data["total"] + 1

        if request.form['approval'] == "approved":
            approval_data["like"] = approval_data["like"] + 1
            pvt_approval_data['approval_type'] = "approved"
        elif request.form['approval'] == "disapproved":
            approval_data["dislike"] = approval_data["dislike"] + 1
            pvt_approval_data['approval_type'] = "disapproved"
        if approval_data["dislike"] > approval_data["like"] or approval_data["total"] == 0:
            approval_data["ratio"] = "0%"
        else:
            approval_data["ratio"] = f"{(approval_data['like'] / approval_data['total']):.0%}"
        update_post_approval(approval_data)
        insert_pvt_approval_user(pvt_approval_data)

    return redirect(request.referrer)

@app.route('/tiangge_process', methods=['POST'])
def tiangge_process():
    banner = "/static/images/banner-default.png"
    user_ids = username_id_grab(session['user'])
    for user_id in user_ids:
        user_id = user_id

    tiangge_subscriber = + 1

    tiangge_data = {
        'name': request.form['name'],
        'subscribers': tiangge_subscriber,
        'date_created': datetime.now().strftime('%a %b %d %Y %X'),
        'banner': banner,
    }

    insert_tiangge(tiangge_data)

    tiangge_ids = tiangge_data_grab(request.form['name'])
    for tiangge_id in tiangge_ids:
        tiangge_id = tiangge_id['id']

    pivot_data = {
        'user_id': user_id,
        'tiangge_id': tiangge_id,
        'is_subscriber': 1,
        'is_moderator': 1,
    }

    insert_pivot_user_tiangge(pivot_data)

    return redirect(url_for('index'))


@app.route('/tiangge_delete', methods=['POST'])
def tiangge_delete():
    id = request.form['id']

    delete_tiangge(id)
    return redirect(url_for('index'))


@app.route('/t/<name>/<hexcd>/<title>')
def post(name, hexcd, title):

    profile_data = Profile_Data(session['user'])
    tiangge_data = Tiangge_Data(name)
    tiangges = select_tiangge()

    cmmnt_cntr = comment_counter(name)

    for tiangge in tiangges:
        if tiangge['name'] == name:
            id = tiangge['id']
            name = tiangge['name']

    posts = select_post_with_tiangge(id)

    for post in posts:
        if post['title'] == title and post['hex_cd'] == hexcd:
            post_id = post['id']
            title = post['title']
            content = post['content']
            hexcd = post['hex_cd']
            poster_id = post['user_id']
            uploader = post['username']
            date_created = post['date_created']

    comments = select_post_comment(id, post_id)
    if 'user' in session:
        user_logged = 'True'
        user_ids = username_id_grab(session['user'])
        for user_id in user_ids:
            user_id = user_id

        user_approvals = users_approvals(user_id, name)

        user_saved = users_saved(user_id, name)

        pvt_user_subr = confirm_pivot_user_tiangge(user_id, id)
        cnfrm_in_pvt = bool(pvt_user_subr)
        return render_template('post.html', tiangges=tiangges, id=id, name=name, user_id=user_id,
                               cnfrm_in_pvt=cnfrm_in_pvt, user_logged=user_logged, posts=posts, title=title,
                               hexcd=hexcd, content=content, post_id=post_id, poster_id=poster_id,
                               comments=comments, user_approvals=user_approvals, uploader=uploader,
                               date_created=date_created, cmmnt_cntr=cmmnt_cntr, user_saved=user_saved,
                               profile_data=profile_data, tiangge_data=tiangge_data)

    elif 'user' not in session:
        user_logged = 'False'

        return render_template('post.html', tiangges=tiangges, id=id, name=name, uploader=uploader,
                               user_logged=user_logged, posts=posts, title=title, hexcd=hexcd,
                               content=content, post_id=post_id, poster_id=poster_id, comments=comments,
                               date_created=date_created, cmmnt_cntr=cmmnt_cntr)


@app.route('/t/<name>/submit_text')
def submit_text_post(name):
    tiangge_ids = tiangge_data_grab(name)

    for tiangge_id in tiangge_ids:
        tiangge_id = tiangge_id['id']

    user_ids = username_id_grab(session['user'])
    for user_id in user_ids:
        user_id = user_id

    return render_template('submit_text_post.html', tiangge_id=tiangge_id, user_id=user_id, name=name)


@app.route('/t/<name>/submit_text_process', methods=['POST'])
def submit_text_process(name):
    identifier_date = datetime.now().strftime('%a %b %d %Y %X')
    approval_type = "approved"

    hexdg = string.hexdigits
    hexcd = ''.join(random.choice(hexdg) for i in range(8))

    post_data = {
        'title': request.form['title'],
        'date_created': identifier_date,
        'user_id': request.form['user_id'],
        'like': 1,
        'dislike': 0,
        'total': 1,
        'ratio': "100%",
    }

    if 'file_confirm' in request.form:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = hexcd + secure_filename(file.filename)
            new_filename, content_type = os.path.splitext(
                os.path.join(app.config['upload_folder'], filename).replace("\\", "/"))
            file.save(new_filename)
            post_data['content'] = new_filename
            post_data['content_type'] = content_type
            insert_post(post_data)
    else:
        post_data['content'] = request.form['content']
        post_data['content_type'] = 'text'
        insert_post(post_data)

    hex_data = {
        'hex_cd': hexcd,
        'date_created': identifier_date,
    }

    insert_hex(hex_data)

    written_hex_data = hex_id_grab(hexcd, identifier_date)

    posted_id = post_id_grab(request.form['title'], request.form['user_id'], identifier_date)

    for post_id in posted_id:
        post_id = post_id

    for hex_data in written_hex_data:
        hex_id = hex_data['id']

    pvt_data = {
        'hex_id': hex_id,
        'user_id': request.form['user_id'],
        'tiangge_id': request.form['tiangge_id'],
        'post_id': post_id,
    }

    insert_pvt_hex_tiangge_post(pvt_data)

    pvt_approval_data = {
        'user_id': request.form['user_id'],
        'post_id': post_id,
        'approval_type': approval_type,
        'date_approval': identifier_date
    }

    insert_pvt_approval_user(pvt_approval_data)

    return redirect(url_for('tiangge', name=name))


@app.route('/t/<name>/<hexcd>/<title>/edit', methods=['POST'])
def text_post_edit(name, hexcd, title):
    return render_template('post_edit.html')


@app.route('/t/<name>/<hexcd>/<title>/delete', methods=['POST'])
def text_post_delete(name, hexcd, title):
    user_data = Data_to_Id(request.form)
    post_id = user_data.post_id()

    delete_hex(request.form['hex_cd'], request.form['post_date_created'])
    delete_post(post_id, request.form['post_date_created'])
    if request.form['content_type'] != "text":
        os.remove(request.form['content'])
        return redirect(request.referrer)
    return redirect(request.referrer)


@app.route('/t/<name>/<hexcd>/<title>/comment', methods=['POST'])
def comment_process(name, hexcd, title):
    if 'user' in session:

        user_ids = username_id_grab(session['user'])

        for user_id in user_ids:
            user_id = user_id

        identifier_date = datetime.now().strftime('%a %b %d %Y %X')

        comment_data = {
            'comment': request.form['post_comment'],
            'date_created': identifier_date,
            'post_id': request.form['post_id'],
            'tiangge_id': request.form['tiangge_id'],
        }

        insert_comment(comment_data)

        comment_data = select_specific_comment(request.form['post_comment'], identifier_date,
                                               request.form['post_id'],
                                               request.form['tiangge_id'])
        for data in comment_data:
            comment_id = data['id']

        pvt_comment_data = {
            'comment_id': comment_id,
            'user_id': user_id,
        }

        insert_pvt_comment_tiangge_post(pvt_comment_data)

        return redirect(url_for('post', name=name, hexcd=hexcd, title=title))

    elif 'user' not in session:
        return redirect(url_for('login'))


@app.route('/save_post_process', methods=['POST'])
def save_post_process():
    user_data = Data_to_Id(request.form)
    pvt_data = {
        'tiangge_id': user_data.tiangge_id(),
        'post_id': user_data.post_id(),
        'user_id': user_data.current_user_id(),
        'date_saved': datetime.now().strftime('%a %b %d %Y %X'),
    }
    if request.form['saved_state'] == 'saved':
        insert_pvt_saved_post_user(pvt_data)
    else:
        delete_pvt_saved_post_user(user_data.current_user_id(), user_data.post_id())
    return redirect(request.referrer)


@app.route('/hide_post_process', methods=['POST'])
def hide_post_process():
    user_data = Data_to_Id(request.form)
    pvt_data = {
        'tiangge_id': user_data.tiangge_id(),
        'post_id': user_data.post_id(),
        'user_id': user_data.current_user_id(),
        'date_hidden': datetime.now().strftime('%a %b %d %Y %X'),
    }
    if request.form['hidden_state'] == 'hidden':
        insert_pvt_hidden_post_user(pvt_data)
    else:
        delete_pvt_hidden_post_user(user_data.current_user_id(), user_data.post_id())
    return redirect(request.referrer)

@app.route('/report_post_process', methods=['POST'])
def report_post_process():
    report_data = defaultdict(dict)
    user_data = Data_to_Id(request.form)

    report_data = {
        'date_created': datetime.now().strftime('%a %b %d %Y %X'),
        'user_id': user_data.current_user_id(),
    }
    for reports, data in request.form.items():
        if 'report_type' in reports:
            report_data['report'] = data
            if report_data['report'] != '':
                insert_report(report_data)
            else:
                pass

    if report_data['report'] != '':
        for report_id in report_id_grab(report_data['report'], report_data['date_created']):
            pvt_data = {
                'tiangge_id': user_data.tiangge_id(),
                'post_id': user_data.post_id(),
                'report_id': report_id,
            }
            insert_pvt_post_report(pvt_data)

    return redirect(request.referrer)

@app.route('/interact_user_process', methods=['POST'])
def interact_user_process():
    user_id = username_to_id(request.form['interacting_user'])
    user_id_other = username_to_id(request.form['interacted_user'])
    pvt_data = {
        'user_id': user_id,
        'user_id_other': user_id_other,
        'user_relationship': request.form['user_relationship'],
        'date_other': datetime.now().strftime('%a %b %d %Y %X'),
    }
    if request.form['user_relationship'] == "followed" or request.form['user_relationship'] == "blocked":
        if not slct_pvt_sr_sr_thr(user_id, user_id_other):
            insert_pvt_sr_sr_other(pvt_data)
        else:
            update_pvt_sr_sr_other(pvt_data)
    elif request.form['user_relationship'] == "unfollowed" or request.form['user_relationship'] == "unblocked":
        delete_pvt_sr_sr_other(user_id, user_id_other)

    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True)
