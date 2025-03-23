// 전역 상태 관리
const state = {
    propertyType: null
};

// DOM 요소 초기화 함수
function initializeElements() {
    return {
        form: document.getElementById("preferenceForm"),
        propertyTypeInputs: document.querySelectorAll('input[name="property_type"]'),
        jeonseSection: document.getElementById('jeonseSection'),
        monthlySection: document.getElementById('monthlySection'),
        backButton: document.getElementById('backButton'),
        submitButton: document.getElementById('submitButton'),
        jeonseInputs: {
            minDeposit: document.querySelector('input[name="jeonse_deposit_min"]'),
            maxDeposit: document.querySelector('input[name="jeonse_deposit_max"]')
        },
        monthlyInputs: {
            minDeposit: document.querySelector('input[name="monthly_deposit_min"]'),
            maxDeposit: document.querySelector('input[name="monthly_deposit_max"]'),
            minRent: document.querySelector('input[name="monthly_rent_min"]'),
            maxRent: document.querySelector('input[name="monthly_rent_max"]')
        }
    };
}

// 매물 형태에 따른 섹션 표시 처리
function handlePropertyTypeChange(propertyType, elements) {
    state.propertyType = propertyType;
    
    if (propertyType === 'jeonse') {
        elements.jeonseSection.style.display = 'block';
        elements.monthlySection.style.display = 'none';
    } else {
        elements.jeonseSection.style.display = 'none';
        elements.monthlySection.style.display = 'block';
    }
}

// 시세 범위 유효성 검사
function validatePriceRange(elements) {
    if (state.propertyType === 'jeonse') {
        const minDeposit = parseInt(elements.jeonseInputs.minDeposit.value);
        const maxDeposit = parseInt(elements.jeonseInputs.maxDeposit.value);
        
        if (minDeposit && maxDeposit && minDeposit > maxDeposit) {
            alert("최소 보증금이 최대 보증금보다 클 수 없습니다.");
            return false;
        }
    } else {
        const minDeposit = parseInt(elements.monthlyInputs.minDeposit.value);
        const maxDeposit = parseInt(elements.monthlyInputs.maxDeposit.value);
        const minRent = parseInt(elements.monthlyInputs.minRent.value);
        const maxRent = parseInt(elements.monthlyInputs.maxRent.value);
        
        if (minDeposit && maxDeposit && minDeposit > maxDeposit) {
            alert("최소 보증금이 최대 보증금보다 클 수 없습니다.");
            return false;
        }
        if (minRent && maxRent && minRent > maxRent) {
            alert("최소 월세가 최대 월세보다 클 수 없습니다.");
            return false;
        }
    }
    return true;
}

// 폼 유효성 검사
function validateForm(elements) {
    const propertyType = elements.form.querySelector('input[name="property_type"]:checked');

    if (!propertyType) {
        alert("매물 형태를 선택해주세요.");
        return false;
    }

    return validatePriceRange(elements);
}

// 이벤트 리스너 설정
function setupEventListeners(elements) {
    // 이전 페이지로 버튼
    elements.backButton.addEventListener('click', () => {
        window.location.href = "/recommendations/modal_page1/";
    });

    // 제출 버튼 클릭 이벤트
    elements.submitButton.addEventListener('click', () => {
        if (validateForm(elements)) {
            elements.form.submit();
        }
    });

    // 매물 형태 변경 이벤트
    elements.propertyTypeInputs.forEach(input => {
        input.addEventListener('change', () => {
            handlePropertyTypeChange(input.value, elements);
        });
    });

    // 폼 제출 이벤트 처리
    elements.form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (validateForm(elements)) {
            elements.form.submit();
        }
    });
}

// 메인 초기화 함수
export function initialize() {
    document.addEventListener("DOMContentLoaded", function() {
        const elements = initializeElements();
        setupEventListeners(elements);
    });
} 