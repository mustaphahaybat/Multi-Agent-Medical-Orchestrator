import streamlit as st
import requests
import os

st.set_page_config(page_title="Multi-Specialist AI", layout="wide")

# SIDEBAR: top_k Kontrolü
st.sidebar.title("Ayarlar")
top_k = st.sidebar.slider("Danisilacak Uzman Sayisi (top_k)", 1, 20, 3)

st.title("🏥 Multi-Agent Tibbi Analiz Paneli")

case_input = st.text_area("Vaka Detaylarini Girin:", height=200)

if st.button("Analiz Baslat"):
    if case_input:
        with st.spinner(f"Supervisor {top_k} uzman seciyor ve analizler paralel yapiliyor..."):
            try:
                api_url = os.getenv("API_URL", "http://localhost:8000")
                payload = {"case": case_input, "top_k": top_k}
                response = requests.post(f"{api_url}/run", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analiz Tamamlandi!")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown("### 📝 Nihai Sentez Ozet")
                        st.write(data["final_summary"])
                    with col2:
                        st.markdown("### 🕵️ Secilen Uzmanlar")
                        for s in data["selected"]:
                            st.write(f"✅ {s}")
                else:
                    st.error("API Hatasi!")
            except Exception as e:
                st.error(f"Baglanti Hatasi: {str(e)}")