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
        const address = event.data.address;
        console.log("📌 지도 이동 요청 수신: ", address);

        if (!address) {
            console.error("❌ map.js - 받은 주소가 유효하지 않음!");
            return;
        }

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