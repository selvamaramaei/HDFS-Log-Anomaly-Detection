import pandas as pd
import numpy as np
from collections import Counter

input_path = 'data/processed/event_tracer.csv'
output_path = 'data/processed/labeled_data.csv'

df = pd.read_csv(input_path)

# Gecikme analizi: %99'luk dilimin üzerindeki süreleri "yüksek gecikme" (anomaly) kabul ediyoruz
df['Lat_Val'] = df['Latency'].str.replace('ms', '').astype(float)
latency_threshold = df['Lat_Val'].quantile(0.99)

# MODELİ ZORLAŞTIRMA (Masking): 
# Modelin sadece "hata kodu" görüp ezberlemesini önlemek için kritik kodları 'E99' ile maskeliyoruz.
hint_codes = {
    'E14', 'E15', 'E16', 'E19', 'E20', 'E21', 'E22', 'E23', 'E24', 
    'E26', 'E27', 'E28', 'E29', 'E30', 'E31', 'E33', 'E34', 'E40', 
    'E41', 'E42', 'E43', 'E44'
}

def label_and_mask_logic(row):
    features_raw = str(row['Features']).split(',')
    latency = row['Lat_Val']
    counts = Counter(features_raw)
    
    # Mantıksal kontroller için yardımcı indexler
    idx_del = next((i for i, e in enumerate(features_raw) if e in ['E17', 'E32']), None)
    idx_e5 = features_raw.index('E5') if 'E5' in features_raw else None
    idx_e10 = features_raw.index('E10') if 'E10' in features_raw else None

    label = 0
    reason = "Normal"

    # --- 12 FARKLI ANOMALİ SENARYOSU ---
    
    # 1. Kritik Sistem Hataları (Fatal Errors)
    if any(err in features_raw for err in ['E14', 'E16', 'E19', 'E20', 'E23', 'E30', 'E42']):
        label, reason = 1, "Scenario 1: Fatal System Error"
    
    # 2. Blok ve Kayıt Hataları (Orphan/Redundant Blocks)
    elif 'E21' in features_raw: label, reason = 1, "Scenario 2: Redundant Add"
    elif 'E33' in features_raw: label, reason = 1, "Scenario 3: Block Info Not Found"
    elif 'E34' in features_raw: label, reason = 1, "Scenario 4: Orphan Block"
    
    # 3. Yazma Hattı ve Yaşam Döngüsü Bozuklukları
    elif 'E1' in features_raw and not ('E4' in features_raw or 'E5' in features_raw):
        if len(features_raw) > 2: label, reason = 1, "Scenario 5: Broken Write Pipeline"
    elif features_raw[0] in ['E17', 'E32']:
        label, reason = 1, "Scenario 6: Premature Deletion"
    
    # 4. Silme Sonrası Usulsüz İşlemler (Serving after Deletion vb.)
    elif idx_del is not None:
        if any(features_raw.index(e) > idx_del for e in features_raw if e == 'E10'):
            label, reason = 1, "Scenario 7: Serving After Deletion"
        elif any(features_raw.index(e) > idx_del for e in features_raw if e == 'E13'):
            label, reason = 1, "Scenario 8: Verification After Deletion"
        elif any(features_raw.index(e) > idx_del for e in features_raw if e in ['E7', 'E9', 'E11']):
            label, reason = 1, "Scenario 9: Replicating Deleted Block"
    
    # 5. Okuma ve Replikasyon Anomalileri
    elif 'E10' in features_raw:
        if 'E5' not in features_raw or idx_e10 < idx_e5:
            label, reason = 1, "Scenario 10: Premature/Ghost Serving"
    elif counts['E5'] > 3:
        label, reason = 1, "Scenario 11: Excessive Replication"
    
    # 6. Zaman Aşımı (Outlier Latency)
    elif latency > latency_threshold:
        label, reason = 1, "Scenario 12: High Latency Outlier"

    # Maskeleme: Belirlenen kritik kodlar E99 yapılarak 'Features' sütunu güncellenir
    masked_features = ['E99' if e in hint_codes else e for e in features_raw]
    
    return label, ",".join(masked_features), reason

print("Anomali senaryoları analiz ediliyor ve maskeleme uygulanıyor...")
results = df.apply(label_and_mask_logic, axis=1)

df['Label'] = [r[0] for r in results]
df['Features'] = [r[1] for r in results]
df['Anomaly_Reason'] = [r[2] for r in results]

# Veri dağılımı özeti
print(f"\nToplam Blok: {len(df)}")
print(f"Normal: {len(df[df['Label'] == 0])} | Anomali: {len(df[df['Label'] == 1])}")
print("\nSenaryo Dağılımı:")
print(df[df['Label'] == 1]['Anomaly_Reason'].value_counts())

# Sadece gerekli sütunları kaydediyoruz
final_cols = ['BlockId', 'Label', 'Type', 'Features', 'TimeInterval', 'Latency']
df[final_cols].to_csv(output_path, index=False)