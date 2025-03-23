import { showToast } from './modal-function.js';

// 지도 관련 함수들
export function sendLocationToMap() {
    const mapFrame = document.getElementById("mapFrame");

    if (!mapFrame.contentWindow) {
        console.error("❌ mapFrame.contentWindow가 null입니다! iframe이 아직 로드되지 않았을 가능성이 큼.");
        return;
    }

    let selectedDistrict = decodeURIComponent(sessionStorage.getItem("selectedDistrict"));
    let selectedDong = decodeURIComponent(sessionStorage.getItem("selectedDong"));
    let type = decodeURIComponent(sessionStorage.getItem("type"));

    if (selectedDistrict && selectedDong && type === 'moveToLocation') {
        const fullAddress = `${selectedDistrict} ${selectedDong}`;
        console.log("📤 지도에 메시지 전송 (iframe 완전 로드 후): ", fullAddress);

        mapFrame.contentWindow.postMessage({
            type: "moveToLocation",
            address: fullAddress 
        }, "*");

        // 메시지 전송 후 sessionStorage 초기화
        sessionStorage.removeItem("selectedDistrict");
        sessionStorage.removeItem("selectedDong");
        sessionStorage.removeItem("type");
    }
    else {
        mapFrame.contentWindow.postMessage({
            type: 'initializeMap',
        }, '*');

        // 메시지 전송 후 sessionStorage 초기화
        sessionStorage.removeItem("selectedDistrict");
        sessionStorage.removeItem("selectedDong");
        sessionStorage.removeItem("type");
    }
}

export function updateMapFilters(filterType, value) {
    const mapFrame = document.getElementById('mapFrame');
    
    if (!mapFrame.contentWindow) {
        console.error("❌ mapFrame이 아직 로드되지 않았습니다.");
        return;
    }

    // 해당 필터 그룹의 모든 버튼 선택 해제
    const buttons = document.querySelectorAll(`[data-type][onclick*="updateMapFilters('${filterType}"]`);
    buttons.forEach(btn => {
        btn.classList.remove('ui-selected', 'bg-blue-500', 'text-white', 'shadow-md');
        btn.classList.add('bg-white', 'text-gray-700');
    });

    // 클릭된 버튼 선택 상태로 변경
    const clickedButton = event ? event.currentTarget : 
        document.querySelector(`[data-type="전체"][onclick*="updateMapFilters('${filterType}"]`);
    clickedButton.classList.remove('bg-white', 'text-gray-700');
    clickedButton.classList.add('ui-selected', 'bg-blue-500', 'text-white', 'shadow-md');

    // 선택 상태 저장
    sessionStorage.setItem(`selected_${filterType}`, value);

    // iframe 로드 완료 후 필터 적용
    if (mapFrame.contentWindow.setPropertyFilter && mapFrame.contentWindow.setTransactionFilter) {
        if (filterType === 'property') {
            mapFrame.contentWindow.setPropertyFilter(value);
        } else {
            mapFrame.contentWindow.setTransactionFilter(value);
        }
    }
}

export function handleCategoryToggle(category) {
    const mapWindow = document.getElementById('mapFrame').contentWindow;
    const btn = event.target;
    
    if (category === 'ALL') {
        // 전체 버튼 클릭 시
        const allButtons = document.querySelectorAll('.category-btn');
        const isActivating = !btn.classList.contains('active');
        
        // 전체 버튼을 포함한 모든 버튼의 스타일 변경
        allButtons.forEach(button => {
            if (isActivating) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // 지도에 전체 카테고리 토글 적용
        mapWindow.toggleAllCategories();
    } else {
        // 개별 카테고리 버튼 클릭 시
        btn.classList.toggle('active');
        mapWindow.toggleCategory(category, btn);
        
        // 모든 개별 버튼이 활성화되었는지 확인
        const categoryButtons = document.querySelectorAll('.category-btn:not([onclick="handleCategoryToggle(\'ALL\')"])');
        const allButton = document.querySelector('.category-btn[onclick="handleCategoryToggle(\'ALL\')"]');
        const allActive = Array.from(categoryButtons).every(button => button.classList.contains('active'));
        
        // 전체 버튼 상태 업데이트
        if (allActive) {
            allButton.classList.add('active');
        } else {
            allButton.classList.remove('active');
        }
    }
}

export function moveToMapLocation(lat, lng) {
    console.log('전역 moveToMapLocation 함수 호출됨:', lat, lng);
    
    const mapFrame = document.getElementById('mapFrame');
    if (mapFrame && mapFrame.contentWindow) {
        mapFrame.contentWindow.postMessage({ 
            type: "moveToLocation", 
            lat: lat,
            lng: lng
        }, "*");
        console.log('지도 iframe으로 좌표 전달 완료');
        return true;
    } else {
        console.error('지도 iframe을 찾을 수 없음');
        return false;
    }
}

export function setupMapMessageHandler() {
    let clusterCenter = null;
    let mapLevel = null;
    
    window.addEventListener('message', function(event) {
        if (event.data.type === 'clusterCenter') {
            clusterCenter = event.data.center;
            mapLevel = clusterCenter.level;

            if (mapLevel <= 4) {
                const distanceButton = document.getElementById('toggleDistance');
                distanceButton.disabled = false;
                distanceButton.classList.remove('opacity-50');
                
                const distanceFrame = document.getElementById('distanceFrame');
                if (distanceFrame) {
                    distanceFrame.contentWindow.postMessage({
                        type: 'updateDistances',
                        center: {
                            lat: clusterCenter.lat,
                            lng: clusterCenter.lng
                        },
                        level: mapLevel
                    }, '*');
                }
            }
        }
    }); 
    return { getClusterCenter: () => clusterCenter, getMapLevel: () => mapLevel };
}

export function setupPropertyCheck() {
    const MapMessageHandler = setupMapMessageHandler();

    document.getElementById('checkProperties').addEventListener('click', function() {
        const clusterCenter = MapMessageHandler.getClusterCenter();
        const mapLevel = MapMessageHandler.getMapLevel();
        console.log('clusterCenter:', clusterCenter);
        console.log('mapLevel:', mapLevel);
        if (clusterCenter) {
            if (mapLevel > 4) {
                showToast();
                return;
            }
            
            const selectedProperty = sessionStorage.getItem('selected_property') || '전체';
            const selectedTransaction = sessionStorage.getItem('selected_transaction') || '전체';
            
            let propertyType = '';
            switch(selectedProperty) {
                case '원룸': propertyType = 'OR'; break;
                case '투룸': propertyType = 'TR'; break;
                default: propertyType = 'OR:TR';
            }

            let transactionType = '';
            switch(selectedTransaction) {
                case '월세': transactionType = 'RENT'; break;
                case '전세': transactionType = 'JEONSE'; break;
                default: transactionType = 'RENT:JEONSE';
            }

            const naverLandUrl = `https://new.land.naver.com/rooms?` + 
                `ms=${clusterCenter.lat},${clusterCenter.lng},16&` +
                `type=${transactionType}&` +
                `roomType=${propertyType}&` +
                `aa=SMALLSPCRENT`;

            window.open(naverLandUrl, '_blank');
        } else {
            alert('먼저 지도에서 클러스터를 선택해주세요.');
        }
    });
}
