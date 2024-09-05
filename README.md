**Cách chạy chương trình**
Chạy lệnh 
- pip install -r requirements.txt

Sau đó chạy lệnh
- streamlit run src/gui/gui.py

---------------------------------
Lưu ý: Python phiên bản đang sử dụng là 3.12.4

**Giải thích các file**
- Thư mục **data** là thư mục chứa các dataset 
- Thư mục **notebooks** là chứa các file notebook 
- Thư mục src chứa chương trình chính, trong đó:
    + gui chứa front-end
    + api chứa back-end

**Requiment**
1. Java version 8
2. Scala 2.12
3. sbt 1.4.0
4. Python 3.12

**Pytorch**
Pytorch will have especial install with other
Please follow the line
1. git clone --recursive https://github.com/pytorch/pytorch
2. cd pytorch
3. python setup.py develop