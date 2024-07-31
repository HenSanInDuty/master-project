import json
import os
import time
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import streamlit as st
import google.generativeai as genai
from tqdm import tqdm

st.title("Phân tích dữ liệu")
# Khởi tạo các biến session 
# data_input giữ lại giá trị trong khi đánh nhãn
if 'data_input' not in st.session_state:
    st.session_state.data_input = None

# progress_num là dùng để đi đến dòng tiếp theo trong tính năng đánh nhãn
if 'progress_num' not in st.session_state:
    st.session_state.progress_num = 0

# btn_label_activation là dùng để disable input "Nhập những cột bạn muốn đánh nhãn" sau khi nhập
if 'btn_label_activation' not in st.session_state:
    st.session_state.btn_label_activation = False

# Check xem thử nút "Bắt đầu đánh nhãn" có click hay chưa
if 'clicked_labeld_btn' not in st.session_state:
    st.session_state.clicked_labeld_btn = 0

def clicked_labeld_btn():
    st.session_state.progress_num = 0
    st.session_state.clicked_labeld_btn = 1
    
# Lấy thông tin của thư mục dự án gốc
working_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

features = ["Thống kê", "Đánh nhãn"]
choiced_feature = st.selectbox("Chọn chức năng", features, index = None)

if choiced_feature == features[0]:
    folder_data_path = f"{working_dir}\\data\\processed"

    # Liệt kê các tập tin trong thư mục
    files = [f for f in os.listdir(folder_data_path) if f.endswith(".csv")]

    selected_file = st.selectbox("Select a file", files, index=None)

    if selected_file: 
        file_path = os.path.join(folder_data_path, selected_file)
        # đọc file
        df = pd.read_csv(file_path)
        
        col1, col2 = st.columns(2)
        
        columns = df.columns.tolist()
        
        with col1:
            st.write("")
            st.write(df.head())
            
        with col2:
            
            plot_list = ["Distribution", "Pie"]
            
            selected_plot = st.selectbox("Chọn loại biểu đồ", options=plot_list, index=None)
            
            x_axis = st.selectbox("Chọn chiều X", options=columns + ["None"])
        
            st.write("Lựa chọn của bạn bao gồm")
            selected_cl1, selected_cl2 = st.columns(2)
            
            with selected_cl1:
                st.write(f"Biểu đồ: {selected_plot}")
            
            with selected_cl2:
                st.write(f"Cột dữ liệu là: {x_axis}")
            
        # Nếu biểu đồ là Histogram
        if selected_plot == plot_list[0]:
            if st.button("Tạo biểu đồ"):
                n_bins = 10
                fig, ax = plt.subplots()
                df[x_axis].plot(kind='hist', bins=n_bins, density=True, color='#6cc7c9')
                df[x_axis].plot(kind='kde', color='#dc8b8c')
                ax.set_xlabel(x_axis)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Histograms for {x_axis}')
                ax.set_xlim(0,10)

                # Tính các số phân vị
                quant_25, quant_50, quant_75 = df[x_axis].quantile(0.25), df[x_axis].quantile(0.5), df[x_axis].quantile(0.75)
                
                distribution_col1, distribution_col2 = st.columns(2)
                
                with distribution_col1:
                    st.pyplot(plt.gcf())
                    
                with distribution_col2:
                    st.text(f"Phân vị 1: {quant_25}")
                    st.text(f"Phân vị 2: {quant_50}")
                    st.text(f"Phân vị 3: {quant_75}")

        # Nếu biểu đồ là biểu đồ tròn
        elif selected_plot == plot_list[1]:
            # Hàm hiện biểu đồ tròn
            def pie_chart_show(count, label, title="", print_summary = False):
                # Đổi lại thành kiểu list hết
                count = list(count)
                label = list(label)
                
                # Hiển thị biểu đồ tròn
                colors = ['#dc8b8c', '#d14e5f', '#831a3d', '#fff28b', '#f7c962', '#f7963e', '#65e0a8', '#448c6d', '#095071', '#42add5', '#6cc7c9']
                colors.reverse()
                fig, ax = plt.subplots()
                ax.pie(count, 
                    labels=label, 
                    radius=1, 
                    wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' },
                    colors = colors)
                ax.set_title(f"Pie chart for {title}")
                # Chia ra 2 cột, cột trái là hình, cột phải là thống kê
                col1, col2 = st.columns(2)
                
                with col1:
                    # Hiển thị ra màn hình
                    st.pyplot(plt.gcf())
                    
                with col2:
                    # Thống kê theo số liệu
                    total_posting = sum(count)
                    for i in range(len(label)):
                        st.write(f'{label[i]}: {count[i]} ({round((count[i] * 100)/total_posting, 2)}%)')
                        
            # Hàm xử lý tính toán số lượng giá trị và tên
            def calculate_label_and_count(df_columns, top, delimeter = ','):
                # Vì 1 bài đăng sẽ có nhiều ngôn ngữ nên cần phải xử lý một chút
                columns_lc = {}
                for column in df_columns:
                    if not pd.isna(column):
                        # Mỗi ngôn ngữ được cách nhau bởi delemeter
                        split_language = column.split(delimeter)
                        
                        for sl in split_language:
                            if sl in columns_lc.keys():
                                columns_lc[f'{sl}'] += 1
                            else:
                                columns_lc[f'{sl}'] = 1

                columns_lc = sorted(columns_lc.items(), key=lambda x:x[1], reverse=True)

                count = []
                label = []

                for i in range(top):
                    count.append(columns_lc[i][1])
                    label.append(columns_lc[i][0])

                # Thêm phần những ngôn ngữ khác sau top 10
                count.append(0)
                label.append('Other')

                for i in range(top, len(columns_lc)):
                    count[top] += columns_lc[i][1]
                    
                return label,count
            
            # Xử lý ở trên màn hình
            top = st.number_input("Chọn top k giá trị để thực hiện vẽ biểu đồ", min_value=1, max_value=11)
            
            if st.button("Tạo biểu đồ"):
                # Lấy ra số lượng ngôn ngữ và tổng của chúng
                label, count = calculate_label_and_count(df[f'{x_axis}'], top)

                # Hiển thị biểu đồ tròn
                pie_chart_show(count, label,title = x_axis, print_summary = True)
        
            
elif choiced_feature == features[1]:
    folder_data_path = f"{working_dir}\\data\\raw"

    # Liệt kê các tập tin trong thư mục
    files = [f for f in os.listdir(folder_data_path) if f.endswith(".csv")]

    selected_file = st.selectbox("Select a file", files, index=None)

    if selected_file: 
        file_path = os.path.join(folder_data_path, selected_file)
        # đọc file
        df = pd.read_csv(file_path)
        st.write("Bạn muốn nhập thêm những cột nào?")
        st.write("Lưu ý: Vui lòng nhập và ngăn cách mỗi cột bằng dấu phẩy và cột không được có khoảng trống")
        
        need_labels = st.text_input("Nhập những cột bạn muốn đánh nhãn")
        file_process_name = st.text_input("Nhập tên file bạn muốn trả về")
        
        method_label = st.selectbox("Bạn muốn dùng phương pháp đánh nhãn nào?", ["Đánh bằng sức người", "Gemini"], index=None)
        
        
        if method_label == "Đánh bằng sức người":
            st.button("Bắt đầu đánh nhãn", on_click=clicked_labeld_btn)
            # Tách cột nhãn theo dấu ,
            need_labels = need_labels.split(",")
            
            # Khởi tạo data input để lưu trữ dữ liệu 
            if st.session_state.data_input == None:
                st.session_state.data_input = [['' for _ in range(len(df))] for _ in range(len(need_labels))]
            
            if st.session_state.clicked_labeld_btn == 1:
                st.session_state.btn_label_activation = True
                
                # Số lượng đánh nhãn
                col1, col2 = st.columns(2)
                with col1:
                    if st.session_state.progress_num < len(df):
                        st.write(f"Dữ liệu thứ {st.session_state.progress_num + 1}/{len(df)}")
                    else:
                        st.write(f"Finish")
                with col2:
                    progress = st.progress(st.session_state.progress_num / len(df))
                
                # Chương trình chính
                main_col1, main_col2 = st.columns([3,1])
                with main_col1:
                    # Lấy ra dòng dữ liệu
                    if st.session_state.progress_num < len(df):
                        data = df[st.session_state.progress_num:st.session_state.progress_num + 1]
                        
                        # In ra dữ liệu của các cột
                        st.markdown(f"👤**JOB_ID:** {data['job_id'].iloc[0]}")
                        st.markdown(f"📌**JOB_TITLE:** {data['job_title'].iloc[0]}")
                        st.markdown(f"🔖**JOB_TAG:** {data['job_tags'].iloc[0]}")
                        st.markdown(f"📝**JOB_REQUEST:**")
                        st.write(data['requests'].iloc[0])
                    
                with main_col2:
                    # Khởi tạo data input để lưu trữ dữ liệu và text input của streamlit
                    text_input = [None for _ in range(len(need_labels))]
                    
                    for i in range(len(need_labels)):
                        need_label = need_labels[i].strip()
                        text_input[i] = st.text_input(need_label, key=f"need_label_{i}")
                        
                    if st.session_state.progress_num < len(df):
                        def next_row():
                            st.session_state.progress_num+=1
                            
                        if st.button("Next Row", on_click=next_row):
                            for i in range(len(need_labels)):
                                st.session_state.data_input[i][st.session_state.progress_num - 1] = text_input[i]
                    else:
                        for i in range(len(need_labels)):
                            st.session_state.data_input[i][st.session_state.progress_num - 1] = text_input[i]
                        # Nếu mà đánh tới cuối file thì dừng và lưu lại
                        new_column = {}
                        for i in range(len(need_labels)):
                            new_column[f'{need_labels[i]}'] = st.session_state.data_input[i]
                            
                        df = df.assign(**new_column)
                        df.to_csv(f"{working_dir}\\data\\processed\\{file_process_name}.csv")
                        
                        def change_finish_state():
                            st.session_state.clicked_labeld_btn = 2
                        st.button("Hoàn thành", on_click=change_finish_state)                
        elif method_label == "Gemini":
            # Test api key: AIzaSyAVZj--laOiadY9F8H_vFB-LWCRw8lUmyQ 
            gemini_key = st.text_input("Điền gemini key api: ", value="AIzaSyAVZj--laOiadY9F8H_vFB-LWCRw8lUmyQ ")
            prompt = '''trích xuất số năm kinh nghiệm, ngôn ngữ lập trình, framework (nếu có), công nghệ chính (như lập trình web hay là ai chẳng hạn), kỹ năng mềm và những công cụ sử dụng sang json với cấu trúc tương tự:
                {
                "experience": "int",
                "industries":[industries1, industries2],
                "languages":[language1, language2],
                "soft-skill":[soft-skill1, soft-skill2],
                "framework":[framework1, framework2],
                "tools":[tool1, tool2]
                }
                Trong đó:
                experience: là số năm kinh nghiệm, lấy giá trị nhỏ nhất nếu có nhiều giá trị, nếu không có giá trị nào thì trả về số 0, không cần phải ghi tiêu đề hay công nghệ. chỉ là một mảng số, không phải object
                industries: là các công nghệ như lập trình ứng dụng web, lập trình ai,...
                languages: là ngôn ngữ lập trình
                soft-skill: kỹ năng mềm như thích ứng nhanh, giải quyết vấn đề,...
                framework: là những framework lập trình như react, spring boot. Nếu không đề cập tới trong câu thì để trống bằng một chuỗi rỗng, tuyệt đối không tự sinh ra bằng cách dựa vào ngôn ngữ lập trình
                tools: những tool như AWS, git, gitlab,...
                Không có giới hạn số lượng phần tử trong mảng và chỉ sử dụng thông tin trong câu, không thêm vào
                Nếu có tiếng Anh thì dịch sang tiếng Việt
                Trả về json không có ```json ở đầu và ``` ở cuối
                Từ đó phân tích câu sau (chỉ cần đưa kết quả của json không cần giải thích):\n'''
                
            text_area = st.text_area("Prompting cho Gemini",value=prompt)
            
            if st.button("Bắt đầu đánh nhãn"):
                # Tách cột nhãn theo dấu ,
                need_labels = need_labels.split(",")
                genai.configure(api_key=gemini_key)
                models = genai.GenerativeModel('gemini-1.5-flash')
                
                
                # Khởi tạo data input để lưu trữ dữ liệu cho các cột nhãn
                text_input = [[] for _ in range(len(need_labels))]
                err = []
                experience = []
                industries = []
                languages = []
                framework = []
                soft_skill = []
                tools = []
                
                for ds in tqdm(df['requests']):
                    content = prompt + ds
                    i = 0
                    try:
                        response = models.generate_content(content).text.split("\n")
                        result_json = json.loads(''.join(response))
                        st.write(result_json)
                        
                        for result_key, result_value in result_json.items():
                            text_input[i].append(result_value)
                            i+=1
                            # experience.append(result['experience'])
                            # industries.append(";".join(result['industries']))
                            # languages.append(";".join(result['languages']))
                            # framework.append(";".join(result['framework']))
                            # soft_skill.append(";".join(result['soft-skill']))
                            # tools.append(";".join(result['tools']))
                    except Exception as e:
                        for i in range(len(need_labels)):
                            text_input[i].append("")
                        traceback.print_exc()
                        err.append(ds)
                    finally:
                        time.sleep(5)

                # Kết thúc chạy Gemini
                new_assign_column = {}
                for i in range(len(need_labels)):
                    new_assign_column[f'{need_labels[i]}'] = text_input[i]
                df = df.assign(**new_assign_column)
                df.to_csv(f"{working_dir}\\data\\processed\\{file_process_name}.csv")
                
                st.session_state.clicked_labeld_btn = 2
        
        if st.session_state.clicked_labeld_btn == 2:
            st.success(f"Hoàn thành đánh nhãn, vui lòng xem lại file trong thư mục: {working_dir}\\data\\processed")