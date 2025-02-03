# -*- coding: utf-8 -*-
"""CODE.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g3Vk1MnLHW6XMRkpVWTwiBnWUeQ7h6ul

# US AIRLINE TWITTER SENTIMENT ANALYSIS

>**Libraries Required**
>
> - numpy
>
> - pandas
>
> - imblearn
>
> - sklearn (scikit-learn)
>
> - keras
>
> - copy
>
> - re
>
> - nltk
>
> - itertools
>
> - wordcloud
>
> - matplotlib
>
> - seaborn
>
> - warnings

Import Required Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')
import random
random.seed(1234)
!pip install sklearn
import sklearn
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
import numpy as np
import seaborn as sns
import re
import nltk
!pip install nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from wordcloud import WordCloud,STOPWORDS
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
# %matplotlib inline
#!pip install sklearn.model_selection.cross_validate
#sklearn.model_selection.cross_validate
from sklearn.model_selection import train_test_split
import numpy as np
import seaborn as sns
import re

"""Import Tweets Dataset to a pandas Dataframe"""

tweet= pd.read_csv("Tweets5.csv")
df = pd.read_csv('Tweets5.csv')
df

count_plot = sns.countplot(data = df,
                           y = 'airline_sentiment')
count_plot.bar_label(count_plot.containers[0])
plt.show()

colors=sns.color_palette("husl", 10)
pd.Series(tweet["airline_sentiment"]).value_counts().plot(kind="pie",colors=colors,
    labels=["negative", "neutral", "positive"],explode=[0.05,0.02,0.04],
    shadow=True,autopct='%.2f', fontsize=12,figsize=(6, 6),title = "Total Tweets for Each Sentiment")

#Plotting the number of tweets each airlines has received
colors=sns.color_palette("husl", 10) 
pd.Series(tweet["airline"]).value_counts().plot(kind = "bar",
                        color=colors,figsize=(8,6),fontsize=10,rot = 0, title = "Total No. of Tweets for each Airlines")
plt.xlabel('Airlines', fontsize=10)
plt.ylabel('No. of Tweets', fontsize=10)

air_senti=pd.crosstab(tweet.airline, tweet.airline_sentiment)
air_senti

percent=air_senti.apply(lambda a: a / a.sum() * 100, axis=1)
percent

pd.crosstab(index = tweet["airline"],columns = tweet["airline_sentiment"]).plot(kind='bar',
                figsize=(10, 6),alpha=0.5,rot=0,stacked=True,title="Airline Sentiment")

percent.plot(kind='bar',figsize=(10, 6),alpha=0.5,
                rot=0,stacked=True,title="Airline Sentiment Percentage")

"""From the graph it is clear that the dataset is class imbalanced. Hence we use Random Oversampling Technique to balance the data"""

from imblearn.over_sampling import *

X = df[['text','tweet_id']]
y = df['airline_sentiment']

ros = RandomOverSampler(random_state=0)
X_resampled, y_resampled = ros.fit_resample(X, y)

df = X_resampled.join(y_resampled)

df

"""Visualizing the results"""

count_plot = sns.countplot(data = df,
                           y = 'airline_sentiment')
count_plot.bar_label(count_plot.containers[0])
plt.show()

df.drop(df[df['airline_sentiment'] == 2].index, inplace = True)
df = df.reset_index()
df = df.drop('index', 1)

#for col in df.columns:
#    print(col)

df.head()

df.airline_sentiment.unique()

"""In the below line of code, we have duplicated the dataframe to use for Machine Learning Model Training. We have done this because when we experienced variable data type clash after Exploratory Data Analysis"""

from copy import deepcopy
df2 = deepcopy(df)

labels = df.airline_sentiment.unique()

count_plot = sns.countplot(data = df,
                           y = 'airline_sentiment')
count_plot.bar_label(count_plot.containers[0])
plt.show()

"""We Observe that there are more number of tweets in the class """

plt.pie(df["airline_sentiment"].value_counts(),
        labels=labels,
        autopct="%1.0f%%",
        startangle=90,
        explode=tuple([0.1] * len(labels)))
plt.show()

count = df.airline_sentiment.value_counts()
count.name = "Count"

percent = df.airline_sentiment.value_counts(normalize=True)
percent.name = "Percentage"

display(pd.concat([count, percent], axis=1))

df_pro = df[df.airline_sentiment == 1]
df_neutral = df[df.airline_sentiment == 0]
df_anti = df[df.airline_sentiment == -1]

df.text.str.len().describe()

sns.distplot(df.text.str.len())

plt.show()

""">**Tweet Stats**
>
>Largest Tweet: 623 character
>
>Shortest Tweet: 7 characters
>
>Average Length is 120 characters
"""

plt.figure(figsize=(10, 10))
sns.boxplot(x="airline_sentiment", y = df["text"].str.len(), data=df)
plt.title("Tweet Length Distribution for each Sentiment")
plt.show()

import re
import nltk
import itertools

"""Finding few most frequent words for all three classes"""

top20 = {}


for sentiment, group in df.groupby("airline_sentiment"):
    freq_words = group["text"].apply(lambda tweet: re.findall(r"#(\w+)", tweet))
    freq_words = itertools.chain(*freq_words)
    freq_words = [ht.lower() for ht in freq_words]
    
    frequency = nltk.FreqDist(freq_words)
    
    df_freq_words = pd.DataFrame({
        "freq_words": list(frequency.keys()),
        "counts": list(frequency.values()),
    })
    top20_htags = df_freq_words.nlargest(20, columns=["counts"])
    
    top20[sentiment] = top20_htags.reset_index(drop=True)

display(pd.concat(top20, axis=1))

"""Visualize the frequent words and frequency"""

fig, axes = plt.subplots(3, 1, figsize=(35, 50))
counter = 0

for airline_sentiment, top in top20.items():
    sns.barplot(data=top, 
                y="freq_words", 
                x="counts", 
                ax=axes[counter],
               palette = 'flare')
    axes[counter].set_title(f"Most frequent words reflecting class {airline_sentiment}", fontsize=35)
    counter += 1
plt.show()

from sklearn.feature_extraction.text import CountVectorizer

frequency = {}

by_sentiment = df.groupby("airline_sentiment")
for sentiment, group in df.groupby("airline_sentiment"):
    cv = CountVectorizer(stop_words="english")
    words = cv.fit_transform(group["text"])
    
    n_words = words.sum(axis=0)
    word_freq = [(word, n_words[0, idx]) for word, idx in cv.vocabulary_.items()]
    word_freq = sorted(word_freq, key=lambda x: x[1], reverse=True)
    
    freq = pd.DataFrame(word_freq, columns=["word", "freq"])
    
    frequency[sentiment] = freq.head(n=25)

to_view = pd.concat(frequency, axis=1).head(n=25)
display(to_view)

import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
nltk.download('punkt')


def clean_text(d):
    d = d.lower()
    
    to_del = [
        r"@[\w]*",  # strip account mentions
        r"http(s?):\/\/.*\/\w*",  # strip URLs
        r"#\w*",  # strip hashtags
        r"\d+",  # delete numeric values
        r"U+FFFD",  # remove the "character note present" diamond
    ]
    for key in to_del:
        d = re.sub(key, "", d)
    
    # strip punctuation and special characters
    d = re.sub(r"[,.;':@#?!\&/$]+\ *", " ", d)
    # strip excess white-space
    d = re.sub(r"\s\s+", " ", d)
    
    return d.lstrip(" ")

def clean_stopword(d):
    stop_words = stopwords.words('english')
    return " ".join([w.lower() for w in d.split() if w.lower() not in stop_words and len(w) > 1])

def tokenize(d):
    return word_tokenize(d)

df['final_text']= df.text.apply(clean_text).apply(clean_stopword).apply(tokenize)
df.final_text.head()

df['final_text']= df.text.apply(clean_text).apply(clean_stopword).apply(tokenize)
df.final_text.head()

"""Use Vader Analyser to analyse sentiment analysis"""

df['text_for_freq_cal']=df.text.apply(clean_text).apply(clean_stopword)

frequency = {}

by_sentiment = df.groupby("airline_sentiment")
for sentiment, group in df.groupby("airline_sentiment"):
    cv = CountVectorizer(stop_words="english")
    words = cv.fit_transform(group["text_for_freq_cal"])
    
    n_words = words.sum(axis=0)
    word_freq = [(word, n_words[0, idx]) for word, idx in cv.vocabulary_.items()]
    word_freq = sorted(word_freq, key=lambda x: x[1], reverse=True)
    
    freq = pd.DataFrame(word_freq, columns=["word", "freq"])
    
    frequency[sentiment] = freq.head(n=25)

to_view = pd.concat(frequency, axis=1).head(n=25)
display(to_view)

nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()
vader.polarity_scores(" ".join(df.final_text[0]))

texts = ' '
for i in range(5):
    print(df.final_text[i])

texts = [" ".join(df.final_text[i]) for i in range(len(df))]

print(df.text_for_freq_cal[0])
print(texts[0])
print(vader.polarity_scores(texts[0]), f'--> Class as per dataset: {df.airline_sentiment[0]}', '\n')

print(df.text_for_freq_cal[4])
print(texts[4])
print(vader.polarity_scores(texts[4]), f'--> Class as per dataset: {df.airline_sentiment[4]}', '\n')
                                                                    
print(df.text_for_freq_cal[5])
print(texts[5])
print(vader.polarity_scores(texts[5]), f'--> Class as per dataset: {df.airline_sentiment[5]}', '\n')
print(df.text_for_freq_cal[15])
print(texts[15])
print(vader.polarity_scores(texts[15]), f'--> Class as per dataset: {df.airline_sentiment[15]}', '\n')
print(df.text_for_freq_cal[20])
print(texts[20])
print(vader.polarity_scores(texts[20]), f'--> Class as per dataset: {df.airline_sentiment[20]}', '\n')
print(df.text_for_freq_cal[25])
print(texts[25])
print(vader.polarity_scores(texts[25]), f'--> Class as per dataset: {df.airline_sentiment[25]}', '\n')
print(df.text_for_freq_cal[30])
print(texts[30])
print(vader.polarity_scores(texts[30]), f'--> Class as per dataset: {df.airline_sentiment[30]}', '\n')
print(df.text_for_freq_cal[35])
print(texts[35])
print(vader.polarity_scores(texts[35]), f'--> Class as per dataset: {df.airline_sentiment[35]}', '\n')
print(df.text_for_freq_cal[40])
print(texts[40])
print(vader.polarity_scores(texts[40]), f'--> Class as per dataset: {df.airline_sentiment[40]}', '\n')
print(df.text_for_freq_cal[45])
print(texts[45])
print(vader.polarity_scores(texts[45]), f'--> Class as per dataset: {df.airline_sentiment[45]}', '\n')
print(df.text_for_freq_cal[55])
print(texts[55])
print(vader.polarity_scores(texts[55]), f'--> Class as per dataset: {df.airline_sentiment[55]}', '\n')

print(df.text_for_freq_cal[10])
print(texts[10])
print(vader.polarity_scores(texts[10]), f'--> Class as per dataset: {df.airline_sentiment[10]}', '\n')

print(df.text_for_freq_cal[50])
print(texts[50])
print(vader.polarity_scores(texts[50]), f'--> Class as per dataset: {df.airline_sentiment[50]}', '\n')

print(df.text_for_freq_cal[100])
print(texts[100])
print(vader.polarity_scores(texts[100]), f'--> Class as per dataset: {df.airline_sentiment[100]}', '\n')

print(df.text_for_freq_cal[500])
print(texts[500])
print(vader.polarity_scores(texts[500]), f'--> Class as per dataset: {df.airline_sentiment[500]}', '\n')

print(df.text_for_freq_cal[1000])
print(texts[1000])
print(vader.polarity_scores(texts[1000]), f'--> Class as per dataset: {df.airline_sentiment[1000]}', '\n')

from wordcloud import WordCloud

#visualization using wordcloud for the negative tweets
df=tweet[tweet['airline_sentiment']=='negative']

words = ' '.join(df['text'])
cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and word != 'RT'])

wordcloud = WordCloud(stopwords=STOPWORDS,
                      background_color='black',
                      width=3000,
                      height=2500
                     ).generate(cleaned_word)

plt.figure(1,figsize=(12, 12))
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

#visualization using wordcloud for the positive tweets
df=tweet[tweet['airline_sentiment']=='positive']

words = ' '.join(df['text'])
cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and word != 'RT'])

wordcloud = WordCloud(stopwords=STOPWORDS,
                      background_color='black',
                      width=3000,
                      height=2500
                     ).generate(cleaned_word)

plt.figure(1,figsize=(12, 12))
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

#visualization using wordcloud for the nuetral tweets
df=tweet[tweet['airline_sentiment']=='neutral']

words = ' '.join(df['text'])
cleaned_word = " ".join([word for word in words.split()
                            if 'http' not in word
                                and not word.startswith('@')
                                and word != 'RT'])

wordcloud = WordCloud(stopwords=STOPWORDS,
                      background_color='black',
                      width=3000,
                      height=2500
                     ).generate(cleaned_word)

plt.figure(1,figsize=(12, 12))
plt.imshow(wordcloud)
plt.axis('off')
plt.show()

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.naive_bayes import MultinomialNB as MNB
from sklearn.naive_bayes import ComplementNB as CNB
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.svm import SVC as SVC
from sklearn.linear_model import LogisticRegression as LGR
from sklearn.metrics import *

import warnings
warnings.filterwarnings('ignore')

df2.head()

from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Bidirectional,Embedding, Dropout, Conv1D, MaxPooling1D
from keras.preprocessing.text import Tokenizer
!pip install keras
!pip install pad_sequences
import keras
from keras.utils import pad_sequences
from keras.utils.vis_utils import plot_model
from keras.callbacks import EarlyStopping

from keras.metrics import Precision, Recall

from sklearn.model_selection import train_test_split

import re
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
nltk.download('punkt')
def tweet_to_words(raw_tweet):
    letters_only = re.sub("[^a-zA-Z]", " ",raw_tweet) 
    words = letters_only.lower().split()                             
    stops = set(stopwords.words("english"))                  
    meaningful_words = [w for w in words if not w in stops] 
    return( " ".join( meaningful_words )) 
def clean_tweet_length(raw_tweet):
    letters_only = re.sub("[^a-zA-Z]", " ",raw_tweet) 
    words = letters_only.lower().split()                             
    stops = set(stopwords.words("english"))                  
    meaningful_words = [w for w in words if not w in stops] 
    return(len(meaningful_words))

tweet['sentiment']=tweet['airline_sentiment'].apply(lambda x: 0 if x=='negative' else 1)
tweet.sentiment.head()

#Splitting the data into train and test and validation
tweet['clean_tweet']=tweet['text'].apply(lambda x: tweet_to_words(x))
tweet['Tweet_length']=tweet['text'].apply(lambda x: clean_tweet_length(x))
train,test = train_test_split(tweet,test_size=0.1,random_state=42)
train,val = train_test_split(tweet,train_size=0.9,random_state=42)

train_clean_tweet=[]
val_clean_tweet=[] #temp code
for tweets in train['clean_tweet']:
    train_clean_tweet.append(tweets)
test_clean_tweet=[]
for tweets in val['clean_tweet']:
    val_clean_tweet.append(tweets)
for tweets in test['clean_tweet']:
    test_clean_tweet.append(tweets)

from sklearn.feature_extraction.text import CountVectorizer
v = CountVectorizer(analyzer = "word")
train_features= v.fit_transform(train_clean_tweet)
test_features=v.transform(test_clean_tweet)

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.metrics import accuracy_score

Classifiers = [
    LogisticRegression(C=0.000000001,solver='liblinear',max_iter=200),
    KNeighborsClassifier(3),
    SVC(kernel="rbf", C=0.025, probability=True),
    DecisionTreeClassifier(),
    RandomForestClassifier(n_estimators=200),
    AdaBoostClassifier(),
    GaussianNB()]

#using validation data to find prameters to get best accuracy
from sklearn.feature_extraction.text import CountVectorizer
v = CountVectorizer(analyzer = "word")
train_features= v.fit_transform(train_clean_tweet)
val_features=v.transform(val_clean_tweet)

dense_features=train_features.toarray()
dense_val= val_features.toarray()
Accuracy=[]
Model=[]
for classifier in Classifiers:
    try:
        fit = classifier.fit(train_features,train['sentiment'])
        pred = fit.predict(val_features)
    except Exception:
        fit = classifier.fit(dense_features,train['sentiment'])
        pred = fit.predict(dense_val)
    accuracy = accuracy_score(pred,val['sentiment'])
    Accuracy.append(accuracy)
    Model.append(classifier.__class__.__name__)
    print('Accuracy of '+classifier.__class__.__name__+' is '+str(accuracy))
    print(classifier.__class__.__name__)
    print(classification_report(pred,test['sentiment']))

Index = [1,2,3,4,5,6,7]
plt.bar(Index,Accuracy)
plt.xticks(Index, Model, rotation=45)
plt.ylabel('Accuracy')
plt.xlabel('Model')
plt.title('Accuracies of Models')

#using trained model on test data
dense_features=train_features.toarray()
dense_test= test_features.toarray()
Accuracy=[]
Model=[]
for classifier in Classifiers:
    try:
        fit = classifier.fit(train_features,train['sentiment'])
        pred = fit.predict(test_features)
    except Exception:
        fit = classifier.fit(dense_features,train['sentiment'])
        pred = fit.predict(dense_test)
    accuracy = accuracy_score(pred,test['sentiment'])
    Accuracy.append(accuracy)
    Model.append(classifier.__class__.__name__)
    print('Accuracy of '+classifier.__class__.__name__+' is '+str(accuracy))
    print(classifier.__class__.__name__)
    print(classification_report(pred,test['sentiment']))

Index = [1,2,3,4,5,6,7]
plt.bar(Index,Accuracy)
plt.xticks(Index, Model, rotation=45)
plt.ylabel('Accuracy')
plt.xlabel('Model')
plt.title('Accuracies of Models')