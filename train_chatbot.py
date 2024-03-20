import random
import json
import pickle
import numpy as np
import tensorflow as tf
import os

import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()

# Get the full path to the intents.json file
intents_file = os.path.join(os.path.dirname(__file__), 'intents.json')

# Load the intents from the file
with open(intents_file) as file:
    intents = json.load(file)

words = []
classes = []
documents = []
ignoreLetters = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        wordList = nltk.word_tokenize(pattern)
        words.extend(wordList)
        documents.append((wordList, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(word) for word in words if word not in ignoreLetters]
words = sorted(set(words))

classes = sorted(set(classes))

# Get the full path to the words.pkl file
words_file = os.path.join(os.path.dirname(__file__), 'words.pkl')

# Save the words to the file
with open(words_file, 'wb') as file:
    pickle.dump(words, file)

# Get the full path to the classes.pkl file
classes_file = os.path.join(os.path.dirname(__file__), 'classes.pkl')

# Save the classes to the file
with open(classes_file, 'wb') as file:
    pickle.dump(classes, file)

training = []
outputEmpty = [0] * len(classes)

for document in documents:
    bag = []
    wordPatterns = document[0]
    wordPatterns = [lemmatizer.lemmatize(word.lower()) for word in wordPatterns]
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)

    outputRow = list(outputEmpty)
    outputRow[classes.index(document[1])] = 1
    training.append(bag + outputRow)

random.shuffle(training)
training = np.array(training)

trainX = training[:, :len(words)]
trainY = training[:, len(words):]

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(128, input_shape=(len(trainX[0]),), activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(64, activation = 'relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(trainY[0]), activation='softmax'))

sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

model.fit(trainX, trainY, epochs=200, batch_size=5, verbose=1)

# Get the full path to the chatbot_model.h5 file
model_file = os.path.join(os.path.dirname(__file__), 'chatbot_model.h5')

# Save the model to the file
model.save(model_file)

print('Done')