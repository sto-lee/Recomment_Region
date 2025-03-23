// 전역 상태 관리
const state = {
    selectedFacilities: new Set()
};

// DOM 요소 초기화 함수
function initializeElements() {
    return {
        districtSelect: document.getElementById("district-select"),
        dongSelect: document.getElementById("dong-select"),
        form: document.getElementById("recommendForm"),
        facilityItems: document.querySelectorAll('.facility-item'),
        preferredFacilitiesInput: document.getElementById('preferred_facilities'),
        selectedFacilitiesDiv: document.getElementById('selectedFacilities'),
        submitBtn: document.getElementById('submitBtn'),
        ageInput: document.getElementById("id_age")
    };
}

// 구 목록 가져오기
async function fetchDistricts(districtSelect) {
    try {
        const response = await fetch('/recommendations/get_districts/');
        const data = await response.json();
        
        districtSelect.innerHTML = '<option value="">구 선택</option>';
        data.districts.forEach(district => {
            const option = document.createElement('option');
            option.value = district;
            option.textContent = district;
            districtSelect.appendChild(option);
        });
    } catch (error) {
        console.error('구 목록 조회 중 오류:', error);
    }
}

// 나이 입력 제한 처리
function handleAgeInput(ageInput) {
    const value = parseInt(ageInput.value);
    if (value < 1) ageInput.value = 1;
    if (value > 150) ageInput.value = 150;
}

// 편의시설 선택 처리
function handleFacilitySelection(item, elements) {
    const facility = item.dataset.facility;
    
    if (item.classList.contains('selected')) {
        item.classList.remove('selected', 'bg-blue-500', 'text-white');
        state.selectedFacilities.delete(facility);
    } else {
        item.classList.add('selected', 'bg-blue-500', 'text-white');
        state.selectedFacilities.add(facility);
    }
    
    elements.preferredFacilitiesInput.value = Array.from(state.selectedFacilities).join(',');
    updateSelectedFacilitiesDisplay(elements.selectedFacilitiesDiv);
}

// 선택된 시설 표시 업데이트
function updateSelectedFacilitiesDisplay(selectedFacilitiesDiv) {
    if (state.selectedFacilities.size > 0) {
        const facilitiesList = Array.from(state.selectedFacilities).map((facility, index) => {
            const facilityElement = document.querySelector(`[data-facility="${facility}"]`);
            return `${index + 1}. ${facilityElement.textContent}`;
        }).join(', ');
        selectedFacilitiesDiv.textContent = `선택된 순서: ${facilitiesList}`;
    } else {
        selectedFacilitiesDiv.textContent = '';
    }
}

// 구/동 선택 처리
async function handleDistrictChange(district, dongSelect) {
    dongSelect.innerHTML = "<option value=''>동 선택 (선택사항)</option>";
    if (!district) return;

    try {
        const response = await fetch(`/recommendations/get_dongs/?district=${encodeURIComponent(district)}`);
        if (!response.ok) throw new Error('서버 응답 오류');

        const data = await response.json();
        if (!Array.isArray(data.dongs)) throw new Error('잘못된 데이터 형식');

        data.dongs.forEach(dong => {
            const option = document.createElement("option");
            option.value = dong;
            option.textContent = dong;
            dongSelect.appendChild(option);
        });
    } catch (error) {
        console.error("동 목록 조회 중 오류:", error);
        alert("동 목록을 불러오는데 실패했습니다. 다시 시도해주세요.");
    }
}

// 폼 유효성 검사
function validateForm(elements) {
    const age = elements.ageInput.value.trim();
    const gender = elements.form.querySelector('input[name="gender"]:checked');
    const district = elements.districtSelect.value;
    const facilities = elements.preferredFacilitiesInput.value;

    if (!age || !gender || !district || !facilities) {
        alert("필수 항목을 모두 입력해주세요.");
        return false;
    }

    if (state.selectedFacilities.size < 1) {
        alert("최소 1개 이상의 선호 편의시설을 선택해주세요.");
        return false;
    }

    if (age < 1 || age > 150) {
        alert("올바른 나이를 입력해주세요.");
        return false;
    }

    return true;
}

// 이벤트 리스너 설정
function setupEventListeners(elements) {
    elements.submitBtn.addEventListener('click', () => {
        if (validateForm(elements)) {
            elements.form.submit();
        }
    });

    elements.ageInput.addEventListener('input', () => handleAgeInput(elements.ageInput));

    elements.facilityItems.forEach(item => {
        item.addEventListener('click', () => handleFacilitySelection(item, elements));
    });

    elements.districtSelect.addEventListener('change', () => {
        handleDistrictChange(elements.districtSelect.value, elements.dongSelect);
    });

    elements.form.addEventListener('submit', (event) => {
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
        fetchDistricts(elements.districtSelect);
        setupEventListeners(elements);
    });
} 