import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, SpatialDropout1D
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# 1. Klasörleri Oluştur
if not os.path.exists('models'): os.makedirs('models')
if not os.path.exists('outputs'): os.makedirs('outputs')

# 2. Veriyi Yükle
print("Dengeli veri yükleniyor...")
df = pd.read_csv('data/processed/balanced_data.csv')

# 3. NLP Ön İşlemleri (Tokenization)
tokenizer = Tokenizer(filters='', lower=False)
tokenizer.fit_on_texts(df['Features'])
sequences = tokenizer.texts_to_sequences(df['Features'])
vocab_size = len(tokenizer.word_index) + 1

# Tokenizer'ı kaydet 
with open('models/tokenizer.pkl', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Padding (Dizi Boyutlarını Eşitleme)
max_len = 50 
X = pad_sequences(sequences, maxlen=max_len, padding='post')
y = df['Label'].values

# Train/Test Split (%80 Eğitim, %20 Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. LSTM Model Mimarisi
model = Sequential([
    Embedding(input_dim=vocab_size, output_dim=64, input_length=max_len),
    SpatialDropout1D(0.2), # Embedding sonrası dropout
    LSTM(128, return_sequences=True),
    Dropout(0.2),
    LSTM(64),
    Dense(32, activation='relu'),
    Dense(1, activation='sigmoid') # Binary Output
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# 5. Eğitim (En iyi modeli otomatik kaydetme ve erken durdurma)
checkpoint = ModelCheckpoint('models/hdfs_lstm_model.h5', monitor='val_loss', save_best_only=True)
early_stop = EarlyStopping(monitor='val_loss', patience=3)

print("\nEğitim başlıyor...")
history = model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=64,
    validation_split=0.1,
    callbacks=[checkpoint, early_stop]
)

# 6. Performans Analizi ve Grafikleme
print("\nModel değerlendiriliyor...")
y_pred = (model.predict(X_test) > 0.5).astype("int32")

# Classification Report
report = classification_report(y_test, y_pred, target_names=['Normal', 'Anomaly'])
print("\nİstatistiksel Rapor:")
print(report)

# Confusion Matrix
plt.figure(figsize=(8,6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal', 'Anomaly'], yticklabels=['Normal', 'Anomaly'])
plt.xlabel('Tahmin')
plt.ylabel('Gerçek')
plt.title('Confusion Matrix')
plt.savefig('outputs/confusion_matrix.png')
