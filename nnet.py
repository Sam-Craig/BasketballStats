import tensorflow as tf
from tensorflow import keras
import numpy as np
import datasetup

data, labels = datasetup.makedata(2005, 2006)

data, labels = datasetup.scaledata(data, labels)

data, labels, testdata, testlabels = datasetup.gettestdata(data, labels, .1)

# Taken from: https://www.tensorflow.org/tutorials/keras/basic_classification, might be suboptimal for this problem

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(16, 9)),
    keras.layers.Dense(128, activation=tf.nn.relu),
    keras.layers.Dense(10, activation=tf.nn.softmax)
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# I feel like 20 epochs is too few, but the example used 5
# I will try to expirement with more at some point

model.fit(data, labels, epochs = 20)

testloss, testacc = model.evaluate(testdata, testlabels)

print(testloss, testacc)

predictions = model.predict(testdata)



