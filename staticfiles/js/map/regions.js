let seoulRegions = {};

// 구/동 데이터 초기화
async function initRegions() {
    try {
        const response = await fetch('/static/data/gu_dong.json');
        const data = await response.json();
        seoulRegions = data;
        
        // 부모 창의 select 요소들에 접근
        const parentDistrictSelect = window.parent.document.getElementById('district-select');
        if (parentDistrictSelect) {
            populateDistrictSelect(parentDistrictSelect);
        } else {
            // 서울 전체 지도로 이동
            const seoulCenter = { lat: 37.5665, lng: 126.9780 };
            map.setCenter(new kakao.maps.LatLng(seoulCenter.lat, seoulCenter.lng));
            map.setLevel(9);
        }
    } catch (error) {
        console.error('Error loading regions:', error);
    }
}

// 구 선택 옵션 채우기
function populateDistrictSelect(districtSelect) {
    districtSelect.innerHTML = '<option value="">구 선택</option>';
    
    Object.keys(seoulRegions).forEach(district => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        districtSelect.appendChild(option);
    });

    // 구 선택 이벤트 리스너 추가
    districtSelect.addEventListener('change', handleDistrictChange);
}

// 구 선택 시 실행되는 함수
function handleDistrictChange() {
    const districtSelect = window.parent.document.getElementById('district-select');
    const dongSelect = window.parent.document.getElementById('dong-select');
    updateDongSelect(districtSelect, dongSelect);
    
    const selectedDistrict = districtSelect.value;
    
    if (selectedDistrict && seoulRegions[selectedDistrict]) {
        // 구 중심으로 이동
        const districtCenter = seoulRegions[selectedDistrict].center;
        map.setCenter(new kakao.maps.LatLng(districtCenter.lat, districtCenter.lng));
        map.setLevel(6);
    }
}

// 동 선택 시 실행되는 함수
function handleDongChange() {
    const districtSelect = window.parent.document.getElementById('district-select');
    const dongSelect = window.parent.document.getElementById('dong-select');
    const selectedDistrict = districtSelect.value;
    const selectedDong = dongSelect.value;
    
    if (selectedDistrict && selectedDong && seoulRegions[selectedDistrict].dongs[selectedDong]) {
        const dongCoords = seoulRegions[selectedDistrict].dongs[selectedDong];
        map.setCenter(new kakao.maps.LatLng(dongCoords.lat, dongCoords.lng));
        map.setLevel(4);
    }
}

// 동 선택 옵션 업데이트
function updateDongSelect(districtSelect, dongSelect) {
    dongSelect.innerHTML = '<option value="">동 선택</option>';
    const selectedDistrict = districtSelect.value;
    
    if (selectedDistrict && seoulRegions[selectedDistrict]) {
        const dongs = seoulRegions[selectedDistrict].dongs;
        Object.keys(dongs).forEach(dong => {
            const option = document.createElement('option');
            option.value = dong;
            option.textContent = dong;
            dongSelect.appendChild(option);
        });
    }

    // 동 선택 이벤트 리스너 추가
    dongSelect.addEventListener('change', handleDongChange);
}

// 특정 구로 이동하는 함수
function moveToDistrict(district) {
    if (seoulRegions[district]) {
        // 구 중심으로 이동
        const districtCenter = seoulRegions[district].center;
        map.setCenter(new kakao.maps.LatLng(districtCenter.lat, districtCenter.lng));
        map.setLevel(6);
        
        // 부모 창의 select 요소 업데이트
        const parentDistrictSelect = window.parent.document.getElementById('district-select');
        const parentDongSelect = window.parent.document.getElementById('dong-select');
        if (parentDistrictSelect) {
            parentDistrictSelect.value = district;
            updateDongSelect(parentDistrictSelect, parentDongSelect);
        }
    }
}

// 특정 동으로 이동하는 함수
function moveToDong(dong) {
    // 모든 구를 순회하면서 해당 동을 찾음
    for (const district in seoulRegions) {
        if (seoulRegions[district].dongs[dong]) {
            const dongCoords = seoulRegions[district].dongs[dong];
            map.setCenter(new kakao.maps.LatLng(dongCoords.lat, dongCoords.lng));
            map.setLevel(4);
            
            // 부모 창의 select 요소 업데이트
            const parentDistrictSelect = window.parent.document.getElementById('district-select');
            const parentDongSelect = window.parent.document.getElementById('dong-select');
            if (parentDistrictSelect) {
                parentDistrictSelect.value = district;
                updateDongSelect(parentDistrictSelect, parentDongSelect);
                parentDongSelect.value = dong;
            }
            break;
        }
    }
}