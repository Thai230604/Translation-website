document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const sourceText = document.getElementById('sourceText');
    const targetText = document.getElementById('targetText');
    const translateBtn = document.getElementById('translateBtn');
    const swapBtn = document.getElementById('swapBtn');
    const clearSourceBtn = document.getElementById('clearSource');
    const copyTargetBtn = document.getElementById('copyTarget');
    const sourceLanguage = document.getElementById('sourceLanguage');
    const targetLanguage = document.getElementById('targetLanguage');
    const statusMessage = document.getElementById('statusMessage');
    const directionRadios = document.querySelectorAll('input[name="direction"]');
    
    // Default direction
    let currentDirection = 'en_to_vi';
    
    // Translation function
    async function translateText() {
        const text = sourceText.value.trim();
        
        if (!text) {
            showStatus('Please enter text to translate', 'warning');
            return;
        }
        
        // Show loading status
        showStatus('Translating...', 'info');
        
        try {
            const response = await fetch('/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    direction: currentDirection
                }),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            targetText.value = data.translation;
            
            // Hide status message after successful translation
            hideStatus();
        } catch (error) {
            console.error('Error:', error);
            showStatus('Translation failed. Please try again.', 'danger');
        }
    }
    
    // Event handlers
    translateBtn.addEventListener('click', translateText);
    
    // Translation on typing with debounce
    let typingTimer;
    const doneTypingInterval = 1000;  // 1 second
    
    sourceText.addEventListener('keyup', function() {
        clearTimeout(typingTimer);
        if (sourceText.value) {
            typingTimer = setTimeout(translateText, doneTypingInterval);
        }
    });
    
    // Handle direction change
    directionRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentDirection = this.value;
            updateLanguageLabels();
            
            // If there's text in the source, translate it with the new direction
            if (sourceText.value.trim()) {
                translateText();
            }
        });
    });
    
    // Swap languages
    swapBtn.addEventListener('click', function() {
        if (currentDirection === 'en_to_vi') {
            document.getElementById('vi_to_en').checked = true;
            currentDirection = 'vi_to_en';
        } else if (currentDirection === 'vi_to_en') {
            document.getElementById('en_to_vi').checked = true;
            currentDirection = 'en_to_vi';
        }
        // Don't swap if auto-detect is selected
        
        // Swap text content
        const temp = sourceText.value;
        sourceText.value = targetText.value;
        targetText.value = temp;
        
        updateLanguageLabels();
        
        // If there's text in the source after swapping, translate it
        if (sourceText.value.trim()) {
            translateText();
        }
    });
    
    // Clear source text
    clearSourceBtn.addEventListener('click', function() {
        sourceText.value = '';
        targetText.value = '';
        hideStatus();
    });
    
    // Copy target text
    copyTargetBtn.addEventListener('click', function() {
        if (targetText.value) {
            navigator.clipboard.writeText(targetText.value)
                .then(() => {
                    showStatus('Copied to clipboard!', 'success');
                    setTimeout(hideStatus, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy text: ', err);
                    showStatus('Failed to copy text', 'danger');
                });
        }
    });
    
    // Update language labels based on direction
    function updateLanguageLabels() {
        if (currentDirection === 'en_to_vi') {
            sourceLanguage.textContent = 'English';
            targetLanguage.textContent = 'Vietnamese';
        } else if (currentDirection === 'vi_to_en') {
            sourceLanguage.textContent = 'Vietnamese';
            targetLanguage.textContent = 'English';
        } else {
            sourceLanguage.textContent = 'Auto Detect';
            targetLanguage.textContent = 'Translation';
        }
    }
    
    // Status message functions
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `alert alert-${type}`;
        statusMessage.classList.remove('d-none');
    }
    
    function hideStatus() {
        statusMessage.classList.add('d-none');
    }
    
    // Initialize language labels
    updateLanguageLabels();
});