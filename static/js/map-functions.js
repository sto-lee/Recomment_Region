import { showToast } from './modal-function.js';

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

    // 클로저를 통해 현재 상태를 반환
    return {
        getClusterCenter: () => clusterCenter,
        getMapLevel: () => mapLevel
    };
}

export function setupPropertyCheck() {
    const mapHandler = setupMapMessageHandler(); // 핸들러 초기화

    document.getElementById('checkProperties').addEventListener('click', function() {
        const clusterCenter = mapHandler.getClusterCenter();
        const mapLevel = mapHandler.getMapLevel();
        
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