import sys
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
import joblib
from data_utils import load_data  # Make sure you have this function defined elsewhere


# ==========================================================
# Generator: takes noise + context -> next predicted price
# ==========================================================
def make_generator(noise_dim, context_dim):
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=noise_dim + context_dim))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    return model


# ==========================================================
# Discriminator: takes context + candidate next price -> real/fake
# ==========================================================
def make_discriminator(context_dim):
    model = Sequential()
    model.add(Dense(128, activation='relu', input_dim=context_dim + 1))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=Adam(1e-4), metrics=['accuracy'])
    return model


# ==========================================================
# Adversarial Training
# ==========================================================
def train(path_to_csv, seq_len=20, epochs=200, batch=32):
    X, y, scaler = load_data(path_to_csv, seq_len)
    context_dim = X.shape[1]
    noise_dim = 10

    gen = make_generator(noise_dim, context_dim)
    disc = make_discriminator(context_dim)

    # Build combined model
    noise_input = Input(shape=(noise_dim,))
    context_input = Input(shape=(context_dim,))
    merged = Dense(64, activation='relu')(tf.keras.layers.concatenate([noise_input, context_input]))
    out = Dense(1, activation='sigmoid')(merged)
    combined = Model([noise_input, context_input], out)
    combined.compile(loss='binary_crossentropy', optimizer=Adam(1e-4))

    # Training loop (simple custom loop)
    real = np.ones((batch, 1))
    fake = np.zeros((batch, 1))

    for epoch in range(epochs):
        # Train discriminator on real
        idx = np.random.randint(0, X.shape[0], batch)
        contexts = X[idx]
        reals = y[idx].reshape(-1, 1)

        # Sample noise and generate fake samples
        noise = np.random.normal(0, 1, (batch, noise_dim))
        gen_samples = gen.predict(np.concatenate([noise, contexts], axis=1))

        d_loss_real = disc.train_on_batch(np.concatenate([contexts, reals], axis=1), real)
        d_loss_fake = disc.train_on_batch(np.concatenate([contexts, gen_samples], axis=1), fake)

        # Train generator via combined model (tricking discriminator)
        g_loss = combined.train_on_batch([noise, contexts], real)

        if epoch % 10 == 0:
            print(f"Epoch {epoch} | d_real {d_loss_real[0]:.4f} d_fake {d_loss_fake[0]:.4f} g {g_loss:.4f}")

    # Save models and scaler
    gen.save('generator.h5')
    disc.save('discriminator.h5')
    joblib.dump(scaler, 'scaler.pkl')


# ==========================================================
# Entry Point
# ==========================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python train_gan.py path/to/stock.csv')
        sys.exit(1)
    train(sys.argv[1])
