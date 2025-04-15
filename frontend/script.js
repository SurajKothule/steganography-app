document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.getElementById('fileLabel');
    const imagePreview = document.getElementById('imagePreview');
    const encodeBtn = document.getElementById('encodeBtn');
    const decodeBtn = document.getElementById('decodeBtn');
    const message = document.getElementById('message');
    const password = document.getElementById('password');
    const result = document.getElementById('result');

    // Drag and drop functionality
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--accent)';
        dropZone.style.backgroundColor = 'rgba(76, 201, 240, 0.1)';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.borderColor = '#ccc';
        dropZone.style.backgroundColor = '';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
        dropZone.style.backgroundColor = '';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileDisplay();
        }
    });

    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', updateFileDisplay);

    function updateFileDisplay() {
        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            fileLabel.textContent = file.name;
            
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.style.display = 'block';
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        }
    }

    // Encode button
    encodeBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            showResult('Please select an image first', 'error');
            return;
        }

        if (!message.value.trim()) {
            showResult('Please enter a message to encode', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('message', message.value);
        formData.append('password', password.value);

        try {
            encodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Encoding...';
            encodeBtn.disabled = true;
            
            const response = await fetch('/api/encode', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Encoding failed');
            }
            
            showResult(
                `Message encoded successfully!<br><br>
                <a href="${data.download_url}" download class="download-btn">
                    <i class="fas fa-download"></i> Download encoded image
                </a>`,
                'success'
            );
        } catch (err) {
            showResult(`Error: ${err.message}`, 'error');
        } finally {
            encodeBtn.innerHTML = '<i class="fas fa-lock"></i> Encode';
            encodeBtn.disabled = false;
        }
    });

    // Decode button
    decodeBtn.addEventListener('click', async () => {
        if (!fileInput.files.length) {
            showResult('Please select an image first', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('password', password.value);

        try {
            decodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Decoding...';
            decodeBtn.disabled = true;
            
            const response = await fetch('/api/decode', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Decoding failed');
            }
            
            showResult(`<strong>Decoded message:</strong><br><br><div class="decoded-message">${data.message}</div>`, 'success');
        } catch (err) {
            showResult(`Error: ${err.message}`, 'error');
        } finally {
            decodeBtn.innerHTML = '<i class="fas fa-unlock"></i> Decode';
            decodeBtn.disabled = false;
        }
    });

    function showResult(text, type) {
        result.innerHTML = `<div class="${type}">${text}</div>`;
        result.scrollIntoView({ behavior: 'smooth' });
    }
});