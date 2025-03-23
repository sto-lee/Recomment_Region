// 모달 관련 함수들
export function showToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('hidden');
    toast.classList.add('animate-fade-in-down');
    
    setTimeout(() => {
        toast.classList.add('animate-fade-out-up');
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.classList.remove('animate-fade-in-down', 'animate-fade-out-up');
        }, 300);
    }, 3000);
}

export function setupModalHandlers() {
    const recommendButton = document.getElementById('recommendButton');
    const minimizedModalContainer = document.getElementById('minimizedModalContainer');
    const recommendModal = document.getElementById('recommendModal');
    const closeRecommendModal = document.getElementById('closeRecommendModal');
    const minimizeRecommendModal = document.getElementById('minimizeRecommendModal');
    const modalIframe = document.getElementById('modalIframe');
    const mapFrame = document.getElementById('mapFrame');

    // 최소화된 모달 컨테이너 클릭 이벤트
    minimizedModalContainer.addEventListener('click', function() {
        recommendModal.classList.remove('hidden');
        minimizedModalContainer.classList.add('hidden');
    });

    // 추천 버튼 클릭 이벤트
    recommendButton.addEventListener('click', function() {
        modalIframe.src = "/recommendations/modal_page1/";
        recommendModal.classList.remove('hidden');
        minimizedModalContainer.classList.add('hidden');
    });

    // 최소화 버튼 이벤트
    minimizeRecommendModal.addEventListener('click', function() {
        recommendModal.classList.add('hidden');
        minimizedModalContainer.classList.remove('hidden');
    });
    
    // 닫기 버튼 이벤트
    closeRecommendModal.addEventListener('click', function() {
        recommendModal.classList.add('hidden');
        minimizedModalContainer.classList.add('hidden');
        modalIframe.src = 'about:blank';
    });
}

export function setupModalMessageHandler() {
    const mapFrame = document.getElementById('mapFrame');
    const recommendModal = document.getElementById('recommendModal');
    const minimizedModalContainer = document.getElementById('minimizedModalContainer');
    const modalIframe = document.getElementById('modalIframe');

    window.addEventListener('message', function(event) {
        if (event.data.action === 'closeModal') {
            recommendModal.classList.add('hidden');
            minimizedModalContainer.classList.add('hidden');
            modalIframe.src = 'about:blank';
        } else if (event.data.action === 'moveToLocation') {
            const { lat, lng } = event.data;
            if (mapFrame && mapFrame.contentWindow) {
                mapFrame.contentWindow.postMessage({ 
                    type: "moveToLocation", 
                    lat: lat,
                    lng: lng
                }, "*");
            }
        } else if (event.data.action === 'viewOnMap') {
            const location = event.data.location;
            if (mapFrame && mapFrame.contentWindow && location) {
                mapFrame.contentWindow.postMessage({ 
                    type: "moveToLocation", 
                    lat: location.lat,
                    lng: location.lng
                }, "*");
            }
        }
    });
}
