// API Configuration
const API_BASE_URL = 'http://localhost:8000';
const POLL_INTERVAL = 10000; // 10 seconds

const MODELS = {
    RUNWAY: 'runway_act_two',
    PIPELINE: 'seedream_runway'
};

// Presets Configuration
const PRESETS = {
    tiktok: {
        name: 'TikTok',
        icon: '🎵',
        ratio: '720:1280',  // 9:16 portrait
        expression_intensity: 5,  // High energy
        body_control: true,
        description: 'Вертикальное видео, высокая энергия'
    },
    instagram: {
        name: 'Instagram',
        icon: '📸',
        ratio: '960:960',  // 1:1 square
        expression_intensity: 4,
        body_control: true,
        description: 'Квадратный формат, живо'
    },
    youtube: {
        name: 'YouTube',
        icon: '▶️',
        ratio: '1280:720',  // 16:9 landscape
        expression_intensity: 3,
        body_control: true,
        description: 'Широкоформатное, естественно'
    },
    professional: {
        name: 'Professional',
        icon: '💼',
        ratio: '1280:720',  // 16:9
        expression_intensity: 2,  // Subtle
        body_control: false,
        description: 'Деловой, сдержанные движения'
    }
};

// State
let currentMode = 'url'; // fixed to url mode
let characterFile = null;
let referenceFile = null;
let uploadId = null;
let taskId = null;
let pollingTimer = null;
let pollingErrorCount = 0;
let selectedModel = MODELS.RUNWAY;
let frameUrl = null;           // uploaded frame URL for pipeline
let intermediateUrl = null;    // result after Seedream Edit
let currentCharacterUrl = null;
let currentReferenceUrl = null;

// DOM Elements
const modeFileBtn = document.getElementById('mode-file');
const modeUrlBtn = document.getElementById('mode-url');
const fileMode = document.getElementById('file-mode');
const urlMode = document.getElementById('url-mode');
const modelSection = document.getElementById('model-section');
const modelRadios = document.querySelectorAll('input[name="model"]');

const characterInput = document.getElementById('character-input');
const referenceInput = document.getElementById('reference-input');
const characterPreview = document.getElementById('character-preview');
const referencePreview = document.getElementById('reference-preview');

const characterUrlInput = document.getElementById('character-url-input');
const referenceUrlInput = document.getElementById('reference-url-input');
const intensitySlider = document.getElementById('intensity-slider');
const intensityValue = document.getElementById('intensity-value');
const generateBtn = document.getElementById('generate-btn');
const againBtn = document.getElementById('again-btn');
const retryBtn = document.getElementById('retry-btn');
const downloadBtn = document.getElementById('download-btn');

const uploadSection = document.getElementById('upload-section');
const presetsSection = document.getElementById('presets-section');
const settingsSection = document.getElementById('settings-section');
const statusSection = document.getElementById('status-section');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');
const pipelineProgress = document.getElementById('pipeline-progress');
const stepFrame = document.getElementById('step-frame');
const stepNano = document.getElementById('step-nano-banana');
const stepVeo = document.getElementById('step-veo3');
const stepFrameIndicator = document.getElementById('step-frame-indicator');
const stepNanoIndicator = document.getElementById('step-nano-indicator');
const stepVeoIndicator = document.getElementById('step-veo-indicator');
const stepFrameStatus = document.getElementById('step-frame-status');
const stepNanoStatus = document.getElementById('step-nano-status');
const stepVeoStatus = document.getElementById('step-veo-status');
const intermediatePreview = document.getElementById('intermediate-preview');
const intermediateImage = document.getElementById('intermediate-image');

// Gallery DOM elements
const galleryBtn = document.getElementById('gallery-btn');
const galleryCount = document.getElementById('gallery-count');
const galleryModal = document.getElementById('gallery-modal');
const galleryOverlay = document.getElementById('gallery-overlay');
const galleryClose = document.getElementById('gallery-close');
const galleryGrid = document.getElementById('gallery-grid');
const galleryEmpty = document.getElementById('gallery-empty');
const galleryDetailModal = document.getElementById('gallery-detail-modal');
const detailOverlay = document.getElementById('detail-overlay');
const detailClose = document.getElementById('detail-close');
const detailBody = document.getElementById('detail-body');

// Comparison DOM elements
const comparisonContainer = document.getElementById('comparison-container');
const singleViewContainer = document.getElementById('single-view-container');
const referenceComparisonVideo = document.getElementById('reference-comparison-video');
const resultComparisonVideo = document.getElementById('result-comparison-video');
const comparisonSlider = document.getElementById('comparison-slider');
const playComparisonBtn = document.getElementById('play-comparison');
const toggleViewBtn = document.getElementById('toggle-view');
const toggleComparisonBtn = document.getElementById('toggle-comparison');

// Comparison state
let currentView = 'comparison'; // 'comparison' or 'single'
let isComparisonPlaying = false;
let currentResultUrl = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    // safety: make sure modals are closed on first load
    closeGallery();
    closeDetailModal();
    // force URL mode visible, hide file mode
    switchMode('url');
});

function setupEventListeners() {
    // Mode toggle removed (URL only)

    // Model selection
    modelRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            selectedModel = e.target.value;
        });
    });

    // File inputs
    characterInput.addEventListener('change', (e) => handleFileSelect(e, 'character'));
    referenceInput.addEventListener('change', (e) => handleFileSelect(e, 'reference'));

    // URL inputs
    characterUrlInput.addEventListener('input', checkUrlInputs);
    referenceUrlInput.addEventListener('input', checkUrlInputs);

    // Intensity slider
    intensitySlider.addEventListener('input', (e) => {
        intensityValue.textContent = e.target.value;
    });

    // Buttons
    generateBtn.addEventListener('click', handleGenerate);
    againBtn.addEventListener('click', resetAll);
    retryBtn.addEventListener('click', resetAll);

    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const presetKey = e.currentTarget.dataset.preset;
            applyPreset(presetKey);
        });
    });

    // Gallery
    galleryBtn.addEventListener('click', openGallery);
    galleryClose.addEventListener('click', closeGallery);
    galleryOverlay.addEventListener('click', closeGallery);
    detailClose.addEventListener('click', closeDetailModal);
    detailOverlay.addEventListener('click', closeDetailModal);

    // Ensure modals are closed on load
    galleryModal.classList.add('hidden');
    galleryDetailModal.classList.add('hidden');

    // Comparison
    toggleViewBtn.addEventListener('click', () => toggleView('single'));
    toggleComparisonBtn.addEventListener('click', () => toggleView('comparison'));
    playComparisonBtn.addEventListener('click', toggleComparisonPlayback);

    // Load gallery count on startup
    updateGalleryCount();
}

// Mode Switching
function switchMode(mode) {
    currentMode = mode;

    // Only URL mode is allowed
    urlMode.classList.remove('hidden');
    fileMode.classList.add('hidden');
}

function checkUrlInputs() {
    // Sections always visible; validation happens on generate
}

// File Selection
function handleFileSelect(event, type) {
    const file = event.target.files[0];
    if (!file) return;

    if (type === 'character') {
        characterFile = file;
        showPreview(file, characterPreview, 'image');
    } else {
        referenceFile = file;
        showPreview(file, referencePreview, 'video');
    }

    // Show presets and settings sections when both files are selected
    if (characterFile && referenceFile) {
        presetsSection.classList.remove('hidden');
        settingsSection.classList.remove('hidden');
        presetsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function showPreview(file, container, type) {
    container.innerHTML = '';
    container.classList.remove('hidden');

    const url = URL.createObjectURL(file);

    if (type === 'image') {
        const img = document.createElement('img');
        img.src = url;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '8px';
        container.appendChild(img);
    } else {
        const video = document.createElement('video');
        video.src = url;
        video.controls = true;
        video.style.maxWidth = '100%';
        video.style.borderRadius = '8px';
        container.appendChild(video);
    }

    const fileName = document.createElement('p');
    fileName.textContent = file.name;
    fileName.style.marginTop = '8px';
    fileName.style.fontSize = '14px';
    fileName.style.color = '#666';
    container.appendChild(fileName);
}

// Generate Video
async function handleGenerate() {
    console.log('handleGenerate: click');
    showToast('Запускаю генерацию...');
    try {
        generateBtn.disabled = true;
        pipelineProgress.classList.add('hidden');
        intermediatePreview.classList.add('hidden');
        frameUrl = null;
        intermediateUrl = null;

        const settings = {
            ratio: document.getElementById('ratio-select').value,
            expression_intensity: parseInt(intensitySlider.value),
            body_control: document.getElementById('body-control').checked,
            model: selectedModel
        };

        let requestBody;
        let referencePlayableUrl = null;

        // URL mode only
        const charUrl = characterUrlInput.value.trim();
        const refUrl = referenceUrlInput.value.trim();

        if (!charUrl || !refUrl) {
            showError('Пожалуйста, заполните оба URL');
            generateBtn.disabled = false;
            return;
        }

        // Basic URL validation
        try {
            new URL(charUrl);
            new URL(refUrl);
        } catch (e) {
            showError('Пожалуйста, введите корректные URL');
            generateBtn.disabled = false;
            return;
        }

        if (!isLikelyImageUrl(charUrl)) {
            showError('Character Image URL должен быть ссылкой на картинку (jpg/png/webp)');
            generateBtn.disabled = false;
            return;
        }
        if (!isLikelyVideoUrl(refUrl)) {
            showError('Reference Video URL должен быть ссылкой на видео (mp4/mov)');
            generateBtn.disabled = false;
            return;
        }

        if (selectedModel === MODELS.PIPELINE) {
            updatePipelineProgress('FRAME_EXTRACTION');
            generateBtn.textContent = 'Извлекаем кадр...';
            referencePlayableUrl = refUrl;
            const frameBlob = await extractVideoFrame(refUrl);
            generateBtn.textContent = 'Подготовка кадра...';
            frameUrl = await blobToBase64(frameBlob);
            updatePipelineProgress('FRAME_UPLOADED');
        } else {
            pipelineProgress.classList.add('hidden');
        }

        requestBody = {
            direct_urls: {
                character_url: charUrl,
                reference_url: refUrl
            },
            settings: settings
        };

        currentCharacterUrl = charUrl;
        currentReferenceUrl = refUrl;

        // Add frame_url for pipeline model
        if (selectedModel === MODELS.PIPELINE) {
            if (!frameUrl) {
                throw new Error('Не удалось получить кадр из видео для pipeline модели');
            }
            requestBody.frame_url = frameUrl;
        }

        // Step 2: Start generation
        generateBtn.textContent = 'Создание задачи...';

        const generateResponse = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!generateResponse.ok) {
            const error = await generateResponse.json();
            throw new Error(error.error || 'Generation failed');
        }

        const generateData = await generateResponse.json();
        taskId = generateData.task_id;

        // Step 3: Show status section and start polling
        showSection('status');
        if (selectedModel !== MODELS.PIPELINE) {
            pipelineProgress.classList.add('hidden');
        }
        startPolling();

    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        generateBtn.disabled = false;
        generateBtn.textContent = '🚀 Сгенерировать видео';
    }
}

// Polling
function startPolling() {
    pollingErrorCount = 0;
    if (selectedModel === MODELS.PIPELINE) {
        pipelineProgress.classList.remove('hidden');
        updatePipelineProgress('IMAGE_EDIT_STARTED');
        updateStatus('Seedream Edit: запуск', 30);
    } else {
        updateStatus('Uploaded', 25);
        pipelineProgress.classList.add('hidden');
    }
    pollingTimer = setInterval(checkStatus, POLL_INTERVAL);
    checkStatus(); // Check immediately
}

function stopPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
        pollingTimer = null;
    }
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status/${taskId}`);

        if (!response.ok) {
            let errorMessage = 'Status check failed';
            try {
                const error = await response.json();
                errorMessage = error.error || error.detail || errorMessage;
            } catch (parseError) {
                // ignore JSON parse errors
            }
            if (response.status >= 500) {
                handleTransientPollError(errorMessage);
                return;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        pollingErrorCount = 0;
        const status = data.status;
        const modelUsed = data.model_used || selectedModel;

        if (modelUsed === MODELS.PIPELINE) {
            const stage = data.pipeline_stage || 'IMAGE_EDIT_STARTED';
            updatePipelineProgress(stage, data);

            // Map pipeline stages to progress bar
            const pipelineProgressMap = {
                'FRAME_EXTRACTION': 15,
                'FRAME_UPLOADED': 25,
                'IMAGE_EDIT_STARTED': 40,
                'IMAGE_EDIT_COMPLETED': 60,
                'VIDEO_STARTED': 80,
                'PIPELINE_COMPLETED': 100,
                'FAILED': 0
            };
            updateStatus(stage, pipelineProgressMap[stage] || 40);

            if (data.intermediate_url) {
                intermediateUrl = data.intermediate_url;
                intermediateImage.src = intermediateUrl;
                intermediatePreview.classList.remove('hidden');
            }

            if (status === 'COMPLETED') {
                stopPolling();
                const videoUrl = data.result_urls[0];
                showResult(videoUrl, modelUsed, intermediateUrl);
                saveToGallery(videoUrl, modelUsed, intermediateUrl);
            } else if (status === 'FAILED') {
                stopPolling();
                showError('Pipeline завершился с ошибкой. Попробуйте снова.');
            }
        } else {
            const progressStage = data.progress_stage;
            const progressMap = {
                'Uploaded': 25,
                'In Progress': 40,
                'Processing': 50,
                'Finalizing': 75,
                'Ready': 100,
                'COMPLETED': 100,
                'Failed': 0
            };

            pipelineProgress.classList.add('hidden');
            updateStatus(progressStage, progressMap[progressStage] || 50);

            if (status === 'READY' || status === 'COMPLETED') {
                stopPolling();
                const videoUrl = data.result_urls[0];
                showResult(videoUrl, modelUsed);
                saveToGallery(videoUrl, modelUsed);
            } else if (status === 'FAILED') {
                stopPolling();
                showError('Генерация не удалась. Попробуйте с другими настройками или файлами.');
            }
        }

    } catch (error) {
        console.error('Polling error:', error);
        handleTransientPollError(error.message);
    }
}

function handleTransientPollError(message) {
    pollingErrorCount += 1;
    updateStatus(`Временная ошибка: ${message}. Повторяем...`, 50);
    if (pollingErrorCount >= 5) {
        stopPolling();
        showError(message);
    }
}

function updateStatus(text, progress) {
    document.getElementById('status-text').textContent = text;
    document.getElementById('progress-fill').style.width = `${progress}%`;
}

// Pipeline progress UI
function updatePipelineProgress(stage, data = {}) {
    pipelineProgress.classList.remove('hidden');

    // reset classes
    [stepFrame, stepNano, stepVeo].forEach(step => {
        step.classList.remove('active', 'complete');
    });

    switch (stage) {
        case 'FRAME_EXTRACTION':
            stepFrame.classList.add('active');
            stepFrameIndicator.textContent = '⏳';
            stepFrameStatus.textContent = 'Извлечение кадра...';
            stepNanoIndicator.textContent = '⏸️';
            stepNanoStatus.textContent = 'Ожидание...';
            stepVeoIndicator.textContent = '⏸️';
            stepVeoStatus.textContent = 'Ожидание...';
            break;
        case 'FRAME_UPLOADED':
        case 'IMAGE_EDIT_STARTED':
            stepFrame.classList.add('complete');
            stepFrameIndicator.textContent = '✅';
            stepFrameStatus.textContent = 'Кадр готов';
            stepNano.classList.add('active');
            stepNanoIndicator.textContent = '⏳';
            stepNanoStatus.textContent = 'Редактирование кадра...';
            stepVeoIndicator.textContent = '⏸️';
            stepVeoStatus.textContent = 'Ожидание...';
            break;
        case 'IMAGE_EDIT_COMPLETED':
        case 'VIDEO_STARTED':
            stepFrame.classList.add('complete');
            stepFrameIndicator.textContent = '✅';
            stepNano.classList.add('complete');
            stepNanoIndicator.textContent = '✅';
            stepNanoStatus.textContent = 'Кадр готов';
            stepVeo.classList.add('active');
            stepVeoIndicator.textContent = '⏳';
            stepVeoStatus.textContent = 'Генерация видео...';
            if (data.intermediate_url) {
                intermediateUrl = data.intermediate_url;
                intermediateImage.src = intermediateUrl;
                intermediatePreview.classList.remove('hidden');
            }
            break;
        case 'PIPELINE_COMPLETED':
            stepFrame.classList.add('complete');
            stepNano.classList.add('complete');
            stepVeo.classList.add('complete');
            stepFrameIndicator.textContent = '✅';
            stepNanoIndicator.textContent = '✅';
            stepVeoIndicator.textContent = '✅';
            stepFrameStatus.textContent = 'Готово';
            stepNanoStatus.textContent = 'Готово';
            stepVeoStatus.textContent = 'Видео готово';
            break;
        case 'FAILED':
            stepNanoStatus.textContent = 'Ошибка';
            stepVeoStatus.textContent = 'Ошибка';
            stepNanoIndicator.textContent = '⚠️';
            stepVeoIndicator.textContent = '⚠️';
            break;
    }
}

async function extractVideoFrame(videoSrc) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.crossOrigin = 'anonymous';
        video.src = videoSrc;
        video.muted = true;
        video.playsInline = true;

        const cleanup = () => {
            video.pause();
            video.removeAttribute('src');
            video.load();
        };

        video.addEventListener('loadeddata', () => {
            // Seek a bit into the video to avoid black frames
            const targetTime = Math.min(0.2, video.duration ? Math.min(0.2, video.duration / 4) : 0.2);
            video.currentTime = targetTime;
        }, { once: true });

        video.addEventListener('seeked', () => {
            try {
                const canvas = document.createElement('canvas');
                const maxWidth = 768;
                const srcWidth = video.videoWidth || 1280;
                const srcHeight = video.videoHeight || 720;
                const scale = Math.min(1, maxWidth / srcWidth);
                canvas.width = Math.round(srcWidth * scale);
                canvas.height = Math.round(srcHeight * scale);
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.toBlob((blob) => {
                    if (!blob) {
                        cleanup();
                        reject(new Error('Не удалось получить кадр из видео'));
                        return;
                    }
                    cleanup();
                    resolve(blob);
                }, 'image/jpeg', 0.9);
            } catch (err) {
                cleanup();
                reject(err);
            }
        }, { once: true });

        video.addEventListener('error', () => {
            cleanup();
            reject(new Error('Не удалось загрузить видео для извлечения кадра (возможно, CORS)'));
        }, { once: true });
    });
}

async function uploadFrameToCloudinary(frameBlob) {
    const formData = new FormData();
    formData.append('file', frameBlob, 'frame.jpg');

    const res = await fetch(`${API_BASE_URL}/api/upload-frame`, {
        method: 'POST',
        body: formData
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Не удалось загрузить кадр на сервер');
    }

    const data = await res.json();
    return data.frame_url;
}

async function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const result = reader.result;
            if (!result || typeof result !== 'string') {
                reject(new Error('Не удалось подготовить кадр'));
                return;
            }
            const base64 = result.split(',')[1] || result;
            resolve(base64);
        };
        reader.onerror = () => reject(new Error('Не удалось подготовить кадр'));
        reader.readAsDataURL(blob);
    });
}

function isLikelyImageUrl(url) {
    const lower = url.toLowerCase().split('?')[0];
    return ['.jpg', '.jpeg', '.png', '.webp'].some(ext => lower.endsWith(ext));
}

function isLikelyVideoUrl(url) {
    const lower = url.toLowerCase().split('?')[0];
    return ['.mp4', '.mov', '.avi', '.webm'].some(ext => lower.endsWith(ext));
}

// Show Result
function showResult(videoUrl, modelUsed = MODELS.RUNWAY, intermediate = null) {
    // Store URLs for comparison
    currentResultUrl = videoUrl;

    // Setup single view
    const resultVideo = document.getElementById('result-video');
    resultVideo.src = videoUrl;

    // Setup comparison view
    referenceComparisonVideo.src = currentReferenceUrl || '';
    resultComparisonVideo.src = videoUrl;

    // Initialize comparison slider
    initComparisonSlider();
    syncVideos();

    // Setup download
    downloadBtn.href = videoUrl;
    downloadBtn.download = 'character-replacement-result.mp4';

    if (modelUsed === MODELS.PIPELINE && intermediate) {
        intermediateUrl = intermediate;
        intermediateImage.src = intermediate;
        intermediatePreview.classList.remove('hidden');
    }

    // Show comparison view by default
    toggleView('comparison');

    showSection('result');
}

// Show Error
function showError(message) {
    document.getElementById('error-text').textContent = message;
    showSection('error');
}

// UI Helpers
function showSection(sectionName) {
    // Hide all sections
    [uploadSection, modelSection, presetsSection, settingsSection, statusSection, resultSection, errorSection].forEach(section => {
        section.classList.add('hidden');
    });

    // Show requested section
    const sectionMap = {
        'upload': uploadSection,
        'model': modelSection,
        'settings': settingsSection,
        'status': statusSection,
        'result': resultSection,
        'error': errorSection
    };

    const section = sectionMap[sectionName];
    if (section) {
        section.classList.remove('hidden');
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function resetAll() {
    // Stop polling
    stopPolling();

    // Reset state
    characterFile = null;
    referenceFile = null;
    uploadId = null;
    taskId = null;
    frameUrl = null;
    intermediateUrl = null;
    selectedModel = MODELS.RUNWAY;
    currentCharacterUrl = null;
    currentReferenceUrl = null;

    // Reset URL inputs
    characterUrlInput.value = '';
    referenceUrlInput.value = '';

    // Reset settings
    intensitySlider.value = 3;
    intensityValue.textContent = '3';
    document.getElementById('ratio-select').value = '1280:720';
    document.getElementById('body-control').checked = true;
    modelRadios.forEach(r => r.checked = r.value === MODELS.RUNWAY);

    generateBtn.disabled = false;
    generateBtn.textContent = '🚀 Сгенерировать видео';

    // Force URL mode
    switchMode('url');

    // Show upload section
    showSection('upload');
    uploadSection.scrollIntoView({ behavior: 'smooth' });

    // Clear preset selection
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    pipelineProgress.classList.add('hidden');
    intermediatePreview.classList.add('hidden');
}

// Preset Application
function applyPreset(presetKey) {
    const preset = PRESETS[presetKey];
    if (!preset) return;

    // Update form values
    document.getElementById('ratio-select').value = preset.ratio;
    document.getElementById('intensity-slider').value = preset.expression_intensity;
    document.getElementById('intensity-value').textContent = preset.expression_intensity;
    document.getElementById('body-control').checked = preset.body_control;

    // Visual feedback - highlight selected preset
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.preset-btn').classList.add('active');

    // Show notification
    showToast(`✓ ${preset.name} пресет применен`);

    console.log(`Preset applied: ${preset.name}`, preset);
}

// Toast Notification
function showToast(message) {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create new toast
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    // Show toast
    setTimeout(() => toast.classList.add('show'), 10);

    // Hide and remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ================== GALLERY FUNCTIONS ==================

// Save to Gallery
async function saveToGallery(videoUrl, modelUsed = MODELS.RUNWAY, intermediate = null) {
    try {
        const generations = JSON.parse(localStorage.getItem('generations') || '[]');

        // Generate thumbnail from video
        const thumbnail = await generateThumbnail(videoUrl);

        // Get current settings
        const settings = {
            model: modelUsed,
            ratio: document.getElementById('ratio-select').value,
            expression_intensity: parseInt(document.getElementById('intensity-slider').value),
            body_control: document.getElementById('body-control').checked
        };

        // Get character and reference URLs
        let characterUrl = '';
        let referenceUrl = '';

        if (currentMode === 'file') {
            // Get from uploads if available
            characterUrl = currentCharacterUrl || (uploadId ? `Character from upload ${uploadId}` : '');
            referenceUrl = currentReferenceUrl || (uploadId ? `Reference from upload ${uploadId}` : '');
        } else {
            characterUrl = characterUrlInput.value;
            referenceUrl = referenceUrlInput.value;
        }

        // Create generation entry
        const generation = {
            id: crypto.randomUUID(),
            timestamp: new Date().toISOString(),
            character_url: characterUrl,
            reference_url: referenceUrl,
            result_url: videoUrl,
            intermediate_url: intermediate,
            settings: settings,
            thumbnail: thumbnail
        };

        // Add to beginning of array
        generations.unshift(generation);

        // Keep only last 20
        if (generations.length > 20) {
            generations.length = 20;
        }

        // Save to localStorage
        localStorage.setItem('generations', JSON.stringify(generations));

        // Update count
        updateGalleryCount();

        console.log('Saved to gallery:', generation.id);
    } catch (error) {
        console.error('Failed to save to gallery:', error);
    }
}

// Generate Thumbnail from Video
async function generateThumbnail(videoUrl) {
    return new Promise((resolve) => {
        const video = document.createElement('video');
        video.src = videoUrl;
        video.crossOrigin = 'anonymous';
        video.muted = true;

        video.addEventListener('loadeddata', () => {
            video.currentTime = 0.5; // 0.5 sec into video
        });

        video.addEventListener('seeked', () => {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = 320;
                canvas.height = 180;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, 320, 180);
                const thumbnail = canvas.toDataURL('image/jpeg', 0.7);
                resolve(thumbnail);
            } catch (error) {
                console.error('Thumbnail generation failed:', error);
                // Return placeholder on error
                resolve('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ddd" width="320" height="180"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EVideo%3C/text%3E%3C/svg%3E');
            }
        });

        video.addEventListener('error', () => {
            console.error('Video load failed for thumbnail');
            // Return placeholder on error
            resolve('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%23ddd" width="320" height="180"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999"%3EVideo%3C/text%3E%3C/svg%3E');
        });
    });
}

// Update Gallery Count
function updateGalleryCount() {
    const generations = JSON.parse(localStorage.getItem('generations') || '[]');
    galleryCount.textContent = `(${generations.length})`;
}

// Open Gallery
function openGallery() {
    const generations = JSON.parse(localStorage.getItem('generations') || '[]');

    if (generations.length === 0) {
        galleryEmpty.classList.remove('hidden');
        galleryGrid.classList.add('hidden');
    } else {
        galleryEmpty.classList.add('hidden');
        galleryGrid.classList.remove('hidden');
        renderGallery(generations);
    }

    galleryModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden'; // Prevent background scroll
}

// Close Gallery
function closeGallery() {
    galleryModal.classList.add('hidden');
    document.body.style.overflow = '';
}

// Render Gallery Grid
function renderGallery(generations) {
    galleryGrid.innerHTML = generations.map(gen => `
        <div class="gallery-item" data-id="${gen.id}">
            <img src="${gen.thumbnail}" alt="Video thumbnail" class="gallery-thumbnail">
                <div class="gallery-item-info">
                    <div class="gallery-item-date">${formatDate(gen.timestamp)}</div>
                    <div class="gallery-item-settings">
                    ${gen.settings.model || 'runway_act_two'} • ${gen.settings.ratio} • ${gen.settings.expression_intensity}/5
                    </div>
                </div>
            <div class="gallery-item-actions">
                <button class="gallery-view-btn" data-id="${gen.id}" title="View">👁️</button>
                <button class="gallery-delete-btn" data-id="${gen.id}" title="Delete">🗑️</button>
            </div>
        </div>
    `).join('');

    // Add event listeners
    document.querySelectorAll('.gallery-view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.currentTarget.dataset.id;
            showGalleryItem(id);
        });
    });

    document.querySelectorAll('.gallery-delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const id = e.currentTarget.dataset.id;
            deleteFromGallery(id);
        });
    });

    // Also make whole item clickable
    document.querySelectorAll('.gallery-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (!e.target.closest('.gallery-item-actions')) {
                const id = item.dataset.id;
                showGalleryItem(id);
            }
        });
    });
}

// Show Gallery Item Detail
function showGalleryItem(id) {
    const generations = JSON.parse(localStorage.getItem('generations') || '[]');
    const item = generations.find(g => g.id === id);

    if (!item) return;

    detailBody.innerHTML = `
        <div class="detail-video">
            <video src="${item.result_url}" controls loop class="detail-video-player"></video>
        </div>
        <div class="detail-info">
            <div class="detail-row">
                <strong>Created:</strong> ${formatDate(item.timestamp)}
            </div>
            <div class="detail-row">
                <strong>Model:</strong> ${item.settings.model || 'runway_act_two'}
            </div>
            <div class="detail-row">
                <strong>Aspect Ratio:</strong> ${item.settings.ratio}
            </div>
            <div class="detail-row">
                <strong>Expression Intensity:</strong> ${item.settings.expression_intensity}/5
            </div>
            <div class="detail-row">
                <strong>Body Control:</strong> ${item.settings.body_control ? 'Yes' : 'No'}
            </div>
            ${item.intermediate_url ? `<div class="detail-row"><strong>Intermediate:</strong> <a href="${item.intermediate_url}" target="_blank">Open image</a></div>` : ''}
        </div>
        <div class="detail-actions">
            <a href="${item.result_url}" download="video-${id}.mp4" class="btn btn-primary">
                💾 Download Video
            </a>
            <button class="btn btn-secondary" onclick="deleteFromGallery('${id}'); closeDetailModal(); openGallery();">
                🗑️ Delete
            </button>
        </div>
    `;

    galleryDetailModal.classList.remove('hidden');
}

// Close Detail Modal
function closeDetailModal() {
    galleryDetailModal.classList.add('hidden');
}

// Delete from Gallery
function deleteFromGallery(id) {
    if (!confirm('Удалить это видео из галереи?')) return;

    let generations = JSON.parse(localStorage.getItem('generations') || '[]');
    generations = generations.filter(g => g.id !== id);
    localStorage.setItem('generations', JSON.stringify(generations));

    updateGalleryCount();
    showToast('✓ Видео удалено из галереи');

    // Refresh gallery if open
    if (!galleryModal.classList.contains('hidden')) {
        openGallery();
    }
}

// Format Date
function formatDate(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;

    return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
}

// ==================== COMPARISON VIEW FUNCTIONS ====================

// Initialize comparison slider
function initComparisonSlider() {
    const wrapper = document.querySelector('.comparison-wrapper');
    const leftSide = document.querySelector('.video-side-left');
    let isDragging = false;

    // Mouse events
    comparisonSlider.addEventListener('mousedown', startDrag);
    document.addEventListener('mouseup', stopDrag);
    wrapper.addEventListener('mousemove', drag);

    // Touch events for mobile
    comparisonSlider.addEventListener('touchstart', startDrag);
    document.addEventListener('touchend', stopDrag);
    wrapper.addEventListener('touchmove', dragTouch);

    function startDrag(e) {
        e.preventDefault();
        isDragging = true;
        comparisonSlider.style.cursor = 'grabbing';
    }

    function stopDrag() {
        isDragging = false;
        comparisonSlider.style.cursor = 'ew-resize';
    }

    function drag(e) {
        if (!isDragging) return;

        const rect = wrapper.getBoundingClientRect();
        const x = e.clientX - rect.left;
        updateSliderPosition(x, rect.width);
    }

    function dragTouch(e) {
        if (!isDragging) return;

        const rect = wrapper.getBoundingClientRect();
        const touch = e.touches[0];
        const x = touch.clientX - rect.left;
        updateSliderPosition(x, rect.width);
    }

    function updateSliderPosition(x, width) {
        // Constrain between 10% and 90%
        const percentage = Math.max(10, Math.min(90, (x / width) * 100));

        leftSide.style.width = `${percentage}%`;
        comparisonSlider.style.left = `${percentage}%`;
    }

    // Set initial position to 50%
    leftSide.style.width = '50%';
    comparisonSlider.style.left = '50%';
}

// Sync video playback
function syncVideos() {
    // Sync play/pause
    referenceComparisonVideo.addEventListener('play', () => {
        if (!isComparisonPlaying) return;
        resultComparisonVideo.play();
    });

    referenceComparisonVideo.addEventListener('pause', () => {
        resultComparisonVideo.pause();
    });

    // Sync seeking
    referenceComparisonVideo.addEventListener('seeked', () => {
        resultComparisonVideo.currentTime = referenceComparisonVideo.currentTime;
    });

    // Loop synchronization - restart both when reference loops
    referenceComparisonVideo.addEventListener('ended', () => {
        referenceComparisonVideo.currentTime = 0;
        resultComparisonVideo.currentTime = 0;
        if (isComparisonPlaying) {
            referenceComparisonVideo.play();
            resultComparisonVideo.play();
        }
    });

    // Periodic re-sync to prevent drift (every 5 seconds)
    setInterval(() => {
        if (isComparisonPlaying && Math.abs(referenceComparisonVideo.currentTime - resultComparisonVideo.currentTime) > 0.3) {
            resultComparisonVideo.currentTime = referenceComparisonVideo.currentTime;
        }
    }, 5000);
}

// Toggle between comparison and single view
function toggleView(view) {
    currentView = view;

    if (view === 'comparison') {
        comparisonContainer.classList.remove('hidden');
        singleViewContainer.classList.add('hidden');
    } else {
        comparisonContainer.classList.add('hidden');
        singleViewContainer.classList.remove('hidden');
    }
}

// Toggle play/pause for comparison videos
function toggleComparisonPlayback() {
    isComparisonPlaying = !isComparisonPlaying;

    if (isComparisonPlaying) {
        referenceComparisonVideo.play();
        resultComparisonVideo.play();
        playComparisonBtn.textContent = '⏸️';
    } else {
        referenceComparisonVideo.pause();
        resultComparisonVideo.pause();
        playComparisonBtn.textContent = '▶️';
    }
}
