import sys
import pandas as pd
import os
from logparser.Drain import LogParser

# Dosya yolları
input_dir = 'data/raw'  
output_dir = 'data/processed' 
log_file = 'HDFS_5m.log' 

# HDFS log yapısını sütunlara ayırmak için tanımlanan format
log_format = '<Date> <Time> <Pid> <Level> <Component>: <Content>'

# Dinamik verileri (IP, ID, Sayı) maskeleyerek ortak log şablonlarını bulmak için regex listesi
regex = [
    r'blk_(|-)[0-9]+', 
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', 
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$', 
]

# Drain algoritması için benzerlik eşiği ve ağaç derinliği ayarları
st = 0.5  
depth = 4 

def parse_hdfs():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("--- Parsing İşlemi Başlıyor ---")
    
    # Ham logları yapılandırılmış (structured) formata dönüştüren Drain parser
    parser = LogParser(log_format, indir=input_dir, outdir=output_dir, depth=depth, st=st, rex=regex)
    
    try:
        parser.parse(log_file)
        print(f"\nBAŞARILI: Sonuçlar '{output_dir}' klasörüne kaydedildi.")
    except Exception as e:
        print(f"\nHATA: {e}")

if __name__ == '__main__':
    parse_hdfs()