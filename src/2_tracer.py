import pandas as pd
import numpy as np
import ast
import re
from datetime import datetime

# Parser aşamasından gelen yapılandırılmış verileri yüklüyoruz
df_structured = pd.read_csv('data/processed/log_structured.csv')
df_templates = pd.read_csv('data/processed/log_templates.csv')

# Karmaşık Event ID'leri modelin daha rahat işleyebileceği kısa isimlere (E1, E2...) eşliyoruz
df_templates['ShortID'] = ['E' + str(i+1) for i in range(len(df_templates))]
mapping_dict = dict(zip(df_templates['EventId'], df_templates['ShortID']))

def extract_block_id(param_list):
    """Log parametreleri içinden 'blk_...' formatındaki HDFS blok numarasını ayıklar."""
    try:
        # String formatındaki listeyi Python listesine dönüştür
        params = ast.literal_eval(param_list)
        for p in params:
            match = re.search(r'(blk_-?\d+)', str(p))
            if match:
                return match.group(1).strip()
        return None
    except:
        return None

print("BlockId ayıklanıyor...")
df_structured['BlockId'] = df_structured['ParameterList'].apply(extract_block_id)
df_structured = df_structured.dropna(subset=['BlockId'])

# Tarih ve saat bilgisini zaman bazlı analiz için standart datetime objesine dönüştürüyoruz
df_structured['DateTime'] = pd.to_datetime(
    df_structured['Date'].astype(str).str.zfill(6) + 
    df_structured['Time'].astype(str).str.zfill(6), 
    format='%y%m%d%H%M%S'
)

# Her bir BlockID için gerçekleşen olayları zaman sırasına dizip 'olay dizileri' oluşturuyoruz
print("Bloklar gruplanıyor...")
tracer_data = []

for block_id, group in df_structured.groupby('BlockId'):
    group = group.sort_values(by='DateTime')
    
    # Event dizisini oluşturma (Örn: E1, E4, E2)
    events = [mapping_dict.get(eid, 'UNK') for eid in group['EventId']]
    features = ",".join(events)
    
    # Süre ve ortalama gecikme (latency) gibi zaman bazlı özelliklerin hesaplanması
    start_time = group['DateTime'].min()
    end_time = group['DateTime'].max()
    duration = (end_time - start_time).total_seconds() 
    
    if len(group) > 1:
        latency = (duration * 1000) / (len(group) - 1)
    else:
        latency = 0.0
        
    tracer_data.append({
        'BlockId': block_id,
        'Type': 'HDFS_Sequence',
        'Features': features,
        'TimeInterval': f"{duration}s",
        'Latency': f"{round(latency, 2)}ms"
    })

# Etiketleme (labeling) öncesi hazır hale getirilen veriyi kaydediyoruz
df_tracer = pd.DataFrame(tracer_data)
df_tracer.to_csv('data/processed/event_tracer.csv', index=False)

print(f"İşlem tamam: {len(df_tracer)} adet blok dizisi oluşturuldu.")