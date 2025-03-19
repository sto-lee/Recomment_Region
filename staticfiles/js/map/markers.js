// 마커 관련 전역 변수
let markers = [];
let propertyData = [];

// 전역 변수 선언
var rentalMarkers = [];
var clusterer;

// 마커 초기화
async function initMarkers() {
    try {
        const response = await fetch('/static/data/dataset/property/property_data.csv');
        const buffer = await response.arrayBuffer();
        const decoder = new TextDecoder('EUC-KR');
        const text = decoder.decode(buffer);
        
        var lines = text.split('\n');
        // 첫 줄은 헤더라고 가정
        for (var i = 1; i < lines.length; i++) {
            var line = lines[i].trim();
            if (!line) continue;
            
            var row = line.split(',');
            var propertyType = row[0].trim();
            var rentalType = row[1].trim();
            var lat = parseFloat(row[2]);
            var lng = parseFloat(row[3]);
            
            if (isNaN(lat) || isNaN(lng)) continue;
            
            var marker = new kakao.maps.Marker({
                position: new kakao.maps.LatLng(lat, lng)
            });
            
            // 마커에 속성 추가
            marker.propertyType = propertyType;
            marker.rentalType = rentalType;
            
            rentalMarkers.push(marker);
        }
        
        // 클러스터러 초기화
        clusterer = new kakao.maps.MarkerClusterer({
            map: map,
            markers: rentalMarkers,
            averageCenter: true,
            minLevel: 0,
            minClusterSize: 1,
            styles: [{
                width: '36px',
                height: '36px',
                background: '#2ecc71',  // 초록색
                color: '#fff',
                borderRadius: '50%',
                textAlign: 'center',
                lineHeight: '36px',
                fontSize: '14px',
                fontWeight: 'bold',
                border: '2px solid #27ae60'  // 테두리 색상
            }]
        });
        
        // 초기 필터링 적용
        updateMarkers();
        
    } catch (error) {
        console.error('Error loading property data:', error);
    }
}

// 함수를 전역으로 노출
window.initMarkers = initMarkers;

// CSV 파싱 함수
function parseCSV(csv) {
    const lines = csv.split('\n');
    const headers = lines[0].split(',');
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (!lines[i]) continue;
        const values = lines[i].split(',');
        const obj = {};
        headers.forEach((header, index) => {
            obj[header.trim()] = values[index]?.trim();
        });
        data.push(obj);
    }
    
    return data;
}

// 마커 생성 함수
function createMarkers() {
    // 기존 마커 제거
    markers.forEach(marker => marker.setMap(null));
    markers = [];
    clusterer.clear();
    
    // 필터링된 데이터로 마커 생성
    const filteredData = propertyData.filter(property => {
        return (selectedProperty === "전체" || property.type === selectedProperty) &&
                (selectedRental === "전체" || property.transaction === selectedRental);
    });
    
    filteredData.forEach(property => {
        const marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(property.lat, property.lng)
        });
        
        // 마커에 속성 추가
        marker.propertyType = property.type;
        marker.rentalType = property.transaction;
        
        // 마커 클릭 이벤트
        kakao.maps.event.addListener(marker, 'click', function() {
            showPropertyInfo(property, marker);
        });
        
        markers.push(marker);
    });
    
    // 클러스터러에 마커 추가
    clusterer.addMarkers(markers);
}

// 매물 정보 표시
function showPropertyInfo(property, marker) {
    const content = `
        <div class="property-info">
            <h3>${property.name}</h3>
            <p>종류: ${property.type}</p>
            <p>거래: ${property.transaction}</p>
            <p>가격: ${property.price}</p>
            <p>면적: ${property.area}㎡</p>
        </div>
    `;
    
    const infowindow = new kakao.maps.InfoWindow({
        content: content
    });
    
    infowindow.open(map, marker);
} 