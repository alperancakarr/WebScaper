import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import json

start_time = time.time()
Books = []

# Örnek çıktı için 1'den 5'e kadar olan sayfalarda döngü oluşturuldu.
for page in range(1, 6):
    url = f"https://www.kitapsepeti.com/roman?pg={page}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_items = soup.find_all('div', class_='product-item')

    for item in product_items:
        # Kitap başlığı çekiliyor; başlık bulunamazsa NaN atanıyor
        title_tag = item.find('a', class_='product-title text-center')
        title = title_tag.get_text(strip=True) if title_tag else np.nan

        # Yıldız puanı çekiliyor; Yıldızın alan genişliği hesaplanarak 5 üzerinden puan hesaplanıyor
        # Puan bulunamazsa NaN atanıyor
        stars_div = item.find('div', class_='stars')
        if stars_div:
            rating_span = stars_div.find('span', class_='stars-fill')
            if rating_span:
                rating_width = rating_span['style']
                rating_percentage = rating_width.split(':')[1].strip().strip('%')
                stars = float(rating_percentage) / 20
            else:
                stars = np.nan
        else:
            stars = np.nan

        # Fiyat bilgisi çekiliyor; eğer bulunamazsa NaN atanıyor
        price_div = item.find('div', class_='fw-regular current-price')
        if price_div:
            price_tag = price_div.find('span', class_='product-price')
            price = price_tag.get_text(strip=True) if price_tag else np.nan
        else:
            price = np.nan

        # Dictionary ile Books listesine ekleme yapılıyor
        book_data = {
            "book_name": title,
            "stars": None if stars == 0.0 else stars, # Puan değeri boş ise json dosyasında null yazılıyor.
            "price": price
        }
        Books.append(book_data)

# Books listesini JSON dosyasına kaydetme
with open('books.json', 'w', encoding='utf-8') as json_file:
    json.dump(Books, json_file, ensure_ascii=False, indent=4)

print('JSON dosyasına yazma işlemi tamamlandı.')

# JSON dosyasından verileri okuma
with open('books.json', 'r', encoding='utf-8') as json_file:
    books_data = json.load(json_file)

# Her kitap objesine yeni bir field ekleme
for book in books_data:
    book['category'] = 'Roman'  # Örnek olarak 'Roman' kategorisi ekleniyor

# Güncellenmiş veriler tekrar JSON dosyasına kaydediliyor
with open('books_updated.json', 'w', encoding='utf-8') as json_file:
    json.dump(books_data, json_file, ensure_ascii=False, indent=4)

print('Güncellenmiş JSON dosyasına yazma işlemi tamamlandı.')

# Güncellenmiş JSON'dan CSV'ye dönüştürme
df = pd.DataFrame(books_data)

# Başlıkları yeniden adlandırma
df = df[['category', 'book_name', 'stars', 'price']]
df.columns = ['Kategori', 'Kitap Adı', 'Puan', 'Fiyat']

# 0.0 ve boş değerleri NaN ile değiştirme
df.replace({0.0: np.nan}, inplace=True)

# DataFrame'i CSV dosyasına kaydetme
df.to_csv('Books.csv', index=False, encoding='utf-8', na_rep='NaN')

print('Books.csv dosyasına yazma işlemi tamamlandı.')

end_time = time.time()
print(f'İşlem süresi: {end_time - start_time:.2f} saniye')