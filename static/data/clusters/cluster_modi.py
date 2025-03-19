import pandas as pd

# CSV 파일 읽기
df = pd.read_csv('all_clusters.csv', encoding='cp949')

print("중복 제거 전 데이터 수:", len(df))

# 모든 컬럼의 값이 동일한 중복 행 제거
df_unique = df.drop_duplicates(subset=['위도', '경도', '클러스터내마커수', '줌레벨'], keep='first')

print("중복 제거 후 데이터 수:", len(df_unique))

# 결과를 다시 CSV 파일로 저장
df_unique.to_csv('all_clusters.csv', index=False, encoding='cp949')

print("중복이 제거된 데이터가 저장되었습니다.")



