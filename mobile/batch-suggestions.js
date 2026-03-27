// 显示波次号联想提示
async function showBatchSuggestions() {
  const batchNo = document.getElementById('batchNo').value.trim();
  const suggestionsBox = document.getElementById('batchSuggestions');
  
  if (!batchNo || batchNo.length < 2) {
    suggestionsBox.style.display = 'none';
    return;
  }
  
  const token = localStorage.getItem('token');
  try {
    const response = await fetch(`${API_BASE}/api/batches/search?batch_no=${encodeURIComponent(batchNo)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.length > 0) {
        const suggestions = data.slice(0, 5);
        suggestionsBox.innerHTML = suggestions.map(item => 
          `<div class="suggestion-item" onclick="selectBatchSuggestion('${item.batch_no}', '${item.factory_name}')">` +
          `<div class="batch-code">${item.batch_no}</div>` +
          `<div class="factory-name">🏭 ${item.factory_name}</div></div>`
        ).join('');
        suggestionsBox.style.display = 'block';
      } else {
        suggestionsBox.style.display = 'none';
      }
    }
  } catch (error) {
    console.error('联想提示失败:', error);
    suggestionsBox.style.display = 'none';
  }
}

function selectBatchSuggestion(batchNo, factoryName) {
  document.getElementById('batchNo').value = batchNo;
  document.getElementById('factory').value = factoryName;
  document.getElementById('batchSuggestions').style.display = 'none';
  showToast('已选择波次号');
}

function hideBatchSuggestions() {
  setTimeout(() => {
    document.getElementById('batchSuggestions').style.display = 'none';
  }, 200);
}
