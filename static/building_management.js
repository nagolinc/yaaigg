document.addEventListener("DOMContentLoaded", function () {
    const buildingThumbnails = document.getElementById("building-thumbnails");
    const buildingImage = document.getElementById("building-image");
    const buildingName = document.getElementById("building-name");
    const messageDiv = document.getElementById("message");
    const buildingDescription = document.getElementById("building-description");
    const upgradeButton = document.getElementById("upgrade-button");
    const selectedMaterials = document.getElementById("selected-materials");
    const availableMaterials = document.getElementById("available-materials");
    const progressBar = document.querySelector(".progress-bar .progress");

    let selectedBuilding = null;
    let selectedMaterialIds = [];
    let user_data = {};

    function loadBuildingData() {
        fetch('/get_user_data')
            .then(response => response.json())
            .then(data => {
                user_data = data;
                setBuildingFromUrl();
                populateBuildingThumbnails(data.buildings);
                populateAvailableMaterials(data.items);
            });
    }

    function populateBuildingThumbnails(buildings) {
        buildingThumbnails.innerHTML = "";
        buildings.forEach(building => {
            const img = document.createElement("img");
            img.src = building.thumbnail_filename;
            img.className = "thumbnail";
            img.alt = building.name;
            img.addEventListener("click", () => selectBuilding(building));
            buildingThumbnails.appendChild(img);
        });
    }

    function selectBuilding(building) {


        //set the url to /building_management?building_id={building.id}
        const url = new URL(window.location.href);
        url.searchParams.set('building_id', building.id);
        window.history.pushState({}, '', url);

        selectedBuilding = building;
        buildingImage.src = building.filename;
    
        // Building name with star rating
        let buildingNameText = building.name;
        for (let i = 0; i < building.starRating; i++) {
            buildingNameText += "⭐";
        }
        buildingName.innerHTML = buildingNameText;
    
        // Building details
        buildingDescription.innerHTML = `
            <div><b>Caption:</b> ${building.caption}</div>
            <div><b>Level:</b> ${building.level}</div>
            <div><b>Element:</b> ${building.element}</div>
            <div><b>Race:</b> ${building.race}</div>
            <div><b>Type:</b> ${building.buildingType}</div>
        `;
    
        selectedMaterials.innerHTML = "";
        selectedMaterialIds = [];
        populateAvailableMaterials(user_data.items);
    }
    
    

    function populateAvailableMaterials(items) {

        if (!selectedBuilding) {
            return;
        }

        availableMaterials.innerHTML = "";
        items.forEach(item => {
            if (item.element === selectedBuilding.element) {
                const div = createMaterialDiv(item);
                if (item.equipped) {
                    div.classList.add("red-box");
                    div.style.pointerEvents = "none";
                } else {
                    div.addEventListener("click", () => selectMaterial(item));
                }
                //we need to add the id  as a data attribute to the div
                div.setAttribute('data-id', item.id);

                availableMaterials.appendChild(div);
            }
        });
    }

    function createMaterialDiv(item) {
        const div = document.createElement("div");
        div.className = "material-item";
        let stars='';
        for (let i = 0; i < item.starRating; i++) {
            stars += "⭐";
        }
        div.innerHTML = `
            <img src="${item.thumbnail_filename}" alt="${item.name}">
            <div>${item.name}</div>
            <div>${stars}</div>
            <div>Level: ${item.level}</
            
        `;
        return div;
    }

    function selectMaterial(item) {
        if (!selectedMaterialIds.includes(item.id)) {
            selectedMaterialIds.push(item.id);
            const div = createMaterialDiv(item);
            div.addEventListener("click", () => deselectMaterial(item, div));
            selectedMaterials.appendChild(div);
            calculateUpgradeChance();

            //we also need to remove the div from the available materials
            const divToRemove = document.querySelector(`.material-item[data-id="${item.id}"]`);
            divToRemove.remove();

        }
    }

    function deselectMaterial(item, div) {
        selectedMaterialIds = selectedMaterialIds.filter(id => id !== item.id);
        selectedMaterials.removeChild(div);


        //we also need to add the div back to the available materials
        const divToAdd = createMaterialDiv(item);
        divToAdd.addEventListener("click", () => selectMaterial(item));
        divToAdd.setAttribute('data-id', item.id);
        availableMaterials.appendChild(divToAdd);


        calculateUpgradeChance();
    }

    function calculateUpgradeChance() {
        fetch('/upgrade_success_chance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ building: selectedBuilding.id, materials: selectedMaterialIds })
        })
        .then(response => response.json())
        .then(data => {
            messageDiv.innerHTML = data.message;
            //set the timeout attribute to the message div
            messageDiv.setAttribute('data-timeout', data.timeout);
            console.log('timeout',data.timeout);
        });
    }

    upgradeButton.addEventListener("click", () => {
        if (selectedBuilding && selectedMaterialIds.length > 0) {
            startUpgradeProcess();
        }
    });

    function startUpgradeProcess() {
        const timeout = parseFloat(messageDiv.getAttribute('data-timeout')) || 5;
        console.log('timeout',timeout);
        progressBar.style.width = "0";
        let startTime = null;

        function updateProgress(timestamp) {
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;
            const progress = Math.min((elapsed / (timeout * 1000)) * 100, 100);
            progressBar.style.width = `${progress}%`;
            if (progress < 100) {
                requestAnimationFrame(updateProgress);
            } else {
                finalizeUpgrade();
            }
        }

        requestAnimationFrame(updateProgress);
    }

    function finalizeUpgrade() {
        fetch('/do_upgrade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ building: selectedBuilding.id, materials: selectedMaterialIds })
        })
        .then(response => response.json())
        .then(data => {
            messageDiv.innerHTML = data.message;
            loadBuildingData();
            //clear the selected materials
            selectedMaterials.innerHTML = "";
        });
    }

    loadBuildingData();


    function setBuildingFromUrl(){
        //if url looks like /building_management?building_id=1 then we need to select the building with id 1
        const urlParams = new URLSearchParams(window.location.search);
        const buildingId = urlParams.get('building_id');
        if(buildingId){
            
            //find building with buildingId in the user_data
            const building = user_data.buildings.find(b => b.id === buildingId);
            if(building){
                selectBuilding(building);
            }

            console.log(buildingId,building);
        }
    }

});
