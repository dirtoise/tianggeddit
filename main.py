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

upload_folder = 'static/images/uploads'
legal_extensions = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mkv', 'avi', 'wmv', 'mov', 'flv', 'webm']
legal_extensions_img = ['.png', '.jpg', '.jpeg', '.gif']
legal_extensions_vid = ['.mp4', '.avi', '.wmv', '.mov', '.webm']

app = Flask(__name__, )
app.secret_key = 'ew34ERv3570'
app.config['upload_folder'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 200 * 1000 * 1000
csrf = CSRFProtect(app)


# GOAL: Make a class function that contains all the information from sql.
# It must be able to call data from the class that the website/user requires
class Profile_Data:
    def __init__(self, user_name):
        self.user_name = user_name

    def profile_name_to_id(self):
        user_data = username_id_grab(self.user_name)
        return user_data

    def data_user_name(self):
        user_data = select_users_specific(self.user_name)
        for name in user_data:
            return name['username']

    def data_user_avatar(self):
        user_data = select_users_specific(self.user_name)
        for avatar in user_data:
            return avatar['avatar']

    def user_sub_privileges(self, tiangge_id):
        self.tiangge_id = tiangge_id
        user_privileges = confirm_pivot_user_tiangge(profile_name_to_id(self.user_name), self.tiangge_id)
        for user_privilege in user_privileges:
            if user_privilege['is_subscriber'] == "1":
                return True
            else:
                return False

    def user_mod_privileges(self, tiangge_id):
        self.tiangge_id = tiangge_id
        user_privileges = confirm_pivot_user_tiangge(profile_name_to_id(self.user_name), self.tiangge_id)
        for user_privilege in user_privileges:
            if user_privilege['is_moderator'] == "1":
                return True
            else:
                return False

    def user_tiangges(self):
        tiangge_list = []
        user_tiangge = slct_sr_tngg(profile_name_to_id(self.user_name))
        for data in user_tiangge:
            tiangge_list.append(data['name'])
        return tiangge_list

    def user_approved(self):
        user_approval_dict = defaultdict(dict)
        current_user_approval = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        user_posts = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in user_posts:
            user_approval_dict[post['post_id']] = 3

            for user_data in current_user_approval:
                if user_data['post_id'] == post['post_id']:
                    user_approval_dict[user_data['post_id']] = user_data['approval_type']

        return user_approval_dict

    def user_likes(self):
        user_likes_dict = defaultdict(dict)
        for post_id, approval_type in self.user_approved().items():
            if approval_type == 1:
                user_likes_dict[post_id] = approval_type
        return user_likes_dict

    def user_dislikes(self):
        user_dislikes_dict = defaultdict(dict)
        for post_id, approval_type in self.user_approved().items():
            if approval_type == 0:
                user_dislikes_dict[post_id] = approval_type
        return user_dislikes_dict

    def user_privileges_in_approved(self):
        # used as privilege check for posts
        submitted_posts_dict = defaultdict(dict)
        approved_posts_dict = defaultdict(dict)
        user_privileges_dict = defaultdict(dict)

        current_user_post_data = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for data in current_user_post_data:
            submitted_posts_dict[data['post_id']] = data['post_id']
        for post_ids, approval_types in self.user_approved().items():
            approved_posts_dict[post_ids] = approval_types

        for x, y in submitted_posts_dict.items():
            for a, b in self.user_approved().items():
                if a in submitted_posts_dict:
                    user_privileges_dict[a] = 'Allowed'
                else:
                    user_privileges_dict[a] = 'Not allowed'
        return user_privileges_dict

    def user_saved(self):
        user_saved_dict = defaultdict(dict)
        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        user_approvals = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:

            user_saved_dict[post['post_id']] = 'Unsaved'

            for user_data in current_user_saved_post:

                if user_data['post_id'] == post['post_id']:
                    user_saved_dict[user_data['post_id']] = 'Saved'

        return user_saved_dict

    def user_hidden(self):
        user_hidden_dict = defaultdict(dict)
        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))
        user_approvals = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:
            user_hidden_dict[post['post_id']] = 'Unhide'

            for user_data in current_user_hidden_post:

                if user_data['post_id'] == post['post_id']:
                    user_hidden_dict[user_data['post_id']] = 'Hidden'

        return user_hidden_dict

    def tiangges_in_profile(self):
        # returns a dict of tiangges the current user is subscribed in

        tiangge_dict = defaultdict(dict)
        tiangge_id_name_dict = defaultdict(dict)

        user_posts = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for post in user_posts:
            tiangge_dict[post['tiangge_id']] = ''
        for tiangge_id, names in tiangge_dict.items():
            tiangge_specific = select_tiangge_with_id(tiangge_id)
            for data in tiangge_specific:
                if data['id'] == tiangge_id:
                    tiangge_id_name_dict[data['id']] = data['name']
        return tiangge_id_name_dict

    def user_data_in_approvals(self):
        # dict that contains all other dict
        user_data_approvals_dict = defaultdict(dict)
        # a dict of posts' comment count
        # specifically showing only the comments posted by the session user
        comment_count_dict = defaultdict(dict)
        # a dict of posts that are masked
        masked_posts_ids = defaultdict(dict)
        # random hexstrings that act as post id masks
        hexstr = string.ascii_letters
        hexint = string.digits
        # returns a dictionary of a user's saved posts. Data specific to a subtiangge
        # primarily used to track current user's saved posts
        saved_posts_ids = defaultdict(dict)
        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        # returns a dictionary of a user's saved posts. Data is specific to a subtiangge
        # primarily used to track current user's saved posts
        hidden_posts_ids = defaultdict(dict)
        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))
        # main content
        user_approvals = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:
            # adds 0 counter to post id
            comment_count_dict[post['post_id']] = 0
            # adds Unsaved as default values for post ids
            saved_posts_ids[post['post_id']] = 'Unsaved'
            # adds Unhide as default values for post ids
            hidden_posts_ids[post['post_id']] = 'Unhide'
            # adds random hexcode to post id
            masked_posts_ids[post['post_id']] = rand_mask()
            # adds Saved to post ids that are in saved and approved pivot tables
            for user_data in current_user_saved_post:
                if user_data['post_id'] == post['post_id']:
                    saved_posts_ids[user_data['post_id']] = 'Saved'
            # adds Hidden to post ids that are in Hidden and approved pivot tables
            for user_data in current_user_hidden_post:
                if user_data['post_id'] == post['post_id']:
                    hidden_posts_ids[user_data['post_id']] = 'Hidden'
        # calculates and assigns comment counter to post id in dict
        for post_ids, counter in comment_count_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for comments in post_comments:
                counter = counter + 1
                comment_count_dict[post_ids] = counter
        # resulting comment counter dict
        user_data_approvals_dict['comment_count_dict'] = comment_count_dict
        # resulting masked post ids dict
        user_data_approvals_dict['masked_post_ids'] = masked_posts_ids
        # resulting saved post ids dict
        user_data_approvals_dict['saved_posts_ids'] = saved_posts_ids
        # resulting saved post ids dict
        user_data_approvals_dict['hidden_post_ids'] = hidden_posts_ids

        return user_data_approvals_dict

    def comment_counter_in_approvals(self):
        # returns a dict of posts' comment count
        # specifically showing only the comments posted by the session user
        comment_count_dict = defaultdict(dict)
        user_approvals = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:
            comment_count_dict[post['post_id']] = 0

        for post_ids, counter in comment_count_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for values in post_comments:
                counter = counter + 1
                comment_count_dict[post_ids] = counter

        return comment_count_dict

    def mask_post_id_approvals(self):

        masked_posts_ids = defaultdict(dict)

        posts_submitted = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in posts_submitted:
            masked_posts_ids[post['post_id']] = rand_mask()

        return masked_posts_ids

    def users_saved_approvals(self):
        # returns a dictionary of a user's saved posts
        # returns data specific to a subtiangge
        # primarily used to track current user's saved posts
        tiangge_posts_ids = defaultdict(dict)

        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        user_approvals = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:

            tiangge_posts_ids[post['post_id']] = 'Unsaved'

            for user_data in current_user_saved_post:

                if user_data['post_id'] == post['post_id']:
                    tiangge_posts_ids[user_data['post_id']] = 'Saved'

        return tiangge_posts_ids

    def users_hidden_approvals(self):
        # returns a dictionary of a user's saved posts
        # returns data specific to a subtiangge
        # primarily used to track current user's saved posts
        tiangge_posts_ids = defaultdict(dict)

        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))
        user_approvals = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post in user_approvals:

            tiangge_posts_ids[post['post_id']] = 'Unhide'

            for user_data in current_user_hidden_post:

                if user_data['post_id'] == post['post_id']:
                    tiangge_posts_ids[user_data['post_id']] = 'Hidden'

        return tiangge_posts_ids

    def users_hidden_saved(self):

        user_data = defaultdict(dict)
        user_saved_in_hidden_dict = defaultdict(dict)
        user_privileges_in_saved_dict = defaultdict(dict)
        user_hidden_in_saved_dict = defaultdict(dict)
        user_privileges_in_hidden_dict = defaultdict(dict)
        submitted_posts_dict = defaultdict(dict)
        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))
        current_user_post_data = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for data in current_user_post_data:
            submitted_posts_dict[data['post_id']] = data['post_id']

        for hidden_post in current_user_hidden_post:
            user_saved_in_hidden_dict[hidden_post['post_id']] = 'Unsaved'

            for x, y in submitted_posts_dict.items():
                if hidden_post['post_id'] in submitted_posts_dict:
                    user_privileges_in_hidden_dict[hidden_post['post_id']] = 'Allowed'
                else:
                    user_privileges_in_hidden_dict[hidden_post['post_id']] = 'Not allowed'

            for saved_post in current_user_saved_post:
                if saved_post['post_id'] == hidden_post['post_id']:
                    user_saved_in_hidden_dict[hidden_post['post_id']] = 'Saved'

        user_data['privileges_in_hidden'] = user_privileges_in_hidden_dict
        user_data['saved_in_hidden'] = user_saved_in_hidden_dict

        for saved_post in current_user_saved_post:
            user_hidden_in_saved_dict[saved_post['post_id']] = 'Unhide'

            for x, y in submitted_posts_dict.items():
                if saved_post['post_id'] in submitted_posts_dict:
                    user_privileges_in_saved_dict[saved_post['post_id']] = 'Allowed'
                else:
                    user_privileges_in_saved_dict[saved_post['post_id']] = 'Not allowed'

            for hidden_post in current_user_hidden_post:
                if hidden_post['post_id'] == saved_post['post_id']:
                    user_hidden_in_saved_dict[hidden_post['post_id']] = 'Hidden'

        user_data['privileges_in_saved'] = user_privileges_in_saved_dict
        user_data['hidden_in_saved'] = user_hidden_in_saved_dict

        return user_data

    def users_approval_in_others(self):

        approved_data = defaultdict(dict)
        user_saved_dict = defaultdict(dict)
        user_hidden_dict = defaultdict(dict)
        # a dict of posts' comment count
        comment_count_saved_dict = defaultdict(dict)
        comment_count_hidden_dict = defaultdict(dict)
        # a dict of posts that are masked
        masked_saved_posts_ids = defaultdict(dict)
        masked_hidden_posts_ids = defaultdict(dict)

        user_saved = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        user_hidden = slct_pvt_hddn_pst_sr(profile_name_to_id(self.user_name))
        user_approval = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        for post_data in user_saved:
            user_saved_dict[post_data['post_id']] = 3
            # adds 0 counter to post id
            comment_count_saved_dict[post_data['post_id']] = 0
            # adds random hexcode to post id
            masked_saved_posts_ids[post_data['post_id']] = rand_mask()

            for user_data in user_approval:
                if user_data['post_id'] == post_data['post_id']:
                    user_saved_dict[user_data['post_id']] = user_data['approval_type']

        approved_data['approved_in_saved'] = user_saved_dict

        for post_data in user_hidden:
            user_hidden_dict[post_data['post_id']] = 3
            # adds 0 counter to post id
            comment_count_hidden_dict[post_data['post_id']] = 0
            # adds random hexcode to post id
            masked_hidden_posts_ids[post_data['post_id']] = rand_mask()

            for user_data in user_approval:
                if user_data['post_id'] == post_data['post_id']:
                    user_hidden_dict[user_data['post_id']] = user_data['approval_type']

        # resulting masked post ids dict
        approved_data['masked_saved_posts_ids'] = masked_saved_posts_ids
        approved_data['masked_hidden_posts_ids'] = masked_hidden_posts_ids
        approved_data['approved_in_hidden'] = user_hidden_dict
        # calculates and assigns comment counter to post id in dict
        for post_ids, counter in comment_count_saved_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for comments in post_comments:
                counter = counter + 1
                comment_count_saved_dict[post_ids] = counter
        # resulting comment counter dict
        approved_data['comment_count_saved_dict'] = comment_count_saved_dict
        # calculates and assigns comment counter to post id in dict
        for post_ids, counter in comment_count_hidden_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for comments in post_comments:
                counter = counter + 1
                comment_count_hidden_dict[post_ids] = counter
        # resulting comment counter dict
        approved_data['comment_count_hidden_dict'] = comment_count_hidden_dict

        return approved_data

    def users_approvals_profile(self):
        # returns a dictionary of a user's liked and disliked posts
        # primarily used to track current user's liked and disliked posts
        # ONLY USES USER ID

        user_approval_dict = defaultdict(dict)
        current_user_approval = slct_pvt_pprvl_sr(profile_name_to_id(self.user_name))

        user_posts = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))
        # this function takes the user's submitted posts' ids only
        # if used for getting approvals, etc. shows ONLY the users submitted posts

        for post in user_posts:

            user_approval_dict[post['post_id']] = 3

            for user_data in current_user_approval:

                if user_data['post_id'] == post['post_id']:
                    user_approval_dict[user_data['post_id']] = user_data['approval_type']

        return user_approval_dict

    def comment_counter_in_profile(self):
        # returns a dict of posts' comment count
        # specifically showing only the comments posted by the session user

        i = 0
        comment_count_dict = defaultdict(dict)
        user_posts = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for post in user_posts:
            comment_count_dict[post['post_id']] = 0

        for post_ids, counter in comment_count_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for values in post_comments:
                counter = counter + 1
                comment_count_dict[post_ids] = counter

        return comment_count_dict

    def users_saved_profile(self):
        # returns a dictionary of a user's saved posts
        # primarily used to track current user's saved posts
        # ONLY USES USER ID

        posts_ids = defaultdict(dict)
        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.user_name))
        user_posts = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for post in user_posts:

            posts_ids[post['post_id']] = 'Unsaved'

            for user_data in current_user_saved_post:

                if user_data['post_id'] == post['post_id']:
                    posts_ids[user_data['post_id']] = 'Saved'

        return posts_ids

    def users_hidden_profile(self):
        # returns a dictionary of a user's saved posts
        # primarily used to track current user's saved posts
        # ONLY USES USER ID

        user_hidden_dict = defaultdict(dict)
        user_posts = slct_pvt_hx_tngg_pst_w_sr(profile_name_to_id(self.user_name))

        for post in user_posts:
            user_hidden_dict[post['post_id']] = 'Hidden'

        return user_hidden_dict

    def mask_post_id_profile(self):

        posts_ids = defaultdict(dict)
        posts_submitted = select_post_with_user_id(profile_name_to_id(self.user_name))

        for post in posts_submitted:
            posts_ids[post['id']] = rand_mask()

        return posts_ids


# class containing all data about current tiangge
class Tiangge_Data:
    def __init__(self, tiangge_name):
        self.tiangge_name = tiangge_name

    def tiangge_name_to_id(self):
        tiangge_id = tiangge_id_grab(self.tiangge_name)
        return tiangge_id

    def data_tiangge_banner(self):
        tiangge_data = select_tiangge_with_id(self.tiangge_name_to_id()['id'])
        for banner in tiangge_data:
            return banner['banner']

    def data_tiangge_icon(self):
        tiangge_data = select_tiangge_with_id(self.tiangge_name_to_id()['id'])
        for icon in tiangge_data:
            return icon['icon']

    def user_hidden(self, session_user):
        self.session_user = session_user
        user_hidden_dict = defaultdict(dict)
        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.session_user))
        tiangge_posts = select_post_with_tiangge(self.tiangge_name_to_id()['id'])

        for post in tiangge_posts:
            user_hidden_dict[post['id']] = 'Unhide'

            for user_data in current_user_hidden_post:

                if user_data['post_id'] == post['id']:
                    user_hidden_dict[user_data['post_id']] = 'Hidden'

        return user_hidden_dict

    def post_data_in_tiangge(self):

        masked_posts_ids = defaultdict(dict)
        tiangge_posts = select_post_with_tiangge(self.tiangge_name_to_id()['id'])

        for post in tiangge_posts:
            masked_posts_ids[post['id']] = rand_mask()

        return masked_posts_ids

    def user_data_in_tiangge(self, session_username):
        self.session_username = session_username
        # dict that contains all other dict
        user_data_approvals_dict = defaultdict(dict)
        # a dict of posts' comment count
        # specifically showing only the comments posted by the session user
        comment_count_dict = defaultdict(dict)
        # a dict of posts that are masked
        masked_posts_ids = defaultdict(dict)
        # random hexstrings that act as post id masks
        hexstr = string.ascii_letters
        hexint = string.digits
        # returns a dictionary of a user's saved posts. Data specific to a subtiangge
        # primarily used to track current user's saved posts
        saved_posts_ids = defaultdict(dict)
        current_user_saved_post = slct_pvt_svd_pst_sr(profile_name_to_id(self.session_username))
        # returns a dictionary of a user's saved posts. Data is specific to a subtiangge
        # primarily used to track current user's saved posts
        hidden_posts_ids = defaultdict(dict)
        current_user_hidden_post = slct_pvt_hddn_pst_sr(profile_name_to_id(self.session_username))
        # main content
        user_approvals = select_post_with_tiangge(self.tiangge_name_to_id()['id'])

        for post in user_approvals:
            # adds 0 counter to post id
            comment_count_dict[post['id']] = 0
            # adds Unsaved as default values for post ids
            saved_posts_ids[post['id']] = 'Unsaved'
            # adds Unhide as default values for post ids
            hidden_posts_ids[post['id']] = 'Unhide'
            # adds random hexcode to post id
            masked_posts_ids[post['id']] = rand_mask()
            # adds Saved to post ids that are in saved and approved pivot tables
            for user_data in current_user_saved_post:
                if user_data['post_id'] == post['id']:
                    saved_posts_ids[user_data['post_id']] = 'Saved'
            # adds Hidden to post ids that are in Hidden and approved pivot tables
            for user_data in current_user_hidden_post:
                if user_data['post_id'] == post['id']:
                    hidden_posts_ids[user_data['post_id']] = 'Hidden'
        # calculates and assigns comment counter to post id in dict
        for post_ids, counter in comment_count_dict.items():
            post_comments = select_post_comment_with_post_id(post_ids)
            for comments in post_comments:
                counter = counter + 1
                comment_count_dict[post_ids] = counter
        # resulting comment counter dict
        user_data_approvals_dict['comment_count_dict'] = comment_count_dict
        # resulting masked post ids dict
        user_data_approvals_dict['masked_post_ids'] = masked_posts_ids
        # resulting saved post ids dict
        user_data_approvals_dict['saved_posts_ids'] = saved_posts_ids
        # resulting saved post ids dict
        user_data_approvals_dict['hidden_post_ids'] = hidden_posts_ids

        return user_data_approvals_dict

    # returns a dict of posts' comment count
    # specific to a tiangge
    def comment_counter_tiangge(self):
        i = 0
        comment_count_dict = defaultdict(dict)
        tiangge_id = self.tiangge_name_to_id()
        posts_in_tiangge = select_post_tiangge(self.tiangge_name)

        for ids in posts_in_tiangge:
            comment_count_dict[ids['id']] = 0

        for post_ids, counter in comment_count_dict.items():
            for id in tiangge_id:
                post_comments = select_post_comment(id, post_ids)
                for values in post_comments:
                    counter = counter + 1
                    comment_count_dict[post_ids] = counter

        return comment_count_dict


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


class Data_to_Id:

    def __init__(self, data, ):
        self.data = data

    def tiangge_id(self):
        id_data = tiangge_id_grab(self.data['tiangge_name'])
        for id_tiangge in id_data:
            id_tiangge = id_tiangge
        return id_tiangge

    def user_interacted_id(self):
        id_data = username_id_grab(self.data['interacting_username'])
        for id_user in id_data:
            id_user = id_user
        return id_user

    def user_id(self):
        id_data = username_id_grab(self.data['uploader_username'])
        for id_user in id_data:
            id_user = id_user
        return id_user

    def post_id(self):
        id_data = post_id_grab(self.data['post_title'], self.user_id(), self.data['post_date_created'])
        for id_post in id_data:
            id_post = id_post
        return id_post


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
    posts_submitted = select_post_with_user_id(profile_data.profile_name_to_id()['id'])
    user_mask = profile_data.mask_post_id_profile()

    # content checker
    if bool(posts_submitted):
        submit_content = 'True'
    else:
        submit_content = 'False'

    if not user_logged:
        post_user_privileges = 'Not allowed'

    elif user_logged:
        if session['user'] == profile_name:
            post_user_privileges = 'Allowed'
        else:
            post_user_privileges = 'Not allowed'

    return render_template('/profiles/submitted.html', profile_data=profile_data, posts_submitted=posts_submitted,
                           user_logged=user_logged, profile_name=profile_name,
                           post_user_privileges=post_user_privileges,
                           submit_content=submit_content, legal_extensions_img=legal_extensions_img,
                           legal_extensions_vid=legal_extensions_vid, user_mask=user_mask)


@app.route('/u/<profile_name>/liked')
def profile_liked(profile_name):
    user_logged = user_log()

    if user_logged:
        # main content
        profile_data = Profile_Data(profile_name)
        posts_liked = select_post_approval_with_user_id(profile_data.profile_name_to_id()['id'])
        user_mask = profile_data.mask_post_id_approvals()

        # content checker
        if bool(posts_liked):
            liked_content = 'True'
        else:
            liked_content = 'False'

        return render_template('/profiles/liked.html', profile_data=profile_data, user_logged=user_logged,
                               posts_liked=posts_liked, liked_content=liked_content,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask, )
    else:
        visited_profile_split = request.referrer.strip("/liked")
        return redirect(visited_profile_split)


@app.route('/u/<profile_name>/disliked')
def profile_disliked(profile_name):
    user_logged = user_log()

    if user_logged:

        # main content
        profile_data = Profile_Data(profile_name)
        posts_disliked = select_post_approval_with_user_id(profile_data.profile_name_to_id()['id'])
        user_mask = profile_data.mask_post_id_approvals()

        # content checker
        if bool(posts_disliked):
            disliked_content = 'True'
        else:
            disliked_content = 'False'

        return render_template('/profiles/disliked.html', profile_data=profile_data, user_logged=user_logged,
                               posts_disliked=posts_disliked, disliked_content=disliked_content,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask)
    else:
        visited_profile_split = request.referrer.strip("/disliked")
        return redirect(visited_profile_split)


@app.route('/u/<profile_name>/saved')
def profile_saved(profile_name):
    user_logged = user_log()

    if user_logged:
        # main content
        profile_data = Profile_Data(profile_name)
        posts_saved = select_post_saved_with_user_id(profile_data.profile_name_to_id()['id'])
        user_mask = profile_data.users_approval_in_others()['masked_saved_posts_ids']

        # content checker
        if bool(posts_saved):
            saved_content = 'True'
        else:
            saved_content = 'False'

        return render_template('/profiles/saved.html', profile_data=profile_data, user_logged=user_logged,
                               posts_saved=posts_saved, saved_content=saved_content,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask, )
    else:
        visited_profile_split = request.referrer.strip("/saved")
        return redirect(visited_profile_split)


@app.route('/u/<profile_name>/hidden')
def profile_hidden(profile_name):
    user_logged = user_log()

    if user_logged:
        # main content
        profile_data = Profile_Data(profile_name)
        posts_hidden = select_hidden_post_with_user_id(profile_data.profile_name_to_id()['id'])
        user_mask = profile_data.users_approval_in_others()['masked_hidden_posts_ids']

        # content checker
        if bool(posts_hidden):
            hidden_content = 'True'
        else:
            hidden_content = 'False'

        return render_template('/profiles/hidden.html', profile_data=profile_data, user_logged=user_logged,
                               posts_hidden=posts_hidden, hidden_content=hidden_content,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               user_mask=user_mask, )
    else:
        visited_profile_split = request.referrer.strip("/saved")
        return redirect(visited_profile_split)


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
        profile_data = Profile_Data(session['user'])
        user_ids = username_id_grab(session['user'])

        for user_id in user_ids:
            user_id = user_id

        user_saved = users_saved(user_id, name)
        approvals_again = users_approvals(user_id, name)
        approval_list = slct_pvt_pprvl_sr(user_id)
        pvt_pprvl_tngg_pst = slct_pvt_pprvl_tngg_pst(tiangge_data.tiangge_name_to_id()['id'])

        return render_template('tiangge.html', tiangge_name=tiangge_name, user_id=user_id,
                               tiangge_data=tiangge_data, user_logged=user_logged, profile_data=profile_data,
                               approval_list=approval_list, post_mask=post_mask,
                               legal_extensions_img=legal_extensions_img, legal_extensions_vid=legal_extensions_vid,
                               tiangge_posts=tiangge_posts, pvt_pprvl_tngg_pst=pvt_pprvl_tngg_pst,
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


@app.route('/t/<name>/<hexcd>/<title>/cntnt_pprvl', methods=['POST'])
def cntnt_pprvl_process(name, hexcd, title):
    # Redo user and post id inputs by running a loop here
    # html users can view ids in front end
    # not good practice

    user_data = Data_to_Id(request.form)
    tiangge_id = user_data.tiangge_id()
    user_id = user_data.user_id()
    interacting_user_id = user_data.user_interacted_id()
    post_id = user_data.post_id()
    date = datetime.now().strftime('%a %b %d %Y %X')

    approval_data = {
        'id': post_id,
    }

    pvt_approval_data = {
        'user_id': interacting_user_id,
        'post_id': post_id,
        'date_approval': date,
    }

    if 'user' in session:

        usrs_pprvls = slct_spcfc_pvt_pprvl_sr(interacting_user_id, post_id)
        pvt_chckr = bool(usrs_pprvls)

        if pvt_chckr == True:
            for pprvls in usrs_pprvls:
                if pprvls['approval_type'] == 1:

                    if request.form['approval'] == 'approve':

                        approval_data['like'] = int(request.form['approval_like']) - 1
                        approval_data['dislike'] = int(request.form['approval_dislike'])
                        approval_data['total'] = approval_data['like'] - approval_data['dislike']
                        if approval_data['total'] == 0:
                            approval_data['ratio'] = '0%'
                        else:
                            approval_data['ratio'] = f"{(approval_data['like'] / (approval_data['total'])):.0%}"

                        update_post_approval(approval_data)

                        delete_pvt_approval_user(interacting_user_id, post_id)

                    if request.form['approval'] == 'disapprove':

                        approval_data['like'] = int(request.form['approval_like']) - 1
                        approval_data['dislike'] = int(request.form['approval_dislike']) + 1
                        approval_data['total'] = approval_data['like'] - approval_data['dislike']
                        if approval_data['total'] == 0:
                            approval_data['ratio'] = '0%'
                        else:
                            approval_data['ratio'] = f"{(approval_data['like'] / (approval_data['total'])):.0%}"

                        update_post_approval(approval_data)

                        pvt_approval_data['approval_type'] = 0

                        update_pvt_approval_user(pvt_approval_data)

                elif pprvls['approval_type'] == 0:

                    if request.form['approval'] == 'approve':

                        approval_data['like'] = int(request.form['approval_like']) + 1
                        approval_data['dislike'] = int(request.form['approval_dislike']) - 1
                        approval_data['total'] = approval_data['like'] - approval_data['dislike']
                        if approval_data['total'] == 0:
                            approval_data['ratio'] = '0%'
                        else:
                            approval_data['ratio'] = f"{(approval_data['like'] / (approval_data['total'])):.0%}"

                        update_post_approval(approval_data)

                        pvt_approval_data['approval_type'] = 1

                        update_pvt_approval_user(pvt_approval_data)

                    if request.form['approval'] == 'disapprove':

                        approval_data['like'] = int(request.form['approval_like'])
                        approval_data['dislike'] = int(request.form['approval_dislike']) - 1
                        approval_data['total'] = approval_data['like'] - approval_data['dislike']
                        if approval_data['total'] == 0:
                            approval_data['ratio'] = '0%'
                        else:
                            approval_data['ratio'] = f"{(approval_data['like'] / (approval_data['total'])):.0%}"

                        update_post_approval(approval_data)

                        delete_pvt_approval_user(interacting_user_id, post_id)

        elif pvt_chckr == False:
            if request.form['approval'] == 'approve':

                approval_data['like'] = int(request.form['approval_like']) + 1
                approval_data['dislike'] = int(request.form['approval_dislike'])
                approval_data['total'] = approval_data['like'] - approval_data['dislike']
                approval_data[
                    'ratio'] = f"{(approval_data['like'] / (approval_data['like'] + approval_data['dislike'])):.0%}"

                update_post_approval(approval_data)

                pvt_approval_data['approval_type'] = 1

                insert_pvt_approval_user(pvt_approval_data)

            elif request.form['approval'] == 'disapprove':

                approval_data['like'] = int(request.form['approval_like'])
                approval_data['dislike'] = int(request.form['approval_dislike']) + 1
                approval_data['total'] = approval_data['like'] - approval_data['dislike']
                approval_data[
                    'ratio'] = f"{(approval_data['like'] / (approval_data['like'] + approval_data['dislike'])):.0%}"

                update_post_approval(approval_data)

                pvt_approval_data['approval_type'] = 0

                insert_pvt_approval_user(pvt_approval_data)

        return redirect(request.referrer)

    elif 'user' not in session:

        return redirect(url_for('login', ))


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
    approval_type = 1

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
    if 'user' in session:
        user_data = Data_to_Id(request.form)
        date = datetime.now().strftime('%a %b %d %Y %X')

        pvt_data = {
            'tiangge_id': user_data.tiangge_id(),
            'post_id': user_data.post_id(),
            'user_id': user_data.user_id(),
            'date_saved': date,
        }

        insert_pvt_saved_post_user(pvt_data)
        return redirect(request.referrer)

    elif 'user' not in session:
        return redirect(url_for('login'))


@app.route('/unsave_post_process', methods=['POST'])
def unsave_post_process():
    user_data = Data_to_Id(request.form)
    user_id = user_data.user_id()
    post_id = user_data.post_id()

    delete_pvt_saved_post_user(user_id, post_id)
    return redirect(request.referrer)


@app.route('/hide_post_process', methods=['POST'])
def hide_post_process():
    if 'user' in session:
        user_data = Data_to_Id(request.form)
        date = datetime.now().strftime('%a %b %d %Y %X')

        pvt_data = {
            'tiangge_id': user_data.tiangge_id(),
            'post_id': user_data.post_id(),
            'user_id': user_data.user_id(),
            'date_hidden': date,
        }

        insert_pvt_hidden_post_user(pvt_data)
        return redirect(request.referrer)

    elif 'user' not in session:
        return redirect(url_for('login'))


@app.route('/unhide_post_process', methods=['POST'])
def unhide_post_process():
    user_data = Data_to_Id(request.form)
    user_id = user_data.user_id()
    post_id = user_data.post_id()

    delete_pvt_hidden_post_user(user_id, post_id)
    return redirect(request.referrer)


@app.route('/report_post_process', methods=['POST'])
def report_post_process():
    report_data = defaultdict(dict)
    user_data = Data_to_Id(request.form)

    report_data = {
        'date_created': datetime.now().strftime('%a %b %d %Y %X'),
        'user_id': user_data.user_id(),
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


if __name__ == '__main__':
    app.run(debug=True)
