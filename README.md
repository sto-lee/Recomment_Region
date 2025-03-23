# 지역 추천 프로젝트

> 서울에서 자취하고자 하는 20~30대 사용자를 타겟으로 하는 지역 추천 시스템을 구축하는 토이 프로젝트입니다.

기술 스택
- front-end: javascript
- back-end: django
- css: tailwind-css
- map api: kakao map

## 추천 시스템 방식
- 데이터 분석을 통한 추천 유형을 나누고, 각 유형 별 가중치를 부과하여 추천을 진행

### 1. 추천 유형
- 편의시설 우선: 편의시설(60%), 시세(30%), 안전(5%), 인구통계(5%)
- 시세 우선: 시세(50%), 편의시설(30%), 안전(15%), 인구통계(5%)
- 안전 우선: 안전(40%), 편의시설(30%), 시세(25%), 인구통계(5%)
- 사용자 지정: 사용자가 각 요소의 가중치를 직접 설정

### 2. 평가 요소

#### 2.1 편의시설 점수
- 선호하는 시설에 대해 가중치 부여
- 500m 이내 시설(1.5배 가중치)과 1km 이내 시설(0.5배 가중치) 고려
- 시설까지의 평균 거리 반영

#### 2.2 안전 점수
- 구별 범죄율 데이터 활용
- CCTV 밀도 반영 (구역 면적당 CCTV 수)
- 성별에 따른 가중치 적용 (여성의 경우 1.2배)

#### 2.3 시세 점수
- 전세/월세 선택에 따른 차별화된 평가
- 월세의 경우: 월세(30%), 보증금(30%), 월세/보증금 비율(20%), 거래량(20%)
- 전세의 경우: 보증금(80%), 거래량(20%)

#### 2.4 인구통계 점수
- 사용자 연령대와 해당 지역 연령대 분포 매칭
- 20대의 경우 추가 가중치(1.2배) 부여

### 3. 결과 제공
- 점수 기반 상위 10개 지역 추천
- 구 단위 및 동 단위 정보 제공
- 위도/경도 좌표 정보 포함