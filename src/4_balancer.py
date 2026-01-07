import pandas as pd

# 1. Dosyaları Yükle
input_path = 'data/processed/labeled_data.csv'
output_path = 'data/processed/balanced_data.csv'

df = pd.read_csv(input_path)

# 2. Sınıfları Ayır
df_normal = df[df['Label'] == 0]
df_anomaly = df[df['Label'] == 1]

num_anomaly = len(df_anomaly)
num_normal_target = num_anomaly * 3 # 3'e 1 oranı

print(f"Mevcut Durum:")
print(f"Anomali Sayısı: {num_anomaly}")
print(f"Normal Sayısı : {len(df_normal)}")

# 3. Downsampling İşlemi
if len(df_normal) > num_normal_target:
    df_normal_downsampled = df_normal.sample(n=num_normal_target, random_state=42)
    print(f"\nDownsampling yapıldı. Yeni Normal sayısı: {len(df_normal_downsampled)}")
else:
    df_normal_downsampled = df_normal
    print(f"\nUyarı: Normal veri sayısı zaten hedeften az. Örnekleme yapılmadı.")

# 4. Verileri Birleştir ve Karıştır (Shuffle)
df_balanced = pd.concat([df_normal_downsampled, df_anomaly])
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. Sonuçları Yazdır ve Kaydet
print("\n" + "="*40)
print(f"{'DENGELENMİŞ VERİ ÖZETİ':^40}")
print("="*40)
print(f"Toplam Satır : {len(df_balanced)}")
print(f"Normal (0)   : {len(df_balanced[df_balanced['Label'] == 0])} (%75)")
print(f"Anomali (1)  : {len(df_balanced[df_balanced['Label'] == 1])} (%25)")
print("="*40)

df_balanced.to_csv(output_path, index=False)
print(f"\nDengeli veri seti kaydedildi: {output_path}")