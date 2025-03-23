// DOM 요소 초기화 함수
function initializeElements() {
    return {
        backButton: document.getElementById('backButton'),
        closeButton: document.getElementById('closeButton'),
        cards: document.querySelectorAll('.bg-white'),
        progressBars: document.querySelectorAll('.progress-bar-fill'),
        moveButtons: document.querySelectorAll('[data-lat][data-lng]')
    };
}

// 카드 애니메이션 설정
function setupCardAnimations(cards) {
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('shadow-lg');
        });
        card.addEventListener('mouseleave', () => {
            card.classList.remove('shadow-lg');
        });
    });
}

// 프로그레스 바 설정
function setupProgressBars(progressBars) {
    progressBars.forEach(bar => {
        const score = parseFloat(bar.getAttribute('data-score'));
        if (!isNaN(score)) {
            bar.style.width = score + '%';
        }
    });
}

// 지도 이동 함수
function moveToLocation(buttonElement) {
    // 좌표 추출
    const lat = parseFloat(buttonElement.getAttribute('data-lat'));
    const lng = parseFloat(buttonElement.getAttribute('data-lng'));
    
    // 입력 좌표 유효성 검사
    if (isNaN(lat) || isNaN(lng)) {
        alert("유효한 지도 좌표를 찾을 수 없습니다.");
        return false;
    }
    
    try {
        // 부모 창 찾기
        let parentWindow = window;
        
        // iframe인 경우 부모 창 참조
        if (window.parent && window.parent !== window) {
            parentWindow = window.parent;
        }
        
        // 지도 iframe에 직접 메시지 전송
        const mapFrame = parentWindow.document.getElementById('mapFrame');
        if (mapFrame && mapFrame.contentWindow) {
            mapFrame.contentWindow.postMessage({ 
                type: "moveToLocation", 
                lat: lat,
                lng: lng
            }, "*");
            console.log("지도 iframe으로 직접 좌표 전송 성공");
            
            // 모달 상태 변경
            const modalElement = document.querySelector('.content-container');
            if (modalElement) {
                modalElement.style.opacity = '0.7';
                setTimeout(() => {
                    modalElement.style.opacity = '1';
                }, 3000);
            }
            
            return true;
        }
        
        // 백업 방법: 부모 창의 moveToMapLocation 함수 사용
        if (typeof parentWindow.moveToMapLocation === 'function') {
            parentWindow.moveToMapLocation(lat, lng);
            return true;
        }
        return false;
        
    } catch (e) {
        alert("지도 이동 중 오류가 발생했습니다.");
        return false;
    }
}

// 이벤트 리스너 설정
function setupEventListeners(elements) {
    // 이전 페이지로 버튼
    elements.backButton.addEventListener('click', () => {
        window.location.href = "/recommendations/modal_page2/";
    });
    
    // 모달 닫기 버튼
    elements.closeButton.addEventListener('click', () => {
        if (window.parent !== window) {
            window.parent.postMessage({ action: 'closeModal' }, '*');
        }
    });

    // 지도 이동 버튼들에 이벤트 리스너 추가
    elements.moveButtons.forEach(button => {
        button.addEventListener('click', function() {
            moveToLocation(this);
        });
    });
}

// 첫 번째 추천 지역으로 자동 이동
function moveToFirstRecommendation(moveButtons) {
    if (moveButtons.length > 0) {
        console.log("첫 번째 추천 지역으로 자동 이동 준비");
        setTimeout(() => {
            moveToLocation(moveButtons[0]);
        }, 1000);
    }
}

// 메인 초기화 함수
export function initialize() {
    document.addEventListener("DOMContentLoaded", function() {
        const elements = initializeElements();
        
        setupCardAnimations(elements.cards);
        setupProgressBars(elements.progressBars);
        setupEventListeners(elements);
        moveToFirstRecommendation(elements.moveButtons);
    });
}

// moveToLocation 함수를 전역으로 노출
window.moveToLocation = moveToLocation; 