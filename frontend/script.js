// script.js - 毕业设计管理系统前端脚本

// 全局变量，用于存储当前用户信息和项目信息
let currentUser = {
    id: null,
    role: localStorage.getItem("userRole") || "admin" // 默认admin
};
let currentProject = null;

document.addEventListener(
    'DOMContentLoaded', function() {
      // 初始化导航
      initNavigation();
      
      // 简单角色->用户ID映射（配合后端测试数据）
      if (currentUser.role === 'student') currentUser.id = 1;
      if (currentUser.role === 'teacher') currentUser.id = 2;
      if (currentUser.role === 'admin') currentUser.id = 3;
      
      // 模拟登录：根据角色设置 ID (已移除，等待后续逻辑设置)
      // if (currentUser.role === 'student') currentUser.id = 1; 
      // if (currentUser.role === 'teacher') currentUser.id = 2; 
      // if (currentUser.role === 'admin') currentUser.id = 3;   
      
      // 如果当前页面是模块5，加载数据
      const activeModule = document.querySelector('.module-content.active');
      if (activeModule && activeModule.id === 'module5') {
          loadGuidanceModule();
      }
    });

function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');

  navItems.forEach(item => {
    item.addEventListener('click', function() {
      const target = this.getAttribute('data-target');
      const moduleId = target.replace('.html', '');

      // 移除所有active类
      document.querySelectorAll('.module-content').forEach(module => {
        module.classList.remove('active');
      });
      document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.remove('active');
      });

      // 添加active类
      const targetModule = document.getElementById(moduleId);
      if (targetModule) {
        targetModule.classList.add('active');
      }
      this.classList.add('active');

      // 更新页面标题
      const titleEl = document.getElementById('module-title');
      if(titleEl) titleEl.textContent = this.textContent.trim();
      
      // 特定模块加载逻辑
      if (moduleId === 'module5') {
          loadGuidanceModule();
      }
    });
  });
}

// --- 模块5：指导记录管理逻辑 ---

async function loadGuidanceModule() {
    try {
        // 1. 获取基本信息
        let infoData = {};
        
        // 如果是学生角色，直接使用写死的信息
        if (currentUser.role === 'student') {
            infoData = {
                studentName: '图图',
                teacherName: 'David',
                title: '基于深度学习的图像识别系统研究',
                id: 1 // 默认projectId
            };
            currentProject = infoData;
        } else {
            // 其他角色从后端获取
            try {
                const infoRes = await fetch('/api/guidance/info', {
                    headers: { 'X-User-Id': currentUser.id || 1 }
                });
                if (infoRes.ok) {
                    infoData = await infoRes.json();
                    currentProject = infoData;
                }
            } catch (e) {
                console.warn('获取基本信息失败，使用默认值', e);
            }
        }
        
        // 渲染学生基本信息
        const infoCard = document.querySelector('#module5 .user-info-base-card');
        if (infoCard && (infoData.studentName || currentUser.role === 'student')) {
            infoCard.innerHTML = `
                <div class="info-item">
                    <span class="label">学生姓名</span>
                    <p class="value">${infoData.studentName || '图图'}</p>
                </div>
                <div class="info-item">
                    <span class="label">指导教师</span>
                    <p class="value">${infoData.teacherName || 'David'}</p>
                </div>
                <div class="info-item topic">
                    <span class="label">选题课题</span>
                    <p class="value">${infoData.title || '基于深度学习的图像识别系统研究'}</p>
                </div>
            `;
        }
        
        // 确保"已申报数量/下限"只在学生视角显示
        const recordCountHeader = document.getElementById('record-count-header');
        if (recordCountHeader) {
            if (currentUser.role === 'student') {
                recordCountHeader.style.display = 'inline';
            } else {
                recordCountHeader.style.display = 'none';
            }
        }

        // 2. 获取指导记录列表
        try {
            const recordsRes = await fetch('/api/guidance/records', {
                headers: { 'X-User-Id': currentUser.id || 1 }
            });
            if (recordsRes.ok) {
                const records = await recordsRes.json();
                renderRecordsTable(records);
            } else {
                // 如果获取失败，显示空列表
                renderRecordsTable([]);
            }
        } catch (e) {
            console.error('获取指导记录失败:', e);
            renderRecordsTable([]);
        }
        
    } catch (error) {
        console.error('加载指导记录失败:', error);
        // 即使出错也显示基本信息
        if (currentUser.role === 'student') {
            const infoCard = document.querySelector('#module5 .user-info-base-card');
            if (infoCard) {
                infoCard.innerHTML = `
                    <div class="info-item">
                        <span class="label">学生姓名</span>
                        <p class="value">图图</p>
                    </div>
                    <div class="info-item">
                        <span class="label">指导教师</span>
                        <p class="value">David</p>
                    </div>
                    <div class="info-item topic">
                        <span class="label">选题课题</span>
                        <p class="value">基于深度学习的图像识别系统研究</p>
                    </div>
                `;
            }
        }
        
        // 确保"已申报数量/下限"只在学生视角显示
        const recordCountHeader = document.getElementById('record-count-header');
        if (recordCountHeader) {
            if (currentUser.role === 'student') {
                recordCountHeader.style.display = 'inline';
            } else {
                recordCountHeader.style.display = 'none';
            }
        }
        
        renderRecordsTable([]);
    }
}

function renderRecordsTable(records) {
    const tbody = document.getElementById('guidance-record-list');
    const countSpan = document.getElementById('record-count');
    if (!tbody) return;
    
    // 保存当前记录列表，供修改功能使用
    currentRecordsList = records;
    
    tbody.innerHTML = '';
    if(countSpan) countSpan.textContent = records.length;

    // 计算已通过的记录数（教科办返回“通过”）
    const submittedCount = records.filter(r => r.teacherComment === '通过').length;
    const submittedCountSpan = document.getElementById('submitted-count');
    if (submittedCountSpan) {
        submittedCountSpan.textContent = submittedCount;
    }

    records.forEach(record => {
        const tr = document.createElement('tr');
        
        // 转义HTML特殊字符，防止XSS
        const escapeHtml = (text) => {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        };
        
        // 按钮逻辑
        let actionButtons = '';
        if (currentUser.role === 'admin') {
            actionButtons = `<button class="btn btn-primary" onclick="openEditModal(${record.id}, '${escapeHtml(record.teacherComment || '')}')">修改</button>`;
        } else if (currentUser.role === 'student') {
             // 学生逻辑：如果未提交(status=0)，显示修改和提交按钮；如果已提交(status=1)，只显示已提交
             if (record.status === 0) {
                 actionButtons = `
                     <button class="btn btn-secondary" onclick="openEditRecordModal(${record.id})" style="margin-right: 5px;">修改</button>
                     <button class="btn btn-primary" onclick="submitRecordToAdmin(${record.id})">提交指导记录到教科办</button>
                 `;
             } else {
                 actionButtons = `<button class="btn btn-secondary" disabled>已提交</button>`;
             }
        }

        // 处理文件内容显示和导出/打印
        const contentDisplay = record.content ? `<span style="color:blue">${escapeHtml(record.content)}</span>` : '无内容';
        const exportButton = record.content ? 
            `<button class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px; margin-left:5px;" onclick="viewRecordFile('${escapeHtml(record.content)}', ${record.id})">导出/打印</button>` :
            `<button class="btn btn-secondary" style="padding: 4px 12px; font-size: 12px; margin-left:5px;" disabled>导出/打印</button>`;

        const disableCheckbox = currentUser.role === 'student' && record.status === 1;

        tr.innerHTML = `
            <td><input type="checkbox" class="record-checkbox" value="${record.id}" ${disableCheckbox ? 'disabled' : ''} onchange="updateSelectAllState()"></td>
            <td>${escapeHtml(record.studentName)}</td>
            <td>${escapeHtml(record.teacherName)}</td>
            <td>
                ${contentDisplay}
                ${exportButton}
            </td>
            <td>${record.teacherComment ? escapeHtml(record.teacherComment) : '<span style="color:#999">待审查</span>'}</td>
            <td>${actionButtons}</td>
        `;
        tbody.appendChild(tr);
    });
    
    // 更新全选复选框状态
    updateSelectAllState();
}

// 打开新增模态框 (学生)
function openAddRecordModal() {
    document.getElementById('modal-title').textContent = '新增指导记录';
    document.getElementById('record-id').value = ''; // 空ID表示新增
    
    // 尝试自动填充，如果没有则留空
    document.getElementById('student-name').value = currentProject ? (currentProject.studentName || '') : '';
    document.getElementById('teacher-name').value = currentProject ? (currentProject.teacherName || '') : '';
    
    const teacherSelect = document.getElementById('teacher-comment-select');
    if (teacherSelect) teacherSelect.value = '';
    document.getElementById('record-file').value = '';
    
    // 删除可能存在的当前文件提示
    const existingHint = document.getElementById('current-file-hint');
    if (existingHint) {
        existingHint.remove();
    }
    
    // 显示/隐藏对应字段
    document.querySelectorAll('#guidance-form [data-role="student"]').forEach(el => el.style.display = 'block');
    document.querySelectorAll('#guidance-form [data-role="admin"]').forEach(el => el.style.display = 'none');
    
    document.getElementById('modal-submit-btn').textContent = '完成';
    document.getElementById('guidance-modal').style.display = 'block';
}

// 存储当前记录列表，用于修改时获取记录信息
let currentRecordsList = [];

// 打开修改模态框 (学生修改自己的记录)
function openEditRecordModal(recordId) {
    // 从当前记录列表中查找记录
    const record = currentRecordsList.find(r => r.id === recordId);
    
    if (!record) {
        alert('记录不存在，请刷新页面后重试');
        return;
    }
    
    // 检查是否已提交，已提交的不允许修改
    if (record.status === 1) {
        alert('该记录已提交，无法修改');
        return;
    }
    
    document.getElementById('modal-title').textContent = '修改指导记录';
    document.getElementById('record-id').value = recordId;
    
    // 填充现有数据
    document.getElementById('student-name').value = record.studentName || '';
    document.getElementById('teacher-name').value = record.teacherName || '';
    document.getElementById('record-file').value = ''; // 文件输入框不能预设值，需要重新选择
    
    // 显示当前文件名（作为提示）
    const fileInput = document.getElementById('record-file');
    if (fileInput && record.content && record.content !== '未上传文件' && record.content !== '无内容') {
        // 在文件输入框后面显示当前文件名提示
        const fileGroup = fileInput.closest('.form-group');
        if (fileGroup) {
            // 如果已存在提示，先删除
            const existingHint = document.getElementById('current-file-hint');
            if (existingHint) {
                existingHint.remove();
            }
            
            const hint = document.createElement('p');
            hint.id = 'current-file-hint';
            hint.style.fontSize = '12px';
            hint.style.color = '#666';
            hint.style.marginTop = '5px';
            hint.textContent = `当前文件: ${record.content}（如需修改，请重新选择文件）`;
            fileGroup.appendChild(hint);
        }
    }
    
    // 显示/隐藏对应字段
    document.querySelectorAll('#guidance-form [data-role="student"]').forEach(el => el.style.display = 'block');
    document.querySelectorAll('#guidance-form [data-role="admin"]').forEach(el => el.style.display = 'none');
    
    document.getElementById('modal-submit-btn').textContent = '保存修改';
    document.getElementById('guidance-modal').style.display = 'block';
}

// 打开修改模态框 (教科办)
function openEditModal(id, currentComment) {
    document.getElementById('modal-title').textContent = '审查指导记录';
    document.getElementById('record-id').value = id;
    
    // 隐藏学生填写的字段，只显示审查意见
    document.querySelectorAll('#guidance-form [data-role="student"]').forEach(el => el.style.display = 'none');
    document.querySelectorAll('#guidance-form [data-role="admin"]').forEach(el => el.style.display = 'block');
    
    const teacherSelect = document.getElementById('teacher-comment-select');
    if (teacherSelect) {
        teacherSelect.value = currentComment === '通过' || currentComment === '不通过' ? currentComment : '';
    }
    document.getElementById('modal-submit-btn').textContent = '提交指导记录';
    document.getElementById('guidance-modal').style.display = 'block';
}

function closeModal() {
    document.getElementById('guidance-modal').style.display = 'none';
    // 清除可能存在的当前文件提示
    const existingHint = document.getElementById('current-file-hint');
    if (existingHint) {
        existingHint.remove();
    }
}

// 保存记录 (新增或修改)
async function saveRecord() {
    const id = document.getElementById('record-id').value;
    const isEdit = !!id;
    
    const url = isEdit ? `/api/guidance/records/${id}` : '/api/guidance/records';
    const method = isEdit ? 'PUT' : 'POST';
    
    const body = {};
    
    if (isEdit) {
        // 判断是学生修改还是教科办修改
        const teacherSelect = document.getElementById('teacher-comment-select');
        const isAdminEdit = teacherSelect && teacherSelect.parentElement.style.display !== 'none';
        
        if (isAdminEdit) {
            // 教科办修改审查意见
            body.teacherComment = teacherSelect.value;
        } else {
            // 学生修改记录内容
            const fileInput = document.getElementById('record-file');
            const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : null;
            
            // 如果选择了新文件，更新内容；否则保持原内容不变
            if (fileName) {
                body.content = fileName;
            }
            // 修改时保持原有状态
        }
    } else {
        // 学生新增
        const fileInput = document.getElementById('record-file');
        const fileName = fileInput.files.length > 0 ? fileInput.files[0].name : '未上传文件';
        
        // 确保有projectId，学生角色时使用默认值1
        body.projectId = currentProject ? (currentProject.id || 1) : 1; 
        body.content = fileName; 
        body.status = 0; // 状态0：草稿/已完成但未提交教科办
    }
    
    try {
        const res = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1 // 临时 fallback ID
            },
            body: JSON.stringify(body)
        });
        
        if (res.ok) {
            alert(isEdit ? '修改成功' : '记录已保存');
            closeModal();
            // 延迟一下再刷新，确保数据库已提交
            setTimeout(() => {
                loadGuidanceModule(); // 刷新列表
            }, 100);
        } else {
            const errData = await res.json().catch(() => ({ error: '未知错误' }));
            alert('操作失败: ' + (errData.error || '未知错误'));
        }
    } catch (error) {
        console.error('保存失败:', error);
        alert('网络错误: ' + error.message);
    }
}

// 提交记录到教科办 (新增功能)
async function submitRecordToAdmin(recordId) {
    if(!confirm('确认提交该记录至教科办吗？提交后不可修改。')) return;

    try {
        const res = await fetch(`/api/guidance/records/${recordId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({ status: 1 }) // 状态1：已提交教科办
        });
        
        if (res.ok) {
            alert('提交成功');
            loadGuidanceModule();
        } else {
            alert('提交失败');
        }
    } catch (error) {
        console.error('提交失败:', error);
    }
}

// 全选/取消全选
function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllRecords');
    const recordCheckboxes = document.querySelectorAll('.record-checkbox');
    
    recordCheckboxes.forEach(checkbox => {
        if (!checkbox.disabled) {
            checkbox.checked = selectAllCheckbox.checked;
        }
    });
}

// 更新全选复选框状态
function updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('selectAllRecords');
    const recordCheckboxes = Array.from(document.querySelectorAll('.record-checkbox')).filter(cb => !cb.disabled);
    
    if (recordCheckboxes.length === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
        return;
    }
    
    const checkedCount = recordCheckboxes.filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === recordCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

// 查看/导出记录文件
function viewRecordFile(fileName, recordId) {
    if (!fileName || fileName === '无内容' || fileName === '未上传文件') {
        alert('该记录没有上传文件');
        return;
    }
    
    // 创建一个新窗口显示文件信息，实际项目中这里应该下载或预览文件
    const fileInfo = `文件名: ${fileName}\n记录ID: ${recordId}\n\n注意：这是演示版本，实际项目中这里会显示文件预览或下载文件。`;
    
    // 可以打开一个新窗口显示文件信息，或者直接下载
    if (confirm(fileInfo + '\n\n是否要下载该文件？')) {
        // 实际项目中应该调用后端API下载文件
        alert('文件下载功能需要后端支持，当前为演示版本');
        // 示例：window.open(`/api/guidance/records/${recordId}/download`, '_blank');
    }
}

// 批量删除
async function deleteSelectedRecords() {
    const checkboxes = document.querySelectorAll('.record-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('请先选择要删除的记录');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 条记录吗？`)) return;
    
    const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    try {
        const res = await fetch('/api/guidance/records', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({ ids: ids })
        });
        
        if (res.ok) {
            alert('删除成功');
            loadGuidanceModule();
        } else {
            alert('删除失败');
        }
    } catch (error) {
        console.error('删除失败:', error);
    }
}

// 模拟功能函数
function showAlert(message) { alert(message); }

function uploadFile() { alert('文件上传功能模拟'); }

function submitReview() { alert('评审提交成功'); }

function exportData() { alert('导出功能模拟'); }

function checkPlagiarism() { alert('查重功能模拟'); }

function convertAudioToText() { alert('录音转文字功能模拟'); }

function calculateScore() {
  // 简单分数计算示例
  const score1 =
      parseFloat(document.querySelector('input[type="number"]:nth-of-type(1)')
                     .value) ||
      0;
  const score2 =
      parseFloat(document.querySelector('input[type="number"]:nth-of-type(2)')
                     .value) ||
      0;
  const score3 =
      parseFloat(document.querySelector('input[type="number"]:nth-of-type(3)')
                     .value) ||
      0;
  const score4 =
      parseFloat(document.querySelector('input[type="number"]:nth-of-type(4)')
                     .value) ||
      0;

  // 假设权重：开题20%，平时30%，论文评价20%，答辩30%
  const total = score1 * 0.2 + score2 * 0.3 + score3 * 0.2 + score4 * 0.3;
  document.getElementById('total1').textContent = total.toFixed(1);
  alert('总分计算完成：' + total.toFixed(1));
}

function archiveMaterials() { alert('归档功能模拟'); }