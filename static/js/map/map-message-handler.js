/**
 * HOME Genie - 지도 메시지 처리기
 * iframe에서 보내는 메시지를 처리하여 지도를 제어하는 스크립트
 */

// 전역 변수로 kakaoMap과 currentMarker가 정의되어 있어야 합니다.
// window.kakaoMap - 카카오맵 객체
// window.currentMarker - 현재 활성화된 마커

// 메시지 이벤트 리스너 등록
window.addEventListener("message", function(event) {
    console.log("부모 창에서 메시지 수신:", event.data);
    
    // 메시지 타입 확인
    if (!event.data || typeof event.data !== 'object') {
        console.log("유효하지 않은 메시지 형식");
        return;
    }
    
    // 메시지 액션에 따라 처리
    switch (event.data.action) {
        case 'moveToLocation':
            handleMoveToLocation(event.data);
            break;
            
        case 'closeModal':
            handleCloseModal();
            break;
            
        default:
            console.log("지원하지 않는 메시지 액션:", event.data.action);
    }
});

/**
 * 지도 이동 처리 함수
 * @param {Object} data - 좌표 데이터 ({lat, lng})
 */
function handleMoveToLocation(data) {
    console.log("지도 이동 처리 함수 호출:", data);
    
    // 좌표 유효성 검사
    const lat = parseFloat(data.lat);
    const lng = parseFloat(data.lng);
    
    if (isNaN(lat) || isNaN(lng)) {
        console.error("유효하지 않은 좌표:", lat, lng);
        return;
    }
    
    try {
        // 지도 객체 확인
        if (!window.kakaoMap || !window.kakao || !window.kakao.maps) {
            console.error("카카오맵 객체를 찾을 수 없습니다");
            return;
        }
        
        // 좌표 생성 및 이동
        const moveLatLng = new window.kakao.maps.LatLng(lat, lng);
        window.kakaoMap.setCenter(moveLatLng);
        console.log("지도 중심 이동 완료:", lat, lng);
        
        // 마커 처리
        if (window.currentMarker) {
            window.currentMarker.setMap(null); // 기존 마커 제거
        }
        
        // 새 마커 생성
        window.currentMarker = new window.kakao.maps.Marker({
            position: moveLatLng
        });
        window.currentMarker.setMap(window.kakaoMap);
        console.log("마커 추가 완료");
        
        // 확대 레벨 설정
        window.kakaoMap.setLevel(3);
        console.log("확대 레벨 설정 완료");
        
        // 모달 표시 조정
        adjustModalVisibility();
        
    } catch (error) {
        console.error("지도 이동 중 오류 발생:", error);
    }
}

/**
 * 모달 닫기 처리 함수
 */
function handleCloseModal() {
    console.log("모달 닫기 요청");
    try {
        // 모달 관련 요소 찾기
        const modal = document.querySelector('.modal') || 
                      document.getElementById('recommendationModal') || 
                      document.querySelector('.modal-container');
        
        // 모달 닫기 버튼 찾기
        const closeButton = modal ? 
                           modal.querySelector('.close-button') || 
                           document.getElementById('closeModalButton') ||
                           modal.querySelector('[data-action="close"]') : null;
        
        // 닫기 버튼 클릭 이벤트 발생
        if (closeButton) {
            closeButton.click();
            console.log("모달 닫기 버튼 클릭");
        } else if (modal) {
            // 모달 숨기기
            modal.style.display = 'none';
            console.log("모달 숨김 처리");
        } else {
            console.warn("모달 또는 닫기 버튼을 찾을 수 없습니다");
        }
        
        // iframe 초기화
        const modalIframe = document.getElementById('modalIframe');
        if (modalIframe) {
            modalIframe.src = 'about:blank';
            console.log("iframe 초기화");
        }
        
    } catch (error) {
        console.error("모달 닫기 중 오류 발생:", error);
    }
}

/**
 * 모달 표시 조정 함수
 */
function adjustModalVisibility() {
    // 모달 반투명하게 만들거나 사이즈 조정
    const modal = document.querySelector('.modal-content') || 
                  document.querySelector('.modal-container');
    
    if (modal) {
        // 모달 위치나 크기 조정
        console.log("모달 표시 조정");
    }
}

/**
 * 전역 스코프에 지도 이동 함수 노출
 * iframe에서 직접 호출할 수 있도록 함
 */
window.moveToMapLocation = function(lat, lng) {
    console.log("전역 moveToMapLocation 함수 호출:", lat, lng);
    handleMoveToLocation({ lat, lng });
    return true;
};

// 스크립트 로딩 완료 로그
console.log("지도 메시지 처리기 로드 완료"); 