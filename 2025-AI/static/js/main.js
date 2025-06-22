// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const inventoryDiv = document.getElementById('inventory');
    const generateBtn = document.getElementById('generate-btn');
    const cityInput = document.getElementById('city-input');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsSection = document.getElementById('results-section');
    const weatherInfoDiv = document.getElementById('weather-info');
    const outfitResultsDiv = document.getElementById('outfit-results');

    // --- Load initial inventory on page load ---
    loadInventory();

    // --- Drag and Drop Logic ---
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length) {
            handleFiles(files);
        }
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });

    // --- File Handling and Uploading ---
    async function handleFiles(files) {
        const formData = new FormData();
        for (const file of files) {
            // Basic client-side check for image types
            if (file.type.startsWith('image/')) {
                formData.append('files', file);
            }
        }
        
        if (formData.getAll('files').length === 0) {
            uploadStatus.textContent = "Please select image files only.";
            return;
        }

        uploadStatus.textContent = `Uploading ${formData.getAll('files').length} item(s)...`;
        loadingSpinner.style.display = 'block';

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Upload failed');
            }

            uploadStatus.textContent = result.message;
            result.items.forEach(addItemToInventory);
        } catch (error) {
            uploadStatus.textContent = `Error: ${error.message}`;
        } finally {
            loadingSpinner.style.display = 'none';
        }
    }

    // --- Inventory Display ---
    function addItemToInventory(item) {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'inventory-item';
        // Corrected to use the /uploads/ route and item.filename
        itemDiv.innerHTML = `
            <img src="/uploads/${item.filename}" alt="${item.category} item">
            <div class="category-tag">${item.category}</div>
        `;
        inventoryDiv.appendChild(itemDiv);
    }

    async function loadInventory() {
        try {
            const response = await fetch('/get_inventory');
            const items = await response.json();
            inventoryDiv.innerHTML = '';
            items.forEach(addItemToInventory);
        } catch (error) {
            console.error('Failed to load inventory:', error);
        }
    }

    // --- Outfit Generation ---
    generateBtn.addEventListener('click', async () => {
        const city = cityInput.value.trim();
        if (!city) {
            alert('Please enter a city.');
            return;
        }

        loadingSpinner.style.display = 'block';
        resultsSection.classList.add('hidden');
        outfitResultsDiv.innerHTML = '';
        weatherInfoDiv.innerHTML = '';

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city: city })
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to generate outfits.');
            }
            
            displayResults(result);

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            loadingSpinner.style.display = 'none';
        }
    });

    // --- Display Results ---
    function displayResults(data) {
        resultsSection.classList.remove('hidden');

        // Display weather
        const weather = data.weather;
        weatherInfoDiv.innerHTML = `
            <strong>${weather.city}:</strong> ${weather.temp}°C, ${weather.description}
        `;

        // Display outfits
        outfitResultsDiv.innerHTML = ''; // Clear previous results
        data.outfits.forEach(outfit => {
            const outfitCard = document.createElement('div');
            outfitCard.className = 'outfit-card';

            let imagesHTML = '';
            ['top', 'bottom', 'outerwear', 'shoes'].forEach(category => {
                if (outfit[category]) {
                    // Corrected to use the /uploads/ route and item.filename
                    imagesHTML += `
                        <div class="outfit-piece">
                            <img src="/uploads/${outfit[category].filename}" alt="${category}">
                            <div class="category-tag">${outfit[category].category}</div>
                        </div>
                    `;
                }
            });

            outfitCard.innerHTML = `
                <h3>${outfit.label}</h3>
                <div class="outfit-images">
                    ${imagesHTML}
                </div>
            `;
            outfitResultsDiv.appendChild(outfitCard);
        });
         if (data.outfits.length === 0) {
            outfitResultsDiv.innerHTML = "<p>Couldn't generate outfits. Try uploading more items (especially tops, bottoms, and shoes)!</p>"
        }
    }
});