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

    mode_choice = ['Trainning', 'Inference', 'Evaluate']

    mode = st.selectbox("Chọn chế độ cho chương trình", mode_choice, index = None)

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
                            [{'topic':'Chủ đề của văn bản', 'content':'Nội dung của văn bản'}]''')
        document_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="document_uploaded")
        
        # -- Chọn tập hư từ, có thể thêm file hoặc là thêm văn bảng hoặc không cần hư từ
        st.write("Đưa vào tập hư từ có từ ghép với dưới dạng _. Ví dụ: học_sinh")
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
        word_similarity_tools = st.selectbox("Chọn công cụ", st.session_state.api_data_trainning['word_similarity_tools'], key="word_similarity_tools_trainning")
        
        # Trainning
        if st.button("Bắt đầu huấn luyện"):
            with st.spinner("Đang huấn luyện"):
                try:
                    trainning_option = {
                        'pos_tool': pos_tools,
                        'threshold_core_word': topic_word_threshold,
                        'similarity_calculation_method': word_similarity_tools
                    }
                    result_trainning = await api.trainning(document_uploaded_json, stop_word_text_file, trainning_option)
                    st.success(f"Đã hoàn thành huấn luyện")
                    
                    # # Hiển thị 2 độ đo
                    # st.write("Đánh giá mô hình")
                    # result = pd.DataFrame.from_dict(result_trainning['evaluate'], orient='index', columns=['Max','Min','Mean'])
                    # st.dataframe(result)
                    
                    # Tải mô hình về
                    st.download_button(
                        "Ấn vào để tải mô hình về",
                        data=json.dumps(result_trainning),
                        file_name="topic_model.json",
                        mime="application/json",
                    )
                except Exception as e:
                    st.error("Có lỗi trong lúc huấn luyện")
                    st.error(e)
                    
    # ====================== Inference Module ======================
    elif mode == mode_choice[1]:
        # Chưa gọi API thì hiện cái vòng tròn lên
        if not st.session_state.api_data_inference['finish']:
            with st.spinner("Đợi xíu, đang lấy dữ liệu"):
                st.session_state.api_data_inference['pos_tools'] = await api.get_pos_tools()
                st.session_state.api_data_inference['finish'] = True
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
        
        # -- Chọn tool để thực hiện gán nhãn từ loại
        st.write("Chọn công cụ thực hiện gán nhãn từ loại")
        
        # Gọi api để lấy danh sách các tool có thể sử dụng
        pos_tools = st.selectbox("Chọn công cụ", st.session_state.api_data_inference['pos_tools'])
        
        # ----- Đưa vào mô hình chủ đề
        st.subheader("Tải lên mô hình (dạng json)")
        model_hint_col1, model_hint_col2 = st.columns(2)
        with model_hint_col1:
            st.write("Mô hình có dạng json")
        with model_hint_col2:
            with st.popover("Bấm vào để xem dịnh dạng json", use_container_width=True):
                st.markdown('''```json
{'topic_model':{'chủ đề': [từ cốt lõi]},
'word_similarity':{'type': 'loại công cụ cho độ tương tự từ', 
                    'word_similarity': 'kết quả của công cụ',
                    'stop_words': 'danh sách hư từ cho mô hình'}}''')
        model_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="model_uploaded")
        
        # ----- Nhập các thông số
        st.subheader("Các thông số tóm tắt")
        
        # Tỉ lệ tóm tắt
        r_threshold = st.number_input("Chọn độ nén (tỉ lệ tóm tắt)", 0.0, 1.0, step=1.0, format="%.2f")
        r_threshold = round(r_threshold, 2)
        
        # Comment lại vì không còn dùng nữa -> chuyển qua dùng GA cho bài toán tối ưu
        # # Tỉ lệ tương đồng của câu
        # similarity_word = st.number_input("Chọn ngưỡng dành cho tỉ lệ tương đồng của câu", 0.0, 1.0, step=1.0, format="%.2f")
        # similarity_word = round(similarity_word, 2)
        
        if st.button("Bắt đầu tóm tắt") or st.session_state.btn_result:
            # ----- Kết quả
            with st.spinner("Đang tiến hành tóm tắt văn bản"):
                result = await api.inference(document_uploaded_json,
                                            model_uploaded_json,
                                            {'r_threshold':r_threshold, 'pos_tool':pos_tools})
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
                    
                # ----- Bảng thông tin tóm tắt của văn bản 
                tab1, tab2, tab3 = st.tabs(["Danh sách câu", "Thông tin câu", "Thông tin độ tương đồng"])

                # -- Tab danh sách các câu
                with tab1:
                    sentences = result["sentences"]

                    for i, sentence in enumerate(sentences):
                        # font_large = f'<p style="font-size: 24px;"></p>'
                        font_large = f'{i + 1}. {sentence.replace("\n", "")}'
                        st.markdown(font_large, unsafe_allow_html=False)

                # -- Tab thông tin của câu (trọng số)
                with tab2:
                    ratio_tab2 = [1, 3]
                    # Chia ra làm 2 cột, cột đầu là số thứ tự câu, cột 2 là trọng số của câu
                    header_tab2_col1, header_tab2_col2 = st.columns(ratio_tab2, vertical_alignment="center")
                    with header_tab2_col1:
                        st.write("Câu")
                    with header_tab2_col2:
                        st.write("Trọng số")
                        
                    for i in range(result['number_sentence']):
                        tab2_col1, tab2_col2 = st.columns(ratio_tab2, vertical_alignment="center")
                        with tab2_col1:
                            with st.popover(f"Câu {i+1}"):
                                st.write(result['sentences'][i])
                            
                        with tab2_col2:
                            font_large = f'<p style="font-size: 18px;">{result['sentences_weight'][i]}</p>'
                            st.markdown(font_large, unsafe_allow_html=True)

                # -- Tab thông tin độ tương đồng
                with tab3:
                    ratio_tab3 = [1, 1, 3]
                    # Chia làm 3 cột, cột 1 và 2 là số thứ tự câu, cột 3 là thông tin độ tương đồng
                    header_tab3_col1, header_tab3_col2, header_tab3_col3 = st.columns(ratio_tab3, vertical_alignment="center")
                    with header_tab3_col1:
                        st.write("Câu")
                    with header_tab3_col2:
                        st.write("Câu")
                    with header_tab3_col3:
                        st.write("Độ tương đồng của câu")
                        
                    for i in range(len(result['sentences_similarity'])):
                        index_sentence_1, index_sentence_2, similarity = result['sentences_similarity'][i]
                        tab3_col1, tab3_col2, tab3_col3 = st.columns(ratio_tab3, vertical_alignment="center")
                        with tab3_col1:
                            with st.popover(f"Câu {index_sentence_1 + 1}"):
                                st.write(result['sentences'][index_sentence_1])
                        
                        with tab3_col2:
                            with st.popover(f"Câu {index_sentence_2 + 1}"):
                                st.write(result['sentences'][index_sentence_2])
                            
                        with tab3_col3:
                            font_large = f'<p style="font-size: 18px;">{similarity}</p>'
                            st.markdown(font_large, unsafe_allow_html=True)
                
    # ====================== Evaluation Module ======================
    elif mode == mode_choice[2]:
        # Chưa gọi API thì hiện cái vòng tròn lên
        if not st.session_state.api_data_inference['finish']:
            with st.spinner("Đợi xíu, đang lấy dữ liệu"):
                st.session_state.api_data_inference['pos_tools'] = await api.get_pos_tools()
                st.session_state.api_data_inference['finish'] = True
        # ----- Đưa vào tập văn bảng
        # Thêm văn bản
        st.subheader("Tải lên tập văn bản để thực hiện đánh giá")
        file_hint_col1, file_hint_col2 = st.columns(2)
        with file_hint_col1:
            st.write("Đưa vào tập văn bảng theo định dạng json")
        with file_hint_col2:
            with st.popover("Bấm vào để xem dịnh dạng json", use_container_width=True):
                st.markdown('''```json
[
    {
        'document': [{'topic':'chủ đề của văn bản 1', 'content':'nội dung của văn bản 1'}, ...],
        'summary_content': ['văn bản tóm tắt 1', 'văn bản tóm tắt 2', ...]
    }
]''')
        document_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="document_uploaded")
        
        # -- Chọn tool để thực hiện gán nhãn từ loại
        st.write("Chọn công cụ thực hiện gán nhãn từ loại")
        
        # Gọi api để lấy danh sách các tool có thể sử dụng
        pos_tools = st.selectbox("Chọn công cụ", st.session_state.api_data_inference['pos_tools'])
        
        # ----- Đưa vào mô hình chủ đề
        st.subheader("Tải lên mô hình (dạng json)")
        model_hint_col1, model_hint_col2 = st.columns(2)
        with model_hint_col1:
            st.write("Mô hình có dạng json")
        with model_hint_col2:
            with st.popover("Bấm vào để xem dịnh dạng json", use_container_width=True):
                st.markdown('''```json
{'topic_model':{'chủ đề': [từ cốt lõi]},
'word_similarity':{'type': 'loại công cụ cho độ tương tự từ', 
                    'word_similarity': 'kết quả của công cụ',
                    'stop_words': 'danh sách hư từ cho mô hình'}}''')
        model_uploaded_json = st.file_uploader("Tải tệp lên", accept_multiple_files= False, key="model_uploaded")
        
        # ----- Nhập các thông số
        st.subheader("Các thông số tóm tắt")
        
        # Tỉ lệ tóm tắt
        r_threshold = st.number_input("Chọn độ nén (tỉ lệ tóm tắt)", 0.0, 1.0, step=1.0, format="%.2f")
        r_threshold = round(r_threshold, 2)
        
        if st.button("Bắt đầu đánh giá mô hình"):
            with st.spinner("Đang thực hiện đánh giá"):
                results = await api.evaluate(document_uploaded_json,
                                            model_uploaded_json,
                                            {'r_threshold':r_threshold, 'pos_tool':pos_tools})
                for i in range(len(results)):
                    st.write(f"Với cách tóm tắt thứ {i} thì phương pháp có giá trị của các độ đo như sau:")
                    metric = pd.DataFrame.from_dict(results[i], orient='index', columns=['Max', 'Min', 'Mean'])
                    st.dataframe(metric)
if __name__ == "__main__":
    asyncio.run(main())