from numpy import loadtxt
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.python.keras.metrics import accuracy

loadDataSet = loadtxt('pima-indians-diabetes.csv', delimiter=',')
slicedColumns0to7Index = loadDataSet[:,0:8]
slicedColumn8Index = loadDataSet[:,8]

""" 
The model expects rows of data with 8 variables (the input_dim=8 argument)
The first hidden layer has 12 nodes and uses the relu activation function.
The second hidden layer has 8 nodes and uses the relu activation function.
The output layer has one node and uses the sigmoid activation function.

Note, the most confusing thing here is that the shape of the input to 
the model is defined as an argument on the first hidden layer. 
This means that the line of code that adds the first Dense layer is doing 2 things, 
defining the input or visible layer and the first hidden layer.

"""
model = Sequential()
model.add(Dense(12, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

"""
We must specify the loss function to use to evaluate a set of weights, 
the optimizer is used to search through different weights for the network and any optional
 metrics we would like to collect and report during training.

In this case, we will use cross entropy as the loss argument. This loss is for a binary 
classification problems and is defined in Keras as “binary_crossentropy“.

We will define the optimizer as the efficient stochastic gradient descent algorithm “adam“.
This is a popular version of gradient descent because it automatically tunes itself and 
gives good results in a wide range of problems.
"""

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

"""Training occurs over epochs and each epoch is split into batches.

Epoch: One pass through all of the rows in the training dataset.
Batch: One or more samples considered by the model within an epoch before weights are updated.

"""
model.fit(slicedColumns0to7Index, slicedColumn8Index, epochs=150, batch_size=10)


"""
The evaluate() function will return a list with two values. The first will be the loss of the model 
on the dataset and the second will be the accuracy of the model on the dataset. We are only interested 
in reporting the accuracy, so we will ignore the loss value.
"""
_, accuracy = model.evaluate(slicedColumns0to7Index, slicedColumn8Index)
print('Accuracy: %.2f' % (accuracy*100))

...
# make probability predictions with the model
predictions = model.predict(slicedColumns0to7Index)
# round predictions 
rounded = [round(x[0]) for x in predictions]
...
# make class predictions with the model
predictions = (model.predict(slicedColumns0to7Index) > 0.5).astype(int)

