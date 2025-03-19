from django.db import models
import pandas as pd
import json

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
    
    # 범죄 민감도 (0-5)
    crime_sensitivity = models.IntegerField(default=3)
    
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
            # CSV 파일 읽기
            df = pd.read_csv('../static/data/clusters/all_clusters_updated.csv')
            
            # 1. 편의시설 점수 계산 (기존 코드 유지)
            facility_scores = cls._calculate_facility_score(df, user_preferences)
            
            # 2. 범죄 정보 점수 계산
            crime_scores = cls._calculate_crime_score(df, user_preferences.gender, user_preferences.crime_sensitivity)
            
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
            
            recommendations = []
            for _, cluster in top_clusters.iterrows():
                recommendation = cls.objects.create(
                    input_data=user_preferences,
                    recommended_district=cluster['district'],  # 구 정보만 저장
                    recommendation_score=cluster['final_score'],
                    cluster_lat=cluster['위도'],
                    cluster_lng=cluster['경도']
                )
                recommendations.append(recommendation)
            
            return recommendations

        except Exception as e:
            print(f"Error creating recommendations: {str(e)}")
            return None

    @classmethod
    def _calculate_crime_score(cls, df, gender, sensitivity):
        """범죄 정보 점수 계산"""
        crime_scores = {}
        
        # 성별에 따른 가중치 설정
        gender_weight = 1.2 if gender == 'F' else 1.0
        # 민감도 점수 변환 (0-5 -> 0.5-1.5)
        sensitivity_weight = 0.5 + (sensitivity * 0.2)
        
        for district in df['district'].unique():
            # 범죄 변화율과 CCTV 점수를 구별로 계산
            crime_rate = df[df['district'] == district]['crime_rate'].mean()
            cctv_score = df[df['district'] == district]['cctv_score'].mean()
            
            # 범죄 점수 계산
            crime_score = (crime_rate * gender_weight + cctv_score * gender_weight) * sensitivity_weight
            crime_scores[district] = crime_score
            
        return crime_scores

    @classmethod
    def _calculate_price_score(cls, df, preferences):
        """시세 정보 점수 계산"""
        price_scores = {}
        
        for idx, row in df.iterrows():
            # 1. 평균 시세와 사용자 니즈 일치도
            price_match = cls._calculate_price_match(row, preferences)
            
            # 2. 거래량 점수
            transaction_score = row['transaction_volume'] / df['transaction_volume'].max()
            
            # 3. 보증금 대비 월세 가격 적절성
            price_ratio_score = cls._calculate_price_ratio_score(row)
            
            # 최종 시세 점수 계산 (각각 가중치 부여)
            price_scores[idx] = (price_match * 0.4 + 
                               transaction_score * 0.3 + 
                               price_ratio_score * 0.3)
        
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