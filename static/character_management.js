document.addEventListener("DOMContentLoaded", function () {
    const npcThumbnails = document.getElementById("npc-thumbnails");
    const npcImage = document.getElementById("npc-image");
    const npcName = document.getElementById("npc-name");
    const buildingImage = document.getElementById("building-image");
    const buildingNameDiv = document.getElementById("building-name");
    const buildingsDropdown = document.getElementById("buildings");
    const equippedItems = document.getElementById("equipped-items");
    const unequippedItems = document.getElementById("unequipped-items");
    const npcInfo = document.getElementById("npc-info-detailed");

    let selectedNPC = null;

    let user_data = {}

    function loadNPCData() {
        fetch('/get_user_data')
            .then(response => response.json())
            .then(data => {

                user_data = data;
                populateNPCThumbnails(data.npcs);
                populateBuildingsDropdown(data.buildings);
            });
    }


    function loadNPCDataThenSelect(npcId) {
        fetch('/get_user_data')
            .then(response => response.json())
            .then(data => {

                user_data = data;
                populateNPCThumbnails(data.npcs);
                populateBuildingsDropdown(data.buildings);
                selectedNPC = data.npcs.find(npc => npc.id === npcId);
                console.log('about to die', selectedNPC)
                showNPCDetails(selectedNPC);
            });
    }


    function populateNPCThumbnails(npcs) {
        npcThumbnails.innerHTML = "";
        npcs.forEach(npc => {
            const img = document.createElement("img");
            img.src = npc.thumbnail_filename;
            img.className = "thumbnail";
            img.alt = npc.name;
            img.addEventListener("click", () => showNPCDetails(npc));
            npcThumbnails.appendChild(img);
        });
    }

    let once = true

    function populateBuildingsDropdown(buildings) {

        if (!once) return
        once = false

        console.log('this should only happen once')

        buildings.forEach(building => {
            const option = document.createElement("option");
            option.value = building.id;
            option.textContent = building.name;
            buildingsDropdown.appendChild(option);
        });

        buildingsDropdown.addEventListener("change", () => {
            console.log('huh', selectedNPC.id, buildingsDropdown.value)
            moveToBuilding(selectedNPC.id, buildingsDropdown.value);
            loadNPCDataThenSelect(selectedNPC.id);
        });
    }


    async function populateAvailableBuildingsDropdown(npcId, npcLocation,npcLocation_name) {
        console.log('populateAvailableBuildingsDropdown', npcId, npcLocation);
    
        try {
            const response = await fetch('/availablebuildings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ npc: npcId })
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const data = await response.json();
            const availableBuildings = data.available_buildings;
    
            // Clear existing options
            buildingsDropdown.innerHTML = '';
    
            // Add "None" option
            const noneOption = document.createElement("option");
            noneOption.value = '';
            noneOption.textContent = 'None';
            buildingsDropdown.appendChild(noneOption);
    
            // If npcLocation is not null and not in availableBuildings, add it to the list
            if (npcLocation && !availableBuildings.some(building => building.id === npcLocation)) {
                availableBuildings.push({"name": npcLocation_name, "id": npcLocation});
            }

            // Sort available buildings
            availableBuildings.sort((a, b) => a.name.localeCompare(b.name));
    
            // Add available buildings options
            availableBuildings.forEach(building => {
                const option = document.createElement("option");
                option.value = building.id;
                option.textContent = building.name;
                buildingsDropdown.appendChild(option);
            });
    
            // Select the current location
            if (npcLocation) {
                buildingsDropdown.value = npcLocation;
            } else {
                // Select "None"
                console.log('setting to none');
                buildingsDropdown.value = '';
            }
    
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
    }



    function updateBuildingsDropdownSelection(npc) {

        console.log('here', npc, npc.location, buildingsDropdown.value)

        if (npc && npc.location) {
            buildingsDropdown.value = npc.location;


            // Update the building image
            const building = user_data.buildings.find(b => b.id === npc.location);
            if (building && building.thumbnail_filename) {
                console.log('huh', building.thumbnail_filename)
                buildingImage.src = building.thumbnail_filename;
            } else {
                buildingImage.src = ''; // Set a default image if no image is found
                console.log('this should never happen!', building)
            }

        } else {
            buildingsDropdown.value = ''; // Clear selection if no building is set

            // Clear the building image
            //buildingImage.src = ''; // Set a default image if no image is found
        }
    }


    async function fetchPowerLevel(npcId) {
        try {
            const response = await fetch('/power_level', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ npc: npcId })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return data.power_level;
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
        }
    }


    function showNPCDetails(npc) {
        selectedNPC = npc;
        npcImage.src = npc.filename;

        let text = npc.name
        //add ⭐'s based on npc.star_rating
        for (let i = 0; i < npc.star_rating; i++) {
            text += "⭐"
        }
        //add level (default 1 if not found)
        text += ` (Level: ${npc.level || 1})`;


        //add power level
        fetchPowerLevel(npc.id).then((powerLevel) => {
            text += ` (Power: <span id=power>${powerLevel}</span>)`;
            npcName.innerHTML = text;
        });

        npcName.textContent = text


        // Set npc-info HTML content
        npcInfo.innerHTML = npc.caption + "<br>" +
            "<b>Race:</b> " + npc.race + "<br>" +
            "<b>Class:</b> " + npc.class + "<br>" +
            "<b>Element:</b> " + npc.element;


        const currentBuilding = user_data.buildings.find(b => b.id === npc.location);
        if (currentBuilding) {
            buildingImage.src = currentBuilding.thumbnail_filename;
            buildingNameDiv.textContent = currentBuilding.name;
            //add ⭐'s based on building.star_rating
            for (let i = 0; i < currentBuilding.star_rating; i++) {
                buildingNameDiv.textContent += "⭐"
            }

            //add a mange button to the building (which is just a link to /building_management?building_id={building.id})
            const manageButton = document.createElement("button");
            manageButton.textContent = "Manage";
            //should have class btn btn-primary manage-btn
            manageButton.className = "btn btn-primary manage-btn";
            manageButton.onclick = () => window.location.href = `/building_management?building_id=${currentBuilding.id}`;
            buildingNameDiv.appendChild(manageButton);



            //show modal with building
            buildingImage.onclick = () => showModal(currentBuilding.thumbnail_filename, currentBuilding.name);

        } else {
            buildingImage.src = "";
            buildingNameDiv.textContent = "None";
        }
        loadEquippedItems(npc);
        loadUnequippedItems();
        updateBuildingsDropdownSelection(npc)
        // Example usage
        populateAvailableBuildingsDropdown(npc.id, npc.location,npc.location_name);
    }


    function makeItemdiv(item, action, npcId,prevId) {
        const div = document.createElement("div");
        div.className = "item";
        div.setAttribute("data-item-id", item.id); // Add data attribute

        // Create a span for the item name
        const nameSpan = document.createElement("span");
        nameSpan.className = "item-name";
        nameSpan.textContent = item.name;
        //add ⭐'s based on item.star_rating
        for (let i = 0; i < item.star_rating; i++) {
            nameSpan.textContent += "⭐"
        }
        div.appendChild(nameSpan);

        // Create the image element
        const img = document.createElement("img");
        img.src = item.thumbnail_filename;
        img.alt = item.name;
        img.className = "item-image";
        img.addEventListener("click", () => showModal(item.filename, item.name)); // Add click event to show modal
        div.appendChild(img);

        // Create the button element
        const button = document.createElement("button");
        button.textContent = action;
        button.addEventListener("click", () => equipItem(item.id, npcId,prevId));
        div.appendChild(button);
        return div
    }

    

    function loadEquippedItems(npc) {
        equippedItems.innerHTML = "";
        user_data.items.forEach(item => {
            if (item.equipped === npc.id) {
                const div = makeItemdiv(item, "Unequip", "None",npc.id)

                equippedItems.appendChild(div);
            }
        });
    }

    function loadUnequippedItems() {
        unequippedItems.innerHTML = "";
        user_data.items.forEach(item => {

            //make sure item.element or item.class matches selectedNPC.element or selectedNPC.class
            if (item.element !== selectedNPC.element && item.class !== selectedNPC.class) {
                return
            }


            if (!item.equipped) {
                const div = makeItemdiv(item, "Equip", selectedNPC.id,"None")

                unequippedItems.appendChild(div);
            }
        });
    }


    function equipItem(itemId, npcId,prevId) {
        fetch('/equip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ item: itemId, npc: npcId }),
        })
            .then(response => response.json())
            .then(() => {
                // Get the unequippedItems and equippedItems containers
                const unequippedItemsContainer = document.getElementById('unequipped-items');
                const equippedItemsContainer = document.getElementById('equipped-items');

                console.log('Unequipped Items Container:', unequippedItemsContainer);
                console.log('Equipped Items Container:', equippedItemsContainer);

                // Find the item in the unequippedItems container using the data attribute
                const itemElement = Array.from(unequippedItemsContainer.children).find(child => child.getAttribute('data-item-id') === itemId);
                console.log('Item Element in Unequipped Items:', itemElement);

                if (itemElement) {
                    // Move from unequippedItems to equippedItems
                    unequippedItemsContainer.removeChild(itemElement);
                    equippedItemsContainer.appendChild(itemElement);
                    console.log(`Moved ${itemId} from unequipped to equipped`);
                } else {
                    // Find the item in the equippedItems container using the data attribute
                    const equippedItemElement = Array.from(equippedItemsContainer.children).find(child => child.getAttribute('data-item-id') === itemId);
                    console.log('Item Element in Equipped Items:', equippedItemElement);

                    if (equippedItemElement) {
                        // Move from equippedItems to unequippedItems
                        equippedItemsContainer.removeChild(equippedItemElement);
                        unequippedItemsContainer.appendChild(equippedItemElement);
                        console.log(`Moved ${itemId} from equipped to unequipped`);
                    } else {
                        console.log(`Item ${itemId} not found in either container`);
                    }
                }
                // Reload NPC data
                loadNPCData();
                //redo the npc details
                //add power level
                fetchPowerLevel(npcId).then((powerLevel) => {
                    //text += ` (Power: <span id=power>${powerLevel}</span>)`;
                    //npcName.textContent = text
                    //set innerHTML to include power level
                    console.log('powerLevel', powerLevel)
                    document.getElementById('power').textContent = powerLevel
                });

                let selectId=npcId
                if(prevId!=="None"){
                    selectId=prevId
                }

                loadNPCDataThenSelect(selectId)
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function moveToBuilding(npcId, buildingId) {
        fetch('/move_to_building', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ npc: npcId, building: buildingId }),
        })
            .then(response => response.json())
            .then(() => loadNPCData());


        if(buildingId){
            // Update the building image
            const building = user_data.buildings.find(b => b.id === buildingId);
            if (building && building.thumbnail_filename) {
                buildingImage.src = building.thumbnail_filename;
            } else {
                buildingImage.src = ''; // Set a default
            }

            //show modal with building
            buildingImage.onclick = () => showModal(building.thumbnail_filename, building.name);


            //update the building name
            buildingNameDiv.textContent = building.name;
            //add ⭐'s based on building.star_rating
            for (let i = 0; i < building.star_rating; i++) {
                buildingNameDiv.textContent += "⭐"
            }
            //add a mange button to the building (which is just a link to /building_management?building_id={building.id})
            const manageButton = document.createElement("button");
            manageButton.textContent = "Manage";
            //should have class btn btn-primary manage-btn
            manageButton.className = "btn btn-primary manage-btn";
            manageButton.onclick = () => window.location.href = `/building_management?building_id=${building.id}`;
            buildingNameDiv.appendChild(manageButton);

        }else{
            buildingImage.src = "";
            buildingNameDiv.textContent = "None";
        }


        
    }



    //check if the url looks like npc=ID
    const urlParams = new URLSearchParams(window.location.search);
    const npcIdFromUrl = urlParams.get('npc');
    if (npcIdFromUrl) {
        loadNPCDataThenSelect(npcIdFromUrl);
    } else {
        loadNPCData();
    }


});
