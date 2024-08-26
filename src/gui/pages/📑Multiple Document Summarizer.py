import streamlit as st
from utils import api
import asyncio

# ---------- Tạo session state ----------
# API state
if 'api_data_trainning' not in st.session_state:
    st.session_state.api_data_trainning = {
        'finish' : False
    }
# Widget state
if 'btn_result' not in st.session_state:
    st.session_state.btn_result = False
    
# ---------- Chương trình chính ----------
async def main():
    st.title("Tóm tắt đa văn bản tiếng Việt 📑")

    mode_choice = ['Trainning', 'Inference']

    mode = st.selectbox("Chọn chế độ cho chương trình", ['Trainning', 'Inference'], index = None)

    # ====================== Trainning Module ======================
    if mode == mode_choice[0]:
        # Chưa gọi API thì hiện cái vòng tròn lên
        if not st.session_state.api_data_trainning['finish']:
            with st.spinner("Đợi xíu, đang lấy dữ liệu"):
                st.session_state.api_data_trainning['pos_tools'] = await api.get_pos_tools()
                st.session_state.api_data_trainning['word_similarity_tools'] = await api.get_word_similarity_tools()
                st.session_state.api_data_trainning['finish'] = True
                
        st.subheader("Huấn luyện mô hình 🏋🏼‍♂️")
        
        # Đưa vào tập văn bản theo định dạng cho trước
        file_hint_col1, file_hint_col2 = st.columns(2)
        with file_hint_col1:
            st.write("Đưa vào tập văn bảng theo định dạng json")
        with file_hint_col2:
            with st.popover("Bấm vào để xem dịnh dạng json", use_container_width=True):
                st.markdown('''```json
                            [{'topic':'Chủ đề của văn bản',
'content':'Nội dung của văn bản'}]''')
        document_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="document_uploaded")
        
        # -- Chọn tập hư từ, có thể thêm file hoặc là thêm văn bảng hoặc không cần hư từ
        st.write("Đưa vào tập hư từ có từ ghép với dưới dạng _. Ví dụ: ba_ngày")
        stop_word_text_file = st.file_uploader("Tải tệp lên", accept_multiple_files = False, key="stop_words_uploaded")
        
        # -- Chọn tool để thực hiện gán nhãn từ loại
        st.write("Chọn công cụ thực hiện gán nhãn từ loại")
        
        # Gọi api để lấy danh sách các tool có thể sử dụng
        pos_tools = st.selectbox("Chọn công cụ", st.session_state.api_data_trainning['pos_tools'])
        
        # ------ Trainning Topic Model
        st.markdown("#### Phần cấu hình dành cho mô hình chủ đề")
        
        # Chọn ngưỡng cho các từ chủ đề (số lần xuất hiện của từ / số lần xuất hiện của từ core)
        topic_word_threshold = st.number_input("Chọn ngưỡng dành cho từ chủ đề", 0.0, 1.0, step=1.0, format="%.2f")
        topic_word_threshold = round(topic_word_threshold, 2)
        # ------ Trainning PMI 
        st.markdown("#### Phần cấu hình dành cho tính toán độ tương tự của từ")
        word_similarity_tools = st.selectbox("Chọn công cụ", st.session_state.api_data_trainning['word_similarity_tools'])
        
        # Trainning
        if st.button("Bắt đầu huấn luyện"):
            with st.spinner("Đang huấn luyện"):
                try:
                    # TODO: Call API
                    st.success("Đã hoàn thành huấn luyện")
                except:
                    st.error("Có lỗi trong lúc huấn luyện")
                    
    # ====================== Inference Module ======================
    elif mode == mode_choice[1]:
        # ----- Đưa vào tập văn bảng
        # Thêm văn bản
        st.subheader("Tải lên tập văn bản để thực hiện tóm tắt")
        file_hint_col1, file_hint_col2 = st.columns(2)
        with file_hint_col1:
            st.write("Đưa vào tập văn bảng theo định dạng json")
        with file_hint_col2:
            with st.popover("Bấm vào để xem dịnh dạng json", use_container_width=True):
                st.markdown('''```json
                            [{'topic':'Chủ đề của văn bản',
'content':'Nội dung của văn bản'}]''')
        document_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="document_uploaded")
        
        # ----- Đưa vào mô hình chủ đề
        st.subheader("Tải lên mô hình (dạng json)")
        model_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="model_uploaded")
        
        # ----- Nhập các thông số
        st.subheader("Các thông số tóm tắt")
        
        # Tỉ lệ tóm tắt
        r_threshold = st.number_input("Chọn ngưỡng dành cho tỉ lệ tóm tắt", 0.0, 1.0, step=1.0, format="%.2f")
        r_threshold = round(r_threshold, 2)
        
        # Tỉ lệ tương đồng của câu
        similarity_word = st.number_input("Chọn ngưỡng dành cho tỉ lệ tương đồng của câu", 0.0, 1.0, step=1.0, format="%.2f")
        similarity_word = round(similarity_word, 2)
        
        if st.button("Bắt đầu tóm tắt") or st.session_state.btn_result:
            # ----- Kết quả
            # TODO: CALL API
            result = {
                "summary_document":"Con mẹ nó. Nhức đầu vãi",
                "sentences": ["Câu 1", "Câu 2", "Câu 3"],
                "sentences_weight": [0.2, 0.2, 0.6],
                "sentences_similarity": [["s1", "s2", 2], ["s1", "s3", 1]],
                "metric_info": {
                    "ROGUE-2": 2.0,
                    "ROGUE-3": 3.0,
                    "ROGUE-n": 4.0 ,
                    "BERTScore": 5.0,
                    "Gemini-Review": "Tương đối ngon"
                }
            }
            st.session_state.btn_result = True
            
            # Style cho disable textarea
            st.markdown("""
            <style>
            .stTextArea [data-baseweb=base-input] [disabled=""]{
                -webkit-text-fill-color: black;
            }
            </style>
            """,unsafe_allow_html=True)
            
            # Văn bản sau khi tóm tắt
            st.subheader("Kết quả tóm tắt văn bản")
            summarized_text = result['summary_document']
            st.text_area("",value=summarized_text,height=300,disabled=True)

            # Tải tập tin tóm tắt
            st.download_button("Tải về nội dung tóm tắt", summarized_text)
                
            # -- Tab danh sách các câu
            st.subheader("Danh sách câu")

            # Sample tabs
            tab1, tab2, tab3, tab4 = st.tabs(["Danh sách câu", "Thông tin câu", "Thông tin độ tương đồng", "Thông tin các độ đo"])

            with tab1:
                sentences = result["sentences"]

                for i, sentence in enumerate(sentences):
                    # font_large = f'<p style="font-size: 24px;"></p>'
                    font_large = f'{i + 1}. {sentence}'
                    st.markdown(font_large, unsafe_allow_html=False)

            # -- Tab thông tin của câu (trọng số)
            with tab2:
                st.write("Thông tin câu...")

            # -- Tab thông tin độ tương đồng
            with tab3:
                st.write("Thông tin độ tương đồng...")
            
            # -- Tab thông tin độ đo (ROGUE, ....)
            with tab4:
                st.write("Thông tin các độ đo")


    # TODO: CRAWL MODE
    # elif mode == mode_choice[2]:
    #     st.subheader("Hé lô, this is spider")

if __name__ == "__main__":
    asyncio.run(main())