import streamlit as st

st.title("Tóm tắt đa văn bản tiếng Việt")

# Tải file
st.subheader("Chọn các tập tin để thực hiện tóm tắt")
uploaded_files = st.file_uploader("", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        text_data = bytes_data.decode("utf_8")
    st.text_area("Nội dung tệp", value=text_data, height=300)

# Sample summarized text and related information
st.subheader("Kết quả tóm tắt văn bản")
summarized_text = """Người dân, nhất là cư dân mạng, nếu thiếu cảnh giác sẽ còn tiếp tục bị lừa. Chỉ với email đã được thu thập từ các diễn đàn, chatroom, website. Vì sao bạn dễ bị lừa trên mạng.
"""
st.text_area("",value=summarized_text,height=50)

# Tải tập tin tóm tắt
if st.button("Tải về nội dung tóm tắt"):
    st.write("Đang tải....")

st.subheader("Danh sách câu")

# Sample tabs
tab1, tab2, tab3, tab4 = st.tabs(["Danh sách câu", "Thông tin câu", "Thông tin độ tương đồng", "Thông tin các độ đo"])

with tab1:
    sentences = [
    "Vì sao bạn dễ bị lừa trên mạng?",
    "Hiện tượng lập web kêu gọi đầu tư tài chính ảo trong thời gian vừa qua chỉ là một phần nhỏ trong các mánh lới lừa đảo sử dụng công cụ là internet hiện nay.",
    "Người dân, nhất là cư dân mạng, nếu thiếu cảnh giác sẽ còn tiếp tục bị lừa.",
    "Từ thư điện tử, diễn đàn, website.",
    "Đâu đâu bẫy lừa cũng sẵn sàng úp xuống vì miếng mồi câu mà những tay lừa đảo áp dụng đánh thẳng vào lòng tham của mỗi người.",
    "Mỗi ngày email của bạn có thể nhận hàng trăm thư rác, trong đó có thể có những lá thư 'chúc mừng trúng số' trị giá triệu USD."
    ]

    for i, sentence in enumerate(sentences):
        font_large = f'<p style="font-size: 24px;">{i}. {sentence}</p>'
        st.markdown(font_large, unsafe_allow_html=True)

with tab2:
    st.write("Thông tin câu...")

with tab3:
    st.write("Thông tin độ tương đồng...")

