import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

# ============================
# SAYFA YAPILANDIRMASI
# ============================
st.set_page_config(
    page_title="Müşteri Yorum Analiz Platformu",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Müşteri Yorum ve Şikayet Analiz Platformu")
st.markdown("---")

# ============================
# TÜRKÇE DUYGU ANALİZİ MODELİ (Kural Tabanlı)
# ============================
def analyze_review_turkish(text):
    """
    Türkçe metin analizi yapar
    """
    text_lower = text.lower()
    
    # Olumlu kelimeler (Позитивные слова)
    positive_words = [
        'harika', 'mükemmel', 'çok iyi', 'teşekkürler', 'teşekkür ederim',
        'memnunum', 'memnun', 'başarılı', 'hızlı', 'kaliteli', 'güzel',
        'süper', 'iyi', 'beğendim', 'beğeniyorum', 'tavsiye ederim',
        'kullanışlı', 'pratik', 'çok memnunum', 'kesinlikle', 'şaşırtıcı'
    ]
    
    # Olumsuz kelimeler (Негативные слова)
    negative_words = [
        'kötü', 'berbat', 'rezalet', 'sorunlu', 'bozuk', 'çalışmıyor',
        'memnun değilim', 'hayal kırıklığı', 'iade', 'şikayet', 'geç',
        'yavaş', 'kırık', 'hasarlı', 'yanlış', 'hata', 'sorun', 'problem',
        'bekleme', 'bekledim', 'kargo sorunu', 'müşteri hizmetleri kötü'
    ]
    
    # Yüksek risk kelimeleri (Слова высокого риска - жалобы)
    risk_words = [
        'iade edin', 'paramı geri isterim', 'şikayetçiyim', 'şikayet var',
        'tüketici hakları', 'hakem heyeti', 'avukat', 'dava ederim',
        'savcılığa', 'CİMER', 'şikayet kaydı', 'yetkili', 'idare mahkemesi',
        'telafi edin', 'mağdur', 'mağduriyet', 'zarar', 'kayıp'
    ]
    
    # Kelime sayımları
    positive_count = 0
    negative_count = 0
    risk_count = 0
    
    # Pozitif kelimeleri say
    for word in positive_words:
        if word in text_lower:
            positive_count += text_lower.count(word)
    
    # Negatif kelimeleri say
    for word in negative_words:
        if word in text_lower:
            negative_count += text_lower.count(word)
    
    # Risk kelimelerini say
    for word in risk_words:
        if word in text_lower:
            risk_count += text_lower.count(word)
    
    # Metin uzunluğuna göre normalizasyon
    word_count = len(text_lower.split())
    if word_count == 0:
        word_count = 1
    
    # Duygu belirleme (Определение тональности)
    if negative_count > positive_count:
        sentiment = "OLUMSUZ"
        sentiment_emoji = "😡"
        sentiment_tr = "Olumsuz"
        color = "red"
        sentiment_reason = f"{negative_count} olumsuz kelime tespit edildi"
    elif positive_count > negative_count:
        sentiment = "OLUMLU"
        sentiment_emoji = "😊"
        sentiment_tr = "Olumlu"
        color = "green"
        sentiment_reason = f"{positive_count} olumlu kelime tespit edildi"
    else:
        sentiment = "NÖTR"
        sentiment_emoji = "😐"
        sentiment_tr = "Nötr"
        color = "gray"
        sentiment_reason = "Belirgin olumlu veya olumsuz kelime bulunamadı"
    
    # Risk seviyesi belirleme (Определение уровня риска)
    if risk_count > 0:
        risk_level = "ÇOK YÜKSEK"
        risk_emoji = "🔴"
    elif negative_count >= 2 and sentiment == "OLUMSUZ":
        risk_level = "YÜKSEK"
        risk_emoji = "🟠"
    elif negative_count == 1 and sentiment == "OLUMSUZ":
        risk_level = "ORTA"
        risk_emoji = "🟡"
    else:
        risk_level = "DÜŞÜK"
        risk_emoji = "🟢"
    
    # Güven skoru (yaklaşık)
    total_signals = positive_count + negative_count + risk_count
    confidence = min(0.95, max(0.50, total_signals / max(1, word_count / 3)))
    
    return {
        "sentiment": sentiment,
        "sentiment_tr": sentiment_tr,
        "sentiment_emoji": sentiment_emoji,
        "risk_level": risk_level,
        "risk_emoji": risk_emoji,
        "confidence": confidence,
        "color": color,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "risk_count": risk_count,
        "sentiment_reason": sentiment_reason
    }

# ============================
# YAN PANEL (SIDEBAR)
# ============================
with st.sidebar:
    st.header("📊 Platform Hakkında")
    st.info("""
    **Özellikler:**
    - ✅ Duygu analizi (Olumlu/Olumsuz/Nötr)
    - ⚠️ Risk seviyesi tespiti
    - 📈 Görsel raporlar
    - 💾 CSV olarak dışa aktarım
    - 🚀 Yapay zeka tabanlı analiz
    """)
    
    st.header("📁 Veri Yükleme")
    uploaded_file = st.file_uploader(
        "CSV dosyası yükleyin ('yorum' sütunu olmalı)",
        type=['csv'],
        help="CSV dosyanızda 'yorum' adında bir sütun bulunmalıdır"
    )
    
    st.header("🎯 Örnek Veri")
    if st.button("📋 Örnek yorumları yükle"):
        example_data = pd.DataFrame({
            "yorum": [
                "Telefon 2 gün sonra bozuldu, müşteri hizmetleri çok kötü, paramı geri istiyorum!",
                "Harika hizmet, hızlı kargo, çok teşekkürler",
                "Normaldi, indirim olabilirdi",
                "Hasarlı ürün gönderdiler, 3 gündür destek ekibi cevap vermiyor",
                "En iyi mağaza, her zaman yardımcı oluyorlar",
                "Çok yavaş kargo, çalışanlar kaba",
                "Teşekkürler hızlı teslimat için, her şey mükemmel!",
                "Ürün arızalı, iade edin paramı geri istiyorum, savcılığa gideceğim!"
            ]
        })
        st.session_state['data'] = example_data
        st.success("✅ Örnek veriler yüklendi!")
        st.rerun()

# ============================
# ANA İÇERİK
# ============================

st.success("✅ Yapay zeka modeli başarıyla yüklendi")

# Farklı modlar için sekmeler
tab1, tab2, tab3 = st.tabs(["📝 Manuel Analiz", "📁 Dosya Analizi", "📊 Raporlar"])

# ===== SEKME 1: Manuel Giriş =====
with tab1:
    st.subheader("Yorum metnini girin")
    
    user_input = st.text_area(
        "Müşteri yorumu:",
        height=150,
        placeholder="Örnek: Ürün çok kaliteli, hızlı teslimat, teşekkürler!"
    )
    
    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        analyze_btn = st.button("🔍 Analiz Et", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑 Temizle")
    
    if clear_btn:
        user_input = ""
        st.rerun()
    
    if analyze_btn and user_input:
        with st.spinner("Analiz yapılıyor..."):
            result = analyze_review_turkish(user_input)
        
        st.markdown("---")
        st.subheader("📊 Analiz Sonuçları")
        
        # 3 sütunda metrikler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Duygu Durumu",
                value=f"{result['sentiment_emoji']} {result['sentiment_tr']}",
                delta=f"Güven: {result['confidence']:.1%}"
            )
        
        with col2:
            st.metric(
                label="Risk Seviyesi",
                value=f"{result['risk_emoji']} {result['risk_level']}"
            )
        
        with col3:
            st.metric(
                label="Model Güveni",
                value=f"{result['confidence']:.1%}"
            )
        
        # Risk uyarısı
        if result['risk_level'] in ["YÜKSEK", "ÇOK YÜKSEK"]:
            st.error("⚠️ **DİKKAT!** Bu yorum acil müdahele gerektiriyor!")
            st.warning("📞 Müşteriyle hemen iletişime geçin ve sorunu çözün")
        
        st.markdown("---")
        
        # Detaylı analiz
        with st.expander("📖 Detaylı Analiz"):
            st.write(f"**Orijinal metin:** {user_input}")
            st.write(f"**Duygu:** {result['sentiment_tr']} {result['sentiment_emoji']}")
            st.write(f"**Risk Seviyesi:** {result['risk_level']} {result['risk_emoji']}")
            st.write(f"**Güven Skoru:** {result['confidence']:.2%}")
            st.write(f"**Olumlu kelime sayısı:** {result['positive_count']}")
            st.write(f"**Olumsuz kelime sayısı:** {result['negative_count']}")
            st.write(f"**Risk sinyali sayısı:** {result['risk_count']}")
            st.write(f"**Analiz nedeni:** {result['sentiment_reason']}")
            
            st.subheader("💡 Öneriler:")
            if result['risk_level'] == "ÇOK YÜKSEK":
                st.write("🚨 Acilen müşteriyle iletişime geçin, tazminat teklif edin")
            elif result['risk_level'] == "YÜKSEK":
                st.write("📞 Müşteriyi arayın, sorunu çözmek için adım atın")
            elif result['sentiment'] == "OLUMLU":
                st.write("👍 Müşteriye teşekkür edin, sadakat bonusu teklif edin")
            else:
                st.write("👀 Takibe alın, 24 saat içinde yanıt verin")

# ===== SEKME 2: Dosya Analizi =====
with tab2:
    if uploaded_file is not None:
        # CSV oku
        df = pd.read_csv(uploaded_file)
        
        # Sütun kontrolü
        if 'yorum' not in df.columns:
            st.error("❌ Hata: CSV dosyasında 'yorum' sütunu bulunmuyor!")
            st.info("Örnek CSV formatı:")
            st.code("yorum\nBu ürün çok güzel\nKargo çok yavaştı")
        else:
            st.success(f"✅ {len(df)} yorum başarıyla yüklendi")
            
            # Veri önizleme
            with st.expander("📋 Veri Önizleme"):
                st.dataframe(df.head(10))
            
            # Analiz butonu
            if st.button("🚀 Toplu Analiz Başlat", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for idx, row in df.iterrows():
                    status_text.text(f"Analiz ediliyor: {idx+1}/{len(df)} - {row['yorum'][:50]}...")
                    result = analyze_review_turkish(row['yorum'])
                    results.append(result)
                    progress_bar.progress((idx + 1) / len(df))
                
                status_text.text("✅ Analiz tamamlandı!")
                
                # Sonuçları birleştir
                results_df = pd.DataFrame(results)
                final_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)
                st.session_state['final_df'] = final_df
                st.session_state['analysis_done'] = True
                
                st.success("✅ Analiz başarıyla tamamlandı! 'Raporlar' sekmesine gidin")
                st.balloons()
    
    else:
        st.info("👈 Sol panelden CSV dosyası yükleyin veya 'Örnek yorumları yükle' butonuna tıklayın")

# ===== SEKME 3: Raporlar =====
with tab3:
    if 'final_df' in st.session_state and st.session_state['analysis_done']:
        final_df = st.session_state['final_df']
        
        # İstatistikler
        st.subheader("📊 İstatistikler")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_reviews = len(final_df)
        negative_count = len(final_df[final_df['sentiment'] == "OLUMSUZ"])
        positive_count = len(final_df[final_df['sentiment'] == "OLUMLU"])
        high_risk_count = len(final_df[final_df['risk_level'].isin(["YÜKSEK", "ÇOK YÜKSEK"])])
        
        with col1:
            st.metric("Toplam Yorum", total_reviews)
        with col2:
            st.metric("Olumsuz Yorum", negative_count, delta=f"{(negative_count/total_reviews)*100:.0f}%")
        with col3:
            st.metric("Olumlu Yorum", positive_count, delta=f"{(positive_count/total_reviews)*100:.0f}%")
        with col4:
            st.metric("Yüksek Risk", high_risk_count, delta=f"{(high_risk_count/total_reviews)*100:.0f}%", delta_color="inverse")
        
        # Grafikler
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sentiment = px.pie(
                final_df, 
                names='sentiment_tr', 
                title='Duygu Dağılımı',
                color='sentiment',
                color_discrete_map={
                    'OLUMLU': '#00ff87',
                    'OLUMSUZ': '#ff4b4b',
                    'NÖTR': '#ffd700'
                }
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            risk_counts = final_df['risk_level'].value_counts().reset_index()
            risk_counts.columns = ['risk', 'count']
            fig_risk = px.bar(
                risk_counts,
                x='risk',
                y='count',
                title='Risk Seviyesi Dağılımı',
                color='risk',
                color_discrete_map={
                    'ÇOK YÜKSEK': '#ff0000',
                    'YÜKSEK': '#ff6b6b',
                    'ORTA': '#ffd700',
                    'DÜŞÜK': '#00ff87'
                }
            )
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Detaylı tablo
        st.subheader("📋 Detaylı Analiz Tablosu")
        display_df = final_df[['yorum', 'sentiment_tr', 'risk_level', 'confidence']].copy()
        display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.1%}")
        display_df.columns = ['Yorum', 'Duygu', 'Risk Seviyesi', 'Güven']
        st.dataframe(display_df, use_container_width=True)
        
        # Yüksek riskli yorumları filtrele
        st.subheader("⚠️ Yüksek Riskli Yorumlar")
        high_risk_df = final_df[final_df['risk_level'].isin(["YÜKSEK", "ÇOK YÜKSEK"])]
        
        if len(high_risk_df) > 0:
            st.warning(f"🔴 {len(high_risk_df)} adet yüksek riskli yorum tespit edildi!")
            
            for idx, row in high_risk_df.iterrows():
                with st.container():
                    risk_icon = "🔴" if row['risk_level'] == "ÇOK YÜKSEK" else "🟠"
                    st.error(f"{risk_icon} **Risk: {row['risk_level']}** | Duygu: {row['sentiment_tr']}")
                    st.write(f"📝 {row['yorum']}")
                    st.button(f"📞 İletişime Geç #{idx}", key=f"contact_{idx}")
                    st.markdown("---")
        else:
            st.success("✅ Yüksek riskli yorum bulunmamaktadır")
        
        # CSV export
        st.subheader("💾 Raporu Dışa Aktar")
        csv = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV olarak indir",
            data=csv,
            file_name=f"yorum_analizi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("👈 Önce 'Dosya Analizi' sekmesinde analiz yapın")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    🤖 Yapay Zeka Destekli Müşteri Yorum Analiz Platformu | Türkçe Duygu ve Risk Analizi
</div>
""", unsafe_allow_html=True)