# dummy_generator.py
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np

# SEQ_LEN = 20, noise = 10 => input size = 30
INPUT_SIZE = 30

# Create a simple dummy generator model
dummy_gen = Sequential()
dummy_gen.add(Dense(1, input_shape=(INPUT_SIZE,)))  # outputs a single value

# Save the dummy generator
dummy_gen.save("generator.h5")
print("✅ Dummy generator saved as 'generator.h5'. Place this in your backend folder.")

