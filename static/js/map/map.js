// 지도 관련 전역 변수
let map;
let currentMarker; // 현재 활성화된 마커

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
            const propertyMatch = currentFilters.propertyType === '전체' || 
                                marker.propertyType === currentFilters.propertyType;
            const transactionMatch = currentFilters.transactionType === '전체' || 
                                marker.transactionType === currentFilters.transactionType;
            
            if (propertyMatch && transactionMatch) {
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

    // ✅ 지도 로딩 완료 후, 부모 페이지("동선택화면.html")에 알림
    window.parent.postMessage({ type: "mapLoaded" }, "*");

    // ✅ 지도 로딩 후 카테고리 기능 활성화
    window.toggleCategory = toggleCategory;
    window.toggleAllCategories = toggleAllCategories;
};

console.log("✅ map.js - 메시지 리스너 등록됨");

// ✅ 메시지를 받아서 지도 이동
window.addEventListener("message", function(event) {
    console.log("📥 map.js - 메시지 수신됨:", event.data);

    if (!event.data) {
        console.error("❌ map.js - event.data가 비어 있음!");
        return;
    }

    if (event.data.type === "moveToLocation") {
        // 위치 이동 요청 처리
        if (event.data.address) {
            // 주소 기반 이동 (기존 기능)
            const address = event.data.address;
            console.log("📌 주소 기반 지도 이동 요청 수신: ", address);

            // ✅ 주소를 좌표로 변환하여 지도 이동
            const geocoder = new kakao.maps.services.Geocoder();
            geocoder.addressSearch(address, function(result, status) {
                if (status === kakao.maps.services.Status.OK) {
                    const coords = new kakao.maps.LatLng(result[0].y, result[0].x);
                    console.log("📍 지도 이동 좌표:", coords);
                    map.setCenter(coords);
                    map.setLevel(4); // 줌 레벨 조정
                } else {
                    console.error("📍 지도 이동 실패 - 주소 검색 실패:", status);
                }
            });
        } 
        else if (event.data.lat !== undefined && event.data.lng !== undefined) {
            // 좌표 기반 이동 (새로운 기능)
            const lat = parseFloat(event.data.lat);
            const lng = parseFloat(event.data.lng);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                console.log("📌 좌표 기반 지도 이동 요청 수신:", lat, lng);
                const coords = new kakao.maps.LatLng(lat, lng);
                
                // 마커 처리
                if (window.currentMarker) {
                    window.currentMarker.setMap(null); // 기존 마커 제거
                }
                
                // 새 마커 생성
                window.currentMarker = new kakao.maps.Marker({
                    position: coords,
                    map: map
                });
                
                // 지도 이동
                map.setCenter(coords);
                map.setLevel(3); // 줌 레벨 더 가깝게 조정
                console.log("✅ 좌표 기반 지도 이동 완료");
            } else {
                console.error("❌ 유효하지 않은 좌표:", event.data);
            }
        } else {
            console.error("❌ 이동할 위치 정보가 없음:", event.data);
        }
    } 
    else if (event.data.type === "initializeMap") {
        console.log("📍 지도 초기화 요청 수신");
        // 서울시청 좌표로 지도 중심 이동
        const defaultCenter = new kakao.maps.LatLng(37.5665, 126.9780);
        map.setCenter(defaultCenter);
        map.setLevel(8);  // 기본 줌 레벨로 설정
        console.log("✅ 지도 위치 초기화 완료");
    }
    else {
        console.warn("⚠️ map.js - 알 수 없는 메시지 타입:", event.data);
    }
});

// 필터 설정 함수 추가
function setPropertyFilter(type) {
    currentFilters.propertyType = type;
    updateMarkersBasedOnFilters();
}

// 거래 유형 필터 설정 함수 추가
function setTransactionFilter(type) {
    currentFilters.transactionType = type;
    updateMarkersBasedOnFilters();
}

// 함수들을 window 객체에 추가하여 외부에서 접근 가능하게 함
window.setPropertyFilter = setPropertyFilter;
window.setTransactionFilter = setTransactionFilter;

// 지도 객체를 전역으로 노출
window.kakaoMap = map;
window.currentMarker = currentMarker;

// 좌표로 지도 이동 함수 추가
window.moveToCoordinates = function(lat, lng) {
    if (!map) {
        console.error('지도가 초기화되지 않았습니다.');
        return false;
    }
    
    try {
        const coords = new kakao.maps.LatLng(lat, lng);
        
        // 마커 처리
        if (window.currentMarker) {
            window.currentMarker.setMap(null);
        }
        
        // 새 마커 생성
        window.currentMarker = new kakao.maps.Marker({
            position: coords,
            map: map
        });
        
        // 지도 이동
        map.setCenter(coords);
        map.setLevel(3);
        return true;
    } catch (error) {
        console.error('지도 이동 중 오류 발생:', error);
        return false;
    }
};