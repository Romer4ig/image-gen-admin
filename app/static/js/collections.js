document.addEventListener('DOMContentLoaded', function() {
    // Handle select all checkbox
    const selectAllCheckbox = document.getElementById('selectAllCollections');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.collection-checkbox');
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }

    // Handle bulk generate button state
    const bulkGenerateBtn = document.getElementById('bulkGenerateBtn');
    const bulkProjectSelect = document.getElementById('bulkProjectSelect');
    if (bulkGenerateBtn && bulkProjectSelect) {
        bulkProjectSelect.addEventListener('change', function() {
            bulkGenerateBtn.disabled = !this.value;
        });
    }

    // Toggle prompt edit buttons
    const promptEditors = document.querySelectorAll('.prompt-editor, .negative-prompt-editor');
    promptEditors.forEach(editor => {
        const textarea = editor.querySelector('.prompt-text, .negative-prompt-text');
        const originalValue = textarea.dataset.originalValue;
        
        textarea.addEventListener('input', function() {
            const saveBtn = editor.querySelector('.save-prompt-btn');
            if (!saveBtn && this.value !== originalValue) {
                const saveBtn = document.createElement('button');
                saveBtn.className = 'btn btn-sm btn-primary save-prompt-btn mt-2';
                saveBtn.innerHTML = '<i class="bi bi-save"></i> Сохранить';
                saveBtn.addEventListener('click', savePrompt);
                editor.appendChild(saveBtn);
            } else if (saveBtn && this.value === originalValue) {
                saveBtn.remove();
            }
        });
    });
});

function savePrompt(event) {
    const btn = event.target.closest('button');
    const editor = btn.closest('.prompt-editor, .negative-prompt-editor');
    const textarea = editor.querySelector('.prompt-text, .negative-prompt-text');
    const collectionId = editor.dataset.collectionId;
    const isNegative = editor.classList.contains('negative-prompt-editor');
    
    const data = {
        collection_id: collectionId
    };
    
    if (isNegative) {
        data.negative_prompt = textarea.value;
    } else {
        data.prompt = textarea.value;
    }
    
    fetch('/collections/update_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.remove();
            textarea.dataset.originalValue = textarea.value;
            // Show success message
            const toast = new bootstrap.Toast(document.getElementById('promptSavedToast'));
            toast.show();
        }
    });
}