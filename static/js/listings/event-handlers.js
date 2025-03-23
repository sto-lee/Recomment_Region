// 이벤트 핸들러 관련 함수들
export function setupDistrictEvents() {
    const districtSelect = document.getElementById("district-select");
    const dongSelect = document.getElementById("dong-select");
    const mapFrame = document.getElementById("mapFrame");

    districtSelect.addEventListener("change", function () {
        const selectedDistrict = this.value;
        sessionStorage.setItem("selectedDistrict", selectedDistrict);

        if (selectedDistrict) {
            fetch(`/get_dongs/?district=${encodeURIComponent(selectedDistrict)}`)
                .then(response => response.json())
                .then(data => {
                    dongSelect.innerHTML = "<option value=''>동 선택</option>";
                    data.dongs.forEach(dong => {
                        const option = document.createElement("option");
                        option.value = dong;
                        option.textContent = dong;
                        dongSelect.appendChild(option);
                    });
                    dongSelect.disabled = false;
                })
                .catch(error => console.error("Error fetching dongs:", error));

            mapFrame.contentWindow.postMessage({ 
                type: "moveToLocation", 
                address: selectedDistrict 
            }, "*");
        }
    });
}

export function setupDongEvents() {
    const districtSelect = document.getElementById("district-select");
    const dongSelect = document.getElementById("dong-select");
    const mapFrame = document.getElementById("mapFrame");
    const iframe = document.getElementById("pricesPanelFrame");

    dongSelect.addEventListener("change", function () {
        const selectedDistrict = districtSelect.value;
        const selectedDong = this.value;

        sessionStorage.setItem("selectedDistrict", selectedDistrict);
        sessionStorage.setItem("selectedDong", selectedDong);

        if (selectedDistrict && selectedDong) {
            const fullAddress = `${selectedDistrict} ${selectedDong}`;
            mapFrame.contentWindow.postMessage({ 
                type: "moveToLocation", 
                address: fullAddress 
            }, "*");
        }

        // researchment.html에 동 정보 전달
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: "updateDong",
                dong: selectedDong
            }, "*");
        }
    });
}

export function setupPanelEvents() {
    const surroundingsPanel = document.getElementById('surroundingsPanel');
    const pricesPanel = document.getElementById('pricesPanel');
    const crimePanel = document.getElementById('crimePanel');
    const populationPanel = document.getElementById('populationPanel');
    const distancePanel = document.getElementById('distancePanel');

    function closeAllPanels() {
        surroundingsPanel.classList.add('hidden');
        pricesPanel.classList.add('hidden');
        crimePanel.classList.add('hidden');
        populationPanel.classList.add('hidden');
        distancePanel.classList.add('hidden');
    }

    // 각 패널 토글 이벤트 설정
    ['toggleSurroundings', 'togglePrices', 'toggleCrime', 'togglePopulation', 'toggleDistance'].forEach(id => {
        document.getElementById(id).addEventListener('click', function(event) {
            event.stopPropagation();
            const panel = document.getElementById(id.replace('toggle', '').toLowerCase() + 'Panel');
            const isCurrentlyVisible = panel.classList.contains('hidden');
            closeAllPanels();
            if (isCurrentlyVisible) {
                panel.classList.remove('hidden');
            }
        });
    });
}

export function setupConditionsEvents() {
    const conditionsButton = document.getElementById('conditionsButton');
    const conditionsPanel = document.getElementById('conditionsPanel');
    const arrowIcon = document.querySelector('svg');

    // 조건 버튼 클릭 시 패널 토글
    conditionsButton.addEventListener('click', function(event) {
        event.stopPropagation();
        const isHidden = conditionsPanel.classList.contains('hidden');
        
        conditionsPanel.classList.toggle('hidden');

        if (isHidden) {
            arrowIcon.style.transform = 'rotate(180deg)';
        } else {
            arrowIcon.style.transform = 'rotate(0)';
        }
    });

    // 패널 외부 클릭 시 닫기
    document.addEventListener('click', function(event) {
        if (!conditionsButton.contains(event.target) && !conditionsPanel.contains(event.target)) {
            conditionsPanel.classList.add('hidden');
            arrowIcon.style.transform = 'rotate(0)';
        }
    });

    // 필터 버튼 클릭 시 패널 유지
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    });
}

export function setupTransactionEvents() {
    const iframe = document.getElementById("pricesPanelFrame");
    const transactionButtons = document.querySelectorAll('.filter-btn[data-type="월세"], .filter-btn[data-type="전세"]');

    function sendTransactionToResearchment(transactionType) {
        sessionStorage.setItem("selectedTransaction", transactionType);
        if (iframe && iframe.contentWindow) {
            iframe.contentWindow.postMessage({
                type: "updateTransaction",
                transaction: transactionType
            }, "*");
        }
    }

    transactionButtons.forEach(button => {
        button.addEventListener("click", function () {
            const transactionType = this.getAttribute("data-type");
            sendTransactionToResearchment(transactionType);
        });
    });

    // 페이지 로드 시 기존 선택값 적용
    const savedTransaction = sessionStorage.getItem("selectedTransaction");
    if (savedTransaction) {
        sendTransactionToResearchment(savedTransaction);
    }
}
