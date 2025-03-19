// 지도 관련 전역 변수
let map;

// 필터 상태를 저장할 변수
let currentFilters = {
    propertyType: '전체',
    transactionType: '전체'
};

// 지도 초기화
async function initMap() {
    const container = document.getElementById('map');
    const options = {
        center: new kakao.maps.LatLng(37.5665, 126.9780),
        level: 8
    };

    map = new kakao.maps.Map(container, options);
    
    // 지도 이벤트 리스너 추가
    kakao.maps.event.addListener(map, 'idle', function() {
        updateMarkersBasedOnFilters();  // 필터 적용된 마커 업데이트
    });
    
    return map;
}

// 줌 컨트롤
function zoomIn() {
    map.setLevel(map.getLevel() - 1);
}

function zoomOut() {
    map.setLevel(map.getLevel() + 1);
}

// 필터 업데이트 함수
function updateFilters(filters) {
    currentFilters = { ...currentFilters, ...filters };
    
    // 여기에 필터에 따른 마커 표시/숨김 로직 추가
    updateMarkersBasedOnFilters();
}

// 필터에 따른 마커 업데이트
function updateMarkersBasedOnFilters() {
    if (!map || !markers) return;
    
    const bounds = map.getBounds();
    markers.forEach(marker => {
        if (bounds.contain(marker.getPosition())) {
            // filters.js의 전역 변수 사용
            const propertyMatch = selectedProperty === "전체" || marker.propertyType === selectedProperty;
            const rentalMatch = selectedRental === "전체" || marker.rentalType === selectedRental;
            
            if (propertyMatch && rentalMatch) {
                marker.setMap(map);
            } else {
                marker.setMap(null);
            }
        } else {
            marker.setMap(null);
        }
    });
}

// 페이지 로드 시 지도 초기화
window.onload = async function() {
    map = await initMap();
    await initRegions();
    await initMarkers();
    await initCategories();
    
    // categories.js의 함수들을 window 객체에 추가
    window.toggleCategory = toggleCategory;
    window.toggleAllCategories = toggleAllCategories;
}; 