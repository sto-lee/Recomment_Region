from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings

from .models import RecommendationInput, RecommendationResult
# from .utils import calculate_score_weights  # utils 모듈이 없어 주석 처리
# from .constants import SEOUL_DISTRICTS, FACILITY_CHOICES, CATEGORY_PREFERENCE_MAP  # constants 모듈 없음
from .forms import RecommendationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import requests

# Create your views here.
# 서울시 구/동 데이터
SEOUL_DISTRICTS = {
    "강남구": ["개포1동","개포2동","개포3동","개포4동", "논현1동","논현2동", "대치1동","대치2동","대치4동", 
                "도곡1동","도곡2동", "삼성1동","삼성2동","세곡동","일원본동","일원1동", "수서동",
                "신사동", "압구정동", "역삼1동","역삼2동", "청담동"],
    "강동구": ["강일동", "고덕1동","고덕2동", "길동", "둔촌1동","둔촌2동", "명일1동", "명일2동", "상일1동", "상일2동", 
                "성내1동", "성내2동", "성내3동", "암사1동", "암사2동", "암사3동", "천호1동", "천호2동", "천호3동"],
    "강북구": ["미아동", "번1동", "번2동", "번3동", "수유1동", "수유2동", "수유3동", "우이동", "인수동", "삼양동", "송중동",
                "송천동", "삼각산동"],
    "강서구": ["가양1동","가양2동","가양3동", "공항동", "발산1동", "등촌1동", "등촌2동", "등촌3동", "방화1동","방화2동","방화3동",
                "염창동", "화곡본동", "화곡1동","화곡2동","화곡3동","화곡4동","화곡6동","화곡8동","우장산동"],
    "관악구": ["남현동","은천동","성현동","보라매","청림동","행운동","낙성대동","중앙동","인헌동","서원동","신원동",
                "봉천동", "신림동", "난향동", "조원동", "대학동", "삼성동", "미성동", "난곡동","서림동","신사동"],
    "광진구": ["광장동", "구의1동","구의2동","구의3동", "군자동", "능동", "화양동","중곡1동","중곡2동","중곡3동","중곡4동",
                "자양1동","자양2동","자양3동","자양4동",],   
    "구로구": ["개봉1동","개봉2동","개봉3동", "고척1동","고척2동", "구로1동","구로2동","구로3동","구로4동","구로5동", "신도림동","가리봉동",
                "오류1동","오류2동","항동","수궁동"],
    "금천구": ["가산동", "독산1동","독산2동","독산3동","독산4동", "시흥1동","시흥2동","시흥3동","시흥4동","시흥5동"],
    "노원구": ["공릉1동","공릉2동","하계1동","하계2동","중계본동","중계1동","중계2,3동","중계4동", "상계1동","상계2동","상계3,4동",
                "상계5동","상계6,7동","상계8동","상계9동","상계10동", "월계1동","월계2동","월계3동"],
    "도봉구": ["도봉1동","도봉2동", "방학1동","방학2동","방학3동", "쌍문1동","쌍문2동","쌍문3동","쌍문4동", "창1동","창2동",
                "창3동","창4동","창5동"],
    "동대문구": ["제기동","답십리1동","답십리2동", "신설동", "용신동", "이문1동","이문2동", "장안1동","장안2동", "전농1동","전농2동", "청량리동"
                "회기동", "휘경1동","휘경2동"],
    "동작구": ["노량진1동","노량진2동", "대방동", "사당1동","사당2동","사당3동","사당4동", "상도1동","상도2동","상도3동","상도4동",
                "신대방1동","신대방2동", "흑석동"],
    "마포구": ["아현동","공덕동","도화동","용강동","대흥동","염리동","신수동","서강동","합정동","연남동", "망원1동","망원2동",
                "상암동", "서교동", "성산1동","성산2동", "합정동"],
    "서대문구": ["충현동","천연동","남가좌1동","남가좌2동", "북가좌1동","북가좌2동", "북아현동", "신촌동", "연희동", "홍제1동","홍제2동","홍제3동",
                "홍은1동","홍은2동"],
    "서초구": ["반포본동","반포1동","반포2동","반포3동","반포4동", "방배본동","방배1동","방배2동","방배3동","방배4동",
                "서초1동","서초2동","서초3동","서초4동", "양재1동","양재2동", "잠원동", "내곡동"],
    "성동구": ["사근동","행당1동","행당2동","응봉동","금호1가동","금호2,3가동","금호4가동", "도선동", "마장동", "송정동", "용답동",
                "성수1가1동","성수1가2동","성수2가1동","성수2가3동", "옥수동", "왕십리2동","왕십리도선동"],
    "성북구": ["안암동","길음1동","길음2동", "돈암1동","돈암2동", "동선동", "보문동", "삼선동", "석관동", "성북동", "장위1동","장위2동","장위3동",
                "정릉1동","종암동","정릉2동","정릉3동","정릉4동","월곡1동","월곡2동"],
    "송파구": ["풍납1동","풍납2동","방이1동","방이2동","가락본동","가락1동","가락2동", "거여1동","거여2동", "마천1동","마천2동", "문정1동","문정2동", 
                "석촌동","삼전동","송파1동","송파2동", "오금동","오륜동", "장지동","위례동","잠실본동","잠실2동","잠실3동","잠실4동",
                "잠실6동","잠실7동"],
    "양천구": ["목1동","목2동","목3동","목4동","목5동", "신월1동","신월2동","신월3동","신월4동","신월5동","신월6동","신월7동", 
                "신정1동","신정2동","신정3동","신정4동","신정5동","신정6동","신정7동"],
    "영등포구": ["영등포본동","영등포동","당산1동","당산2동", "대림1동","대림2동","대림3동", "도림동", "문래동", "양평1동","양평2동", "여의동",
                "신길1동","신길2동","신길3동","신길4동","신길5동","신길6동","신길7동"],
    "용산구": ["후암동","용산2가동","남영동", "보광동","청파동","원효로1동","원효로2동","효창동","용문동", "서빙고동", "이태원1동","이태원2동",
                "한강로동","이촌1동","이촌2동","한남동"],
    "은평구": ["갈현1동","갈현2동", "구산동", "녹번동","대조동","응암1동","응암2동","응암3동", "불광1동","불광2동", "수색동", 
                "신사1동","신사2동","증산동", "역촌동","진관동"],
    "종로구": ["청운효자동","삼청동","평창동","가회동", "교남동", "낙원동", "내자동", "무악동", "부암동", "사직동", "창신1동","창신2동","창신3동",
                "종로1.2.3.4가동","종로5,6가동","이화동","혜화동","숭인1동","숭인2동"],
    "중구": ["회현동","명동","필동","장충동","광희동","약수동","남대문로", "다산동", "만리동", "묵정동", "소공동", "신당동","신당5동", 
                "을지로동","청구동","동화동","황학동","중림동"],
    "중랑구": ["망우3동","망우본동", "면목본동","면목2동","면목3.8동","면목4동","면목5동","면목7동", "상봉1동","상봉2동", "중화1동","중화2동",
                "묵1동","묵2동","신내1동","신내2동"]
}

def get_districts(request):
    """구 목록 정보를 제공하는 API"""
    districts_list = list(SEOUL_DISTRICTS.keys())
    return JsonResponse({"districts": districts_list})

def get_dongs(request):
    district = request.GET.get("district", "")
    dongs = SEOUL_DISTRICTS.get(district, [])
    return JsonResponse({"dongs": dongs})

# =========== 모달용 iframe 뷰 함수 추가 ===========

def modal_page1_view(request):
    """모달 첫 페이지 (iframe에서 사용)"""
    districts_list = list(SEOUL_DISTRICTS.keys())
    
    return render(request, "recommendations/modal/page1.html", {
        'districts': districts_list,
        'is_modal': True
    })

def modal_page2_view(request):
    """모달 두번째 페이지 (iframe에서 사용)"""
    if request.method == 'POST':
        # recommend_page_1에서 전달된 데이터 처리
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        preferred_facilities = request.POST.get('preferred_facilities')
        desired_district = request.POST.get('desired_district', "").strip()
        transport = request.POST.get('transport')
        desired_dong = request.POST.get('desired_dong', "").strip()

        # 필수 입력값 검증
        if not all([age, gender, preferred_facilities, desired_district]):
            return redirect('recommendations:modal_page1')

        # 세션에 데이터 저장
        request.session['age'] = age
        request.session['gender'] = gender
        request.session['preferred_facilities'] = preferred_facilities
        request.session['desired_district'] = desired_district
        request.session['transport'] = transport
        request.session['desired_dong'] = desired_dong

        # recommend_page_2 렌더링
        context = {
            "age": age,
            "gender": gender,
            "preferred_facilities": preferred_facilities,
            "transport": transport,
            "desired_district": desired_district,
            "desired_dong": desired_dong,
            "is_modal": True
        }
        return render(request, 'recommendations/modal/page2.html', context)
    
    # GET 방식으로 접근 시 이전 데이터가 있으면 활용
    context = {
        "age": request.session.get('age', ''),
        "gender": request.session.get('gender', ''),
        "preferred_facilities": request.session.get('preferred_facilities', ''),
        "transport": request.session.get('transport', ''),
        "desired_district": request.session.get('desired_district', ''),
        "desired_dong": request.session.get('desired_dong', ''),
        "is_modal": True
    }
    return render(request, 'recommendations/modal/page2.html', context)

def modal_page3_view(request):
    """모달 세번째 페이지 (가중치 설정)"""
    if request.method == 'POST':
        # recommend_page_2에서 전달된 데이터 처리
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        preferred_facilities = request.POST.get('preferred_facilities')
        desired_district = request.POST.get('desired_district')
        transport = request.POST.get('transport')
        desired_dong = request.POST.get('desired_dong')
        property_type = request.POST.get('property_type')
        
        # 전세, 월세에 따른 데이터 처리
        if property_type == 'jeonse':
            jeonse_deposit_min = request.POST.get('jeonse_deposit_min')
            jeonse_deposit_max = request.POST.get('jeonse_deposit_max')
            
            # 세션에 데이터 저장
            request.session['property_type'] = property_type
            request.session['jeonse_deposit_min'] = jeonse_deposit_min
            request.session['jeonse_deposit_max'] = jeonse_deposit_max
            
            # context에 데이터 추가
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "jeonse_deposit_min": jeonse_deposit_min,
                "jeonse_deposit_max": jeonse_deposit_max,
                "is_modal": True
            }
        else:  # 월세인 경우
            monthly_deposit_min = request.POST.get('monthly_deposit_min')
            monthly_deposit_max = request.POST.get('monthly_deposit_max')
            monthly_rent_min = request.POST.get('monthly_rent_min')
            monthly_rent_max = request.POST.get('monthly_rent_max')
            
            # 세션에 데이터 저장
            request.session['property_type'] = property_type
            request.session['monthly_deposit_min'] = monthly_deposit_min
            request.session['monthly_deposit_max'] = monthly_deposit_max
            request.session['monthly_rent_min'] = monthly_rent_min
            request.session['monthly_rent_max'] = monthly_rent_max
            
            # context에 데이터 추가
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "monthly_deposit_min": monthly_deposit_min,
                "monthly_deposit_max": monthly_deposit_max,
                "monthly_rent_min": monthly_rent_min,
                "monthly_rent_max": monthly_rent_max,
                "is_modal": True
            }
            
        return render(request, 'recommendations/modal/page3.html', context)
    
    # GET 방식으로 접근 시 이전 데이터가 있으면 활용
    context = {
        "age": request.session.get('age', ''),
        "gender": request.session.get('gender', ''),
        "preferred_facilities": request.session.get('preferred_facilities', ''),
        "transport": request.session.get('transport', ''),
        "desired_district": request.session.get('desired_district', ''),
        "desired_dong": request.session.get('desired_dong', ''),
        "property_type": request.session.get('property_type', ''),
        "is_modal": True
    }
    
    # 전세, 월세에 따라 다른 데이터 추가
    if context["property_type"] == 'jeonse':
        context.update({
            "jeonse_deposit_min": request.session.get('jeonse_deposit_min', ''),
            "jeonse_deposit_max": request.session.get('jeonse_deposit_max', '')
        })
    else:
        context.update({
            "monthly_deposit_min": request.session.get('monthly_deposit_min', ''),
            "monthly_deposit_max": request.session.get('monthly_deposit_max', ''),
            "monthly_rent_min": request.session.get('monthly_rent_min', ''),
            "monthly_rent_max": request.session.get('monthly_rent_max', '')
        })
        
    return render(request, 'recommendations/modal/page3.html', context)

def modal_confirm_view(request):
    """모달 확인 페이지 (사용자 입력 확인)"""
    if request.method == 'POST':
        # 페이지 3에서 전달된 정보
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        preferred_facilities = request.POST.get('preferred_facilities')
        transport = request.POST.get('transport')
        desired_district = request.POST.get('desired_district')
        desired_dong = request.POST.get('desired_dong')
        property_type = request.POST.get('property_type')
        
        # 가중치 값 처리
        weight_type = request.POST.get('weight_type', 'facility')  # 기본값은 편의시설 우선
        
        # 사용자 지정 가중치인 경우
        if weight_type == 'custom':
            facility_weight = int(request.POST.get('facility_weight', 30))
            price_weight = int(request.POST.get('price_weight', 30))
            crime_weight = int(request.POST.get('crime_weight', 30))
            population_weight = int(request.POST.get('population_weight', 10))
        else:
            # 사전 정의된 가중치 유형
            weights = {
                'facility': {'facility': 60, 'price': 30, 'crime': 5, 'population': 5},
                'price': {'facility': 30, 'price': 50, 'crime': 15, 'population': 5},
                'safety': {'facility': 30, 'price': 25, 'crime': 40, 'population': 5}
            }
            
            facility_weight = weights[weight_type]['facility']
            price_weight = weights[weight_type]['price']
            crime_weight = weights[weight_type]['crime']
            population_weight = weights[weight_type]['population']
        
        # 가중치 값을 세션에 저장
        request.session['weight_type'] = weight_type
        request.session['facility_weight'] = facility_weight
        request.session['price_weight'] = price_weight
        request.session['crime_weight'] = crime_weight
        request.session['population_weight'] = population_weight
        
        # 전세/월세 정보 처리
        if property_type == 'jeonse':
            jeonse_deposit_min = request.POST.get('jeonse_deposit_min')
            jeonse_deposit_max = request.POST.get('jeonse_deposit_max')
            
            # 세션에 값 저장
            request.session['jeonse_deposit_min'] = jeonse_deposit_min
            request.session['jeonse_deposit_max'] = jeonse_deposit_max
            
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "jeonse_deposit_min": jeonse_deposit_min,
                "jeonse_deposit_max": jeonse_deposit_max,
                "weight_type": weight_type,
                "facility_weight": facility_weight,
                "price_weight": price_weight,
                "crime_weight": crime_weight,
                "population_weight": population_weight,
                "is_modal": True
            }
        else:  # 월세인 경우
            monthly_deposit_min = request.POST.get('monthly_deposit_min')
            monthly_deposit_max = request.POST.get('monthly_deposit_max')
            monthly_rent_min = request.POST.get('monthly_rent_min')
            monthly_rent_max = request.POST.get('monthly_rent_max')
            
            # 세션에 값 저장
            request.session['monthly_deposit_min'] = monthly_deposit_min
            request.session['monthly_deposit_max'] = monthly_deposit_max
            request.session['monthly_rent_min'] = monthly_rent_min
            request.session['monthly_rent_max'] = monthly_rent_max
            
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "monthly_deposit_min": monthly_deposit_min,
                "monthly_deposit_max": monthly_deposit_max,
                "monthly_rent_min": monthly_rent_min,
                "monthly_rent_max": monthly_rent_max,
                "weight_type": weight_type,
                "facility_weight": facility_weight,
                "price_weight": price_weight,
                "crime_weight": crime_weight,
                "population_weight": population_weight,
                "is_modal": True
            }
            
        # 편의시설 이름 변환 (CSV -> 리스트)
        if preferred_facilities:
            context['facility_list'] = preferred_facilities.split(',')
        
        # 가중치 유형 이름 한글화
        weight_type_names = {
            'facility': '편의시설 우선형',
            'price': '시세 우선형',
            'safety': '안전 우선형',
            'custom': '사용자 지정'
        }
        context['weight_type_name'] = weight_type_names.get(weight_type, '기본형')
        
        return render(request, 'recommendations/modal/confirm.html', context)
    
    # GET 요청의 경우 세션에서 데이터 로드
    context = {
        "age": request.session.get('age', ''),
        "gender": request.session.get('gender', ''),
        "preferred_facilities": request.session.get('preferred_facilities', ''),
        "transport": request.session.get('transport', ''),
        "desired_district": request.session.get('desired_district', ''),
        "desired_dong": request.session.get('desired_dong', ''),
        "property_type": request.session.get('property_type', ''),
        "weight_type": request.session.get('weight_type', 'facility'),
        "facility_weight": request.session.get('facility_weight', 60),
        "price_weight": request.session.get('price_weight', 30),
        "crime_weight": request.session.get('crime_weight', 5),
        "population_weight": request.session.get('population_weight', 5),
        "is_modal": True
    }
    
    # 전세/월세 관련 데이터
    if context["property_type"] == 'jeonse':
        context.update({
            "jeonse_deposit_min": request.session.get('jeonse_deposit_min', ''),
            "jeonse_deposit_max": request.session.get('jeonse_deposit_max', '')
        })
    else:
        context.update({
            "monthly_deposit_min": request.session.get('monthly_deposit_min', ''),
            "monthly_deposit_max": request.session.get('monthly_deposit_max', ''),
            "monthly_rent_min": request.session.get('monthly_rent_min', ''),
            "monthly_rent_max": request.session.get('monthly_rent_max', '')
        })
    
    # 편의시설 이름 변환 (CSV -> 리스트)
    if context['preferred_facilities']:
        context['facility_list'] = context['preferred_facilities'].split(',')
    
    # 가중치 유형 이름 한글화
    weight_type_names = {
        'facility': '편의시설 우선형',
        'price': '시세 우선형',
        'safety': '안전 우선형',
        'custom': '사용자 지정'
    }
    context['weight_type_name'] = weight_type_names.get(context['weight_type'], '기본형')
    
    return render(request, 'recommendations/modal/confirm.html', context)

def modal_result_view(request):
    """모달 추천 결과 페이지 (iframe에서 사용)"""
    if request.method == 'POST':
        # 페이지 3에서 전달된 가중치 정보
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        preferred_facilities = request.POST.get('preferred_facilities')
        transport = request.POST.get('transport')
        desired_district = request.POST.get('desired_district')
        desired_dong = request.POST.get('desired_dong')
        property_type = request.POST.get('property_type')
        
        # 가중치 값 처리
        weight_type = request.POST.get('weight_type', 'facility')  # 기본값은 편의시설 우선
        
        # 사용자 지정 가중치인 경우
        if weight_type == 'custom':
            facility_weight = int(request.POST.get('facility_weight', 30))
            price_weight = int(request.POST.get('price_weight', 30))
            crime_weight = int(request.POST.get('crime_weight', 30))
            population_weight = int(request.POST.get('population_weight', 10))
        else:
            # 사전 정의된 가중치 유형
            weights = {
                'facility': {'facility': 60, 'price': 30, 'crime': 5, 'population': 5},
                'price': {'facility': 30, 'price': 50, 'crime': 15, 'population': 5},
                'safety': {'facility': 30, 'price': 25, 'crime': 40, 'population': 5}
            }
            
            facility_weight = weights[weight_type]['facility']
            price_weight = weights[weight_type]['price']
            crime_weight = weights[weight_type]['crime']
            population_weight = weights[weight_type]['population']
        
        # 가중치 값을 세션에 저장
        request.session['weight_type'] = weight_type
        request.session['facility_weight'] = facility_weight
        request.session['price_weight'] = price_weight
        request.session['crime_weight'] = crime_weight
        request.session['population_weight'] = population_weight
        
        # 전세/월세 정보 처리
        if property_type == 'jeonse':
            jeonse_deposit_min = request.POST.get('jeonse_deposit_min')
            jeonse_deposit_max = request.POST.get('jeonse_deposit_max')
            
            # 세션에 값 저장
            request.session['jeonse_deposit_min'] = jeonse_deposit_min
            request.session['jeonse_deposit_max'] = jeonse_deposit_max
            
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "jeonse_deposit_min": jeonse_deposit_min,
                "jeonse_deposit_max": jeonse_deposit_max,
                "weight_type": weight_type,
                "facility_weight": facility_weight,
                "price_weight": price_weight,
                "crime_weight": crime_weight,
                "population_weight": population_weight,
                "is_modal": True
            }
        else:  # 월세인 경우
            monthly_deposit_min = request.POST.get('monthly_deposit_min')
            monthly_deposit_max = request.POST.get('monthly_deposit_max')
            monthly_rent_min = request.POST.get('monthly_rent_min')
            monthly_rent_max = request.POST.get('monthly_rent_max')
            
            # 세션에 값 저장
            request.session['monthly_deposit_min'] = monthly_deposit_min
            request.session['monthly_deposit_max'] = monthly_deposit_max
            request.session['monthly_rent_min'] = monthly_rent_min
            request.session['monthly_rent_max'] = monthly_rent_max
            
            context = {
                "age": age,
                "gender": gender,
                "preferred_facilities": preferred_facilities,
                "transport": transport,
                "desired_district": desired_district,
                "desired_dong": desired_dong,
                "property_type": property_type,
                "monthly_deposit_min": monthly_deposit_min,
                "monthly_deposit_max": monthly_deposit_max,
                "monthly_rent_min": monthly_rent_min,
                "monthly_rent_max": monthly_rent_max,
                "weight_type": weight_type,
                "facility_weight": facility_weight,
                "price_weight": price_weight,
                "crime_weight": crime_weight,
                "population_weight": population_weight,
                "is_modal": True
            }
            
        # 편의시설 이름 변환 (CSV -> 리스트)
        if preferred_facilities:
            context['facility_list'] = preferred_facilities.split(',')
        
        # 가중치 유형 이름 한글화
        weight_type_names = {
            'facility': '편의시설 우선형',
            'price': '시세 우선형',
            'safety': '안전 우선형',
            'custom': '사용자 지정'
        }
        
        context['weight_type_name'] = weight_type_names.get(weight_type, '기본형')
        
        # 임시 추천 결과 (실제로는 AI 모델에서 계산)
        context['recommendations'] = []
        
        try:
            # 추천 입력 객체 생성
            recommendation_input = RecommendationInput.objects.create(
                age=int(age),
                gender=gender,
                transport=transport,
                property_type=property_type,
                desired_location=desired_district + " " + (desired_dong if desired_dong else ""),
                preferred_facilities=json.loads(preferred_facilities),
                
                # 전세/월세 정보
                jeonse_deposit_min=request.session.get('jeonse_deposit_min'),
                jeonse_deposit_max=request.session.get('jeonse_deposit_max'),
                monthly_deposit_min=request.session.get('monthly_deposit_min'),
                monthly_deposit_max=request.session.get('monthly_deposit_max'),
                monthly_rent_min=request.session.get('monthly_rent_min'),
                monthly_rent_max=request.session.get('monthly_rent_max'),
                
                # 추천 유형 및 가중치
                recommendation_type=weight_type,
                custom_facility_weight=float(facility_weight)/100 if weight_type == 'custom' else None,
                custom_crime_weight=float(crime_weight)/100 if weight_type == 'custom' else None,
                custom_price_weight=float(price_weight)/100 if weight_type == 'custom' else None,
                custom_population_weight=float(population_weight)/100 if weight_type == 'custom' else None
            )
            
            # 추천 결과 생성
            recommendation_results = RecommendationResult.create_recommendation(recommendation_input)
            
            # 추천 결과가 있을 경우
            if recommendation_results and len(recommendation_results) > 0:
                context['recommendations'] = recommendation_results
            else:
                # 테스트 데이터 생성 (실제 추천이 없는 경우)
                for i in range(5):
                    # 동이름 생성 (첫번째는 사용자가 선택한 동, 나머지는 인근 동들)
                    dong_name = desired_dong if i == 0 and desired_dong else f"테스트동{i+1}"
                    
                    # 점수 생성 (점수는 95점에서 시작해서 약간씩 감소)
                    base_score = 95.0 - (i * 1.5)
                    
                    # 세부 점수 계산
                    facility_score = min(100, max(0, 85.0 - (i * 2.0)))
                    crime_score = min(100, max(0, 90.0 - (i * 1.8)))
                    price_score = min(100, max(0, 80.0 - (i * 2.5)))
                    population_score = min(100, max(0, 75.0 - (i * 2.2)))
                    
                    # 위도/경도 약간씩 변화 (실제로는 클러스터 데이터에서 가져옴)
                    latitude = 37.5665 + (i * 0.002)
                    longitude = 126.9780 + (i * 0.002)
                    
                    # 추천 결과 객체 생성
                    context['recommendations'].append({
                        "recommended_district": desired_district,
                        "cluster_dong": dong_name,
                        "recommendation_score": round(base_score, 1),
                        "facility_score": round(facility_score, 1),
                        "crime_score": round(crime_score, 1),
                        "price_score": round(price_score, 1),
                        "population_score": round(population_score, 1),
                        "cluster_lat": latitude,
                        "cluster_lng": longitude
                    })
        except Exception as e:
            print(f"추천 생성 중 오류 발생: {str(e)}")
            # 오류 발생시 위도/경도에 맞는 동 이름으로 테스트 데이터 생성
            
            # 테스트용 위치 데이터 (위도, 경도, 동 이름)
            locations = [
                {"lat": 37.5665, "lng": 126.9780, "dong": "명동"},
                {"lat": 37.5759, "lng": 126.9768, "dong": "장충동"},
                {"lat": 37.5270, "lng": 127.0392, "dong": "약수동"}
            ]
            
            for i in range(min(3, len(locations))):
                location = locations[i]
                context['recommendations'].append({
                    "recommended_district": desired_district,
                    "cluster_dong": location["dong"],
                    "recommendation_score": round(90.0 - (i * 2.0), 1),
                    "facility_score": round(85.0 - (i * 2.0), 1),
                    "crime_score": round(90.0 - (i * 1.8), 1),
                    "price_score": round(80.0 - (i * 2.5), 1),
                    "population_score": round(75.0 - (i * 2.2), 1),
                    "cluster_lat": location["lat"],
                    "cluster_lng": location["lng"]
                })
        
        return render(request, 'recommendations/modal/result.html', context)
    
    # GET 요청의 경우 세션에서 데이터 로드
    age = request.session.get('age', '')
    gender = request.session.get('gender', '')
    property_type = request.session.get('property_type', '')
    desired_district = request.session.get('desired_district', '')
    desired_dong = request.session.get('desired_dong', '')
    preferred_facilities = request.session.get('preferred_facilities', '')
    weight_type = request.session.get('weight_type', 'facility')
    facility_weight = request.session.get('facility_weight', 60)
    price_weight = request.session.get('price_weight', 30)
    crime_weight = request.session.get('crime_weight', 5)
    population_weight = request.session.get('population_weight', 5)
    
    context = {
        "age": age,
        "gender": gender,
        "preferred_facilities": preferred_facilities,
        "transport": request.session.get('transport', ''),
        "desired_district": desired_district,
        "desired_dong": desired_dong,
        "property_type": property_type,
        "weight_type": weight_type,
        "facility_weight": facility_weight,
        "price_weight": price_weight,
        "crime_weight": crime_weight,
        "population_weight": population_weight,
        "is_modal": True
    }
    
    # 전세/월세 관련 데이터
    if context["property_type"] == 'jeonse':
        context.update({
            "jeonse_deposit_min": request.session.get('jeonse_deposit_min', ''),
            "jeonse_deposit_max": request.session.get('jeonse_deposit_max', '')
        })
    else:
        context.update({
            "monthly_deposit_min": request.session.get('monthly_deposit_min', ''),
            "monthly_deposit_max": request.session.get('monthly_deposit_max', ''),
            "monthly_rent_min": request.session.get('monthly_rent_min', ''),
            "monthly_rent_max": request.session.get('monthly_rent_max', '')
        })
    
    # 임시 추천 결과 (실제로는 AI 모델에서 계산)
    context['recommendations'] = []
    
    # 필수 데이터가 없으면 테스트 데이터 사용
    if not age or not gender or not preferred_facilities or not desired_district:
        print("필수 데이터가 없어 테스트 데이터 사용")
        # 테스트 데이터 생성
        for i in range(3):
            context['recommendations'].append({
                "recommended_district": desired_district or "테스트구",
                "cluster_dong": desired_dong or f"테스트동{i+1}",
                "recommendation_score": round(90.0 - (i * 2.0), 1),
                "facility_score": round(85.0 - (i * 2.0), 1),
                "crime_score": round(90.0 - (i * 1.8), 1),
                "price_score": round(80.0 - (i * 2.5), 1),
                "population_score": round(75.0 - (i * 2.2), 1),
                "cluster_lat": 37.5665 + (i * 0.002),
                "cluster_lng": 126.9780 + (i * 0.002)
            })
        return render(request, 'recommendations/modal/result.html', context)
        
    try:
        # 추천 입력 객체 생성
        recommendation_input = RecommendationInput.objects.create(
            age=int(age),
            gender=gender,
            transport=context['transport'],
            property_type=property_type,
            desired_location=desired_district + " " + (desired_dong if desired_dong else ""),
            preferred_facilities=json.loads(preferred_facilities),
            
            # 전세/월세 정보
            jeonse_deposit_min=request.session.get('jeonse_deposit_min'),
            jeonse_deposit_max=request.session.get('jeonse_deposit_max'),
            monthly_deposit_min=request.session.get('monthly_deposit_min'),
            monthly_deposit_max=request.session.get('monthly_deposit_max'),
            monthly_rent_min=request.session.get('monthly_rent_min'),
            monthly_rent_max=request.session.get('monthly_rent_max'),
            
            # 추천 유형 및 가중치
            recommendation_type=weight_type,
            custom_facility_weight=float(facility_weight)/100 if weight_type == 'custom' else None,
            custom_crime_weight=float(crime_weight)/100 if weight_type == 'custom' else None,
            custom_price_weight=float(price_weight)/100 if weight_type == 'custom' else None,
            custom_population_weight=float(population_weight)/100 if weight_type == 'custom' else None
        )
        
        # 추천 결과 생성
        recommendation_results = RecommendationResult.create_recommendation(recommendation_input)
        
        # 추천 결과가 있을 경우
        if recommendation_results and len(recommendation_results) > 0:
            context['recommendations'] = recommendation_results
        else:
            # 테스트 데이터 생성 (실제 추천이 없는 경우)
            for i in range(5):
                # 동이름 생성 (첫번째는 사용자가 선택한 동, 나머지는 인근 동들)
                dong_name = desired_dong if i == 0 and desired_dong else f"테스트동{i+1}"
                
                # 점수 생성 (점수는 95점에서 시작해서 약간씩 감소)
                base_score = 95.0 - (i * 1.5)
                
                # 세부 점수 계산
                facility_score = min(100, max(0, 85.0 - (i * 2.0)))
                crime_score = min(100, max(0, 90.0 - (i * 1.8)))
                price_score = min(100, max(0, 80.0 - (i * 2.5)))
                population_score = min(100, max(0, 75.0 - (i * 2.2)))
                
                # 위도/경도 약간씩 변화 (실제로는 클러스터 데이터에서 가져옴)
                latitude = 37.5665 + (i * 0.002)
                longitude = 126.9780 + (i * 0.002)
                
                # 추천 결과 객체 생성
                context['recommendations'].append({
                    "recommended_district": desired_district,
                    "cluster_dong": dong_name,
                    "recommendation_score": round(base_score, 1),
                    "facility_score": round(facility_score, 1),
                    "crime_score": round(crime_score, 1),
                    "price_score": round(price_score, 1),
                    "population_score": round(population_score, 1),
                    "cluster_lat": latitude,
                    "cluster_lng": longitude
                })
    except Exception as e:
        print(f"추천 생성 중 오류 발생: {str(e)}")
        # 오류 발생시 위도/경도에 맞는 동 이름으로 테스트 데이터 생성
        
        # 테스트용 위치 데이터 (위도, 경도, 동 이름)
        locations = [
            {"lat": 37.5665, "lng": 126.9780, "dong": "명동"},
            {"lat": 37.5759, "lng": 126.9768, "dong": "종로동"},
            {"lat": 37.5270, "lng": 127.0392, "dong": "강남동"}
        ]
        
        for i in range(min(3, len(locations))):
            location = locations[i]
            context['recommendations'].append({
                "recommended_district": desired_district,
                "cluster_dong": location["dong"],
                "recommendation_score": round(90.0 - (i * 2.0), 1),
                "facility_score": round(85.0 - (i * 2.0), 1),
                "crime_score": round(90.0 - (i * 1.8), 1),
                "price_score": round(80.0 - (i * 2.5), 1),
                "population_score": round(75.0 - (i * 2.2), 1),
                "cluster_lat": location["lat"],
                "cluster_lng": location["lng"]
            })
    
    return render(request, 'recommendations/modal/result.html', context)

def recommend_api(request):
    """AJAX 요청을 처리하는 API 뷰"""
    if request.method == 'POST':
        try:
            # 데이터 처리
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            preferred_facilities = request.POST.get('preferred_facilities')
            property_type = request.POST.get('property_type')
            
            # RecommendationInput 객체 생성 및 추천 처리
            
            # 성공 응답
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'POST 요청만 허용됩니다.'})

