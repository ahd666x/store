const BOM = {
    init() {
        let currentRow = null;
        let editMode = false;
        let editPartId = null;

        function resetModalToCreate() {
            document.getElementById('partModalTitle').textContent = 'ایجاد قطعه جدید';
            document.getElementById('part-submit-btn').textContent = 'ایجاد قطعه';
            document.getElementById('part-form').reset();
            editMode = false;
            editPartId = null;
        }

        function fillHiddenFields() {
            const categoryName = document.getElementById('id_category')?.options?.[document.getElementById('id_category').selectedIndex]?.text?.trim() || '';
            const productName = document.getElementById('id_name')?.value?.trim() || '';
            document.getElementById('part-grain').value = categoryName;
            document.getElementById('part-pname').value = productName;
        }

        document.querySelectorAll('.add-part-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                currentRow = this.closest('.bom-row');
                resetModalToCreate();
                fillHiddenFields();
                const modal = new bootstrap.Modal(document.getElementById('partModal'));
                modal.show();
            });
        });

        document.querySelectorAll('.edit-part-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                currentRow = this.closest('.bom-row');
                const partId = currentRow.dataset.partId;
                if (!partId) return;

                const baseUrl = window.BOMConfig?.ajaxGetPartUrl || '';
                fetch(baseUrl.replace('/0/', '/' + partId + '/'))
                    .then(res => res.json())
                    .then(data => {
                        document.getElementById('partModalTitle').textContent = 'ویرایش قطعه';
                        document.getElementById('part-submit-btn').textContent = 'ذخیره تغییرات';
                        editMode = true;
                        editPartId = partId;

                        document.getElementById('part-name').value = data.name;
                        document.getElementById('part-material').value = data.material;
                        document.getElementById('part-length').value = data.length;
                        document.getElementById('part-width').value = data.width;
                        document.getElementById('part-turn').checked = data.turn;
                        document.getElementById('part-f26').value = data.f26;
                        document.getElementById('part-f18').value = data.f18;
                        document.getElementById('part-f4').value = data.f4;
                        document.getElementById('part-f5').value = data.f5;
                        document.getElementById('part-f3').value = data.f3;
                        document.getElementById('part-routing').value = data.routing_code;
                        document.getElementById('part-base').value = data.base_part;
                        document.getElementById('part-grain').value = data.grain;
                        document.getElementById('part-pname').value = data.pname;

                        const modal = new bootstrap.Modal(document.getElementById('partModal'));
                        modal.show();
                    });
            });
        });

        document.getElementById('partModal').addEventListener('hidden.bs.modal', function() {
            currentRow = null;
            resetModalToCreate();
        });

        document.getElementById('part-form').addEventListener('submit', function(e) {
            e.preventDefault();
            if (!currentRow) {
                alert('ردیف انتخاب نشده است.');
                return;
            }

            const url = editMode
                ? (window.BOMConfig?.ajaxEditPartUrl || '').replace('/0/', '/' + editPartId + '/')
                : (window.BOMConfig?.ajaxCreatePartUrl || '');

            const formData = new FormData(this);
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(response => {
                if (response.success) {
                    currentRow.querySelector('input[name$="-part"]').value = response.id;
                    currentRow.querySelector('.part-name').textContent = response.name;
                    currentRow.dataset.partId = response.id;
                    const existingEditBtn = currentRow.querySelector('.edit-part-btn');
                    if (!existingEditBtn) {
                        const editBtn = document.createElement('button');
                        editBtn.type = 'button';
                        editBtn.className = 'btn btn-sm btn-outline-warning edit-part-btn';
                        editBtn.title = 'ویرایش قطعه';
                        editBtn.innerHTML = '<i class="bi bi-pencil"></i>';
                        currentRow.querySelector('.part-cell').appendChild(editBtn);
                    }
                    const modal = bootstrap.Modal.getInstance(document.getElementById('partModal'));
                    modal.hide();
                } else {
                    alert('خطا: ' + JSON.stringify(response.errors));
                }
            });
        });

        const applyRuleDropdown = (row) => {
            const ruleHidden = row.querySelector('.size-rule-hidden');
            const presetSelect = row.querySelector('.size-rule-preset');
            const customInput = row.querySelector('.size-rule-custom');
            if (!ruleHidden || !presetSelect || !customInput) return;

            const syncRuleField = () => {
                const presetVal = presetSelect.value;
                if (!presetVal) {
                    presetSelect.style.display = '';
                    customInput.style.display = 'none';
                    ruleHidden.value = '';
                    return;
                }
                if (presetVal === 'custom') {
                    presetSelect.style.display = 'none';
                    customInput.style.display = '';
                    ruleHidden.value = customInput.value;
                } else {
                    presetSelect.style.display = '';
                    customInput.style.display = 'none';
                    ruleHidden.value = presetVal;
                }
            };

            presetSelect.addEventListener('change', syncRuleField);
            customInput.addEventListener('input', () => {
                if (presetSelect.value === 'custom') {
                    ruleHidden.value = customInput.value;
                }
            });

            if (ruleHidden.value && presetSelect.options.length) {
                const options = Array.from(presetSelect.options);
                const matched = options.find(opt => opt.value === ruleHidden.value);
                if (matched) {
                    presetSelect.value = ruleHidden.value;
                } else {
                    presetSelect.value = 'custom';
                    customInput.value = ruleHidden.value;
                }
            }
            syncRuleField();
        };

        document.querySelectorAll('#bom-rows tr.bom-row').forEach(row => {
            applyRuleDropdown(row);
        });

        const buildEmptyRowHtml = (index) => {
            return `
            <tr class="bom-row" data-part-id="">
                <td class="part-cell">
                    <span class="part-name">قطعه‌ای انتخاب نشده</span>
                    <button type="button" class="btn btn-sm btn-outline-success add-part-btn" title="ایجاد قطعه جدید">
                        <i class="bi bi-plus"></i>
                    </button>
                    <input type="hidden" name="bom-${index}-part" id="id_bom-${index}-part">
                </td>
                <td><input type="number" name="bom-${index}-quantity" value="1" min="1" class="form-control" id="id_bom-${index}-quantity"></td>
                <td><select name="bom-${index}-color_part" class="form-select color-part-select" id="id_bom-${index}-color_part">
                    <option value="" selected="">---------</option>
                    <option value="بدنه">بدنه</option>
                    <option value="درب">درب</option>
                    <option value="دستگیره">دستگیره</option>
                    <option value="پایه">پایه</option>
                    <option value="صفحه">صفحه</option>
                    <option value="رینگ">رینگ</option>
                </select></td>
                <td class="size-rule-cell">
                    <input type="hidden" name="bom-${index}-size_adjustment_rule" class="size-rule-hidden" id="id_bom-${index}-size_adjustment_rule">
                    <select class="form-select form-select-sm size-rule-preset">
                        <option value="">--- انتخاب قانون ---</option>
                        <option value="length + length_diff">طول + تغییر طول</option>
                        <option value="length + length_diff/3">(طول + تغییر طول) ÷ ۳</option>
                        <option value="length + length_diff/4">(طول + تغییر طول) ÷ ۴</option>
                        <option value="custom">✏️ سفارشی</option>
                    </select>
                    <input type="text" class="form-control form-control-sm size-rule-custom" style="display:none;" placeholder="فرمول دلخواه">
                </td>
                <td class="text-center"></td>
                <input type="hidden" name="bom-${index}-color_material_map" id="id_bom-${index}-color_material_map">
            </tr>`;
        };

        document.getElementById('add-bom-row').addEventListener('click', function() {
            const totalForms = document.getElementById('id_bom-TOTAL_FORMS');
            const currentCount = parseInt(totalForms.value);
            const tbody = document.getElementById('bom-rows');
            const lastRow = tbody.querySelector('tr.bom-row:last');

            let newRow;
            if (!lastRow) {
                newRow = document.createElement('tr');
                newRow.innerHTML = buildEmptyRowHtml(currentCount);
                tbody.appendChild(newRow);
                totalForms.value = currentCount + 1;
                applyRuleDropdown(newRow);
                return;
            }

            newRow = lastRow.cloneNode(true);

            newRow.querySelectorAll('input,select,textarea').forEach(function(el) {
                const name = el.getAttribute('name');
                if (name) {
                    el.setAttribute('name', name.replace(`bom-${currentCount-1}-`, `bom-${currentCount}-`));
                }
                const id = el.getAttribute('id');
                if (id) {
                    el.setAttribute('id', id.replace(`id_bom-${currentCount-1}-`, `id_bom-${currentCount}-`));
                }
                if (el.type === 'checkbox') {
                    el.checked = false;
                } else if (el.tagName === 'SELECT') {
                    el.value = '';
                } else if (el.type !== 'hidden') {
                    el.value = '';
                }
            });

            newRow.querySelector('input[name$="-part"]').value = '';
            newRow.querySelector('.part-name').textContent = 'قطعه‌ای انتخاب نشده';
            newRow.dataset.partId = '';
            const editBtns = newRow.querySelectorAll('.edit-part-btn, .add-part-btn');
            editBtns.forEach(b => b.remove());
            const addBtn = document.createElement('button');
            addBtn.type = 'button';
            addBtn.className = 'btn btn-sm btn-outline-success add-part-btn';
            addBtn.title = 'ایجاد قطعه جدید';
            addBtn.innerHTML = '<i class="bi bi-plus"></i>';
            newRow.querySelector('.part-cell').appendChild(addBtn);
            newRow.querySelector('td:last').innerHTML = '';
            newRow.querySelector('.size-rule-preset').value = '';
            newRow.querySelector('.size-rule-custom').style.display = 'none';
            newRow.querySelector('.size-rule-custom').value = '';
            newRow.querySelector('.size-rule-hidden').value = '';
            newRow.querySelector('input[name$="-color_material_map"]').value = '';

            tbody.appendChild(newRow);
            totalForms.value = currentCount + 1;

            applyRuleDropdown(newRow);
        });
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BOM.init());
} else {
    BOM.init();
}
