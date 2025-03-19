// 전역 변수 수정 (클러스터 관련 변수 제거)
const BATCH_SIZE = 1000;
const BATCH_DELAY = 10;
const VIEWPORT_UPDATE_DELAY = 300;

var categoryMarkers = {};
var categoryVisible = {};
let viewportUpdateTimer = null;
var allCategoriesVisible = false;

// 마커 이미지 기본 설정
var markerImageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/category.png';  // 스프라이트 이미지

// 카테고리별 마커 이미지 옵션
var categoryImageOptions = {
    // 공공기관 및 안전
    'PO': {  // 경찰서
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'CC': {  // 커뮤니티 센터
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'PT': {  // 우체국
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 의료 시설
    'AH': {  // 동물병원
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'DS': {  // 약국
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'HP': {  // 병원
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'PH': {  // 공공 보건 센터
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 편의 시설
    'CS': {  // 편의점
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'EG': {  // 전기차 충전소
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'GS': {  // 주유소
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'SL': {  // 셀프 세탁소
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'SM': {  // 마트
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 교통 관련
    'BS': {  // 버스정류장
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'PS': {  // 공원주차장
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'SB': {  // 지하철역
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 교육 관련
    'DC': {  // 어린이집
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'ED': {  // 교육시설
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'SC': {  // 학교
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'UV': {  // 대학교
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 체육/공원 관련
    'OS': {  // 체육시설
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'PK': {  // 공원
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 여가 관련
    'FN': {  // 피트니스
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'MR': {  // 음악연습실
        spriteOrigin: new kakao.maps.Point(10, 36),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'PR': {  // PC방
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    'TT': {  // 영화관
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 1단계 시설
    'TO': {  // 세무서
        spriteOrigin: new kakao.maps.Point(10, 72),    
        spriteSize: new kakao.maps.Size(36, 98)
    },
    
    // 4단계 시설
    'PO': {  // 경찰서
        spriteOrigin: new kakao.maps.Point(10, 0),    
        spriteSize: new kakao.maps.Size(36, 98)
    }
};

// 마커 이미지 생성 함수
function createMarkerImage(category) {
    return new kakao.maps.MarkerImage(
        markerImageSrc, 
        new kakao.maps.Size(22, 26),
        categoryImageOptions[category]
    );
}

// 마커 생성 함수
function createMarker(category, lat, lng, name) {
    const markerImage = createMarkerImage(category);
    const marker = new kakao.maps.Marker({
        position: new kakao.maps.LatLng(lat, lng),
        image: markerImage
    });
    
    const infowindow = new kakao.maps.InfoWindow({
        content: '<div style="padding:5px;font-size:12px;">' + name + '</div>'
    });
    
    kakao.maps.event.addListener(marker, 'mouseover', makeOverListener(map, marker, infowindow));
    kakao.maps.event.addListener(marker, 'mouseout', makeOutListener(infowindow));
    
    return marker;
}

// 카테고리별 마커 로드 함수 수정
async function loadMarkers(category, file) {
    categoryMarkers[category] = [];
    categoryVisible[category] = false;
    
    try {
        const response = await fetch(file);
        const buffer = await response.arrayBuffer();
        const decoder = new TextDecoder('EUC-KR');
        const text = decoder.decode(buffer);
        
        const lines = text.split('\n');
        const markers = [];
        
        // 마커 객체 생성
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const columns = line.split(',');
            const name = columns[1];
            const lat = parseFloat(columns[3]);
            const lng = parseFloat(columns[4]);
            
            if (isNaN(lat) || isNaN(lng)) continue;
            
            const marker = createMarker(category, lat, lng, name);
            markers.push(marker);
        }
        
        // 배치 처리로 마커 추가
        await loadMarkersInBatches(category, markers);
        
    } catch (error) {
        console.error('Error loading category data:', error);
    }
}

// 배치 처리 함수
async function loadMarkersInBatches(category, markers) {
    for (let i = 0; i < markers.length; i += BATCH_SIZE) {
        const batch = markers.slice(i, i + BATCH_SIZE);
        categoryMarkers[category].push(...batch);
    }
    
    // 로딩 완료 메시지
    console.log(`Loading ${category} complete: ${markers.length} markers`);
    
    await new Promise(resolve => setTimeout(resolve, BATCH_DELAY));
}

// 인포윈도우를 표시하는 클로저를 만드는 함수
function makeOverListener(map, marker, infowindow) {
    return function() {
        infowindow.open(map, marker);
    };
}

// 인포윈도우를 닫는 클로저를 만드는 함수
function makeOutListener(infowindow) {
    return function() {
        infowindow.close();
    };
}

// 지도 레벨 체크 함수 수정
function isValidMapLevel() {
    const currentLevel = map.getLevel();
    return currentLevel <= 4;
}

// 뷰포트 내 마커 업데이트 함수 수정
function updateMarkersInViewport() {
    if (!isValidMapLevel()) return;
    
    const bounds = map.getBounds();
    
    Object.keys(categoryMarkers).forEach(category => {
        if (categoryVisible[category]) {
            categoryMarkers[category].forEach(marker => {
                if (bounds.contain(marker.getPosition())) {
                    marker.setMap(map);
                } else {
                    marker.setMap(null);
                }
            });
        }
    });
}

// 카테고리 토글 함수 수정
function toggleCategory(category) {
    const currentLevel = map.getLevel();
    
    if (currentLevel > 4) {
        alert('지도를 더 확대해주세요 (레벨 4 이하)');
        return;
    }

    if (!categoryMarkers[category]) {
        console.error('카테고리 마커가 로드되지 않았습니다:', category);
        return;
    }

    categoryVisible[category] = !categoryVisible[category];
    
    // 버튼 스타일 업데이트
    const button = document.querySelector(`[data-category="${category}"]`);
    if (button) {
        if (categoryVisible[category]) {
            button.style.backgroundColor = '#4dabf7';
            button.style.color = 'white';
        } else {
            button.style.backgroundColor = '#f8f8f8';
            button.style.color = 'black';
        }
    }
    
    // 마커 표시/숨기기
    categoryMarkers[category].forEach(marker => {
        if (categoryVisible[category] && map.getBounds().contain(marker.getPosition())) {
            marker.setMap(map);
        } else {
            marker.setMap(null);
        }
    });
    
    updateMarkersInViewport();
}

// 전체 카테고리 토글 함수 수정
function toggleAllCategories() {
    const currentLevel = map.getLevel();
    
    if (currentLevel > 4) {
        alert('지도를 더 확대해주세요 (레벨 4 이하)');
        return;
    }
    
    allCategoriesVisible = !allCategoriesVisible;
    
    // 모든 카테고리 버튼 스타일 업데이트
    updateAllButtonsStyle();
    
    // 모든 카테고리 마커 표시/숨기기
    Object.keys(categoryMarkers).forEach(category => {
        categoryVisible[category] = allCategoriesVisible;
        categoryMarkers[category].forEach(marker => {
            if (allCategoriesVisible && map.getBounds().contain(marker.getPosition())) {
                marker.setMap(map);
            } else {
                marker.setMap(null);
            }
        });
    });
}

// 데이터 로드 상태를 추적하는 플래그 추가
let categoriesLoaded = false;

async function loadCategoryData() {
    // 이미 로드된 경우 다시 로드하지 않음
    if (categoriesLoaded) {
        console.log('Categories already loaded');
        return;
    }

    const categoryFiles = {
        // 공공기관 및 안전
        'PO': '/static/data/dataset/public_institutions/police_office.csv',
        'CC': '/static/data/dataset/public_institutions/community_center.csv',
        'PT': '/static/data/dataset/public_institutions/post_office.csv',
        
        // 의료 시설
        'HP': '/static/data/dataset/medical/hospital.csv',
        'PH': '/static/data/dataset/medical/public_health_center.csv',
        
        // 금융 기관
        'TO': '/static/data/dataset/financial/tax_office.csv',

        // 편의 시설
        'CS': '/static/data/dataset/amenities/convenience_store.csv',
        'EG': '/static/data/dataset/amenities/electric_gas_station.csv',
        'GS': '/static/data/dataset/amenities/gas_station.csv',
        'SL': '/static/data/dataset/amenities/self_laundromat.csv',
        'SM': '/static/data/dataset/amenities/supermarket.csv',

        // 교통 관련
        'BS': '/static/data/dataset/transportation/bus.csv',
        'PS': '/static/data/dataset/transportation/park_station.csv',
        'SB': '/static/data/dataset/transportation/subway.csv',
        
        // 교육 관련
        'DC': '/static/data/dataset/education/daycare.csv',
        'ED': '/static/data/dataset/education/education.csv',
        'SC': '/static/data/dataset/education/school.csv',
        'UV': '/static/data/dataset/education/university.csv',

        // 여가 관련
        'FN': '/static/data/dataset/leisure_living/fitness.csv',
        'MR': '/static/data/dataset/leisure_living/music_room.csv',
        'PR': '/static/data/dataset/leisure_living/pc_room.csv',
        'TT': '/static/data/dataset/leisure_living/theater.csv',

        // 체육/공원 관련
        'OS': '/static/data/dataset/parks_natural/outdoor_sports.csv',
        'PK': '/static/data/dataset/parks_natural/park.csv',
    };

    // 각 카테고리의 마커 데이터 로드
    try {
        for (const category in categoryFiles) {
            await loadMarkers(category, categoryFiles[category]);
            console.log(`Successfully loaded markers for category: ${category}`);
        }
        // 모든 카테고리 로드가 완료되면 플래그를 true로 설정
        categoriesLoaded = true;
        console.log('All categories loaded successfully');
    } catch (error) {
        console.error('Error loading category data:', error);
    }
}

// 초기화 함수도 수정
function initCategories() {
    if (!categoriesLoaded) {
        loadCategoryData();
    }
    
    // 지도 이벤트 리스너 추가
    kakao.maps.event.addListener(map, 'idle', () => {
        if (viewportUpdateTimer) {
            clearTimeout(viewportUpdateTimer);
        }
        
        viewportUpdateTimer = setTimeout(() => {
            if (isValidMapLevel()) {
                updateMarkersInViewport();
            }
        }, VIEWPORT_UPDATE_DELAY);
    });
    
    // 줌 레벨 변경 이벤트 리스너
    kakao.maps.event.addListener(map, 'zoom_changed', function() {
        const currentLevel = map.getLevel();
        
        if (currentLevel > 4) {
            // 레벨이 4보다 크면 모든 마커 숨기기
            Object.keys(categoryMarkers).forEach(category => {
                categoryVisible[category] = false;
                categoryMarkers[category].forEach(marker => marker.setMap(null));
            });
            allCategoriesVisible = false;
            updateAllButtonsStyle(false);
        } else {
            // 레벨이 4 이하일 때 이전에 활성화된 카테고리만 표시
            if (allCategoriesVisible) {
                updateMarkersInViewport();
            }
        }
    });
}

// 버튼 스타일 업데이트 헬퍼 함수
function updateAllButtonsStyle(active = allCategoriesVisible) {
    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(button => {
        if (active) {
            button.style.backgroundColor = '#4dabf7';
            button.style.color = 'white';
        } else {
            button.style.backgroundColor = '#f8f8f8';
            button.style.color = 'black';
        }
    });
}

// 전체 버튼 상태 업데이트 함수
function updateAllCategoriesButton() {
    const allSelected = Object.values(categoryVisible).every(visible => visible);
    const allButton = document.querySelector('.category-btn');
    
    allCategoriesVisible = allSelected;
    if (allSelected) {
        allButton.style.backgroundColor = '#4dabf7';
        allButton.style.color = 'white';
    } else {
        allButton.style.backgroundColor = '#f8f8f8';
        allButton.style.color = 'black';
    }
}

// 메인 카테고리 토글 함수
function toggleMainCategory(mainCategory) {
    const subCategories = document.getElementById(`${mainCategory}-categories`);
    const allSubCategories = document.querySelectorAll('.sub-categories');
    
    // 다른 서브 카테고리들을 모두 닫음
    allSubCategories.forEach(category => {
        if (category.id !== `${mainCategory}-categories`) {
            category.style.display = 'none';
        }
    });
    
    // 선택된 서브 카테고리 토글
    if (subCategories.style.display === 'block') {
        subCategories.style.display = 'none';
    } else {
        subCategories.style.display = 'block';
    }
} 