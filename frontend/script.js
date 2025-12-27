// script.js - 毕业设计管理系统前端脚本

// 全局变量，用于存储当前用户信息和项目信息
let currentUser = {
    id: null,
    role: localStorage.getItem("userRole") || "admin" // 默认admin
};
let currentProject = null;
let allRecords = []; // 保存所有原始记录，用于筛选

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
      
      // 如果当前页面是模块3或模块5，加载数据
      const activeModule = document.querySelector('.module-content.active');
      if (activeModule && activeModule.id === 'module5') {
          loadGuidanceModule();
      }
      if (activeModule && activeModule.id === 'module3') {
          loadTaskModule();
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
      if (moduleId === 'module3') {
          loadTaskModule();
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
                allRecords = records; // 保存所有原始记录
                renderRecordsTable(records);
            } else {
                // 如果获取失败，显示空列表
                allRecords = [];
                renderRecordsTable([]);
            }
        } catch (e) {
            console.error('获取指导记录失败:', e);
            allRecords = [];
            renderRecordsTable([]);
        }
        
        // 清空搜索框
        const searchInput = document.getElementById('student-name-search');
        if (searchInput) {
            searchInput.value = '';
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
        
        // 清空搜索框
        const searchInput = document.getElementById('student-name-search');
        if (searchInput) {
            searchInput.value = '';
        }
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

        // 学生视角：已提交的记录无法选中
        // 教师视角：已通过审核的记录无法选中
        const disableCheckbox = (currentUser.role === 'student' && record.status === 1) || 
                                (currentUser.role === 'teacher' && record.teacherComment === '通过');

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

// 根据学生姓名筛选记录
function filterRecordsByStudentName() {
    const searchInput = document.getElementById('student-name-search');
    if (!searchInput) return;
    
    const searchName = searchInput.value.trim();
    
    if (!searchName) {
        // 如果搜索框为空，显示所有记录
        renderRecordsTable(allRecords);
        return;
    }
    
    // 筛选记录：根据学生姓名进行模糊匹配
    const filteredRecords = allRecords.filter(record => {
        const studentName = record.studentName || '';
        return studentName.includes(searchName);
    });
    
    renderRecordsTable(filteredRecords);
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

// --- 模块3：任务书发布管理逻辑 ---

let currentTaskInfo = null;
let currentTaskId = null;

// 初始化上传区域的点击事件
function initTaskUploadAreas() {
    // 学生初稿上传区域
    const studentUploadArea = document.getElementById('student-draft-upload-area');
    if (studentUploadArea) {
        studentUploadArea.onclick = function() {
            const fileInput = document.getElementById('task-upload-input');
            if (fileInput) fileInput.click();
        };
    }
    
    // 教师修改稿上传区域
    const teacherUploadArea = document.getElementById('teacher-revision-upload-area');
    if (teacherUploadArea) {
        teacherUploadArea.onclick = function() {
            const fileInput = document.getElementById('teacher-task-upload-input');
            if (fileInput) fileInput.click();
        };
    }
}

async function loadTaskModule() {
    // 初始化上传区域的点击事件
    initTaskUploadAreas();
    
    try {
        // 获取任务书信息
        const res = await fetch('/api/task/info', {
            headers: { 'X-User-Id': currentUser.id || 1 }
        });
        
        if (res.ok) {
            currentTaskInfo = await res.json();
            currentTaskId = currentTaskInfo.id;
            renderTaskModule();
        } else {
            // 如果没有记录，初始化空状态
            currentTaskInfo = {
                projectId: null,
                studentDraftPath: null,
                studentSubmitted: 0,
                teacherRevisionPath: null,
                teacherSubmitted: 0,
                adminStatus: null
            };
            renderTaskModule();
        }
        
        // 如果是教务处，加载审核列表
        if (currentUser.role === 'admin') {
            loadTaskReviewList();
        }
    } catch (error) {
        console.error('加载任务书模块失败:', error);
        currentTaskInfo = {
            projectId: null,
            studentDraftPath: null,
            studentSubmitted: 0,
            teacherRevisionPath: null,
            teacherSubmitted: 0,
            adminStatus: null
        };
        renderTaskModule();
    }
}

function renderTaskModule() {
    // 即使currentTaskInfo为null，也要渲染（显示初始状态）
    // 移除"当前阶段"文本
    removeCurrentStageText();

    // 更新进度条
    updateTaskProgress();
    
    // 更新状态标识（即使currentTaskInfo为null也要显示）
    updateTaskStatusBadge();
    
    // 更新学生初稿区域
    updateStudentDraftArea();
    
    // 更新教师修改稿区域
    updateTeacherRevisionArea();
}

// 新增函数：移除当前阶段文本
function removeCurrentStageText() {
    const module3 = document.getElementById('module3');
    if (!module3) return;
    
    // 查找包含"当前阶段："的元素并隐藏
    const elements = module3.querySelectorAll('p, div, span, h5, h6');
    elements.forEach(el => {
        if (el.textContent && (el.textContent.includes('当前阶段：') || el.textContent.includes('Current Stage:'))) {
            // 确保只隐藏包含该文本的特定小元素，而不是整个容器
            if (el.children.length === 0 || (el.children.length === 1 && el.children[0].tagName === 'SPAN')) {
                 el.style.display = 'none';
            }
        }
    });
}

// 更新任务书状态标识
function updateTaskStatusBadge() {
    // 在学生和教师视角显示状态标识
    if (currentUser.role !== 'student' && currentUser.role !== 'teacher') return;
    
    const progressCard = document.querySelector('#module3 .card[data-role="student,teacher"]');
    if (!progressCard) return;
    
    const cardHeader = progressCard.querySelector('.card-header');
    if (!cardHeader) return;
    
    // 移除已存在的状态标识
    const existingBadge = cardHeader.querySelector('.task-status-badge');
    if (existingBadge) {
        existingBadge.remove();
    }
    
    // 判断逻辑（基于用户需求）：
    // 1. 如果adminStatus为'approved'，显示"教务处已通过"（绿色）
    // 2. 如果adminStatus为'returned'，显示"教务处已退回"（红色，一直保持直到通过）
    // 3. 如果adminStatus为null（没有记录或第一次提交），显示"教务处未审批"（灰色）
    
    let badgeText = '';
    let badgeColor = '';
    
    // 检查是否有记录（通过检查是否有id或projectId来判断）
    const hasRecord = currentTaskInfo && (currentTaskInfo.id || currentTaskInfo.projectId);
    
    if (currentTaskInfo && currentTaskInfo.adminStatus === 'approved') {
        // 已通过：绿色
        badgeText = '教务处已通过';
        badgeColor = '#34C759';
    } else if (currentTaskInfo && currentTaskInfo.adminStatus === 'returned') {
        // 已退回：红色（一直保持，直到通过）
        badgeText = '教务处已退回';
        badgeColor = '#FF3B30';
    } else {
        // 其他情况（包括初始状态、第一次提交、待审核等）：显示"教务处未审批"
        // 如果currentTaskInfo为null或undefined，也显示"教务处未审批"
        badgeText = '教务处未审批';
        badgeColor = '#86868B';
    }
    
    // 创建状态标识
    const badge = document.createElement('span');
    badge.className = 'task-status-badge';
    badge.style.cssText = `
        margin-left: 12px;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        color: ${badgeColor};
        background-color: ${badgeColor === '#34C759' ? 'rgba(52, 199, 89, 0.1)' : 
                          badgeColor === '#FF3B30' ? 'rgba(255, 59, 48, 0.1)' : 
                          'rgba(134, 134, 139, 0.1)'};
    `;
    badge.textContent = badgeText;
    
    cardHeader.appendChild(badge);
}

function updateTaskProgress() {
    const step1 = document.querySelector('#module3 .step-item:nth-child(1)');
    const step2 = document.querySelector('#module3 .step-item:nth-child(2)');
    const step3 = document.querySelector('#module3 .step-item:nth-child(3)');
    
    if (!step1) return;
    
    // 移除所有active和completed类
    if (step1) {
        step1.classList.remove('active', 'completed');
    }
    if (step2) {
        step2.classList.remove('active', 'completed');
    }
    if (step3) {
        step3.classList.remove('active', 'completed');
    }
    
    // 如果被退回，重置进度条（但如果有重新提交，则根据提交状态显示）
    if (currentTaskInfo && currentTaskInfo.adminStatus === 'returned') {
        // 被退回时，如果学生重新提交了，显示第一步
        if (currentTaskInfo.studentSubmitted === 1) {
            if (step1) {
                step1.classList.add('active', 'completed');
            }
        }
        // 如果教师也重新提交了，显示前两步
        if (currentTaskInfo.teacherSubmitted === 1) {
            if (step1) {
                step1.classList.add('active', 'completed');
            }
            if (step2) {
                step2.classList.add('active');
            }
        }
        return;
    }
    
    // 根据状态更新进度
    if (currentTaskInfo && currentTaskInfo.adminStatus === 'approved') {
        // 已通过：所有步骤点亮，连接线全部标亮
        if (step1) {
            step1.classList.add('active', 'completed');
        }
        if (step2) {
            step2.classList.add('active', 'completed');
        }
        if (step3) {
            step3.classList.add('active', 'completed');
        }
    } else if (currentTaskInfo && currentTaskInfo.teacherSubmitted === 1) {
        // 教师已提交：前两步点亮，第一步到第二步的连接线标亮
        if (step1) {
            step1.classList.add('active', 'completed');
        }
        if (step2) {
            step2.classList.add('active');
        }
    } else if (currentTaskInfo && currentTaskInfo.studentSubmitted === 1) {
        // 学生已提交：第一步点亮，第一步到第二步的连接线左侧标亮
        if (step1) {
            step1.classList.add('active', 'completed');
        }
    }
}

function updateStudentDraftArea() {
    // 优先使用ID选择器
    let uploadArea = document.getElementById('student-draft-upload-area');
    // 使用更精确的选择器：选择包含"学生任务书初稿上传"标题的base-upload-card
    const studentCard = Array.from(document.querySelectorAll('#module3 .base-upload-card')).find(card => {
        const header = card.querySelector('.card-header');
        return header && header.textContent.includes('学生任务书初稿上传');
    });
    if (!uploadArea && studentCard) {
        uploadArea = studentCard.querySelector('.upload-area[data-role="student"]');
    }
    const previewArea = studentCard ? studentCard.querySelector('.card-body div[data-role="teacher"]') : null;
    const submitBtn = studentCard ? studentCard.querySelector('.btn-primary[data-role="student"]') : null;
    
    if (currentUser.role === 'student') {
        // 学生视角：确保只更新上传区域，不影响预览区域
        // 修复：如果currentTaskInfo为null，视为未上传
        if (currentTaskInfo && currentTaskInfo.studentDraftPath) {
            // 已上传文件
            let fileName = '未知文件';
            try {
                fileName = currentTaskInfo.studentDraftPath.split('/').pop();
                // 去除时间戳前缀（格式：时间戳_原文件名）
                const underscoreIndex = fileName.indexOf('_');
                if (underscoreIndex > 0) {
                    fileName = fileName.substring(underscoreIndex + 1);
                }
            } catch (e) {
                console.error('解析文件名失败:', e);
            }
            if (uploadArea) {
                uploadArea.style.cursor = 'default';
                uploadArea.onclick = null;
                uploadArea.innerHTML = `
                    <div style="padding: 20px; text-align: center;">
                        <p style="margin: 0 0 10px; font-weight: 500; color: #1d1d1f;">已上传文件：${fileName}</p>
                        <button class="btn btn-secondary" onclick="deleteStudentDraft()" style="padding: 4px 12px; font-size: 12px;">删除文件</button>
                    </div>
                `;
            }
        } else {
            // 未上传文件时，恢复 HTML 中的默认上传按钮 UI
            if (uploadArea) {
                uploadArea.style.cursor = 'pointer';
                // 恢复默认的上传按钮 UI
                uploadArea.innerHTML = `
                    <input type="file" id="task-upload-input" style="display: none;" onchange="uploadStudentDraft()">
                    <div style="width: 40px; height: 40px; background-color: rgba(0,122,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </div>
                    <p style="margin: 0 0 5px; font-weight: 500; font-size: 14px;">将文件拖到此处上传</p>
                    <p style="margin: 0 0 10px; color: #86868b; font-size: 12px;">或者，您可以单击此处选择一个文件</p>
                    <span style="color: #007AFF; font-size: 13px; font-weight: 500;">点击上传</span>
                `;
                // 重新绑定点击事件
                uploadArea.onclick = () => {
                    const fileInput = document.getElementById('task-upload-input');
                    if (fileInput) fileInput.click();
                };
            }
        }
        
        // 更新提交按钮状态
        if (submitBtn) {
            // 修复：安全访问currentTaskInfo
            if (currentTaskInfo && currentTaskInfo.adminStatus === 'approved') {
                // 已通过，不允许修改
                submitBtn.disabled = true;
                submitBtn.textContent = '已通过，无法修改';
            } else if (currentTaskInfo && currentTaskInfo.adminStatus === 'returned') {
                // 被退回，允许重新提交
                submitBtn.disabled = !currentTaskInfo || !currentTaskInfo.studentDraftPath;
                submitBtn.textContent = '修改/提交';
            } else if (currentTaskInfo && currentTaskInfo.studentSubmitted === 1) {
                // 已提交但未审核或被退回，不允许再次提交（除非被退回）
                submitBtn.disabled = true;
                submitBtn.textContent = '已提交';
            } else {
                // 未提交，允许提交
                submitBtn.disabled = !currentTaskInfo || !currentTaskInfo.studentDraftPath;
                submitBtn.textContent = '修改/提交';
            }
        }
    } else if (currentUser.role === 'teacher') {
        // 教师视角：只更新预览区域，不影响上传区域
        if (currentTaskInfo && currentTaskInfo.studentSubmitted === 1 && currentTaskInfo.studentDraftPath) {
            let fileName = '未知文件';
            try {
                fileName = currentTaskInfo.studentDraftPath.split('/').pop();
                const underscoreIndex = fileName.indexOf('_');
                if (underscoreIndex > 0) {
                    fileName = fileName.substring(underscoreIndex + 1);
                }
            } catch (e) {
                console.error('解析文件名失败:', e);
            }
            if (previewArea) {
                previewArea.style.padding = '20px';
                previewArea.style.textAlign = 'center';
                previewArea.style.backgroundColor = '#f5f5f7';
                previewArea.style.borderRadius = '8px';
                previewArea.innerHTML = `<p style="margin: 0; font-weight: 500; color: #1d1d1f;">学生已提交：${fileName}</p>`;
            }
        } else {
            if (previewArea) {
                previewArea.style.padding = '20px';
                previewArea.style.textAlign = 'center';
                previewArea.style.backgroundColor = '#f5f5f7';
                previewArea.style.borderRadius = '8px';
                previewArea.innerHTML = '<div style="padding: 20px; text-align: center; color: #86868b;">学生尚未提交初稿</div>';
            }
        }
        // 确保上传区域对学生不可见（通过data-role控制）
        if (uploadArea) {
            uploadArea.style.display = 'none';
        }
    }
}

function updateTeacherRevisionArea() {
    // 优先使用ID选择器，如果没有则使用类选择器
    let uploadArea = document.getElementById('teacher-revision-upload-area');
    if (!uploadArea) {
        // 使用更精确的选择器：选择包含"导师任务书修改稿"标题的base-upload-card
        const teacherCard = Array.from(document.querySelectorAll('#module3 .base-upload-card')).find(card => {
            const header = card.querySelector('.card-header');
            return header && header.textContent.includes('导师任务书修改稿');
        });
        if (teacherCard) {
            uploadArea = teacherCard.querySelector('.upload-area[data-role="teacher"]');
        }
    }
    // 同样使用更精确的选择器查找预览区域和提交按钮
    const teacherCard = Array.from(document.querySelectorAll('#module3 .base-upload-card')).find(card => {
        const header = card.querySelector('.card-header');
        return header && header.textContent.includes('导师任务书修改稿');
    });
    const previewArea = teacherCard ? teacherCard.querySelector('.card-body div[data-role="student"]') : null;
    const submitBtn = teacherCard ? teacherCard.querySelector('.btn-primary[data-role="teacher"]') : null;
    
    if (currentUser.role === 'teacher') {
        // 教师视角
        // 修复：如果currentTaskInfo为null，视为未上传
        if (currentTaskInfo && currentTaskInfo.teacherRevisionPath) {
            // 已上传文件
            let fileName = '未知文件';
            try {
                fileName = currentTaskInfo.teacherRevisionPath.split('/').pop();
                // 去除时间戳前缀（格式：时间戳_原文件名）
                const underscoreIndex = fileName.indexOf('_');
                if (underscoreIndex > 0) {
                    fileName = fileName.substring(underscoreIndex + 1);
                }
            } catch (e) {
                console.error('解析文件名失败:', e);
            }
            if (uploadArea) {
                uploadArea.style.cursor = 'default';
                uploadArea.onclick = null;
                uploadArea.innerHTML = `
                    <div style="padding: 20px; text-align: center;">
                        <p style="margin: 0 0 10px; font-weight: 500; color: #1d1d1f;">已上传文件：${fileName}</p>
                        <button class="btn btn-secondary" onclick="deleteTeacherRevision()" style="padding: 4px 12px; font-size: 12px;">删除文件</button>
                    </div>
                `;
            }
        } else {
            // 未上传文件
            if (uploadArea) {
                uploadArea.style.cursor = 'pointer';
                uploadArea.innerHTML = `
                    <input type="file" id="teacher-task-upload-input" style="display: none;" onchange="uploadTeacherRevision()">
                    <div style="width: 40px; height: 40px; background-color: rgba(0,122,255,0.1); border-radius: 8px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </div>
                    <p style="margin: 0 0 5px; font-weight: 500; font-size: 14px;">将文件拖到此处上传</p>
                    <p style="margin: 0 0 10px; color: #86868b; font-size: 12px;">或者，您可以单击此处选择一个文件</p>
                    <span style="color: #007AFF; font-size: 13px; font-weight: 500;">点击上传</span>
                `;
                uploadArea.onclick = (e) => {
                    // 阻止冒泡，防止触发多次
                    if(e) e.stopPropagation();
                    
                    const fileInput = document.getElementById('teacher-task-upload-input');
                    if (fileInput) {
                        fileInput.click();
                    } else {
                        console.error('找不到文件输入框: teacher-task-upload-input');
                    }
                };
            }
        }
        
        // 更新提交按钮状态
        if (submitBtn) {
            // 修复：安全访问currentTaskInfo
            if (currentTaskInfo && currentTaskInfo.adminStatus === 'approved') {
                // 已通过，不允许修改
                submitBtn.disabled = true;
                submitBtn.textContent = '已通过，无法修改';
            } else if (currentTaskInfo && currentTaskInfo.adminStatus === 'returned') {
                // 被退回，允许重新提交
                submitBtn.disabled = !currentTaskInfo || !currentTaskInfo.teacherRevisionPath || (currentTaskInfo.studentSubmitted !== 1);
                submitBtn.textContent = '修改/提交下发';
            } else if (currentTaskInfo && currentTaskInfo.teacherSubmitted === 1) {
                // 已提交但未审核或被退回，不允许再次提交（除非被退回）
                submitBtn.disabled = true;
                submitBtn.textContent = '已提交';
            } else {
                // 未提交，允许提交
                submitBtn.disabled = !currentTaskInfo || !currentTaskInfo.teacherRevisionPath || (currentTaskInfo.studentSubmitted !== 1);
                submitBtn.textContent = '修改/提交下发';
            }
        }
    } else if (currentUser.role === 'student') {
        // 学生视角：只有教师提交后才能看到
        if (currentTaskInfo && currentTaskInfo.teacherSubmitted === 1 && currentTaskInfo.teacherRevisionPath) {
            let fileName = '未知文件';
            try {
                fileName = currentTaskInfo.teacherRevisionPath.split('/').pop();
                const underscoreIndex = fileName.indexOf('_');
                if (underscoreIndex > 0) {
                    fileName = fileName.substring(underscoreIndex + 1);
                }
            } catch (e) {
                console.error('解析文件名失败:', e);
            }
            if (previewArea) {
                previewArea.style.padding = '20px';
                previewArea.style.textAlign = 'center';
                previewArea.style.backgroundColor = '#f5f5f7';
                previewArea.style.borderRadius = '8px';
                previewArea.innerHTML = `
                    <p style="margin: 0; font-weight: 500; color: #1d1d1f;">教师已提交：${fileName}</p>
                `;
            }
        } else {
            if (previewArea) {
                previewArea.style.padding = '20px';
                previewArea.style.textAlign = 'center';
                previewArea.style.backgroundColor = '#f5f5f7';
                previewArea.style.borderRadius = '8px';
                previewArea.innerHTML = '<p style="margin: 0; color: #86868b;">教师尚未提交修改稿</p>';
            }
        }
    }
}

// 学生上传初稿
async function uploadStudentDraft() {
    const fileInput = document.getElementById('task-upload-input');
    if (!fileInput || !fileInput.files[0]) {
        alert('请选择文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('fileType', 'student_draft');
    if (currentTaskInfo && currentTaskInfo.projectId) {
        formData.append('projectId', currentTaskInfo.projectId);
    }
    
    try {
        const res = await fetch('/api/task/upload', {
            method: 'POST',
            headers: { 'X-User-Id': currentUser.id || 1 },
            body: formData
        });
        
        if (res.ok) {
            const data = await res.json();
            currentTaskInfo = data;
            currentTaskId = currentTaskInfo.id;
            renderTaskModule();
            alert('文件上传成功');
        } else {
            // 尝试解析JSON错误响应
            let errorMessage = '未知错误';
            try {
                const errorData = await res.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                // 如果不是JSON，尝试获取文本
                try {
                    const text = await res.text();
                    console.error('服务器返回非JSON响应:', text.substring(0, 200));
                    errorMessage = `服务器错误 (HTTP ${res.status})`;
                } catch (e2) {
                    errorMessage = `HTTP ${res.status}: ${res.statusText}`;
                }
            }
            alert('上传失败: ' + errorMessage);
        }
    } catch (error) {
        console.error('上传失败:', error);
        alert('上传失败: ' + error.message);
    }
}

// 删除学生初稿
async function deleteStudentDraft() {
    if (!confirm('确定要删除已上传的文件吗？')) return;
    
    try {
        const res = await fetch('/api/task/delete-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                fileType: 'student_draft',
                projectId: currentTaskInfo.projectId
            })
        });
        
        if (res.ok) {
            currentTaskInfo = await res.json();
            currentTaskId = currentTaskInfo.id;
            renderTaskModule();
            alert('文件已删除');
        } else {
            const error = await res.json();
            alert('删除失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败: ' + error.message);
    }
}

// 学生提交初稿
async function submitStudentDraft() {
    if (!currentTaskInfo.studentDraftPath) {
        alert('请先上传文件');
        return;
    }
    
    if (!confirm('确认提交任务书初稿给教师吗？提交后无法修改。')) return;
    
    try {
        const res = await fetch('/api/task/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                submitType: 'student',
                projectId: currentTaskInfo.projectId
            })
        });
        
        if (res.ok) {
            const data = await res.json();
            currentTaskInfo = data;
            currentTaskId = currentTaskInfo.id;
            // 立即更新显示
            renderTaskModule();
            alert('提交成功');
        } else {
            const error = await res.json();
            alert('提交失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('提交失败:', error);
        alert('提交失败: ' + error.message);
    }
}

// 教师上传修改稿
async function uploadTeacherRevision() {
    const fileInput = document.getElementById('teacher-task-upload-input');
    if (!fileInput || !fileInput.files[0]) {
        alert('请选择文件');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('fileType', 'teacher_revision');
    if (currentTaskInfo && currentTaskInfo.projectId) {
        formData.append('projectId', currentTaskInfo.projectId);
    }
    
    try {
        const res = await fetch('/api/task/upload', {
            method: 'POST',
            headers: { 'X-User-Id': currentUser.id || 1 },
            body: formData
        });
        
        if (res.ok) {
            const data = await res.json();
            currentTaskInfo = data;
            currentTaskId = currentTaskInfo.id;
            // 立即更新显示
            renderTaskModule();
            alert('文件上传成功');
        } else {
            const error = await res.json();
            alert('上传失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('上传失败:', error);
        alert('上传失败: ' + error.message);
    }
}

// 删除教师修改稿
async function deleteTeacherRevision() {
    if (!confirm('确定要删除已上传的文件吗？')) return;
    
    try {
        const res = await fetch('/api/task/delete-file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                fileType: 'teacher_revision',
                projectId: currentTaskInfo.projectId
            })
        });
        
        if (res.ok) {
            currentTaskInfo = await res.json();
            currentTaskId = currentTaskInfo.id;
            renderTaskModule();
            alert('文件已删除');
        } else {
            const error = await res.json();
            alert('删除失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败: ' + error.message);
    }
}

// 教师提交修改稿
async function submitTeacherRevision() {
    if (!currentTaskInfo.teacherRevisionPath) {
        alert('请先上传文件');
        return;
    }
    
    if (!confirm('确认提交任务书修改稿给教务处吗？提交后无法修改。')) return;
    
    try {
        const res = await fetch('/api/task/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                submitType: 'teacher',
                projectId: currentTaskInfo.projectId
            })
        });
        
        if (res.ok) {
            const data = await res.json();
            currentTaskInfo = data;
            currentTaskId = currentTaskInfo.id;
            // 立即更新显示
            renderTaskModule();
            alert('提交成功');
        } else {
            const error = await res.json();
            alert('提交失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('提交失败:', error);
        alert('提交失败: ' + error.message);
    }
}

// 下载文件
async function downloadTaskFile(fileType) {
    if (!currentTaskId) {
        alert('任务书记录不存在');
        return;
    }
    
    try {
        const res = await fetch(`/api/task/download/${currentTaskId}?type=${fileType}`, {
            headers: { 'X-User-Id': currentUser.id || 1 }
        });
        
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            // 从响应头获取文件名，或使用默认名称
            const contentDisposition = res.headers.get('Content-Disposition');
            let filename = 'task_file';
            if (contentDisposition) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            } else {
                // 如果没有Content-Disposition，从currentTaskInfo获取文件名
                if (currentTaskInfo) {
                    const filePath = fileType === 'student_draft' ? currentTaskInfo.studentDraftPath : currentTaskInfo.teacherRevisionPath;
                    if (filePath) {
                        filename = filePath.split('/').pop().replace(/^[^_]+_/, '');
                    }
                }
            }
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            // 延迟释放URL，确保下载完成
            setTimeout(() => window.URL.revokeObjectURL(url), 100);
        } else {
            let errorMessage = '未知错误';
            try {
                const errorData = await res.json();
                errorMessage = errorData.error || errorMessage;
            } catch (e) {
                errorMessage = `HTTP ${res.status}: ${res.statusText}`;
            }
            alert('下载失败: ' + errorMessage);
        }
    } catch (error) {
        console.error('下载失败:', error);
        alert('下载失败: ' + error.message);
    }
}

// 查看文件（预览）
async function viewTaskFile(fileType) {
    if (!currentTaskId) {
        alert('任务书记录不存在');
        return;
    }
    
    try {
        const res = await fetch(`/api/task/download/${currentTaskId}?type=${fileType}`, {
            headers: { 'X-User-Id': currentUser.id || 1 }
        });
        
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } else {
            const error = await res.json();
            alert('查看失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('查看失败:', error);
        alert('查看失败: ' + error.message);
    }
}

// 打印文件
async function printTaskFile(fileType) {
    if (!currentTaskId) {
        alert('任务书记录不存在');
        return;
    }
    
    const link = document.createElement('a');
    link.href = `/api/task/download/${currentTaskId}?type=${fileType}`;
    link.download = '';
    link.click();
    alert('文件已下载，请在下载的文件中打印');
}

// 教务处：加载审核列表
async function loadTaskReviewList() {
    try {
        const res = await fetch('/api/task/list', {
            headers: { 'X-User-Id': currentUser.id || 1 }
        });
        
        if (res.ok) {
            const tasks = await res.json();
            renderTaskReviewList(tasks);
        } else {
            renderTaskReviewList([]);
        }
    } catch (error) {
        console.error('加载审核列表失败:', error);
        renderTaskReviewList([]);
    }
}

function renderTaskReviewList(tasks) {
    const tbody = document.querySelector('#module3 .card[data-role="admin"] tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    tasks.forEach(task => {
        const tr = document.createElement('tr');
        
        let statusHtml = '';
        if (task.adminStatus === 'approved') {
            statusHtml = '<span style="color: #34C759; font-weight: 500;">已通过</span> ' +
                        '<button class="btn btn-secondary" style="color: var(--color-danger-text); margin-left: 10px;" onclick="deleteTaskRecord(' + task.id + ')">删除</button>';
        } else if (task.adminStatus === 'returned' && task.teacherSubmitted === 1) {
            // 退回后重新提交的，显示为待审核状态
            statusHtml = '<span style="color: #86868B; font-weight: 500;">待审核（已退回后重新提交）</span> ' +
                        '<button class="btn btn-primary" onclick="approveTask(' + task.id + ')">通过</button> ' +
                        '<button class="btn btn-secondary" style="color: var(--color-danger-text);" onclick="returnTask(' + task.id + ')">退回</button>';
        } else if (task.adminStatus === 'returned') {
            // 已退回但未重新提交
            statusHtml = '<span style="color: #FF3B30; font-weight: 500;">已退回</span>';
        } else {
            // 待审核（第一次提交）
            statusHtml = '<button class="btn btn-primary" onclick="approveTask(' + task.id + ')">通过</button> ' +
                        '<button class="btn btn-secondary" style="color: var(--color-danger-text);" onclick="returnTask(' + task.id + ')">退回</button>';
        }
        
        tr.innerHTML = `
            <td><input type="checkbox" value="${task.id}"></td>
            <td>${task.studentName || '图图'}</td>
            <td>${task.teacherName || 'David'}</td>
            <td>
                <button class="btn btn-secondary" onclick="viewTaskDetail(${task.id})">查看任务书详情</button>
                ${statusHtml}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// 查看任务书详情
async function viewTaskDetail(taskId) {
    // 使用fetch下载文件，然后在新窗口打开
    try {
        const res = await fetch(`/api/task/download/${taskId}?type=teacher_revision`, {
            headers: { 'X-User-Id': currentUser.id || 1 }
        });
        
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } else {
            const error = await res.json();
            alert('查看失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('查看失败:', error);
        alert('查看失败: ' + error.message);
    }
}

// 删除任务书记录（教务处用）
async function deleteTaskRecord(taskId) {
    if (!confirm('确认删除该任务书记录吗？删除后业务将重新开始。')) return;
    
    try {
        const res = await fetch('/api/task/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                taskId: taskId
            })
        });
        
        if (res.ok) {
            const data = await res.json();
            alert('删除成功，业务已重新开始');
            loadTaskReviewList();
            // 如果当前用户也在查看任务书模块，刷新显示
            if (currentUser.role !== 'admin') {
                // 重新加载任务书信息
                currentTaskInfo = data;
                currentTaskId = currentTaskInfo.id;
                renderTaskModule();
            }
        } else {
            const error = await res.json();
            alert('删除失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('删除失败:', error);
        alert('删除失败: ' + error.message);
    }
}

// 通过任务书
async function approveTask(taskId) {
    if (!confirm('确认通过该任务书吗？')) return;
    
    try {
        const res = await fetch('/api/task/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                taskId: taskId,
                action: 'approve'
            })
        });
        
        if (res.ok) {
            alert('审核通过');
            loadTaskReviewList();
            // 如果当前用户也在查看任务书模块，刷新显示
            if (currentUser.role !== 'admin') {
                loadTaskModule();
            }
        } else {
            const error = await res.json();
            alert('操作失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('审核失败:', error);
        alert('审核失败: ' + error.message);
    }
}

// 退回任务书
async function returnTask(taskId) {
    if (!confirm('确认退回该任务书吗？退回后学生和教师可以重新提交。')) return;
    
    try {
        const res = await fetch('/api/task/review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-User-Id': currentUser.id || 1
            },
            body: JSON.stringify({
                taskId: taskId,
                action: 'return'
            })
        });
        
        if (res.ok) {
            alert('已退回，学生和教师可以重新提交');
            loadTaskReviewList();
            // 如果当前用户也在查看任务书模块，刷新显示
            if (currentUser.role !== 'admin') {
                loadTaskModule();
            }
        } else {
            const error = await res.json();
            alert('操作失败: ' + (error.error || '未知错误'));
        }
    } catch (error) {
        console.error('退回失败:', error);
        alert('退回失败: ' + error.message);
    }
}