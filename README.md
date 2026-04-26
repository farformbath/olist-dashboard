# Proyek Analisis Data: E-Commerce Public Dataset (Olist)

## Deskripsi Proyek
Proyek akhir analisis data menggunakan **Brazilian E-Commerce Public Dataset** dari Olist.  
Dataset berisi informasi transaksi e-commerce Brasil dari 2016 hingga 2018.

## Pertanyaan Bisnis (SMART)
1. **Kategori produk apa yang menghasilkan total pendapatan tertinggi pada periode 2017–2018, dan bagaimana tren pertumbuhan pendapatan bulanannya?**
2. **Bagaimana hubungan antara waktu pengiriman aktual (hari) dengan skor ulasan pelanggan pada pesanan delivered sepanjang 2017–2018, dan berapa threshold waktu pengiriman yang mulai berdampak negatif?**

## Cara Menjalankan

### Notebook
```bash
pip install -r requirements.txt
jupyter notebook notebook_analisis_ecommerce.ipynb
```

### Dashboard Streamlit
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Dependencies
Lihat `requirements.txt`

## Sumber Dataset
- Drive: https://drive.google.com/file/d/1MsAjPM7oKtVfJL_wRp1qmCajtSG1mdcK/view?usp=sharing
