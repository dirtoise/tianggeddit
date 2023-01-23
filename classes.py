from main import *
from data import *

class Profile_Data:
    def __init__(self, user_name):
        self.user_name = user_name

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
        user_privileges = confirm_pivot_user_tiangge((username_id_grab(self.user_name)['id']), self.tiangge_id)
        for user_privilege in user_privileges:
            if user_privilege['is_subscriber'] == "1":
                return True
            else:
                return False

    def user_mod_privileges(self, tiangge_id):
        self.tiangge_id = tiangge_id
        user_privileges = confirm_pivot_user_tiangge((username_id_grab(self.user_name)['id']), self.tiangge_id)
        for user_privilege in user_privileges:
            if user_privilege['is_moderator'] == "1":
                return True
            else:
                return False

    # profile user's subbed tiangges
    def user_tiangges(self):
        tiangge_list = []
        user_tiangge = slct_sr_tngg((username_id_grab(self.user_name)['id']))
        for data in user_tiangge:
            tiangge_list.append(data['name'])
        return tiangge_list

    def user_approved(self):
        user_approval_dict = defaultdict(dict)
        current_user_approval = slct_pvt_pprvl_sr(username_id_grab(self.user_name)['id'])

        user_posts = slct_pvt_pprvl_sr(username_id_grab(self.user_name)['id'])

        for post in user_posts:
            user_approval_dict[post['post_id']] = 3

            for user_data in current_user_approval:
                if user_data['post_id'] == post['post_id']:
                    user_approval_dict[user_data['post_id']] = user_data['approval_type']

        return user_approval_dict

    # all of the likes of the user inclu post information
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

        current_user_post_data = slct_pvt_hx_tngg_pst_w_sr((username_id_grab(self.user_name)['id']))

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
        current_user_saved_post = slct_pvt_svd_pst_sr((username_id_grab(self.user_name)['id']))
        user_approvals = slct_pvt_svd_pst_sr((username_id_grab(self.user_name)['id']))

        for post in user_approvals:

            user_saved_dict[post['post_id']] = 'Unsaved'

            for user_data in current_user_saved_post:

                if user_data['post_id'] == post['post_id']:
                    user_saved_dict[user_data['post_id']] = 'Saved'

        return user_saved_dict

    def user_hidden(self):
        user_hidden_dict = defaultdict(dict)
        current_user_hidden_post = slct_pvt_hddn_pst_sr((username_id_grab(self.user_name)['id']))
        user_approvals = slct_pvt_hddn_pst_sr((username_id_grab(self.user_name)['id']))

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

        user_posts = slct_pvt_hx_tngg_pst_w_sr((username_id_grab(self.user_name)['id']))

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
            posts_ids[post['post_id']] = rand_mask()

        return posts_ids

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

    def data_tiangge_date_created(self):
        tiangge_data = select_tiangge_with_id(self.tiangge_name_to_id()['id'])
        for date_created in tiangge_data:
            date_create = datetime.strptime(date_created['date_created'], '%a %b %d %Y %X').strftime('%b %d %Y')
        return date_create

    def data_tiangge_subscribers(self):
        subscriber_count = 0
        tiangge_data = select_tiangge_with_id(self.tiangge_name_to_id()['id'])
        for subscribers in tiangge_data:
            subscriber_count = subscribers['subscribers']
        if subscriber_count > 1:
            subscriber_count = str(subscriber_count) + " subscribers"
            return subscriber_count
        elif subscriber_count == 1 or subscriber_count == 0:
            subscriber_count = str(subscriber_count) + " subscriber"
            return subscriber_count

    # code for following/blocking other users (make universal)
    def tiangge_user_user_others(self, other_username):
        user_relationships = defaultdict(dict)
        user_data = slct_pvt_sr_sr_thr(username_to_id(session['user']), username_to_id(other_username))
        for data in user_data:
            user_relationships['relationship'] = data['user_relationship']
        return user_relationships

    # current user's approved posts in current tiangge
    def tiangge_user_approvals(self, username, post_id):
        user_approvals_dict = defaultdict(dict)
        user_approved_posts = slct_spcfc_pvt_pprvl_sr(username_id_grab(username)['id'], post_id)
        for data in user_approved_posts:
            user_approvals_dict['approval_type'] = data['approval_type']
        return user_approvals_dict

    # current user's hidden posts in current tiangge
    def tiangge_user_hidden(self, username, post_id):
        user_hidden_dict = defaultdict(dict)
        user_hidden_posts = slct_spcfc_pvt_hddn_pst_sr(username_id_grab(username)['id'], post_id)
        if user_hidden_posts:
            user_hidden_dict['hidden_state'] = "hidden"
        return user_hidden_dict

    def post_data_in_tiangge(self):

        masked_posts_ids = defaultdict(dict)
        tiangge_posts = select_post_with_tiangge(self.tiangge_name_to_id()['id'])

        for post in tiangge_posts:
            masked_posts_ids[post['id']] = rand_mask()

        return masked_posts_ids

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

class CurrentUser_Data:
    def __init__(self, user_name):
        self.user_name = user_name

    # current user's approved posts
    def current_user_approvals(self, post_id):
        user_approvals_dict = defaultdict(dict)
        user_approved_posts = slct_spcfc_pvt_pprvl_sr(username_id_grab(self.user_name)['id'], post_id)
        for data in user_approved_posts:
            user_approvals_dict['approval_type'] = data['approval_type']
        return user_approvals_dict

    # current user's saved posts
    def current_user_saved(self, post_id):
        user_saved_dict = defaultdict(dict)
        user_saved_posts = slct_spcfc_pvt_svd_pst_sr(username_id_grab(self.user_name)['id'], post_id)
        if user_saved_posts:
            user_saved_dict['saved_state'] = "saved"
        return user_saved_dict

    # current user's hidden posts
    def current_user_hidden(self, post_id):
        user_hidden_dict = defaultdict(dict)
        user_hidden_posts = slct_spcfc_pvt_hddn_pst_sr(username_id_grab(self.user_name)['id'], post_id)
        if user_hidden_posts:
            user_hidden_dict['hidden_state'] = "hidden"
        return user_hidden_dict

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

    def uploader_user_id(self):
        id_data = username_id_grab(self.data['uploader_username'])
        for id_user in id_data:
            id_user = id_user
        return id_user

    def current_user_id(self):
        user_id = username_id_grab(session['user'])
        for id in user_id:
            id = id
        return id

    def post_id(self):
        id_data = post_id_grab(self.data['post_title'], self.uploader_user_id(), self.data['post_date_created'])
        for id_post in id_data:
            id_post = id_post
        return id_post

    def post_id_new(self, post_title, user_id, date_created):
        post_id = post_id_grab(post_title, user_id, date_created)
        for id in post_id:
            id = id
        return id