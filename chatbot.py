import os
import random
import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model


import nltk
from nltk.stem import WordNetLemmatizer

from django.http import HttpResponse

lemmatizer = WordNetLemmatizer()

BASE_DIR = "D:\AdvAssistfinal"
intents_file = os.path.join(os.path.dirname(__file__), 'intents.json')
intents = json.loads(open(intents_file).read())

words = pickle.load(open(os.path.join(BASE_DIR, 'chat', 'words.pkl'), 'rb'))
classes = pickle.load(open(os.path.join(BASE_DIR, 'chat', 'classes.pkl'), 'rb'))
model = load_model(os.path.join(BASE_DIR, 'chat', 'chatbot_model.h5'))
# classes = pickle.load(open('classes.pkl', 'rb'))
# model = tf.keras.models.load_model('chatbot_model.h5')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

# def chatbot(request):
#     message = request.GET.get('message')
#     if message:
#         ints = predict_class(message)
#         res = get_response(ints, intents)
#         return HttpResponse(res)
#     else:
#         return HttpResponse('Please provide a message')

def chatbot(request, message):
    ints = predict_class(message)
    res = get_response(ints, intents)
    return res


