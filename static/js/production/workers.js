const Workers = {
    init() {
        this.bindEvents();
        this.initSelect2();
    },

    bindEvents() {
        document.getElementById('btnAddWorker')?.addEventListener('click', () => {
            this.resetWorkerForm();
            if (window.WorkersModal && window.bootstrap) {
                new bootstrap.Modal(document.getElementById('workerModal')).show();
            }
        });

        document.querySelectorAll('.btn-edit-worker').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openWorkerEdit(btn.dataset.workerId);
            });
        });

        document.querySelectorAll('.btn-delete-worker').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openDelete(btn.dataset.workerId);
            });
        });

        document.querySelectorAll('.btn-exclusion').forEach(btn => {
            btn.addEventListener('click', () => {
                this.openExclusion(btn.dataset.workerId, btn.dataset.type);
            });
        });

        document.getElementById('workerForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveWorker();
        });

        document.getElementById('exclusionForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveExclusion();
        });

        document.getElementById('confirmDeleteBtn')?.addEventListener('click', () => {
            this.confirmDelete();
        });

        document.getElementById('filterForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters(1);
        });
    },

    initSelect2() {
        const exclusionSelect = document.getElementById('exclusionSelect');
        if (!exclusionSelect || typeof $.fn.select2 === 'undefined') return;

        const type = document.getElementById('exclusionType')?.value || 'products';
        const searchUrl = type === 'products' ? window.SEARCH_PRODUCTS_URL : window.SEARCH_ITEMS_URL;

        $(exclusionSelect).select2({
            theme: 'bootstrap-5',
            width: '100%',
            placeholder: 'جستجو...',
            allowClear: true,
            closeOnSelect: false,
            minimumInputLength: 0,
            ajax: {
                url: (params) => searchUrl + '?q=' + (params.term || ''),
                dataType: 'json',
                delay: 250,
                data: (params) => ({ q: params.term || '' }),
                processResults: (data) => ({
                    results: data.results.map(item => ({ id: item.id, text: item.text }))
                }),
                cache: false
            }
        });
    },

    resetWorkerForm() {
        document.getElementById('workerForm')?.reset();
        document.getElementById('workerId').value = '';
        document.getElementById('workerModalTitle').textContent = 'کارگر جدید';
        document.querySelectorAll('.skill-checkbox').forEach(cb => cb.checked = false);
        document.getElementById('id_skills').value = '[]';
        document.getElementById('id_skill_costs').value = '{}';
        document.getElementById('id_is_available').checked = true;
    },

    openWorkerEdit(workerId) {
        fetch(`${window.WORKERS_BASE}${workerId}/`)
            .then(r => r.json())
            .then(data => {
                document.getElementById('workerModalTitle').textContent = 'ویرایش کارگر';
                document.getElementById('workerId').value = data.id;
                document.getElementById('id_user').value = data.user_id;
                document.getElementById('id_stage').value = data.stage || 'paint';
                document.getElementById('id_is_available').checked = data.is_available;

                if (data.skills && data.skills.length) {
                    document.querySelectorAll('.skill-checkbox').forEach(cb => {
                        cb.checked = data.skills.includes(cb.value);
                    });
                }

                if (data.skill_priority) {
                    document.getElementById('id_skill_costs').value = JSON.stringify(data.skill_priority);
                    Object.entries(data.skill_priority).forEach(([skill, cost]) => {
                        const input = document.getElementById(`cost_${skill}`);
                        if (input) input.value = cost;
                    });
                }

                this.updateSkillsHidden();
                if (window.WorkersModal && window.bootstrap) {
                    new bootstrap.Modal(document.getElementById('workerModal')).show();
                }
            });
    },

    openDelete(workerId) {
        document.getElementById('deleteWorkerId')?.remove();
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'deleteWorkerId';
        input.name = 'worker_id';
        input.value = workerId;
        document.getElementById('workerForm')?.appendChild(input);

        const row = document.getElementById(`worker-row-${workerId}`);
        const name = row?.querySelector('td')?.textContent || workerId;
        document.getElementById('deleteWorkerName').textContent = name;

        if (window.WorkersModal && window.bootstrap) {
            new bootstrap.Modal(document.getElementById('deleteModal')).show();
        }
    },

    confirmDelete() {
        const workerId = document.getElementById('deleteWorkerId')?.value;
        if (!workerId) return;

        fetch(`${window.WORKERS_BASE}${workerId}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                TableManager.removeRow(workerId);
                if (window.WorkersModal) window.WorkersModal.hide();
            } else {
                alert(data.error || 'خطا در حذف');
            }
        });
    },

    openExclusion(workerId, type) {
        document.getElementById('exclusionType').value = type;
        document.getElementById('exclusionWorkerId').value = workerId;
        document.getElementById('exclusionModalTitle').textContent = type === 'products' ? 'مدیریت محصولات ممنوع' : 'مدیریت آیتم‌های ممنوع';
        document.getElementById('exclusionLabel').textContent = type === 'products' ? 'محصولات ممنوع:' : 'آیتم‌های ممنوع:';
        document.getElementById('exclusionHelp').textContent = type === 'products' ? 'محصولات انتخاب‌شده را کارگر در زمان‌بندی نمی‌بیند.' : 'آیتم‌های انتخاب‌شده را کارگر در زمان‌بندی نمی‌بیند.';

        const select = document.getElementById('exclusionSelect');
        if (select && typeof $.fn.select2 !== 'undefined') {
            $(select).val(null).trigger('change');
            this.initSelect2();
        }

        if (window.WorkersModal && window.bootstrap) {
            new bootstrap.Modal(document.getElementById('exclusionModal')).show();
        }
    },

    saveWorker() {
        const workerId = document.getElementById('workerId').value;
        const formData = new FormData(document.getElementById('workerForm'));
        const url = workerId ? `${window.WORKERS_BASE}${workerId}/` : window.WORKERS_BASE;

        fetch(url, {
            method: workerId ? 'PUT' : 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('خطا: ' + JSON.stringify(data.errors || data));
            }
        });
    },

    saveExclusion() {
        const formData = new FormData(document.getElementById('exclusionForm'));
        fetch(`${window.WORKERS_BASE}exclusions/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' },
            body: formData
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.error || 'خطا در ذخیره ممنوعیت');
            }
        });
    },

    updateSkillsHidden() {
        const checked = Array.from(document.querySelectorAll('.skill-checkbox:checked')).map(cb => cb.value);
        document.getElementById('id_skills').value = JSON.stringify(checked);

        const costs = {};
        checked.forEach(skill => {
            const input = document.getElementById(`cost_${skill}`);
            if (input && input.value) costs[skill] = parseInt(input.value) || 0;
        });
        document.getElementById('id_skill_costs').value = JSON.stringify(costs);
    },

    applyFilters(page) {
        const form = document.getElementById('filterForm');
        if (!form) return;

        const params = new URLSearchParams();
        params.set('page', page);
        const search = form.querySelector('[name="search"]')?.value;
        const status = form.querySelector('[name="status"]')?.value;
        const skill = form.querySelector('[name="skill"]')?.value;

        if (search) params.set('search', search);
        if (status) params.set('status', status);
        if (skill) params.set('skill', skill);

        fetch(`${window.WORKERS_BASE}?${params.toString()}`)
            .then(r => r.json())
            .then(data => {
                TableManager.updatePagination(data.pagination);
                const tbody = document.getElementById('workerTableBody');
                if (tbody && data.results) {
                    tbody.innerHTML = data.results.map(w => `
                        <tr id="worker-row-${w.id}" data-worker-id="${w.id}">
                            <td>${w.username || ''}</td>
                            <td>${w.stage_label || ''}</td>
                            <td>${(w.skills || []).map(s => `<span class="badge bg-info skill-badge">${s}</span>`).join(' ') || '<span class="text-muted">-</span>'}</td>
                            <td><code class="small">${JSON.stringify(w.skill_priority || {})}</code></td>
                            <td><span class="badge ${w.is_available ? 'bg-success' : 'bg-secondary'} rounded-pill">${w.is_available ? 'فعال' : 'غیرفعال'}</span></td>
                            <td><span class="badge bg-warning text-dark rounded-pill" id="product-count-${w.id}">${w.excluded_products_count || 0}</span></td>
                            <td><span class="badge bg-danger rounded-pill" id="item-count-${w.id}">${w.excluded_items_count || 0}</span></td>
                            <td>${w.active_tasks || 0}</td>
                            <td><div class="dropdown action-dropdown"><button class="dropdown-toggle" type="button" data-bs-toggle="dropdown"><i class="bi bi-three-dots-vertical"></i></button></div></td>
                        </tr>
                    `).join('');
                }
            });
    }
};

window.WorkersModal = {
    hide() {
        document.querySelectorAll('.modal.show').forEach(m => {
            if (window.bootstrap) bootstrap.Modal.getInstance(m)?.hide();
        });
    }
};

document.addEventListener('change', () => Workers.updateSkillsHidden());

const TableManager = {
    updateRow(workerData) {
        const row = document.getElementById(`worker-row-${workerData.id}`);
        if (!row) return;
        const cells = row.querySelectorAll('td');
        if (cells.length < 8) return;

        cells[0].textContent = workerData.username || '';
        cells[1].textContent = workerData.stage_label || '';

        const skills = workerData.skills || [];
        cells[2].innerHTML = skills.length ?
            skills.map(s => `<span class="badge bg-info skill-badge">${s}</span>`).join(' ') :
            '<span class="text-muted">-</span>';

        const costs = workerData.skill_priority || {};
        cells[3].innerHTML = Object.keys(costs).length ?
            `<code class="small">${JSON.stringify(costs)}</code>` :
            '<span class="text-muted">-</span>';

        const isActive = workerData.is_available === true;
        cells[4].innerHTML = `<span class="badge ${isActive ? 'bg-success' : 'bg-secondary'} rounded-pill">${isActive ? 'فعال' : 'غیرفعال'}</span>`;

        const prodCount = document.getElementById(`product-count-${workerData.id}`);
        if (prodCount) prodCount.textContent = workerData.excluded_products_count || 0;

        const itemCount = document.getElementById(`item-count-${workerData.id}`);
        if (itemCount) itemCount.textContent = workerData.excluded_items_count || 0;

        cells[7].textContent = workerData.active_tasks || 0;
    },

    addRow(workerData) {
        const tbody = document.getElementById('workerTableBody');
        if (!tbody) return;

        const emptyRow = tbody.querySelector('tr td[colspan]');
        if (emptyRow) tbody.innerHTML = '';

        const tr = document.createElement('tr');
        tr.id = `worker-row-${workerData.id}`;
        tr.setAttribute('data-worker-id', workerData.id);

        const skills = workerData.skills || [];
        const costs = workerData.skill_priority || {};
        const isActive = workerData.is_available === true;

        tr.innerHTML = `<td>${workerData.username || ''}</td>` +
            `<td>${workerData.stage_label || ''}</td>` +
            `<td>${skills.length ? skills.map(s => `<span class="badge bg-info skill-badge">${s}</span>`).join(' ') : '<span class="text-muted">-</span>'}</td>` +
            `<td>${Object.keys(costs).length ? `<code class="small">${JSON.stringify(costs)}</code>` : '<span class="text-muted">-</span>'}</td>` +
            `<td><span class="badge ${isActive ? 'bg-success' : 'bg-secondary'} rounded-pill">${isActive ? 'فعال' : 'غیرفعال'}</span></td>` +
            `<td><span class="badge bg-warning text-dark rounded-pill" id="product-count-${workerData.id}">0</span> ` +
            `<button class="btn btn-sm btn-outline-warning ms-1 btn-exclusion" data-worker-id="${workerData.id}" data-type="products" title="مدیریت محصولات ممنوع"><i class="bi bi-slash-circle"></i></button></td>` +
            `<td><span class="badge bg-danger rounded-pill" id="item-count-${workerData.id}">0</span> ` +
            `<button class="btn btn-sm btn-outline-danger ms-1 btn-exclusion" data-worker-id="${workerData.id}" data-type="items" title="مدیریت آیتم‌های ممنوع"><i class="bi bi-ban"></i></button></td>` +
            '<td>0</td>' +
            `<td><div class="dropdown action-dropdown"><button class="dropdown-toggle" type="button" data-bs-toggle="dropdown"><i class="bi bi-three-dots-vertical"></i></button>` +
            `<ul class="dropdown-menu dropdown-menu-end">` +
            `<li><a class="dropdown-item btn-edit-worker" href="#" data-worker-id="${workerData.id}"><i class="bi bi-pencil me-2"></i>ویرایش</a></li>` +
            `<li><a class="dropdown-item btn-delete-worker" href="#" data-worker-id="${workerData.id}"><i class="bi bi-trash me-2"></i>حذف</a></li>` +
            '</ul></div></td>';

        tbody.appendChild(tr);
        this.bindRowEvents(tr);
    },

    bindRowEvents(row) {
        row.querySelectorAll('.btn-edit-worker').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                Workers.openWorkerEdit(btn.dataset.workerId);
            });
        });
        row.querySelectorAll('.btn-delete-worker').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                Workers.openDelete(btn.dataset.workerId);
            });
        });
    },

    removeRow(workerId) {
        const row = document.getElementById(`worker-row-${workerId}`);
        if (row) row.remove();
        const tbody = document.getElementById('workerTableBody');
        if (tbody && tbody.children.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted">' +
                '<i class="bi bi-people fs-2 d-block mb-2"></i>' +
                'هیچ کارگری یافت نشد.</td></tr>';
        }
    },

    updatePagination(html) {
        const container = document.getElementById('paginationContainer');
        if (!container) return;
        container.innerHTML = html;
        container.querySelectorAll('.page-link[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.dataset.page;
                if (page) Workers.applyFilters(page);
            });
        });
    }
};
