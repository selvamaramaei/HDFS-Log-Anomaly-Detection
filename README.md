HDFS Log Anomaly Detection
Bu proje, HDFS (Hadoop Distributed File System) günlük verilerindeki (logs) anomallikleri Derin Öğrenme (LSTM) ve Doğal Dil İşleme (NLP) tekniklerini kullanarak tespit eden uçtan uca bir boru hattı (pipeline) sunmaktadır.

Proje kapsamında, ham log verileri yapılandırılmış dizilere dönüştürülmüş ve modelin sadece hata kodlarını ezberlemesini önlemek için özel maskeleme teknikleri uygulanmıştır.

🛠️ Kullanılan Teknolojiler
Python (Pandas, Numpy, Scikit-learn)

TensorFlow/Keras (LSTM Model mimarisi)

LogParser (Drain) (Log yapılandırma için)

NLP Techniques (Tokenization, Sequence Labeling)

🏗️ Proje Mimarisi ve Akış
Proje 5 ana aşamadan oluşmaktadır:

Parsing (1_parser.py): Drain algoritması kullanılarak ham loglar yapılandırılmış .csv formatına dönüştürülür.

Tracer (2_tracer.py): Loglar BlockID bazında gruplanarak zaman sıralı olay dizileri (sequences) oluşturulur.

Labeling (3_labeler.py): 12 farklı anomali senaryosu (Fatal errors, Premature deletion vb.) tanımlanır. Modelin akışı öğrenmesi için kritik hata kodları E99 ile maskelenir.

Balancer (4_balancer.py): Sınıf dengesizliğini (imbalance) gidermek için normal veriler üzerinde downsampling yapılarak 3:1 oranı sağlanır.

Trainer (5_trainer.py): Hazırlanan veriler LSTM modeline beslenerek anomali tespiti eğitimi gerçekleştirilir.

🚀 Kurulum ve Çalıştırma
Depoyu klonlayın:

git clone https://github.com/kullanici_adin/HDFS-Log-Anomaly-Detection.git
cd HDFS-Log-Anomaly-Detection

Gerekli kütüphaneleri yükleyin:

pip install -r requirements.txt
