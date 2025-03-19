import os
import pymysql
import csv

# MySQL 연결 설정
db_config = {
    "host": "127.0.0.1",       # MySQL 서버 호스트
    "user": "GoToHome",   # MySQL 사용자 이름
    "password": "skn1234", # MySQL 비밀번호
    "database": "HomeGenie"  # 대상 데이터베이스 이름
}

def insert_data_district():
    # CSV 파일 경로 설정
    DATA_PATH = "static/data/dataset/final_csv/"
    csv_file_path = os.path.join(DATA_PATH, "District.csv")

    # MySQL 연결
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # 테이블 이름
    table_name = "District"

    # CSV 파일 읽고 데이터 삽입
    try:
        with open(csv_file_path, mode="r", encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # 헤더 스킵
            
            # INSERT 쿼리 생성
            query = f"INSERT INTO {table_name} (district_name) VALUES (%s)"
            
            # 데이터 삽입
            for row in csv_reader:
                mapped_row = (row[0])  # 순서 매핑
                cursor.execute(query, mapped_row)
        
        # 변경사항 커밋
        connection.commit()
        print("Data successfully inserted into MySQL table.")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()

    finally:
        # 연결 종료
        cursor.close()
        connection.close()