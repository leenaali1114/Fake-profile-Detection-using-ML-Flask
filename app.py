from flask import Flask, request, render_template, redirect, url_for
import instaloader
import pandas as pd
import numpy as np
import joblib
import urllib.request

app = Flask(__name__)
L = instaloader.Instaloader()

@app.route("/")
def home():
    return render_template('form.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        user = request.form['user']
        return redirect(url_for('success', name=user, action="post"))
    else:   # request.method == 'GET'
        user = request.args.get('user')
        return redirect(url_for('success', name=user, action="get"))

@app.route('/success/<action>/<name>')
def success(name,action):
    numList = ['0','1','2','3','4','5','6','7','8','9']
    profile_list = []
    appInfo = {  # dict
        'result':0,
        'bool_pic': 0,
        'username': 0,
        'fullname': 0,
        'biography': 0,
        'bool_url': 0,
        'private' : 0,
        'post_count' : 0,
        'followers' : 0,
        'followees' : 0
    }

    #--------------------------爬蟲-----------------------------

    url = "https://www.instagram.com/" + name
    
    try:
        status = urllib.request.urlopen(url).code

        #取得目標ig帳號的profile物件
        profile = instaloader.Profile.from_username(L.context, name)

        appInfo['username'] = name

        #profile_image
        pic = profile.profile_pic_url
        if "44884218_345707102882519_2446069589734326272_n.jpg?" in pic:
            bool_pic = 0
            appInfo['bool_pic'] = "No"
        else:
            bool_pic = 1
            appInfo['bool_pic'] = "Yes"
        profile_list.append(bool_pic)

        #nums/len(username)
        counter1 = 0
        for i in name:
            if i in numList:
                counter1 = counter1 + 1;

        digit_username = counter1 / len(name)
        profile_list.append(digit_username)

        #len(fullname)
        fullname = profile.full_name
        profile_list.append(len(fullname))
        appInfo['fullname'] = fullname

        #nums/len(fullname)
        counter2 = 0
        for i in fullname:
            if i in numList:
                counter2 = counter2 + 1;

        if len(fullname) == 0:
            digit_fullname = 0
        else:
            digit_fullname = counter2 / len(fullname)

        profile_list.append(digit_fullname)

        #biography
        biography = profile.biography
        profile_list.append(len(biography))
        appInfo['biography'] = len(biography)

        #URL
        url = profile.external_url
        if url:
            bool_url = 1
            appInfo['bool_url'] = "Yes"
        else:
            bool_url = 0
            appInfo['bool_url'] = "No"
        profile_list.append(bool_url)

        #private
        if profile.is_private == True:
            private = 1
            appInfo['private'] = "Yes"
        else:
            private = 0
            appInfo['private'] = "No"
        profile_list.append(private)

        #post_count
        post_count = profile.get_posts().count
        profile_list.append(post_count)
        appInfo['post_count'] = post_count

        #followers
        followers = profile.followers
        profile_list.append(followers)
        appInfo['followers'] = followers

        #followees
        followees = profile.followees
        profile_list.append(followees)
        appInfo['followees'] = followees

        loaded_model = joblib.load('Random_model')
        arr = np.array(profile_list).reshape(1, -1)

        result = loaded_model.predict(arr)
        if result == 1:
            appInfo['result'] = "This might be a FAKE account!"
        else:
            appInfo['result'] = "This might be a REAL account!"

        return render_template('page.html', appInfo=appInfo)
    
    except Exception:
        appInfo['result'] = "This account is not found!"
        return render_template('page.html', appInfo=appInfo)

if __name__ == "__main__":
    app.run()
