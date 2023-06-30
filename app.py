from flask import Flask, request, render_template, redirect, url_for
import instaloader
import pandas as pd
import numpy as np
import joblib
import urllib.request
import pickle
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
L = instaloader.Instaloader()


 
  
app.secret_key = 'xyzsdfg'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Leejianah@123'
app.config['MYSQL_DB'] = 'fake'
  
mysql = MySQL(app)

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/insta")
def insta():
    return render_template('form.html')

@app.route("/")
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Logged in successfully !'
            return render_template('home.html', mesage = mesage)
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('login.html', mesage = mesage)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage = mesage)



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

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

def ValuePredictor(to_predict_list): 
    to_predict = np.array(to_predict_list).reshape(1, 7) 
    loaded_model = pickle.load(open("model.pkl", "rb")) 
    result = loaded_model.predict(to_predict) 
    print(result[0])
    return result[0]

@app.route('/matrimony', methods = ['GET','POST']) 
def result():
    prediction = 'Enter data to predict'
    dictionary = {'caste1': {'96K Kokanastha': 0, 'Ad Dharmi': 1, 'Adi Andhra': 2, 'Adi Dravida': 3, 'Adi Karnataka': 4, 'Agarwal': 5, 'Agnikula Kshatriya': 6, 'Agri': 7, 'Ahom': 8, 'Ambalavasi': 9, 'Amil Sindhi': 10, 'Araya': 11, 'Arekatica': 12, 'Arora': 13, 'Arora,Punjabi': 14, 'Arunthathiyar': 15, 'Arya Vysya': 16, 'Aryasamaj': 17, 'Ayyaraka': 18, 'Badaga': 19, 'Bahi': 20, 'Baibhand Sindhi': 21, 'Baidya': 22, 'Baishnab': 23, 'Baishya': 24, 'Balija': 25, 'Balija/Kapu/Kapu Naidu/Naidu/Setti Balija/Settibalija': 26, 'Banik': 27, 'Baniya': 28, 'Banjara': 29, 'Banjara,Lambani': 30, 'Barujibi': 31, 'Bengali': 32, 'Bengali,Nepali': 33, 'Bengali,Pal': 34, 'Besta': 35, 'Bhandari': 36, 'Bhatia': 37, 'Bhatia Sindhi': 38, 'Bhatraju': 39, 'Bhavasar Kshatriya': 40, 'Bhavsar': 41, 'Bhovi': 42, 'Bhumihar Brahmin': 43, 'Billava': 44, 'Bishnoi/Vishnoi': 45, 'Boyer': 46, 'Brahmin': 47, 'Brahmin - Anavil': 48, 'Brahmin - Audichya': 49, 'Brahmin - Barendra': 50, 'Brahmin - Barendra ': 51, 'Brahmin - Bengali': 52, 'Brahmin - Bhatt': 53, 'Brahmin - Bhumihar': 54, 'Brahmin - Daivadnya': 55, 'Brahmin - Danua': 56, 'Brahmin - Davadnya': 57, 'Brahmin - Deshastha': 58, 'Brahmin - Dhiman': 59, 'Brahmin - Dixit': 60, 'Brahmin - Dixit ': 61, 'Brahmin - Dravida': 62, 'Brahmin - Garhwali': 63, 'Brahmin - Gaur': 64, 'Brahmin - Goswami/Gosavi': 65, 'Brahmin - Gour': 66, 'Brahmin - Gurukkal': 67, 'Brahmin - Halua':68, 'Brahmin - Havyaka': 69, 'Brahmin - Havyaka ': 70, 'Brahmin - Hoysala': 71, 'Brahmin - Iyengar': 72, 'Brahmin - Iyer': 73, 'Brahmin - Jangid': 74, 'Brahmin - Jangra': 75, 'Brahmin - Jhadua': 76, 'Brahmin - Kanyakubj': 77, 'Brahmin - Karhade': 78, 'Brahmin - Kashmiri Pandit': 79, 'Brahmin - Kokanastha': 80, 'Brahmin - Kulin': 81, 'Brahmin - Kulin ': 82, 'Brahmin - Kumoani': 83, 'Brahmin - Madhwa': 84, 'Brahmin- Maithil': 85, 'Brahmin - Nagar': 86, 'Brahmin - Namboodiri': 87, 'Brahmin - Niyogi': 88, 'Brahmin - Others': 89, 'Brahmin - Panda': 90, 'Brahmin - Pandit': 91, 'Brahmin - Rarhi': 92, 'Brahmin - Rigvedi': 93, 'Brahmin - Rudraj': 94, 'Brahmin - Sakaldwipi': 95, 'Brahmin - Sanadya': 96, 'Brahmin - Saraswat': 97, 'Brahmin - Saryuparin': 98, 'Brahmin - Shivhalli': 99, 'Brahmin - Sikhwal': 100, 'Brahmin - Smartha': 101, 'Brahmin - Sri Vaishnava': 102, 'Brahmin - Sri Vaishnava ': 103, 'Brahmin - Telugu': 104, 'Brahmin - Tyagi': 105, 'Brahmin - Vaidiki': 106, 'Brahmin - Velanadu': 107, 'Brahmin -Gowd Saraswat': 108, 'Brahmin 6000 Niyogi': 109, 'Brahmin Kanada Madhva': 110, 'Brahmin Shivalli': 111, 'Brahmin,Agarwal': 112, 'Brahmin/Agarwal': 113, 'Bunt': 114, 'Bunt (Shetty)': 115, 'CKP': 116, 'Catholic': 117, 'Chambhar': 118, 'Chandraseniya Kayastha Prab': 119, 'Chandravanshi Kahar': 120, 'Chasa': 121, 'Chattada Sri Vaishnava': 122, 'Chaudary': 123, 'Chaurasia': 124, 'Chettiar': 125, 'Chhetri': 126, 'Coorgi': 127, 'Darji': 128, 'Devadiga': 129, 'Devandra Kula Vellalar': 130, 'Devang Koshthi': 131, 'Devanga': 132, 'Devar/Thevar/Mukkulathor': 133, 'Dhangar': 134, 'Dheevara': 135, 'Dhiman': 136, 'Dhoba': 137, 'Dhobi': 138, 'Digambar': 139, 'Dusadh (Paswan)': 140, 'Ediga': 141, 'Ezhava': 142, 'Ezhuthachan': 143, 'Ganda': 144, 'Gandla': 145, 'Ganiga': 146, 'Ganiga/Panicker': 147,
'Garhwali': 148, 'Garhwali Rajput': 149, 'Gavali': 150, 'Gavara': 151, 'Gawali': 152, 'Ghumar': 153, 'Goala': 154, 'Goan': 155, 'Gomantak': 156, 'Gondhali': 157, 'Goswami/Gosavi Brahmin': 158, 'Goud': 159, 'Gounder': 160, 'Gowda': 161, 'Gudia': 162, 'Gujarati': 163, 'Gujjar': 164, 'Gupta': 165, 'Gupta,Baniya,Vaish': 166, 'Gupta/Baniya/Vaish': 167, 'Guptan': 168, 'Gurav': 169, 'Gurjar': 170, 'Himachali/Pahari': 171, 'Hindu': 172, 'Hindu-Others': 173, 'Hugar (Jeer)': 174, 'Intercaste': 175, 'Iyengar': 176, 'Iyer': 177, 'Jaalari': 178, 'Jain-Others': 179, 'Jaiswal': 180, 'Jangam': 181, 'Jat': 182, 'Jatav': 183, 'Jeer': 184, 'Jogi (Nath)': 185, 'Kachara': 186, 'Kadava Patel': 187, 'Kahar':188, 'Kaibarta': 189, 'Kalal': 190, 'Kalar': 191, 'Kalinga Vysya': 192, 'Kalita': 193, 'Kalwar': 194, 'Kamboj': 195, 'Kamma': 196, 'Kannada Mogaveera': 197, 'Kansari': 198, 'Kapu': 199, 'Kapu Naidu': 200, 'Kapu,Kapu Naidu': 201, 'Karana': 202, 'Karmakar': 203, 'Karuneegar': 204, 'Kasar': 205, 'Kashyap': 206, 'Kayastha': 207, 'Keralite': 208, 'Khandayat': 209, 'Khandelwal': 210, 'Kharwar': 211, 'Khatik': 212, 'Khatri': 213, 'Khatri,Punjabi': 214, 'Koiri': 215, 'Koiri,Kushwaha,Maurya': 216, 'Kokanastha Maratha': 217, 'Koli': 218, 'Koli Mahadev': 219, 'Kongu Vellala Gounder': 220, 'Konkani': 221, 'Kori': 222, 'Koshti': 223, 'Kshatriya': 224, 'Kulal': 225, 'Kulalar': 226, 'Kumaoni Rajput':227, 'Kumawat': 228, 'Kumbara': 229, 'Kumbhakar': 230, 'Kumbhar': 231, 'Kumhar': 232, 'Kummari': 233, 'Kunbi': 234, 'Kurmi': 235, 'Kurmi Kshatriya': 236, 'Kuruba': 237, 'Kuruhina Shetty': 238, 'Kurumbar': 239, 'Kushwaha': 240, 'Kushwaha (Koiri)': 241, 'Kutchi': 242, 'Lambadi': 243, 'Lambani': 244, 'Leva Patidar': 245, 'Leva patel': 246, 'Leva patil': 247, 'Lingayath': 248, 'Lodhi Rajput': 249, 'Lohana': 250, 'Lohar': 251, 'Madiga': 252, 'Mahajan': 253, 'Mahar': 254, 'Maharashtrian': 255, 'Mahendra': 256, 'Maheshwari': 257, 'Mahishya': 258, 'Mahisya': 259, 'MahisyaSaurashtra': 260, 'Mala': 261, 'Malayalee': 262, 'Malayalee Namboodiri': 263, 'Mali': 264, 'Mallah': 265, 'Mangalorean': 266, 'Manipuri': 267, 'Mapila': 268, 'Maratha': 269, 'Marvar': 270, 'Marwari': 271, 'Matang': 272, 'Mathur': 273, 'Maurya': 274, 'Meena': 275,
'Meenavar': 276, 'Mehra': 277, 'Menon': 278, 'Mera': 279, 'Meru Darji': 280, 'Mochi': 281, 'Mogaveera': 282, 'MogaveeraSadgope': 283, 'Monchi': 284, 'Mudaliar': 285, 'Mudaliar - Senguntha': 286, 'Mudaliar Arcot': 287, 'Mudaliar Saiva': 288, 'Mudaliyar': 289, 'Mudiraj': 290, 'Mukkulathor': 291, 'Munnuru Kapu': 292, 'Munnuru Kapu,Reddy': 293, 'Muthuraja': 294, 'Nadar': 295, 'Nai': 296, 'Naicker': 297, 'Naidu': 298,
'Naik': 299, 'Naik/Nayaka': 300, 'Nair': 301, 'Nair Vaniya': 302, 'Nair Vaniya,Nair Vilakkithala': 303, 'Nair Vaniya/Nair Vilakkithala': 304, 'Namasudra': 305, 'Nambiar': 306, 'Namboodiri': 307, 'Napit': 308, 'Nayaka': 309, 'Nepali': 310, 'Nhavi': 311, 'OBC/Barber/Naayee': 312, 'Oriya': 313, 'Orthodox': 314, 'OrthodoxMaharashtrian': 315, 'Others': 316, 'Padmasali': 317, 'Padmashali': 318, 'Pal': 319, 'Panchal': 320, 'Panchal,Suthar': 321, 'Panchal/Suthar': 322, 'Pandaram': 323, 'Panicker': 324, 'Parkava Kulam': 325, 'Pasi': 326, 'Patel': 327, 'Patel Kadva': 328, 'Patel Leva': 329, 'Patil': 330, 'Patnaick/Sistakaranam': 331, 'Perika': 332, 'Pillai': 333, 'Prajapati': 334, 'Protestant': 335, 'Punjabi': 336, 'Raigar': 337, 'Rajaka': 338, 'Rajastani': 339, 'Rajbonshi': 340, 'Rajput': 341, 'Rajput Rohella/Tank': 342, 'Ramgariah': 343, 'Ravidasia': 344, 'Rawat': 345, 'Reddy': 346, 'Rohiri Sindhi': 347, 'Sadgope': 348, 'Saha': 349, 'Sahiti Sindhi': 350, 'Sahu': 351, 'Saini': 352, 'Sakkhar Sindhi': 353, 'Saliya': 354, 'Savji': 355, 'Scheduled Caste': 356, 'Scheduled Caste,Gowda': 357, 'Scheduled Caste,Mahar': 358, 'Scheduled Tribe': 359, 'Sehwani Sindhi': 360, 'Senguntha Mudaliyar': 361, 'Setti Balija': 362, 'Settibalija': 363, 'Shah': 364, 'Shetty': 365, 'Shewetamber': 366, 'Shia': 367, 'Shikarpuri Sindhi': 368, 'Shimpi': 369, 'Sia': 370, 'Sikh': 371, 'Sikh ': 372, 'Sikh - Ahluwalia': 373, 'Sikh - Arora': 374, 'Sikh - Bhatia': 375, 'Sikh - Bhatra': 376, 'Sikh - Clean Shaven': 377, 'Sikh - Gursikh': 378, 'Sikh - Intercaste': 379, 'Sikh - Jat': 380, 'Sikh - Kamboj': 381, 'Sikh - Kesadhari': 382, 'Sikh - Khatri': 383, 'Sikh - Kshatriya': 384, 'Sikh - Lubana': 385, 'Sikh - Majabi': 386, 'Sikh - Others': 387, 'Sikh - Rajput': 388, 'Sikh - Ramgharia': 389, 'Sikh - Ravidasia': 390, 'Sikh - Saini': 391, 'Sikh - Tonk Kshatriya': 392, 'Sindhi': 393, 'Sindhi-Amil': 394, 'Sindhi-Baibhand': 395, 'Sindhi-Dadu': 396, 'Sindhi-Hyderabadi': 397, 'Sindhi-Larkana': 398, 'Sindhi-Lohana': 399, 'Sindhi-Rohiri': 400, 'Sindhi-Sahiti': 401, 'Sindhi-Sakkhar': 402, 'Sindhi-Shikarpuri': 403, 'Sindhi-Thatai': 404, 'Somvanshi': 405, 'Sonar': 406, 'Sonar,Soni': 407, 'Soni': 408, 'Sourashtra': 409, 'Sozhiya Vellalar': 410, 'Sugali (Naika)': 411, 'Sunari': 412, 'Sundhi': 413, 'Sunni': 414, 'Sutar': 415, 'Suthar': 416, 'Swakula Sali': 417, 'Swarnakar': 418, 'Tamboli': 419, 'Tamil': 420, 'Tamil Yadava': 421, 'Tantubai': 422, 'Telaga': 423, 'Teli': 424, 'Telugu': 425, 'Thakkar': 426, 'Thakur': 427, 'Thatai Sindhi': 428, 'Thiyya': 429, 'Tili': 430, 'Togata': 431, 'Udayar': 432, 'Uppara': 433, 'Urali Gounder': 434, 'Urs': 435, 'Vaddera': 436, 'Vaish': 437, 'Vaishnav': 438, 'Vaishnav Vania': 439, 'Vaishnav Vanik': 440, 'Vaishya': 441, 'Vaishya Vani': 442, 'Valluvan': 443, 'Valmiki': 444, 'Vania': 445, 'Vaniya': 446, 'Vanjari': 447, 'Vankar': 448, 'Vannar': 449, 'Vannia Kula Kshatriyar': 450, 'Vanniyar': 451, 'Variar': 452, 'Varshney': 453, 'Veera Saivam': 454, 'Velaan/Vellalar': 455, 'Velama': 456, 'Vellalar': 457, 'Veluthedathu Nair': 458, 'Vilakkithala Nair': 459, 'Vishwakarma': 460, 'ViswaBrahmin - Telugu': 461, 'Viswabrahmin': 462, 'Vokkaliga': 463, 'Vysya': 464, 'Yadav': 465}, 'degree': {'10th': 0, '12th': 1, 'Arts/Graphic Designing': 2, 'B.A. (Arts)': 3, 'B.Arch (Architecture)': 4, 'B.Com (Commerce)': 5, 'B.Ed (Education)': 6, 'B.El.Ed (Elementary Education)': 7, 'B.Lib.Sc (Library Sciences)': 8, 'B.P.Ed. (Physical Education)': 9, 'B.Pharm (Pharmacy)': 10, 'B.Plan (Planning)': 11, 'B.Sc (Science)': 12, 'B.V.Sc. (Veterinary Science)': 13, 'BBA/BBM/BBS': 14, 'BCA (Computer Application)': 15, 'BDS (Dental Surgery)': 16, 'BE B.Tech (Engineering)': 17, 'BFA (Fine Arts)': 18, 'BHM (Hotel Management)': 19, 'BHMS (Homeopathy)': 20,
'BL/LLB/BGL (Law)': 21, 'BPT (Physiotherapy)': 22, 'BSW (Social Work)': 23, 'Bachelor of Fashion Technology': 24, 'CA (Chartered Accountant)': 25, 'CFA (Chartered Financial Analyst)': 26, 'CS (Company Secretary)': 27, 'Engineering': 28, 'Fashion/Design': 29, 'ICWA': 30, 'Integrated PG': 31, 'Intermediate': 32, 'LLB': 33, 'Languages': 34, 'M.Arch. (Architecture)': 35, 'M.Com. (Commerce)': 36, 'M.Ed. (Education)': 37, 'M.Lib.Sc. (Library Sciences)': 38, 'M.Pharm. (Pharmacy)': 39, 'M.Phil. (Philosophy)': 40, 'M.Plan. (Planning)': 41, 'M.Sc. (Science)': 42, 'M.Tech': 43, 'MA (Arts)': 44, 'MBA PGDM part time': 45, 'MBA/PGDM': 46, 'MBBS': 47, 'MCA PGDCA part time': 48, 'MCA/PGDCA': 49, 'MD/MS (Medicine)': 50, 'MDS (Master of Dental Surgery)': 51, 'ME/M.Tech/MS (Engg/Sciences)': 52, 'MFA (Fine Arts)': 53, 'ML/LLM (Law)': 54, 'MS': 55, 'MSW (Social Work)': 56, 'Master of Fashion Technology': 57, 'Master of Health Administration': 58, 'Master of Hospital Administration': 59, 'Masters': 60, 'Other Diploma': 61, 'Other Doctorate': 62, 'Other Post Graduation': 63, 'Other School/Graduation': 64, 'Others': 65, 'PG Diploma': 66, 'PGDBM': 67, 'Ph.D. (Doctorate)': 68, 'Undergraduate': 69}, 'employed1': {'Central Government': 0, 'MNC': 1, 'Not Working': 2, 'Others': 3, 'Private Sector': 4, 'Public Sector': 5, 'State Government': 6}, 'income1': {"Don't wish to specify": 0, 'INR 1 lakh to 2 lakhs': 1, 'INR 10 lakhs  to 15 lakhs': 2, 'INR 10 lakhs to 15 lakhs': 3, 'INR 15 lakhs to 20 lakhs': 4, 'INR 2 lakhs to 3 lakhs': 5, 'INR 20 lakhs to 25 lakhs': 6, 'INR 25 lakhs to 30 lakhs': 7, 'INR 3 lakhs to 4 lakhs': 8, 'INR 30 lakhs to 40 lakhs': 9, 'INR 4 lakhs to 5 lakhs': 10, 'INR 40 lakhs to 50 lakhs': 11, 'INR 5 lakhs to 7 lakhs': 12, 'INR 50 lakhs and above': 13, 'INR 50 lakhs and above.': 14, 'INR 50 thousand to 1 lakh': 15, 'INR 7 lakhs to 10 lakhs': 16, 'INR Under 50 thousand': 17}, 'mother1': {'Arabic ': 0, 'Arunachali': 1, 'Assamese': 2, 'Awadhi': 3, 'Badaga': 4, 'Bengali': 5, 'Bhojpuri': 6, 'Bihari': 7, 'Chatisgarhi': 8, 'Coorgi': 9, 'Dhivehi': 10, 'Dogri': 11, 'English': 12, 'Garhwali': 13, 'Garo': 14, 'Gujarati': 15, 'Haryanvi': 16, 'Himachali/Pahari': 17, 'Hindi': 18, 'Kannada': 19, 'Kashmiri': 20, 'Khasi': 21, 'Konkani': 22, 'Kumoani': 23, 'Kutchi': 24, 'Lambani': 25, 'Magahi': 26, 'Maithili': 27, 'Malayalam': 28, 'Manipuri': 29, 'Marathi': 30, 'Marwari': 31, 'Miji': 32, 'Mizo': 33, 'Nepali': 34, 'Oriya': 35, 'Others': 36, 'Pahari': 37, 'Persian': 38, 'Punjabi': 39, 'Pushtu': 40, 'Rajasthani': 41, 'Sanskrit': 42, 'Santhali': 43, 'Sindhi': 44, 'Singhalese': 45, 'Somali': 46, 'Sowrashtra': 47, 'Swedish': 48, 'Tamil': 49, 'Telugu': 50, 'Thadou kuki': 51, 'Tulu': 52, 'Urdu': 53, 'marwari': 54}, 'occupation': {'Admin/Secretarial': 0, 'Advertising/Entertainment/Media': 1, 'Advertising/Entertainment/Media ': 2, 'Advocate': 3, 'Agriculture': 4, 'Animators/Web Designers': 5, 'Architecture/Design': 6, 'Artists/Animators/Web Designers': 7, 'Banking/Insurance/Financial Services': 8, 'Beauty/Fashion/Jewellery Designers': 9, 'Business Owner/Entrepreneur': 10, 'Civil Services/Law Enforcement': 11, 'Civil Services/Law Enforcement/Construction': 12, 'Construction': 13, 'Customer Service/Call Centre/BPO': 14, 'Defence': 15, 'Defence/Management/Corporate Professionals': 16, 'Defence/Merchant Navy': 17, 'Education/Training': 18, 'Electronics': 19, 'Export/Import': 20, 'Finance and Accounts': 21, 'Government Employee': 22, 'Health Care': 23, 'Hotels/Restaurants': 24, 'Human Resource': 25, 'IT': 26, 'Legal': 27, 'Loss Prevention Manager': 28, 'Management/Corporate Professionals': 29, 'Manufacturing/Engineering': 30, 'Manufacturing/Engineering/R&D': 31, 'Marketing and Communications': 32, 'Merchant Navy': 33, 'Non Working': 34, 'Oil/Gas': 35, 'Others': 36, 'Pharmaceutical/Biotechnology': 37, 'Purchase/Logistics/Supply chain': 38, 'Real Estate': 39, 'Retail Chains': 40, 'Sales/Business Development': 41, 'Science': 42, 'Telecom/ISP': 43, 'Travel/Airlines': 44}, 'religion1': {'Buddhist': 0, 'Christian': 1, 'Hindu': 2, 'Jain': 3, 'Muslim': 4, 'Others': 5, 'Sikh': 6}, 'account': {'fake': 0, 'real': 1}}
    castes = list(dictionary['caste1'].keys())
    degrees = list(dictionary['degree'].keys())
    employs = list(dictionary['employed1'].keys())
    incomes = list(dictionary['income1'].keys())
    mothers = list(dictionary['mother1'].keys())
    occs = list(dictionary['occupation'].keys())
    religions = list(dictionary['religion1'].keys())
    if request.method == 'POST': 
        to_predict_list = request.form.to_dict() 
        to_predict_list = list(to_predict_list.values()) 
        to_predict_list = list(map(int, to_predict_list)) 
        result = ValuePredictor(to_predict_list)     
        if int(result)== 0: 
            prediction ='Fake'
        else: 
            prediction ='Real'            
    return render_template("result.html", prediction=prediction,castes=castes,degrees=degrees,employs=employs,incomes=incomes,mothers=mothers,occs=occs,religions=religions)



if __name__ == "__main__":
    app.run(debug=True)
