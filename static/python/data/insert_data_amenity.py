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

def insert_data_amenity():
    # CSV 파일 경로 설정
    DATA_PATH = "static/data/dataset/final_csv/"
    csv_file_path = os.path.join(DATA_PATH, "Amenity.csv")

    # MySQL 연결
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    # 테이블 이름
    table_name = "Amenity"

    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # 헤더 스킵
            
            for row in csv_reader:
                if row[2].strip():  # title이 있는 경우
                    if row[4].strip(): # 위도 있는 경우
                        query = f"INSERT INTO {table_name} (amenity_type1, amenity_type2, title, amenity_lat, amenity_lon) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(query, (row[0], row[1], row[2], row[4], row[5]))
                    else:  # 위도 없는 경우
                        query = f"INSERT INTO {table_name} (amenity_type1, amenity_type2, title, street_address) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (row[0], row[1], row[2], row[3]))
                else: # title이 없는 경우
                    if row[4].strip(): # 위도 있는 경우
                        query = f"INSERT INTO {table_name} (amenity_type1, amenity_type2, amenity_lat, amenity_lon) VALUES (%s, %s, %s, %s)"
                        cursor.execute(query, (row[0], row[1], row[4], row[5]))
                    else:  # 위도 없는 경우
                        query = f"INSERT INTO {table_name} (amenity_type1, amenity_type2, street_address) VALUES (%s, %s, %s)"
                        cursor.execute(query, (row[0], row[1], row[3]))

        
        # 변경사항 커밋
        connection.commit()
        print("Data successfully inserted into MySQL table.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Failed row:", row if 'row' in locals() else "No row information")
        connection.rollback()

    finally:
        # 연결 종료
        cursor.close()
        connection.close()