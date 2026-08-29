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
