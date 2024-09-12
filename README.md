**Giải thích các thư mục, file**
- Thư mục **data** là thư mục chứa các dataset 
    - Thư mục **ViMs** là tập dữ liệu ban đầu
    - **data_raw.json** là file đã trích xuất các văn bản từ original của **ViMs**
    - **data_raw.json** được mở rộng từ file **data_raw.json** bổ sung thêm phần summary
    - **vietnamese-stopwords-dash.txt** danh sách các hư từ của tiếng Việt, có định dạng từ ghép là dấu _ (ví dụ: học_sinh)
- Thư mục **models** là thư mục chứa mô hình đã được huấn luyện sẵn
- Thư mục **src** chứa chương trình chính, trong đó:
    + **gui** chứa front-end
    + **api** chứa back-end

**Cách chạy chương trình**
- Giải nén thư mục **source**
- Giải nén thư mục **models** và copy vào thư mục **source**

1. Nếu chạy ở Window
Chạy lệnh 
- pip install -r requirements.txt

Sau đó chạy lệnh
- streamlit run src/gui/gui.py
- fastapi dev src/api/api.py

2. Nếu chạy bằng Docker
Thực hiện lệnh
docker-compose up -d --build

Cả 2 cách đều sẽ chạy trên localhost với port
- Frontend: 8501
- Backend: 8000

**Requiment**
1. Java version 8
2. Python 3.12