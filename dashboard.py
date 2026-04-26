import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Dashboard Olist E-Commerce",
    page_icon="🛒",
    layout="wide"
)

BASE_PATH = os.path.join(os.path.dirname(__file__), 'dataset/')

@st.cache_data
def load_data():
    customers    = pd.read_csv(BASE_PATH + 'customers_dataset.csv')
    orders       = pd.read_csv(BASE_PATH + 'orders_dataset.csv')
    order_items  = pd.read_csv(BASE_PATH + 'order_items_dataset.csv')
    payments     = pd.read_csv(BASE_PATH + 'order_payments_dataset.csv')
    reviews      = pd.read_csv(BASE_PATH + 'order_reviews_dataset.csv')
    products     = pd.read_csv(BASE_PATH + 'products_dataset.csv')
    cat_trans    = pd.read_csv(BASE_PATH + 'product_category_name_translation.csv')

    # --- Cleaning ---
    ts_cols = ['order_purchase_timestamp', 'order_approved_at',
               'order_delivered_carrier_date', 'order_delivered_customer_date',
               'order_estimated_delivery_date']
    for col in ts_cols:
        orders[col] = pd.to_datetime(orders[col])

    products['product_category_name'] = products['product_category_name'].fillna('unknown')
    products = products.merge(cat_trans, on='product_category_name', how='left')
    products['product_category_name_english'] = (
        products['product_category_name_english']
        .fillna(products['product_category_name'])
    )

    payments = payments[payments['payment_type'] != 'not_defined']

    orders_delivered = orders[
        (orders['order_status'] == 'delivered') &
        (orders['order_delivered_customer_date'].notna())
    ].copy()
    orders_delivered['delivery_days'] = (
        orders_delivered['order_delivered_customer_date'] -
        orders_delivered['order_purchase_timestamp']
    ).dt.days
    orders_delivered['year_month'] = orders_delivered['order_purchase_timestamp'].dt.to_period('M')
    orders_delivered['year'] = orders_delivered['order_purchase_timestamp'].dt.year

    return orders_delivered, order_items, payments, reviews, products, customers

orders_delivered, order_items, payments, reviews, products, customers = load_data()

#debar
st.sidebar.title("🛒 Olist E-Commerce")
st.sidebar.markdown("**Dashboard Analisis Data**")
st.sidebar.divider()

years = sorted(orders_delivered['year'].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "📅 Filter Tahun",
    options=years,
    default=years
)

top_n = st.sidebar.slider("🏆 Jumlah Top Kategori", min_value=5, max_value=20, value=10)
st.sidebar.divider()
st.sidebar.caption("Sumber: Olist Brazilian E-Commerce Dataset (Kaggle)")

# Filter berdasarkan tahun
orders_filtered = orders_delivered[orders_delivered['year'].isin(selected_years)]

# Header 
st.title("🛒 Dashboard Analisis E-Commerce Olist")
st.markdown("Proyek Akhir Analisis Data — Dataset: Brazilian E-Commerce Public Dataset")
st.divider()

# KPI Cards
items_filtered = order_items.merge(
    orders_filtered[['order_id', 'year_month', 'year', 'delivery_days']],
    on='order_id', how='inner'
)
items_cat = items_filtered.merge(
    products[['product_id', 'product_category_name_english']],
    on='product_id', how='left'
)
orders_reviews = orders_filtered.merge(
    reviews[['order_id', 'review_score']], on='order_id', how='inner'
)

total_orders     = len(orders_filtered)
total_revenue    = items_filtered['price'].sum()
avg_review_score = orders_reviews['review_score'].mean()
avg_delivery     = orders_filtered['delivery_days'].median()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total Pesanan (Delivered)", f"{total_orders:,}")
col2.metric("💰 Total Pendapatan", f"R$ {total_revenue/1e6:.2f}M")
col3.metric("⭐ Avg Review Score", f"{avg_review_score:.2f} / 5")
col4.metric("🚚 Median Waktu Kirim", f"{avg_delivery:.0f} Hari")

st.divider()

# Visualisasi 1: Revenue Analysis
st.subheader("📊 Pertanyaan 1: Kategori Produk & Tren Pendapatan (2017–2018)")
st.markdown(
    "*Kategori produk apa yang menghasilkan total pendapatan tertinggi, "
    "dan bagaimana tren pertumbuhan pendapatan bulanannya?*"
)

revenue_by_cat = (
    items_cat.groupby('product_category_name_english')['price']
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)
revenue_by_cat.columns = ['category', 'total_revenue']

monthly_revenue = (
    items_cat.groupby('year_month')['price']
    .sum()
    .reset_index()
)
monthly_revenue.columns = ['year_month', 'revenue']
monthly_revenue['year_month_str'] = monthly_revenue['year_month'].astype(str)
monthly_revenue = monthly_revenue.sort_values('year_month')

fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig1.patch.set_facecolor('#FAFAFA')

# Bar chart kategori
colors = sns.color_palette('Set2', top_n)
bars = ax1.barh(
    revenue_by_cat['category'][::-1],
    revenue_by_cat['total_revenue'][::-1] / 1e6,
    color=colors
)
for bar, val in zip(bars, revenue_by_cat['total_revenue'][::-1]):
    ax1.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
             f'R${val/1e6:.2f}M', va='center', fontsize=8)
ax1.set_xlabel('Total Pendapatan (juta BRL)')
ax1.set_title(f'Top {top_n} Kategori Produk\nberdasarkan Total Pendapatan', fontweight='bold')
ax1.set_xlim(0, revenue_by_cat['total_revenue'].max()/1e6 * 1.3)
ax1.grid(axis='x', alpha=0.3)
ax1.set_axisbelow(True)

# Line chart tren bulanan
x_vals = range(len(monthly_revenue))
ax2.plot(x_vals, monthly_revenue['revenue']/1e6, color='#2196F3',
         linewidth=2.5, marker='o', markersize=4)
ax2.fill_between(x_vals, monthly_revenue['revenue']/1e6, alpha=0.12, color='#2196F3')

if len(monthly_revenue) > 0:
    peak_idx = monthly_revenue['revenue'].idxmax()
    peak_pos = monthly_revenue.index.get_loc(peak_idx)
    ax2.annotate(
        f"Puncak: {monthly_revenue['year_month_str'].iloc[peak_pos]}\nR${monthly_revenue['revenue'].iloc[peak_pos]/1e6:.2f}M",
        xy=(peak_pos, monthly_revenue['revenue'].iloc[peak_pos]/1e6),
        xytext=(max(0, peak_pos-4), monthly_revenue['revenue'].iloc[peak_pos]/1e6 + 0.1),
        arrowprops=dict(arrowstyle='->', color='red'),
        fontsize=8, color='red'
    )

step = max(1, len(monthly_revenue)//8)
ax2.set_xticks(list(x_vals)[::step])
ax2.set_xticklabels(monthly_revenue['year_month_str'].iloc[::step], rotation=45, ha='right', fontsize=8)
ax2.set_xlabel('Bulan')
ax2.set_ylabel('Total Pendapatan (juta BRL)')
ax2.set_title('Tren Pendapatan Bulanan', fontweight='bold')
ax2.grid(alpha=0.3)

plt.tight_layout()
st.pyplot(fig1)
plt.close()

# Visualisasi 2: Delivery & Satisfaction
st.divider()
st.subheader("🚚 Pertanyaan 2: Waktu Pengiriman vs. Kepuasan Pelanggan")
st.markdown(
    "*Bagaimana hubungan antara waktu pengiriman (hari) dengan review score, "
    "dan berapa threshold yang berdampak negatif pada kepuasan?*"
)

avg_delivery_by_score = (
    orders_reviews.groupby('review_score')['delivery_days']
    .agg(['mean', 'median', 'count'])
    .reset_index()
)
avg_delivery_by_score.columns = ['review_score', 'avg_days', 'median_days', 'count']

def delivery_segment(days):
    if days <= 7:   return '≤7 hari\n(Cepat)'
    elif days <= 14: return '8–14 hari\n(Normal)'
    elif days <= 21: return '15–21 hari\n(Lambat)'
    else:            return '>21 hari\n(Sangat Lambat)'

orders_reviews = orders_reviews.copy()
orders_reviews['delivery_segment'] = orders_reviews['delivery_days'].apply(delivery_segment)
seg_order = ['≤7 hari\n(Cepat)', '8–14 hari\n(Normal)', '15–21 hari\n(Lambat)', '>21 hari\n(Sangat Lambat)']
seg_summary = (
    orders_reviews.groupby('delivery_segment')['review_score']
    .agg(['mean','count'])
    .reindex(seg_order)
    .reset_index()
)
seg_summary.columns = ['delivery_segment', 'avg_review_score', 'count']

fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))
fig2.patch.set_facecolor('#FAFAFA')

# Avg delivery days per score
palette_score = ['#E53935','#EF6C00','#FDD835','#7CB342','#2E7D32']
score_bars = ax3.bar(
    avg_delivery_by_score['review_score'].astype(str),
    avg_delivery_by_score['avg_days'],
    color=palette_score, edgecolor='white'
)
for bar, val in zip(score_bars, avg_delivery_by_score['avg_days']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             f'{val:.1f}h', ha='center', fontsize=9, fontweight='bold')
ax3.set_xlabel('Review Score (1=Buruk, 5=Baik)')
ax3.set_ylabel('Rata-rata Waktu Pengiriman (Hari)')
ax3.set_title('Rata-rata Waktu Pengiriman\nper Review Score', fontweight='bold')
ax3.grid(axis='y', alpha=0.3)
ax3.set_axisbelow(True)

# Avg review score per segment
seg_colors = ['#2E7D32', '#7CB342', '#EF6C00', '#E53935']
seg_bars = ax4.bar(
    seg_summary['delivery_segment'],
    seg_summary['avg_review_score'],
    color=seg_colors, edgecolor='white'
)
for bar, (_, row) in zip(seg_bars, seg_summary.iterrows()):
    if not np.isnan(row['avg_review_score']):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f"{row['avg_review_score']:.2f}\n(n={int(row['count']):,})",
                 ha='center', fontsize=9, fontweight='bold')
ax4.axhline(y=4.0, color='#1565C0', linestyle='--', linewidth=1.5, label='Threshold ≥4.0')
ax4.set_xlabel('Segmen Waktu Pengiriman')
ax4.set_ylabel('Rata-rata Review Score')
ax4.set_title('Rata-rata Review Score\nper Segmen Waktu Pengiriman', fontweight='bold')
ax4.set_ylim(0, 5.5)
ax4.legend(fontsize=9)
ax4.grid(axis='y', alpha=0.3)
ax4.set_axisbelow(True)

plt.tight_layout()
st.pyplot(fig2)
plt.close()

# Insight & Rekomendasi
st.divider()
st.subheader("💡 Kesimpulan & Rekomendasi")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### 📌 Kesimpulan 1 — Pendapatan")
    st.info(
        "**Health & Beauty** adalah kategori dengan pendapatan tertinggi. "
        "Puncak pendapatan terjadi pada **November 2017** (Black Friday) dengan lonjakan signifikan, "
        "diikuti pertumbuhan stabil di 2018."
    )
    st.markdown("#### 📌 Kesimpulan 2 — Pengiriman")
    st.info(
        "Terdapat **korelasi negatif** antara waktu pengiriman dan review score. "
        "Pelanggan yang menunggu >14 hari memberikan skor rata-rata di bawah 4.0, "
        "menjadikan **14 hari sebagai threshold kritis kepuasan**."
    )

with col_b:
    st.markdown("#### ✅ Rekomendasi Action Item")
    st.success(
        "**1. Fokus Promosi pada Kategori Unggulan & Momen Musiman** \n\n"
        "Alokasikan anggaran iklan lebih besar untuk Health & Beauty, Watches & Gifts, "
        "dan Bed Bath & Table. Jalankan kampanye khusus saat November (Black Friday) dan Januari."
    )
    st.success(
        "**2. Tetapkan SLA Pengiriman Maksimal 14 Hari** \n\n"
        "Tim logistik perlu menjaga standar pengiriman ≤14 hari. "
        "Untuk wilayah terpencil, lakukan komunikasi proaktif dan pertimbangkan mitra logistik tambahan."
    )

st.divider()
st.caption("📊 Dashboard dibuat dengan Streamlit | Data: Olist Brazilian E-Commerce (Kaggle)")
