// 전역 상태 관리
const state = {
    weightType: 'facility',
    isCustomWeight: false
};

// DOM 요소 초기화 함수
function initializeElements() {
    return {
        form: document.getElementById("weightForm"),
        weightTypeInput: document.getElementById("weight_type"),
        weightTypes: document.querySelectorAll('.weight-type'),
        useCustomWeights: document.getElementById('useCustomWeights'),
        customWeightsContainer: document.getElementById('customWeightsContainer'),
        weights: {
            facility: document.getElementById('facility_weight'),
            price: document.getElementById('price_weight'),
            crime: document.getElementById('crime_weight'),
            population: document.getElementById('population_weight')
        },
        weightValues: {
            facility: document.getElementById('facilityWeightValue'),
            price: document.getElementById('priceWeightValue'),
            crime: document.getElementById('crimeWeightValue'),
            population: document.getElementById('populationWeightValue')
        },
        totalWeight: document.getElementById('totalWeight'),
        weightWarning: document.getElementById('weightWarning'),
        backButton: document.getElementById('backButton'),
        submitButton: document.getElementById('submitButton')
    };
}

// 가중치 유형 선택 처리
function handleWeightTypeSelection(selectedType, elements) {
    if (state.isCustomWeight) return;
    
    elements.weightTypes.forEach(type => {
        type.classList.remove('selected', 'bg-blue-500', 'text-white');
        type.classList.add('bg-white', 'text-gray-700');
    });
    
    selectedType.classList.remove('bg-white', 'text-gray-700');
    selectedType.classList.add('selected', 'bg-blue-500', 'text-white');
    
    elements.weightTypeInput.value = selectedType.dataset.type;
}

// 사용자 정의 가중치 토글 처리
function handleCustomWeightsToggle(isChecked, elements) {
    state.isCustomWeight = isChecked;
    
    if (isChecked) {
        enableCustomWeights(elements);
    } else {
        disableCustomWeights(elements);
    }
    
    updateTotalWeight(elements);
}

// 사용자 정의 가중치 활성화
function enableCustomWeights(elements) {
    elements.customWeightsContainer.classList.remove('opacity-50');
    Object.values(elements.weights).forEach(weight => weight.disabled = false);
    elements.weightTypeInput.value = 'custom';
    
    elements.weightTypes.forEach(type => {
        type.classList.remove('selected', 'bg-blue-500', 'text-white');
        type.classList.add('bg-white', 'text-gray-700', 'opacity-50');
    });
}

// 사용자 정의 가중치 비활성화
function disableCustomWeights(elements) {
    elements.customWeightsContainer.classList.add('opacity-50');
    Object.values(elements.weights).forEach(weight => weight.disabled = true);
    
    const selectedType = document.querySelector('.weight-type[data-type="facility"]');
    selectedType.classList.remove('bg-white', 'text-gray-700', 'opacity-50');
    selectedType.classList.add('selected', 'bg-blue-500', 'text-white');
    elements.weightTypeInput.value = 'facility';
    
    elements.weightTypes.forEach(type => {
        if (type.dataset.type !== 'facility') {
            type.classList.remove('opacity-50');
        }
    });
}

// 가중치 값 업데이트 처리
function handleWeightChange(weightId, value, elements) {
    const weightValueMap = {
        'facility_weight': 'facility',
        'price_weight': 'price',
        'crime_weight': 'crime',
        'population_weight': 'population'
    };
    
    const weightType = weightValueMap[weightId];
    if (weightType) {
        elements.weightValues[weightType].textContent = value;
    }
    
    updateTotalWeight(elements);
}

// 가중치 합계 업데이트
function updateTotalWeight(elements) {
    const total = Object.values(elements.weights).reduce((sum, weight) => 
        sum + parseInt(weight.value), 0);
    
    elements.totalWeight.textContent = total;
    
    if (total !== 100 && state.isCustomWeight) {
        elements.weightWarning.classList.remove('hidden');
    } else {
        elements.weightWarning.classList.add('hidden');
    }
}

// 폼 유효성 검사
function validateForm(elements) {
    if (state.isCustomWeight) {
        const total = Object.values(elements.weights).reduce((sum, weight) => 
            sum + parseInt(weight.value), 0);
        
        if (total !== 100) {
            alert(`가중치의 합이 100%가 되어야 합니다. 현재: ${total}%`);
            return false;
        }
    }
    return true;
}

// 이벤트 리스너 설정
function setupEventListeners(elements) {
    elements.weightTypes.forEach(type => {
        type.addEventListener('click', () => handleWeightTypeSelection(type, elements));
    });

    elements.useCustomWeights.addEventListener('change', (e) => {
        handleCustomWeightsToggle(e.target.checked, elements);
    });

    Object.entries(elements.weights).forEach(([key, weight]) => {
        weight.addEventListener('input', (e) => {
            handleWeightChange(e.target.id, e.target.value, elements);
        });
    });

    elements.backButton.addEventListener('click', () => {
        window.location.href = "/recommendations/modal_page2/";
    });

    elements.submitButton.addEventListener('click', () => {
        if (validateForm(elements)) {
            elements.form.submit();
        }
    });

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