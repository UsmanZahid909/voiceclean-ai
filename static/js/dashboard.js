// VoiceClean AI Dashboard - Audio Enhancement Interface

class AudioEnhancementDashboard {
    constructor() {
        this.audioFile = null;
        this.originalAudioUrl = null;
        this.enhancedAudioUrl = null;
        this.maxDailyEnhancements = 3;
        this.initializeEventListeners();
        this.loadUsageStats();
    }

    initializeEventListeners() {
        const fileInput = document.getElementById('audioFile');
        const processBtn = document.getElementById('processBtn');
        const downloadBtn = document.getElementById('downloadBtn');
        const removeFileBtn = document.getElementById('removeFile');
        const uploadArea = document.querySelector('[for="audioFile"]');
        const originalBtn = document.getElementById('originalBtn');
        const enhancedBtn = document.getElementById('enhancedBtn');

        // File input change
        fileInput?.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Process button click
        processBtn?.addEventListener('click', () => this.processAudio());
        
        // Download button click
        downloadBtn?.addEventListener('click', () => this.downloadAudio());

        // Remove file button
        removeFileBtn?.addEventListener('click', () => this.removeFile());

        // Comparison buttons
        originalBtn?.addEventListener('click', () => this.showOriginal());
        enhancedBtn?.addEventListener('click', () => this.showEnhanced());

        // Drag and drop functionality
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (!fileInput.disabled) {
                    uploadArea.classList.add('border-purple-300', 'bg-purple-100');
                }
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-purple-300', 'bg-purple-100');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-purple-300', 'bg-purple-100');
                
                if (!fileInput.disabled) {
                    const files = e.dataTransfer.files;
                    if (files.length > 0 && files[0].type.startsWith('audio/')) {
                        fileInput.files = files;
                        this.handleFileSelect({ target: { files: files } });
                    }
                }
            });
        }
    }

    async loadUsageStats() {
        try {
            const response = await fetch('/api/usage');
            if (response.ok) {
                const data = await response.json();
                this.updateUsageDisplay(data);
            }
        } catch (error) {
            console.error('Error loading usage stats:', error);
        }
    }

    updateUsageDisplay(data) {
        // Update progress ring
        const progressCircle = document.querySelector('.progress-ring-circle');
        if (progressCircle) {
            const percentage = (data.daily_count / data.max_daily) * 100;
            const circumference = 2 * Math.PI * 52; // radius = 52
            const offset = circumference - (percentage / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }

        // Update remaining count
        const remainingElement = document.querySelector('.text-2xl.font-bold.text-purple-600');
        if (remainingElement) {
            remainingElement.textContent = data.remaining;
        }

        // Update center text
        const centerText = document.querySelector('.absolute.inset-0 span');
        if (centerText) {
            centerText.textContent = `${data.daily_count}/${data.max_daily}`;
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('audio/')) {
            this.showNotification('Please select a valid audio file.', 'error');
            return;
        }

        // Validate file size (max 50MB)
        const maxSize = 50 * 1024 * 1024; // 50MB
        if (file.size > maxSize) {
            this.showNotification('File size must be less than 50MB.', 'error');
            return;
        }

        this.audioFile = file;
        this.showFileInfo(file);
        this.setupAudioPreview(file);
        document.getElementById('processBtn').disabled = false;
        
        // Track file upload
        this.trackEvent('file_upload', {
            file_type: file.type,
            file_size: file.size
        });
    }

    showFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        
        const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
        
        fileName.textContent = file.name;
        fileSize.textContent = `${sizeInMB} MB • ${file.type.split('/')[1].toUpperCase()}`;
        
        fileInfo.classList.remove('hidden');
    }

    setupAudioPreview(file) {
        const audioUrl = URL.createObjectURL(file);
        this.originalAudioUrl = audioUrl;
    }

    removeFile() {
        this.audioFile = null;
        this.originalAudioUrl = null;
        
        document.getElementById('fileInfo').classList.add('hidden');
        document.getElementById('processBtn').disabled = true;
        document.getElementById('audioFile').value = '';
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Reset upload area
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.innerHTML = `
            <div class="w-20 h-20 bg-gray-200 rounded-xl flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-file-audio text-3xl text-gray-400"></i>
            </div>
            <h3 class="text-2xl font-semibold text-gray-900 mb-3">Drop your audio file here</h3>
            <p class="text-gray-500 mb-6">or click to browse and select</p>
            <button type="button" class="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors">
                Choose Audio File
            </button>
            <p class="text-sm text-gray-400 mt-4">Supports MP3, WAV, M4A, FLAC, OGG, AAC • Max 50MB</p>
        `;
    }

    async processAudio() {
        if (!this.audioFile) {
            this.showNotification('Please select an audio file first.', 'error');
            return;
        }

        const processBtn = document.getElementById('processBtn');
        const processingSection = document.getElementById('processingSection');
        const resultsSection = document.getElementById('resultsSection');

        // Hide previous results
        resultsSection.classList.add('hidden');

        // Show processing
        processingSection.classList.remove('hidden');
        processBtn.disabled = true;
        processBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';

        try {
            // Track processing start
            const enhancementType = document.querySelector('input[name="enhancementType"]:checked').value;
            this.trackEvent('audio_processing_start', { enhancement_type: enhancementType });

            // Simulate progress steps with more realistic timing
            await this.updateProcessingStatus(0, 'Uploading and analyzing audio file...');
            await this.delay(800);

            // Create form data
            const formData = new FormData();
            formData.append('audio', this.audioFile);
            formData.append('type', enhancementType);

            await this.updateProcessingStatus(25, 'Detecting noise patterns and speech...');
            await this.delay(1200);

            await this.updateProcessingStatus(50, 'Applying advanced AI noise reduction...');
            await this.delay(1500);

            await this.updateProcessingStatus(75, 'Enhancing voice clarity and frequencies...');
            await this.delay(1000);

            await this.updateProcessingStatus(90, 'Finalizing professional audio quality...');

            // Make API request
            const response = await fetch('/api/enhance', {
                method: 'POST',
                body: formData
            });

            if (response.status === 429) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Daily limit reached');
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            await this.updateProcessingStatus(100, 'Enhancement complete!');
            await this.delay(500);

            // Get the enhanced audio blob
            const audioBlob = await response.blob();
            this.enhancedAudioUrl = URL.createObjectURL(audioBlob);

            // Show results
            this.showResults();
            
            // Update usage stats
            await this.loadUsageStats();
            
            // Track successful processing
            this.trackEvent('audio_processing_complete', { 
                enhancement_type: enhancementType,
                file_size: this.audioFile.size 
            });

            this.showNotification('Audio enhancement completed successfully!', 'success');

        } catch (error) {
            console.error('Error processing audio:', error);
            
            if (error.message.includes('Daily limit')) {
                this.showNotification(error.message, 'warning');
                // Refresh the page to update UI state
                setTimeout(() => window.location.reload(), 2000);
            } else {
                this.showNotification('Failed to process audio. Please try again.', 'error');
            }
            
            // Track error
            this.trackEvent('audio_processing_error', { error: error.message });
        } finally {
            // Reset UI
            processingSection.classList.add('hidden');
            processBtn.disabled = false;
            processBtn.innerHTML = '<i class="fas fa-magic mr-2"></i>Enhance Audio';
        }
    }

    async updateProcessingStatus(percentage, status) {
        const progressBar = document.getElementById('processingProgress');
        const statusText = document.getElementById('processingStatus');
        
        if (progressBar) progressBar.style.width = `${percentage}%`;
        if (statusText) statusText.textContent = status;
    }

    showResults() {
        const resultsSection = document.getElementById('resultsSection');
        const resultAudio = document.getElementById('resultAudio');
        
        resultAudio.src = this.enhancedAudioUrl;
        resultsSection.classList.remove('hidden');
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    showOriginal() {
        const originalBtn = document.getElementById('originalBtn');
        const enhancedBtn = document.getElementById('enhancedBtn');
        const resultAudio = document.getElementById('resultAudio');
        
        if (this.originalAudioUrl) {
            resultAudio.src = this.originalAudioUrl;
            
            originalBtn.className = 'px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800';
            enhancedBtn.className = 'px-3 py-1 rounded-full text-sm font-medium text-gray-600 hover:bg-gray-100';
        }
    }

    showEnhanced() {
        const originalBtn = document.getElementById('originalBtn');
        const enhancedBtn = document.getElementById('enhancedBtn');
        const resultAudio = document.getElementById('resultAudio');
        
        if (this.enhancedAudioUrl) {
            resultAudio.src = this.enhancedAudioUrl;
            
            enhancedBtn.className = 'px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800';
            originalBtn.className = 'px-3 py-1 rounded-full text-sm font-medium text-gray-600 hover:bg-gray-100';
        }
    }

    downloadAudio() {
        if (!this.enhancedAudioUrl) return;
        
        const a = document.createElement('a');
        a.href = this.enhancedAudioUrl;
        a.download = `enhanced_${this.audioFile.name.replace(/\.[^/.]+$/, '')}.wav`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Track download
        this.trackEvent('audio_download', {
            original_filename: this.audioFile.name
        });

        this.showNotification('Download started successfully!', 'success');
    }

    showNotification(message, type = 'info') {
        const colors = {
            error: 'bg-red-500',
            success: 'bg-green-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };

        const icons = {
            error: 'fas fa-exclamation-triangle',
            success: 'fas fa-check-circle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };

        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300 max-w-md`;
        notification.innerHTML = `
            <div class="flex items-start">
                <i class="${icons[type]} mr-3 mt-0.5"></i>
                <div class="flex-1">
                    <span>${message}</span>
                </div>
                <button class="ml-4 text-white hover:text-gray-200 flex-shrink-0" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full');
        }, 100);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('translate-x-full');
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    trackEvent(eventName, parameters = {}) {
        // Google Analytics 4 event tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, parameters);
        }
        
        // Console log for development
        console.log('Event tracked:', eventName, parameters);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', () => {
    new AudioEnhancementDashboard();
});

// Google Analytics (replace with your tracking ID)
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'GA_TRACKING_ID');