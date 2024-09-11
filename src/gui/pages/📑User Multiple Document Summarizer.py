import json
import streamlit as st
import pandas as pd
import asyncio

from utils import api

st.set_page_config(
    layout="wide"
)

# ---------- Tạo session state ----------
# API state
if 'api_data_trainning' not in st.session_state:
    st.session_state.api_data_trainning = {
        'finish' : False
    }
# API state
if 'api_data_inference' not in st.session_state:
    st.session_state.api_data_inference = {
        'finish' : False
    }
# Widget state
if 'btn_result' not in st.session_state:
    st.session_state.btn_result = False
    
# ---------- Chương trình chính ----------
async def main():
    st.title("Tóm tắt đa văn bản tiếng Việt 📑")
    
    # ----- Đưa vào tập văn bảng
    # Style cho disable textarea
    st.markdown("""
            <style>
            .stTextArea [data-baseweb=base-input] [disabled=""]{
                -webkit-text-fill-color: black;
            }
            </style>
            """,unsafe_allow_html=True)
    # Thêm văn bản
    st.subheader("Tải lên tập văn bản để thực hiện tóm tắt")
    documents = st.file_uploader("Tải tệp lên", accept_multiple_files= True, key="document_uploaded")
    # Tỉ lệ tóm tắt
    r_threshold = st.number_input("Chọn độ nén (tỉ lệ tóm tắt)", 0.0, 1.0, step=1.0, format="%.2f")
    r_threshold = round(r_threshold, 2)
    
    # Chọn mô hình
    choice_model = st.selectbox("Chọn mô hình", ["Mô hình tóm tắt 1.0"])
    
    if st.button("Bắt đầu tóm tắt") or st.session_state.btn_result:
        # ----- Kết quả
        with st.spinner("Đang tiến hành tóm tắt văn bản"):
            result = await api.summary(documents,
                                        {'r_threshold':r_threshold, 'choice_model': choice_model})
            st.session_state.btn_result = True
            
            # Văn bản sau khi tóm tắt
            st.subheader("Kết quả tóm tắt văn bản")
            summarized_text = result['summary_document']
            st.text_area("",value=summarized_text,height=300,disabled=True)

            # Tải tập tin tóm tắt
            st.download_button("Tải về nội dung tóm tắt", summarized_text)
    
if __name__ == "__main__":
    asyncio.run(main())