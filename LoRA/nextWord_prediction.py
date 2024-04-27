import tensorflow as tf
from tensorflow.keras.layers import Embedding,LSTM, Dense
from keras.models import Sequential
from keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
import pickle
import numpy as np

file= open("data.txt",'r',encoding="utf8")
lines=[]
for i in file:
    lines.append(i)

data = " "
for i in lines:
    data= " ".join(lines)

data= data.replace('\n','').replace('\r','').replace('\ufeff','').replace('"','').replace('"','')
data = data.split()
data=" ".join(data)

#print(data[:1000])

tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts([data])

pickle.dump(tokenizer,open('token.pkl','wb'))
#print('okay')
sequence_data = tokenizer.texts_to_sequences([data])[0]

#print(len(sequence_data))

vocab_size=len(tokenizer.word_index)+1
#print(vocab_size)

sequence=[]
for i in range(3, len(sequence_data)):
    words = sequence_data[i-3:i+1]
    sequence.append(words)
#print(len(sequence))
sequence = np.array(sequence)
#print (sequence)

X=[]
y=[]

for i in sequence:
    X.append(i[0:3])
    y.append(i[3])
X=np.array(X)
y=np.array(y)

y = to_categorical(y, num_classes=vocab_size)
#print(y[:5])

#Building the LSTM Model
model = Sequential()
model.add(Embedding(vocab_size, 10, input_length = 3))
model.add(LSTM(1000, return_sequences = True))
model.add(LSTM(1000))
model.add(Dense(1000, activation='relu'))
model.add(Dense(vocab_size, activation="softmax"))
model.summary()



