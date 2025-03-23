from django.db import models
import pandas as pd
import json
import os
from django.conf import settings
import re
import numpy as np
from math import radians, sin, cos, sqrt, atan2

class RecommendationInput(models.Model):
    class Meta:
        app_label = 'recommendations'

    TRANSPORT_CHOICES = [
        ('bus', '버스'),
        ('subway', '지하철'),
        ('car', '자가용'),
    ]
    
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
    ]
    
    FACILITY_CHOICES = [
        ('subway', '지하철'),
        ('bus', '버스정류장'),
        ('park_station', '주차장'),
        ('convenience_store', '편의점'),
        ('electric_gas_station', '전기 충전소'),
        ('gas_station', '주유소'),
        ('supermarket', '마트'),
        ('self_laundromat', '셀프 빨래방'),
        ('hospital', '병원'),
        ('police_office', '경찰서'),
        ('public_health_center', '보건소'),
        ('university', '대학교'),
        ('school', '학교'),
        ('education', '교육기관'),
        ('daycare', '어린이집'),
        ('park', '공원'),
        ('fitness', '운동시설'),
        ('theater', '영화관'),
        ('music_room', '노래방'),
        ('pc_room', 'PC방'),
        ('outdorr_sports', '야외 스포츠'),
        ('tax_office', '세무서'),
        ('post_office', '우체국'),
        ('community_center', '주민센터')
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('jeonse', '전세'),
        ('monthly', '월세'),
    ]
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('facility', '편의시설 우선'),
        ('price', '시세 우선'),
        ('safety', '안전 우선'),
        ('custom', '사용자 지정')
    ]
    
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    transport = models.CharField(max_length=10, choices=TRANSPORT_CHOICES)
    property_type = models.CharField(max_length=10, choices=PROPERTY_TYPE_CHOICES)
    desired_location = models.CharField(max_length=100)
    preferred_facilities = models.JSONField()
    
    
    # 시세 범위
    # 전세
    jeonse_deposit_min = models.PositiveIntegerField(null=True, blank=True)  # 전세 보증금 최소
    jeonse_deposit_max = models.PositiveIntegerField(null=True, blank=True)  # 전세 보증금 최대
    
    # 월세
    monthly_deposit_min = models.PositiveIntegerField(null=True, blank=True)  # 월세 보증금 최소
    monthly_deposit_max = models.PositiveIntegerField(null=True, blank=True)  # 월세 보증금 최대
    monthly_rent_min = models.PositiveIntegerField(null=True, blank=True)    # 월세 최소
    monthly_rent_max = models.PositiveIntegerField(null=True, blank=True)    # 월세 최대

    # 추천 유형 필드 추가
    recommendation_type = models.CharField(
        max_length=10, 
        choices=RECOMMENDATION_TYPE_CHOICES,
        default='facility'
    )
    
    # 사용자 지정 가중치 (custom 타입일 때만 사용)
    custom_facility_weight = models.FloatField(null=True, blank=True)
    custom_crime_weight = models.FloatField(null=True, blank=True)
    custom_price_weight = models.FloatField(null=True, blank=True)
    custom_population_weight = models.FloatField(null=True, blank=True)
    desired_location = models.CharField(max_length=100)
    preferred_facilities = models.JSONField()
    
    
    # 시세 범위
    # 전세
    jeonse_deposit_min = models.PositiveIntegerField(null=True, blank=True)  # 전세 보증금 최소
    jeonse_deposit_max = models.PositiveIntegerField(null=True, blank=True)  # 전세 보증금 최대
    
    # 월세
    monthly_deposit_min = models.PositiveIntegerField(null=True, blank=True)  # 월세 보증금 최소
    monthly_deposit_max = models.PositiveIntegerField(null=True, blank=True)  # 월세 보증금 최대
    monthly_rent_min = models.PositiveIntegerField(null=True, blank=True)    # 월세 최소
    monthly_rent_max = models.PositiveIntegerField(null=True, blank=True)    # 월세 최대

    # 추천 유형 필드 추가
    recommendation_type = models.CharField(
        max_length=10, 
        choices=RECOMMENDATION_TYPE_CHOICES,
        default='facility'
    )
    
    # 사용자 지정 가중치 (custom 타입일 때만 사용)
    custom_facility_weight = models.FloatField(null=True, blank=True)
    custom_crime_weight = models.FloatField(null=True, blank=True)
    custom_price_weight = models.FloatField(null=True, blank=True)
    custom_population_weight = models.FloatField(null=True, blank=True)

class Facility(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class RecommendationResult(models.Model):
    input_data = models.ForeignKey(RecommendationInput, on_delete=models.CASCADE)
    recommended_district = models.CharField(max_length=50)  # 구 정보는 유지
    cluster_dong = models.CharField(max_length=50, null=True, blank=True)  # 동 정보 추가
    recommendation_score = models.FloatField()
    cluster_lat = models.FloatField()  # 클러스터 위도
    cluster_lng = models.FloatField()  # 클러스터 경도
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def _get_score_weights(cls, recommendation_type, custom_weights=None):
        """추천 유형에 따른 가중치 반환"""
        if recommendation_type == 'facility':
            return {
                'facility': 0.60,
                'crime': 0.05,
                'price': 0.30,
                'population': 0.05
            }
        elif recommendation_type == 'price':
            return {
                'facility': 0.30,
                'crime': 0.15,
                'price': 0.50,
                'population': 0.05
            }
        elif recommendation_type == 'safety':
            return {
                'facility': 0.30,
                'crime': 0.40,
                'price': 0.25,
                'population': 0.05
            }
        elif recommendation_type == 'custom' and custom_weights:
            return {
                'facility': custom_weights.get('facility', 0.25),
                'crime': custom_weights.get('crime', 0.25),
                'price': custom_weights.get('price', 0.25),
                'population': custom_weights.get('population', 0.25)
            }
        else:
            # 기본 가중치
            return {
                'facility': 0.60,
                'crime': 0.05,
                'price': 0.30,
                'population': 0.05
            }

    @classmethod
    def create_recommendation(cls, user_preferences):
        try:
            # CSV 파일 경로
            csv_path = os.path.join(settings.STATIC_ROOT, 'data', 'clusters', 'all_clusters_updated_with_stats.csv')
            if not os.path.exists(csv_path):
                print(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
                # 다른 경로 시도
                csv_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'clusters', 'all_clusters_updated_with_stats.csv')
                if not os.path.exists(csv_path):
                    print(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
                    return None
            
            # CSV 파일 읽기
            df = pd.read_csv(csv_path)
            
            # 디버깅: 컬럼명 확인
            print("CSV 파일 컬럼명:", df.columns.tolist())
            # 처음 몇 개의 행 출력
            print("CSV 파일 샘플:\n", df.head(1).to_string())
            
            # 1. 편의시설 점수 계산 (기존 코드 유지)
            facility_scores = cls._calculate_facility_score(df, user_preferences)
            
            # 2. 범죄 정보 점수 계산
            crime_scores = cls._calculate_crime_score(df, user_preferences.gender)
            
            # 3. 시세 정보 점수 계산
            price_scores = cls._calculate_price_score(df, user_preferences)
            
            # 4. 인구 밀도 점수 계산
            population_scores = cls._calculate_population_score(df, user_preferences.age)
            
            # 가중치 설정
            custom_weights = None
            if user_preferences.recommendation_type == 'custom':
                custom_weights = {
                    'facility': user_preferences.custom_facility_weight,
                    'crime': user_preferences.custom_crime_weight,
                    'price': user_preferences.custom_price_weight,
                    'population': user_preferences.custom_population_weight
                }
            
            weights = cls._get_score_weights(
                user_preferences.recommendation_type,
                custom_weights
            )

            # 최종 점수 계산 (가중치 적용)
            def calculate_final_score(row):
                facility_score = facility_scores[row.name]
                crime_score = crime_scores[row['district']]
                price_score = price_scores[row.name]
                population_score = population_scores[row.name]
                
                return (facility_score * weights['facility'] + 
                       crime_score * weights['crime'] + 
                       price_score * weights['price'] + 
                       population_score * weights['population'])

            # 클러스터별 최종 점수 계산
            df['final_score'] = df.apply(calculate_final_score, axis=1)
            
            # 최종 점수 기준으로 상위 10개 추출
            top_clusters = df.nlargest(10, 'final_score')
            
            print("상위 10개 클러스터 데이터 컬럼명:")
            print(top_clusters.columns.tolist())
            print("첫 번째 클러스터 데이터 샘플:")
            print(top_clusters.iloc[0].to_dict())
            
            recommendations = []
            for _, cluster in top_clusters.iterrows():
                # 동 정보 추출 - 여러 컬럼에서 시도
                dong_info = None
                
                # dong 컬럼 직접 확인
                if '동' in cluster and pd.notna(cluster['동']):
                    dong_info = str(cluster['동'])
                    print(f"'동' 컬럼에서 추출: {dong_info}")
                
                # 도로명주소에서 추출 시도
                elif '도로명주소' in cluster and pd.notna(cluster['도로명주소']):
                    address = str(cluster['도로명주소'])
                    # 서울특별시 강남구 역삼동 같은 형태에서 동 추출
                    dong_match = re.search(r'[가-힣]+(동|읍|면|가|로)(?![가-힣])', address)
                    if dong_match:
                        dong_info = dong_match.group(0)
                        print(f"도로명주소에서 추출: {dong_info} (원본: {address})")
                
                # 주소 컬럼에서 추출 시도
                elif '주소' in cluster and pd.notna(cluster['주소']):
                    address = str(cluster['주소'])
                    parts = address.split()
                    for part in parts:
                        if part.endswith(('동', '읍', '면', '가', '로')):
                            dong_info = part
                            print(f"'주소' 컬럼에서 추출: {dong_info} (원본: {address})")
                            break
                
                # 구 정보가 있으면 검색
                district = cluster['district'] if 'district' in cluster else None
                if not dong_info and district:
                    # 가장 가까운 동 찾기
                    def haversine(lat1, lon1, lat2, lon2):
                        # 지구 반경 (km)
                        R = 6371.0
                        
                        # 라디안으로 변환
                        lat1, lon1 = radians(lat1), radians(lon1)
                        lat2, lon2 = radians(lat2), radians(lon2)
                        
                        # 위도/경도 차이
                        dlat = lat2 - lat1
                        dlon = lon2 - lon1
                        
                        # Haversine 공식
                        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1 - a))
                        
                        # 거리 (km)
                        distance = R * c
                        return distance
                    
                    # 구에 속한 모든 동 가져오기
                    from .views import SEOUL_DISTRICTS
                    dongs_in_district = SEOUL_DISTRICTS.get(district, [])
                    
                    # 구에 동이 있으면 처리
                    if dongs_in_district:
                        dong_info = f"{dongs_in_district[0]}"  # 첫 번째 동 기본값
                        print(f"기본 동 선택: {dong_info} (구: {district})")
                
                # 동 정보가 없으면 기본값 설정
                if not dong_info:
                    dong_info = "상세정보 없음"
                    print(f"동 정보를 찾을 수 없어 기본값 사용: {dong_info}")
                
                recommendation = cls.objects.create(
                    input_data=user_preferences,
                    recommended_district=cluster['district'],  # 구 정보
                    cluster_dong=dong_info,  # 동 정보 저장
                    recommendation_score=round(cluster['final_score'], 2),  # 점수를 둘째 자리까지 반올림
                    cluster_lat=cluster['위도'],
                    cluster_lng=cluster['경도']
                )
                recommendations.append(recommendation)
            
            return recommendations

        except Exception as e:
            print(f"Error creating recommendations: {str(e)}")
            return None

    @classmethod
    def _calculate_crime_score(cls, df, gender):
        """
        범죄 정보 점수를 계산하는 함수
        
        Args:
            df: 범죄 데이터와 CCTV 데이터가 포함된 데이터프레임
            gender: 사용자 성별 ('M' 또는 'F')
        
        Returns:
            dict: 구별 범죄 점수
        """
        crime_scores = {}
        
        # 성별에 따른 가중치 (여성은 민감도 높게 설정)
        gender_weight = 1.2 if gender == 'F' else 1.0
        
        # CCTV 밀도 계산 및 정규화
        df['cctv_density'] = df['cctv_count'] / df['area_sqkm']
        max_cctv_density = df['cctv_density'].max()
        
        # CCTV 밀도 점수 정규화 (0-1 스케일)
        df['cctv_score'] = df['cctv_density'] / max_cctv_density
        
        for district in df['구'].unique():
            # 해당 구의 범죄율과 CCTV 점수 추출
            district_data = df[df['구'] == district]
            crime_rate = district_data['crime_rate'].mean()
            cctv_score = district_data['cctv_score'].mean()
            
            # CCTV는 안전에 긍정적 영향을 미치므로 범죄율에서 CCTV 점수를 차감
            # (CCTV가 많을수록 안전, 범죄율이 높을수록 위험)
            safety_score = 100 - (crime_rate * 100) + (cctv_score * 50)
            
            # 성별 가중치 적용 (여성은 안전 점수에 더 민감)
            adjusted_score = safety_score * gender_weight
            
            # 최종 점수 범위 조정 (0-100)
            crime_scores[district] = max(0, min(100, adjusted_score))
        
        return crime_scores

    @classmethod
    def _calculate_price_score(cls, df, user_preferences):
        """시세 정보 점수 계산"""
        # 사용자 입력값(전세/월세 범위)과 CSV 내 시세 지표(평균월세, 평균전세, 보증금, 거래량 등)를 이용해
        # 각 클러스터별 '가격(시세)' 점수를 계산해서 Series로 반환.
        
        # 일단 0으로 초기화
        price_scores = pd.Series(0, index=df.index, dtype=float)

        # 편의 함수: min-max 스케일링(0 ~ 1)
        def min_max_scale(series):
            if series.min() == series.max():
                return pd.Series([1.0]*len(series), index=series.index)  # 전부 동일값이면 전부 1
            return (series - series.min()) / (series.max() - series.min())

        # 거래량 점수 (거래량 높을수록 +가점)
        if '거래량' in df.columns:
            transaction_volume_score = min_max_scale(df['거래량'])
        else:
            transaction_volume_score = 0

        # ------------------------------------------------
        # 1) 월세 선택 시
        # ------------------------------------------------
        if user_preferences.property_type == 'monthly':
            mr_min = user_preferences.monthly_rent_min or 0
            mr_max = user_preferences.monthly_rent_max or 999999999
            md_min = user_preferences.monthly_deposit_min or 0
            md_max = user_preferences.monthly_deposit_max or 999999999

            # 평균 월세 점수: 사용자 범위 중앙값에 가까울수록 높은 점수
            if '평균월세' in df.columns:
                rent_mid = (mr_min + mr_max) / 2
                # 거리(차이)가 작을수록 점수 높이기 위해 1 - minmax(distance) 사용
                rent_diff = (df['평균월세'] - rent_mid).abs()
                rent_score = 1 - min_max_scale(rent_diff)
            else:
                rent_score = 0

            # 평균 월세 보증금 점수
            if '평균월세보증금' in df.columns:
                deposit_mid = (md_min + md_max) / 2
                deposit_diff = (df['평균월세보증금'] - deposit_mid).abs()
                deposit_score = 1 - min_max_scale(deposit_diff)
            else:
                deposit_score = 0

            # 월세/보증금 비율(가성비) 점수: 비율이 낮을수록(보증금 대비 월세가 적을수록) 점수 ↑
            if '평균월세' in df.columns and '평균월세보증금' in df.columns:
                ratio_series = df['평균월세'] / (df['평균월세보증금'] + 1e-9)
                ratio_score = 1 - min_max_scale(ratio_series)
            else:
                ratio_score = 0

            # 가중치 조절해서 종합 점수 산출
            # (예: 월세 0.3, 보증금 0.3, 비율 0.2, 거래량 0.2)
            price_scores = (
                0.3 * rent_score
                + 0.3 * deposit_score
                + 0.2 * ratio_score
                + 0.2 * transaction_volume_score
            )

        # ------------------------------------------------
        # 2) 전세 선택 시
        # ------------------------------------------------
        elif user_preferences.property_type == 'jeonse':
            jd_min = user_preferences.jeonse_deposit_min or 0
            jd_max = user_preferences.jeonse_deposit_max or 999999999

            # 평균 전세 보증금 점수
            if '평균전세보증금' in df.columns:
                deposit_mid = (jd_min + jd_max) / 2
                deposit_diff = (df['평균전세보증금'] - deposit_mid).abs()
                deposit_score = 1 - min_max_scale(deposit_diff)
            else:
                deposit_score = 0

            # 전세라서 월세/보증금 비율은 불필요하니 생략(필요하면 다른 로직 추가)

            # 예: 전세 보증금 점수 0.8 + 거래량 0.2
            price_scores = 0.8 * deposit_score + 0.2 * transaction_volume_score

        return price_scores

    @classmethod
    def _calculate_population_score(cls, df, user_age):
        """인구 밀도 점수 계산"""
        population_scores = {}
        
        # 연령대 그룹 설정 (20대, 30대 등)
        age_group = (user_age // 10) * 10
        
        for idx, row in df.iterrows():
            # 해당 연령대 인구 비율 계산
            age_ratio = row[f'age_{age_group}_ratio']
            
            # 20대의 경우 추가 가중치 부여
            age_weight = 1.2 if age_group == 20 else 1.0
            
            population_scores[idx] = age_ratio * age_weight
        
        return population_scores

    @classmethod
    def _calculate_facility_score(cls, df, user_preferences):
        """편의시설 점수 계산"""
        # 선호 시설 가중치 계산
        facilities = user_preferences.preferred_facilities
        if isinstance(facilities, str):
            facilities = json.loads(facilities)
        
        # 모든 가능한 시설 목록
        all_facilities = [choice[0] for choice in RecommendationInput.FACILITY_CHOICES]
        total_all_facilities = len(all_facilities)
        selected_count = len(facilities)
        
        # 가중치 계산
        weights = {}
        
        # 최소 가중치 = 1 / (전체 시설 수 + 선택된 시설 수)
        MIN_WEIGHT = 1 / (total_all_facilities + selected_count)
        
        # 선택되지 않은 시설에 최소 가중치 부여
        for facility in all_facilities:
            weights[facility] = MIN_WEIGHT
        
        # 선택된 시설들의 가중치 계산
        if selected_count > 0:
            # 선택된 시설들이 나눠가질 총 가중치
            # = (선택된 시설 수 * 2) / (전체 시설 수 + 선택된 시설 수)
            total_selected_weight = (selected_count * 2) / (total_all_facilities + selected_count)
            
            if selected_count > 1:
                # 등차수열의 첫 항(a)과 공차(d) 계산
                first_term = (2 * total_selected_weight) / (selected_count * (1 + 1/selected_count))
                d = -(first_term * (1 - 1/selected_count)) / (selected_count - 1)
                
                # 등차수열로 가중치 계산
                selected_weights = []
                for idx in range(selected_count):
                    selected_weights.append(first_term + (d * idx))
                
                # 정규화: 선택된 시설들의 가중치 합이 total_selected_weight가 되도록 조정
                normalization_factor = total_selected_weight / sum(selected_weights)
                
                # 정규화된 가중치 적용
                for idx, facility in enumerate(facilities):
                    weights[facility] = selected_weights[idx] * normalization_factor
            else:
                # 시설이 하나만 선택된 경우
                weights[facilities[0]] = total_selected_weight

        # 각 클러스터의 편의시설 점수 계산
        facility_scores = {}
        for idx, row in df.iterrows():
            facility_score = 0
            
            # 각 시설에 대한 가중치 적용
            for facility, weight in weights.items():
                # 500m와 1km 내의 시설 수와 거리 정보 활용
                count_500m = row.get(f'{facility}_count_500m', 0)
                count_1km = row.get(f'{facility}_count_1km', 0)
                avg_dist = row.get(f'{facility}_avg_distance', 0)
                
                # 거리에 따른 가중치 계산
                # 500m 내 시설은 더 높은 가중치 부여
                facility_score += (count_500m * 1.5 + count_1km * 0.5) * weight
                
                # 평균 거리가 가까울수록 높은 점수
                if avg_dist > 0:
                    distance_factor = 1 / (avg_dist + 1)  # 0과 1 사이의 값
                    facility_score *= (1 + distance_factor)
            
            facility_scores[idx] = facility_score / len(weights)  # 정규화
        
        return facility_scores

    def __str__(self):
        return f"추천: {self.recommended_district} (점수: {self.recommendation_score})"