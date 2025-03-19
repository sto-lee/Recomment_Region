// 필터 관련 전역 변수
let selectedProperty = "전체";  // 기본 필터: 매물종류 전체
let selectedRental = "전체";    // 기본 필터: 거래유형 전체

// 매물 종류 필터 설정
function setPropertyFilter(type) {
    selectedProperty = type;
    updateMarkers();
}

// 거래 유형 필터 설정
function setTransactionFilter(type) {
    selectedRental = type;
    updateMarkers();
}

// 마커 업데이트
function updateMarkers() {
    if (!clusterer) return;
    
    var filteredMarkers = [];
    for (var i = 0; i < rentalMarkers.length; i++) {
        var marker = rentalMarkers[i];
        
        // 매물 종류 조건 확인
        var propertyMatch = selectedProperty === "전체" || marker.propertyType === selectedProperty;
        // 거래 유형 조건 확인
        var rentalMatch = selectedRental === "전체" || marker.rentalType === selectedRental;
        
        // 두 조건이 모두 만족하면 마커 추가
        if (propertyMatch && rentalMatch) {
            filteredMarkers.push(marker);
        }
    }
    
    // 기존 마커 모두 제거
    clusterer.clear();
    // 필터링된 마커만 추가
    clusterer.addMarkers(filteredMarkers);
}

// 필터 적용 함수
function filterMarkers() {
    createMarkers(); // markers.js의 함수 호출
}

// 필터 초기화
function resetFilters() {
    document.getElementById('propertyType').value = 'all';
    document.getElementById('transactionType').value = 'all';
    filterMarkers();
} 