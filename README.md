

# Install the required Python libraries by (tested under Python 3.10.4)

```
pip install -r requirements.txt
```

# How to use/run the code



<img src="https://i.imgur.com/3wmLYEQ.jpg" width="280" height="250" alt="Model_use"/><br/>



<img src="https://i.imgur.com/SHae8rJ.jpg" width="250" height="150" alt="Features"/><br/>



* **Profile Picture**: User has profile picture or not.

* **Num/Length (Username)**: Ratio of number of numerical characters in username to its length.

* **Num/Length (Fullname)**: Ratio of number of numerical characters in fullname to its length.

* **Fullname words**: How many words are in the fullname?

* **Description Length**: How many characters are in the biography?

* **External URL**: User has external URL or not.

* **Private or not**: User is private or not.

* **Number of Posts**: How many posts does the user have?

* **Number of Followers**: How many followers does the user have?

* **Number of Followees**: How many followees does the user have?

### Training

1. Cross Validation 

   <img src="https://i.imgur.com/GUGUtcY.png" width="180" height="150" alt="Model"/><br/>
   
   RandomForestClassifier 

2. Random Search 

### result

accuracy: 0.925000

precision: 0.932203

recall: 0.916667

confusion matrix:
 [[55  4]
 [ 5 56]]

<img src="https://i.imgur.com/FOWezLR.jpg" width="300" height="250" alt="Result"/><br/>



<img src="https://i.imgur.com/iICVKNj.png" width="270" height="150" alt="GUI"/><br/>

### 判斷結果呈現

<img src="https://i.imgur.com/LuGCAhy.jpg" width="700" height="300" alt="output"/><br/>




<img src="https://i.imgur.com/7F1zgF8.jpg" width="200" height="50" alt="output"/><br/>




# Reference

https://www.kaggle.com/code/khoingo16/predicting-a-fake-instagram-account/notebook
