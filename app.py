import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="Dükkan Gelir-Gider & P&L Takibi", page_icon="🍕", layout="wide")

# Veri Saklama (Session State)
if "giderler" not in st.session_state:
    st.session_state.giderler = pd.DataFrame(columns=["Tarih", "Kategori", "Tutar (TL)", "Açıklama"])

if "satislar" not in st.session_state:
    st.session_state.satislar = pd.DataFrame(columns=["Tarih", "Ödeme Tipi", "Tutar (TL)", "Açıklama"])

# Başlık
st.title("🍕 Dükkan Gelir - Gider & P&L Takip Paneli")
st.markdown("---")

# Sol Menü (Veri Girişi)
st.sidebar.header("📝 Veri Girişi")
islem_tipi = st.sidebar.radio("İşlem Türü", ["Gider Ekle", "Satış (Ciro) Ekle"])

tarih = st.sidebar.date_input("Tarih", datetime.today())
tutar = st.sidebar.number_input("Tutar (TL)", min_value=0.0, step=50.0, format="%.2f")

if islem_tipi == "Gider Ekle":
    kategori = st.sidebar.selectbox("Gider Kategorisi", ["Hammadde (Un/Peynir/Sebze vb.)", "Fatura (Elektrik/Su/Gaz)", "Kira", "Personel / Maaş", "Pazarlama / Reklam", "Diğer"])
    aciklama = st.sidebar.text_input("Açıklama (Örn: 2 Çuval Un, Kasap)")
    
    if st.sidebar.button("➕ Gider Kaydet", use_container_width=True):
        if tutar > 0:
            yeni_gider = pd.DataFrame([{"Tarih": tarih, "Kategori": kategori, "Tutar (TL)": tutar, "Açıklama": aciklama}])
            st.session_state.giderler = pd.concat([st.session_state.giderler, yeni_gider], ignore_index=True)
            st.sidebar.success("Gider başarıyla eklendi!")
        else:
            st.sidebar.warning("Lütfen 0'dan büyük bir tutar girin.")

else:
    odeme_tipi = st.sidebar.selectbox("Satış Tipi", ["Kredi Kartı / POS", "Nakit", "Yemek Sepeti / Getir / Trendyol", "Diğer"])
    aciklama = st.sidebar.text_input("Açıklama (Örn: Gün Sonu Ciro)")
    
    if st.sidebar.button("💰 Satış Kaydet", use_container_width=True):
        if tutar > 0:
            yeni_satis = pd.DataFrame([{"Tarih": tarih, "Ödeme Tipi": odeme_tipi, "Tutar (TL)": tutar, "Açıklama": aciklama}])
            st.session_state.satislar = pd.concat([st.session_state.satislar, yeni_satis], ignore_index=True)
            st.sidebar.success("Satış başarıyla eklendi!")
        else:
            st.sidebar.warning("Lütfen 0'dan büyük bir tutar girin.")

# METRİKLER VE P&L HESAPLAMA
toplam_satis = st.session_state.satislar["Tutar (TL)"].sum() if not st.session_state.satislar.empty else 0.0
toplam_gider = st.session_state.giderler["Tutar (TL)"].sum() if not st.session_state.giderler.empty else 0.0
net_kar = toplam_satis - toplam_gider

kar_marji = (net_kar / toplam_satis * 100) if toplam_satis > 0 else 0.0

# Üst Özet Paneli
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="💵 Toplam Satış (Ciro)", value=f"{toplam_satis:,.2f} TL")

with col2:
    st.metric(label="💸 Toplam Gider", value=f"{toplam_gider:,.2f} TL")

with col3:
    st.metric(
        label="📈 Net Kâr / Zarar", 
        value=f"{net_kar:,.2f} TL", 
        delta=f"{net_kar:,.2f} TL",
        delta_color="normal" if net_kar >= 0 else "inverse"
    )

with col4:
    st.metric(
        label="📊 Kâr Marjı (%)", 
        value=f"%{kar_marji:.1f}",
        delta=f"%{kar_marji:.1f}" if kar_marji >= 0 else f"-%{abs(kar_marji):.1f}"
    )

st.markdown("---")

# Grafik ve Tablo Alanı
tab1, tab2, tab3 = st.tabs(["📊 P&L ve Analiz", "📋 Gider Listesi", "💰 Satış Listesi"])

with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Giderlerin Kategorilere Dağılımı")
        if not st.session_state.giderler.empty:
            fig_gider = px.pie(
                st.session_state.giderler, 
                values="Tutar (TL)", 
                names="Kategori", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_gider, use_container_width=True)
        else:
            st.info("Henüz gider kaydı bulunmuyor.")
            
    with col_g2:
        st.subheader("Satış Yöntemleri Dağılımı")
        if not st.session_state.satislar.empty:
            fig_satis = px.pie(
                st.session_state.satislar, 
                values="Tutar (TL)", 
                names="Ödeme Tipi", 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_satis, use_container_width=True)
        else:
            st.info("Henüz satış kaydı bulunmuyor.")

with tab2:
    st.subheader("Girilen Giderler")
    st.dataframe(st.session_state.giderler, use_container_width=True)

with tab3:
    st.subheader("Girilen Satışlar")
    st.dataframe(st.session_state.satislar, use_container_width=True)
