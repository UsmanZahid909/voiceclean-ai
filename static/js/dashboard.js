// VoiceClean AI Dashboard - Audio Enhancement Interface (No Auth Version)

class AudioEnhancementDashboard {
    constructor() {
        this.audioFile = null;
        this.originalAudioUrl = null;
        this.enhancedAudioUrl = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const fileInput = document.getElementById('audioFile');
        const processBtn = document.getElementById('processBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const processAnotherBtn = document.getElementById('processAnotherBtn');
        const uploadArea = document.querySelector('[for="audioFile"]');

        // File input change
        fileInput?.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Process button click
        processBtn?.addEventListener('click', () => this.processAudio());
        
        // Download button click
        downloadBtn?.addEventListener('click', () => this.downloadAudio());

        // Process another file button
        processAnotherBtn?.addEventListener('click', () => this.resetInterface());

        // Drag and drop functionality
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('border-purple-300', 'bg-purple-100');
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-purple-300', 'bg-purple-100');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-purple-300', 'bg-purple-100');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    this.handleFileSelect({ target: { files: files } });
                }
            });
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/flac', 'audio/ogg', 'audio/aac', 'audio/mpeg'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|flac|ogg|aac)$/i)) {
            this.showError('Please select a valid audio file (MP3, WAV, M4A, FLAC, OGG, AAC)');
            return;
        }

        // Validate file size (50MB limit)
        const maxSize = 50 * 1024 * 1024; // 50MB in bytes
        if (file.size > maxSize) {
            this.showError('File size must be less than 50MB');
            return;
        }

        this.audioFile = file;
        this.updateUploadArea(file);
        this.enableProcessButton();
    }

    updateUploadArea(file) {
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.innerHTML = `
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-file-audio text-2xl text-green-600"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-900 mb-2">${file.name}</h3>
                <p class="text-gray-500 mb-4">Size: ${this.formatFileSize(file.size)}</p>
                <button type="button" class="bg-gray-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors" onclick="dashboard.resetInterface()">
                    <i class="fas fa-times mr-2"></i>
                    Remove File
                </button>
            `;
        }
    }

    enableProcessButton() {
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.disabled = false;
            processBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    async processAudio() {
        if (!this.audioFile) {
            this.showError('Please select an audio file first');
            return;
        }

        const enhancementType = document.querySelector('input[name="enhancementType"]:checked')?.value || 'both';
        
        // Show progress
        this.showProgress();
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', this.audioFile);
        formData.append('type', enhancementType);

        try {
            // Start progress animation
            this.animateProgress();

            const response = await fetch('/api/enhance', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Enhancement failed');
            }

            // Get the enhanced audio blob
            const blob = await response.blob();
            this.enhancedAudioUrl = URL.createObjectURL(blob);
            
            // Show result
            this.showResult();
            
        } catch (error) {
            console.error('Enhancement error:', error);
            this.showError(error.message || 'An error occurred during audio enhancement');
            this.hideProgress();
        }
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        const processBtn = document.getElementById('processBtn');
        
        if (progressSection) {
            progressSection.classList.remove('hidden');
        }
        
        if (processBtn) {
            processBtn.disabled = true;
            processBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        const processBtn = document.getElementById('processBtn');
        
        if (progressSection) {
            progressSection.classList.add('hidden');
        }
        
        if (processBtn) {
            processBtn.disabled = false;
            processBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    animateProgress() {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            
            if (progressBar) {
                progressBar.style.width = `${progress}%`;
            }
            if (progressText) {
                progressText.textContent = `${Math.round(progress)}%`;
            }
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);

        // Store interval for cleanup
        this.progressInterval = interval;
    }

    showResult() {
        // Complete progress
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) progressBar.style.width = '100%';
        if (progressText) progressText.textContent = '100%';
        
        // Clear progress interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }

        // Show result section after a brief delay
        setTimeout(() => {
            this.hideProgress();
            
            const resultSection = document.getElementById('resultSection');
            const resultAudio = document.getElementById('resultAudio');
            
            if (resultSection) {
                resultSection.classList.remove('hidden');
            }
            
            if (resultAudio && this.enhancedAudioUrl) {
                resultAudio.src = this.enhancedAudioUrl;
            }
        }, 500);
    }

    downloadAudio() {
        if (!this.enhancedAudioUrl) {
            this.showError('No enhanced audio available for download');
            return;
        }

        const link = document.createElement('a');
        link.href = this.enhancedAudioUrl;
        link.download = `enhanced_${this.audioFile.name.replace(/\.[^/.]+$/, '')}.wav`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    resetInterface() {
        // Reset file input
        const fileInput = document.getElementById('audioFile');
        if (fileInput) {
            fileInput.value = '';
        }

        // Reset upload area
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.innerHTML = `
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="fas fa-cloud-upload-alt text-2xl text-purple-600"></i>
                </div>
                <h3 class="text-2xl font-semibold text-gray-900 mb-3">Drop your audio file here</h3>
                <p class="text-gray-500 mb-6">or click to browse and select</p>
                <button type="button" class="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors">
                    Choose Audio File
                </button>
            `;
        }

        // Hide sections
        const progressSection = document.getElementById('progressSection');
        const resultSection = document.getElementById('resultSection');
        
        if (progressSection) progressSection.classList.add('hidden');
        if (resultSection) resultSection.classList.add('hidden');

        // Disable process button
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.disabled = true;
            processBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }

        // Reset enhancement type to default
        const defaultRadio = document.querySelector('input[name="enhancementType"][value="both"]');
        if (defaultRadio) {
            defaultRadio.checked = true;
        }

        // Clear URLs
        if (this.originalAudioUrl) {
            URL.revokeObjectURL(this.originalAudioUrl);
            this.originalAudioUrl = null;
        }
        if (this.enhancedAudioUrl) {
            URL.revokeObjectURL(this.enhancedAudioUrl);
            this.enhancedAudioUrl = null;
        }

        // Reset properties
        this.audioFile = null;
    }

    showError(message) {
        // Create or update error message
        let errorDiv = document.getElementById('errorMessage');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'errorMessage';
            errorDiv.className = 'bg-red-50 border border-red-200 rounded-lg p-4 mb-4';
            
            const mainContent = document.querySelector('main .max-w-4xl');
            if (mainContent) {
                mainContent.insertBefore(errorDiv, mainContent.firstChild);
            }
        }

        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle text-red-500 mr-3"></i>
                <div>
                    <h3 class="text-red-800 font-medium">Error</h3>
                    <p class="text-red-600 text-sm">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-red-400 hover:text-red-600">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (errorDiv && errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new AudioEnhancementDashboard();
});