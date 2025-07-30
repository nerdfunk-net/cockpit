import { CONFIG } from '../../src/config.js';

const BACKEND_API = `${CONFIG.API.BASE_URL}${CONFIG.API.ENDPOINTS.DEVICES}`;
const PAGE_SIZE = CONFIG.UI.PAGE_SIZE;
let currentPage = 1;
let currentRightPage = 1; // Add pagination for right table
let devices = [];
let rightTableDevices = [];

let leftTableBody, rightTableBody, toRightBtn, toLeftBtn;

// Initialize DOM elements and event listeners after page loads
function initializeDOMElements() {
  leftTableBody = document.getElementById('left-table-body');
  rightTableBody = document.getElementById('right-table-body');
  toRightBtn = document.getElementById('to-right');
  toLeftBtn = document.getElementById('to-left');
  
  console.log('[DEBUG] DOM elements initialized:', {
    leftTableBody: !!leftTableBody,
    rightTableBody: !!rightTableBody,
    toRightBtn: !!toRightBtn,
    toLeftBtn: !!toLeftBtn
  });

  // Set up button event listeners
  setupButtonEventListeners();
}

function setupButtonEventListeners() {
  if (toRightBtn) {
    console.log('[DEBUG] Setting up toRightBtn event listener');
    toRightBtn.addEventListener('click', () => {
      console.log('[DEBUG] toRightBtn clicked');
      // Get all checked checkboxes in the left table
      if (!leftTableBody) {
        console.error('[ERROR] leftTableBody not found when moving devices right');
        return;
      }
      const checked = leftTableBody.querySelectorAll('input[type="checkbox"]:checked:not(#select-all-left)');
      console.log('[DEBUG] Found checked checkboxes in left table:', checked.length);
      
      const selectedIds = Array.from(checked).map(cb => cb.getAttribute('data-device-id')).filter(Boolean);
      console.log('[DEBUG] Selected device IDs:', selectedIds);
      
      // Find device objects by id
      const selectedDevices = devices.filter(d => selectedIds.includes(d.id));
      console.log('[DEBUG] Selected devices:', selectedDevices);
      
      // Add to right table if not already present
      let addedCount = 0;
      for (const dev of selectedDevices) {
        if (!rightTableDevices.find(d => d.id === dev.id)) {
          rightTableDevices.push(dev);
          addedCount++;
        }
      }
      console.log('[DEBUG] Added', addedCount, 'devices to right table');
      
      // Reset right table pagination to first page if devices were added
      if (addedCount > 0) {
        currentRightPage = 1;
      }
      
      // Uncheck the selected items
      checked.forEach(cb => cb.checked = false);
      
      renderTable();
    });
  } else {
    console.error('[ERROR] toRightBtn element not found!');
  }

  if (toLeftBtn) {
    console.log('[DEBUG] Setting up toLeftBtn event listener');
    toLeftBtn.addEventListener('click', () => {
      console.log('[DEBUG] toLeftBtn clicked');
      // Get all checked checkboxes in the right table
      if (!rightTableBody) {
        console.error('[ERROR] rightTableBody not found when moving devices left');
        return;
      }
      const checked = rightTableBody.querySelectorAll('input[type="checkbox"]:checked:not(#select-all-right)');
      console.log('[DEBUG] Found checked checkboxes in right table:', checked.length);
      
      const selectedIds = Array.from(checked).map(cb => cb.getAttribute('data-device-id')).filter(Boolean);
      console.log('[DEBUG] Selected device IDs to remove:', selectedIds);
      
      // Remove selected devices from rightTableDevices
      const beforeCount = rightTableDevices.length;
      rightTableDevices = rightTableDevices.filter(d => !selectedIds.includes(d.id));
      const removedCount = beforeCount - rightTableDevices.length;
      console.log('[DEBUG] Removed', removedCount, 'devices from right table');
      
      // Adjust right table pagination if we removed devices
      if (removedCount > 0) {
        const totalRightPages = Math.ceil(rightTableDevices.length / PAGE_SIZE);
        if (currentRightPage > totalRightPages && totalRightPages > 0) {
          currentRightPage = totalRightPages;
        } else if (rightTableDevices.length === 0) {
          currentRightPage = 1;
        }
      }
      
      renderTable();
    });
  } else {
    console.error('[ERROR] toLeftBtn element not found!');
  }
}

async function fetchDevices(filterType = null, filterValue = null) {
  console.log('[DEBUG] fetchDevices called with:', { filterType, filterValue });
  
  // Reset to first page when filtering
  if (filterType && filterValue) {
    currentPage = 1;
  }
  
  try {
    let url = BACKEND_API;
    if (filterType === 'name' && filterValue && filterValue.length >= 3) {
      url = BACKEND_API + '?filter_type=name&filter_value=' + encodeURIComponent(filterValue);
    } else if (filterType === 'location' && filterValue && filterValue.length >= 3) {
      url = BACKEND_API + '?filter_type=location&filter_value=' + encodeURIComponent(filterValue);
    } else if (filterType === 'prefix' && filterValue && filterValue.length > 0) {
      url = BACKEND_API + '?filter_type=prefix&filter_value=' + encodeURIComponent(filterValue);
    }
    
    console.log('[DEBUG] Making API request to:', url);
    
    // Convert to relative path for Vite proxy
    const relativePath = url.replace(CONFIG.API.BASE_URL, '');
    const data = await window.authManager.apiRequest(relativePath);
    console.log('[DEBUG] Received data from backend:', data);
    
    if (!data.devices) {
      showError('No device data returned from backend.');
      devices = [];
    } else {
      devices = data.devices;
      console.log('[DEBUG] Devices array set to:', devices);
      console.log('[DEBUG] Number of devices:', devices.length);
    }
    console.log('[DEBUG] About to call renderTable...');
    renderTable();
    renderPagination();
  } catch (error) {
    showError('Failed to fetch devices: ' + error.message);
    devices = [];
    renderTable();
    renderPagination();
  }
}

function showError(message) {
  leftTableBody.innerHTML = `<tr><td colspan="5" style="color:red;text-align:center;">${message}</td></tr>`;
}

function renderTable() {
  console.log('[DEBUG] renderTable called with devices:', devices);
  console.log('[DEBUG] leftTableBody element:', leftTableBody);
  
  if (!leftTableBody) {
    console.error('[ERROR] leftTableBody element not found!');
    return;
  }
  
  leftTableBody.innerHTML = '';
  const start = (currentPage - 1) * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageDevices = devices.slice(start, end);
  console.log('[DEBUG] pageDevices to render:', pageDevices);
  for (const device of pageDevices) {
    const row = document.createElement('tr');
    row.innerHTML = `
                <td><input type="checkbox" data-device-id="${device.id}" class="row-checkbox-left"></td>
                <td>${device.name || ''}</td>
                <td>${device.primary_ip4 ? device.primary_ip4.address : ''}</td>
                <td>${device.location ? device.location.name : ''}</td>
                <td>${device.role ? device.role.name : ''}</td>
            `;
            leftTableBody.appendChild(row);
  }
  // Remove DataTable initialization that might interfere with content display
  renderRightTable();
  // Select-all logic for left table
  const selectAllLeft = document.getElementById('select-all-left');
  if (selectAllLeft) {
    // Remove any existing event listeners to prevent duplicates
    selectAllLeft.removeEventListener('change', selectAllLeftHandler);
    selectAllLeft.checked = false;
    selectAllLeft.addEventListener('change', selectAllLeftHandler);
  }
}

// Separate handler function to avoid duplicates
function selectAllLeftHandler() {
  const selectAllLeft = document.getElementById('select-all-left');
  const checkboxes = leftTableBody.querySelectorAll('.row-checkbox-left');
  checkboxes.forEach(cb => { cb.checked = selectAllLeft.checked; });
}

function renderRightTable() {
  if (!rightTableBody) return;
  rightTableBody.innerHTML = '';
  
  // Calculate pagination for right table
  const start = (currentRightPage - 1) * PAGE_SIZE;
  const end = start + PAGE_SIZE;
  const pageDevices = rightTableDevices.slice(start, end);
  
  if (pageDevices.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="5" style="text-align:center;color:#888;">No devices selected.</td>`;
    rightTableBody.appendChild(row);
    renderRightPagination(); // Still render pagination to maintain layout
    return;
  }
  
  for (const device of pageDevices) {
    const row = document.createElement('tr');
    row.innerHTML = `
                <td><input type="checkbox" data-device-id="${device.id}" class="row-checkbox-right"></td>
                <td>${device.name || ''}</td>
                <td>${device.primary_ip4 ? device.primary_ip4.address : ''}</td>
                <td>${device.location ? device.location.name : ''}</td>
                <td>${device.role ? device.role.name : ''}</td>
            `;
            rightTableBody.appendChild(row);
  }
  
  // Select-all logic for right table
  const selectAllRight = document.getElementById('select-all-right');
  if (selectAllRight) {
    // Remove any existing event listeners to prevent duplicates
    selectAllRight.removeEventListener('change', selectAllRightHandler);
    selectAllRight.checked = false;
    selectAllRight.addEventListener('change', selectAllRightHandler);
  }
  
  // Render pagination for right table
  renderRightPagination();
}

// Separate handler function to avoid duplicates
function selectAllRightHandler() {
  const selectAllRight = document.getElementById('select-all-right');
  const checkboxes = rightTableBody.querySelectorAll('.row-checkbox-right');
  checkboxes.forEach(cb => { cb.checked = selectAllRight.checked; });
}

function renderPagination() {
  let pagination = document.getElementById('left-pagination');
  if (!pagination) {
    // Create pagination container if it doesn't exist
    const paginationContainer = document.querySelector('.left-table-pagination-container .dataTables_wrapper');
    if (paginationContainer) {
      pagination = document.createElement('div');
      pagination.id = 'left-pagination';
      pagination.className = 'dataTables_paginate paging_simple_numbers';
      paginationContainer.appendChild(pagination);
    } else {
      // Fallback: create container structure if it doesn't exist
      const leftTableContainer = document.getElementById('left-table').closest('.table-container');
      if (leftTableContainer) {
        const containerDiv = document.createElement('div');
        containerDiv.className = 'left-table-pagination-container';
        const wrapperDiv = document.createElement('div');
        wrapperDiv.className = 'dataTables_wrapper form-inline dt-bootstrap no-footer';
        pagination = document.createElement('div');
        pagination.id = 'left-pagination';
        pagination.className = 'dataTables_paginate paging_simple_numbers';
        wrapperDiv.appendChild(pagination);
        containerDiv.appendChild(wrapperDiv);
        leftTableContainer.appendChild(containerDiv);
      }
    }
  }
  
  if (!pagination) return; // Safety check
  
  pagination.innerHTML = '';
  
  const totalPages = Math.ceil(devices.length / PAGE_SIZE);
  if (totalPages <= 1) {
    pagination.style.display = 'none';
    return;
  }
  
  pagination.style.display = 'block';
  
  // Create pagination list
  const ul = document.createElement('ul');
  ul.className = 'pagination';
  
  // First button
  const firstLi = document.createElement('li');
  firstLi.className = `paginate_button page-item ${currentPage === 1 ? 'disabled' : ''}`;
  firstLi.innerHTML = `<a href="#" aria-controls="datatable" data-dt-idx="0" tabindex="0" class="page-link">First</a>`;
  if (currentPage > 1) {
    firstLi.onclick = (e) => {
      e.preventDefault();
      currentPage = 1;
      renderTable();
      renderPagination();
    };
  }
  ul.appendChild(firstLi);
  
  // Previous button
  const prevLi = document.createElement('li');
  prevLi.className = `paginate_button page-item previous ${currentPage === 1 ? 'disabled' : ''}`;
  prevLi.innerHTML = `<a href="#" aria-controls="datatable" data-dt-idx="previous" tabindex="0" class="page-link">Previous</a>`;
  if (currentPage > 1) {
    prevLi.onclick = (e) => {
      e.preventDefault();
      currentPage--;
      renderTable();
      renderPagination();
    };
  }
  ul.appendChild(prevLi);
  
  // Page numbers
  const startPage = Math.max(1, currentPage - 2);
  const endPage = Math.min(totalPages, currentPage + 2);
  
  for (let i = startPage; i <= endPage; i++) {
    const li = document.createElement('li');
    li.className = `paginate_button page-item ${i === currentPage ? 'active' : ''}`;
    li.innerHTML = `<a href="#" aria-controls="datatable" data-dt-idx="${i}" tabindex="0" class="page-link">${i}</a>`;
    if (i !== currentPage) {
      li.onclick = (e) => {
        e.preventDefault();
        currentPage = i;
        renderTable();
        renderPagination();
      };
    }
    ul.appendChild(li);
  }
  
  // Next button
  const nextLi = document.createElement('li');
  nextLi.className = `paginate_button page-item next ${currentPage === totalPages ? 'disabled' : ''}`;
  nextLi.innerHTML = `<a href="#" aria-controls="datatable" data-dt-idx="next" tabindex="0" class="page-link">Next</a>`;
  if (currentPage < totalPages) {
    nextLi.onclick = (e) => {
      e.preventDefault();
      currentPage++;
      renderTable();
      renderPagination();
    };
  }
  ul.appendChild(nextLi);
  
  // Last button
  const lastLi = document.createElement('li');
  lastLi.className = `paginate_button page-item ${currentPage === totalPages ? 'disabled' : ''}`;
  lastLi.innerHTML = `<a href="#" aria-controls="datatable" data-dt-idx="${totalPages}" tabindex="0" class="page-link">Last</a>`;
  if (currentPage < totalPages) {
    lastLi.onclick = (e) => {
      e.preventDefault();
      currentPage = totalPages;
      renderTable();
      renderPagination();
    };
  }
  ul.appendChild(lastLi);
  
  pagination.appendChild(ul);
}

// Render pagination for right table
function renderRightPagination() {
  let pagination = document.getElementById('right-pagination');
  if (!pagination) {
    // Create pagination container if it doesn't exist
    const paginationContainer = document.querySelector('.right-table-pagination-container .dataTables_wrapper');
    if (paginationContainer) {
      pagination = document.createElement('div');
      pagination.id = 'right-pagination';
      pagination.className = 'dataTables_paginate paging_simple_numbers';
      paginationContainer.appendChild(pagination);
    } else {
      // Fallback: create container structure if it doesn't exist
      const rightTableContainer = document.getElementById('right-table').closest('.table-container');
      if (rightTableContainer) {
        const containerDiv = document.createElement('div');
        containerDiv.className = 'right-table-pagination-container';
        const wrapperDiv = document.createElement('div');
        wrapperDiv.className = 'dataTables_wrapper form-inline dt-bootstrap no-footer';
        pagination = document.createElement('div');
        pagination.id = 'right-pagination';
        pagination.className = 'dataTables_paginate paging_simple_numbers';
        wrapperDiv.appendChild(pagination);
        containerDiv.appendChild(wrapperDiv);
        rightTableContainer.appendChild(containerDiv);
      }
    }
  }
  
  if (!pagination) return; // Safety check
  
  pagination.innerHTML = '';
  
  const totalPages = Math.ceil(rightTableDevices.length / PAGE_SIZE);
  if (totalPages <= 1) {
    pagination.style.display = 'none';
    return;
  }
  
  pagination.style.display = 'block';
  
  // Create pagination list
  const ul = document.createElement('ul');
  ul.className = 'pagination';
  
  // First button
  const firstLi = document.createElement('li');
  firstLi.className = `paginate_button page-item ${currentRightPage === 1 ? 'disabled' : ''}`;
  firstLi.innerHTML = `<a href="#" aria-controls="right-table" data-dt-idx="0" tabindex="0" class="page-link">First</a>`;
  if (currentRightPage > 1) {
    firstLi.onclick = (e) => {
      e.preventDefault();
      currentRightPage = 1;
      renderRightTable();
    };
  }
  ul.appendChild(firstLi);
  
  // Previous button
  const prevLi = document.createElement('li');
  prevLi.className = `paginate_button page-item previous ${currentRightPage === 1 ? 'disabled' : ''}`;
  prevLi.innerHTML = `<a href="#" aria-controls="right-table" data-dt-idx="previous" tabindex="0" class="page-link">Previous</a>`;
  if (currentRightPage > 1) {
    prevLi.onclick = (e) => {
      e.preventDefault();
      currentRightPage--;
      renderRightTable();
    };
  }
  ul.appendChild(prevLi);
  
  // Page numbers
  const startPage = Math.max(1, currentRightPage - 2);
  const endPage = Math.min(totalPages, currentRightPage + 2);
  
  for (let i = startPage; i <= endPage; i++) {
    const li = document.createElement('li');
    li.className = `paginate_button page-item ${i === currentRightPage ? 'active' : ''}`;
    li.innerHTML = `<a href="#" aria-controls="right-table" data-dt-idx="${i}" tabindex="0" class="page-link">${i}</a>`;
    if (i !== currentRightPage) {
      li.onclick = (e) => {
        e.preventDefault();
        currentRightPage = i;
        renderRightTable();
      };
    }
    ul.appendChild(li);
  }
  
  // Next button
  const nextLi = document.createElement('li');
  nextLi.className = `paginate_button page-item next ${currentRightPage === totalPages ? 'disabled' : ''}`;
  nextLi.innerHTML = `<a href="#" aria-controls="right-table" data-dt-idx="next" tabindex="0" class="page-link">Next</a>`;
  if (currentRightPage < totalPages) {
    nextLi.onclick = (e) => {
      e.preventDefault();
      currentRightPage++;
      renderRightTable();
    };
  }
  ul.appendChild(nextLi);
  
  // Last button
  const lastLi = document.createElement('li');
  lastLi.className = `paginate_button page-item ${currentRightPage === totalPages ? 'disabled' : ''}`;
  lastLi.innerHTML = `<a href="#" aria-controls="right-table" data-dt-idx="${totalPages}" tabindex="0" class="page-link">Last</a>`;
  if (currentRightPage < totalPages) {
    lastLi.onclick = (e) => {
      e.preventDefault();
      currentRightPage = totalPages;
      renderRightTable();
    };
  }
  ul.appendChild(lastLi);
  
  pagination.appendChild(ul);
}

// Fetch statuses from backend and populate the status dropdown
async function fetchAndPopulateStatuses() {
  const statusSelect = document.getElementById('sync-status');
  if (!statusSelect) return;
  try {
    const data = await window.authManager.apiRequest('/api/nautobot/statuses/device');
    if (!data || !Array.isArray(data)) throw new Error('No statuses returned');
    statusSelect.innerHTML = '<option value="">Select status</option>';
    let activeId = null;
    for (const status of data) {
      const opt = document.createElement('option');
      opt.value = status.id;
      opt.textContent = status.name;
      if (status.name.toLowerCase() === 'active') activeId = status.id;
      statusSelect.appendChild(opt);
    }
    // Set default to Active if present
    if (activeId) statusSelect.value = activeId;
  } catch (e) {
    console.error('Failed to fetch device statuses:', e);
    statusSelect.innerHTML = '<option value="">Failed to load statuses</option>';
  }
}

// Fetch namespaces from backend and populate the namespace dropdown
async function fetchAndPopulateNamespaces() {
  const nsSelect = document.getElementById('sync-namespace');
  if (!nsSelect) return;
  try {
    const data = await window.authManager.apiRequest('/api/nautobot/namespaces');
    if (!data || !Array.isArray(data)) throw new Error('No namespaces returned');
    nsSelect.innerHTML = '<option value="">Select namespace</option>';
    let globalId = null;
    for (const ns of data) {
      const opt = document.createElement('option');
      opt.value = ns.id;
      opt.textContent = ns.name;
      if (ns.name.toLowerCase() === 'global') globalId = ns.id;
      nsSelect.appendChild(opt);
    }
    // Set default to Global if present
    if (globalId) nsSelect.value = globalId;
  } catch (e) {
    console.error('Failed to fetch namespaces:', e);
    nsSelect.innerHTML = '<option value="">Failed to load namespaces</option>';
  }
}

window.addEventListener('DOMContentLoaded', () => {
  console.log('[DEBUG] DOMContentLoaded event fired');
  
  // Initialize DOM elements first
  initializeDOMElements();
  
  // Do NOT fetch devices initially. Show empty tables.
  renderTable();
  renderRightTable();
  renderPagination();
  fetchAndPopulateStatuses();
  fetchAndPopulateNamespaces();
  // Set default checked for sync checkboxes
  const syncCheckboxIds = [
    'sync-cables',
    'sync-software-version',
    'sync-vlans',
    'sync-vrfs'
  ];
  for (const id of syncCheckboxIds) {
    const cb = document.getElementById(id);
    if (cb) cb.checked = true;
  }
  // Filter logic
  const filterType = document.getElementById('filter-type');
  const filterValue = document.getElementById('filter-value');
  // Add a message element for regex errors
  let regexMsg = document.getElementById('regex-msg');
  if (!regexMsg) {
    regexMsg = document.createElement('div');
    regexMsg.id = 'regex-msg';
    regexMsg.style.color = 'red';
    regexMsg.style.fontSize = '0.9em';
    regexMsg.style.marginTop = '2px';
    filterValue.parentElement.appendChild(regexMsg);
  }
  function isValidRegex(pattern) {
    try {
      new RegExp(pattern);
      return true;
    } catch (e) {
      return false;
    }
  }
  function isValidCIDR(str) {
    // Simple CIDR validation: n.n.n.n/x
    const cidrRegex = /^(\d{1,3}\.){3}\d{1,3}\/\d{1,2}$/;
    if (!cidrRegex.test(str)) return false;
    const [ip, mask] = str.split('/');
    const parts = ip.split('.').map(Number);
    if (parts.length !== 4 || parts.some(n => n < 0 || n > 255)) return false;
    const m = Number(mask);
    return m >= 0 && m <= 32;
  }
  function handleFilter() {
    console.log('[DEBUG] handleFilter called with:', {
      filterType: filterType.value,
      filterValue: filterValue.value,
      filterValueLength: filterValue.value.length
    });
    
    regexMsg.textContent = '';
    if (filterType.value === 'name' && filterValue.value.length >= 3) {
      if (!isValidRegex(filterValue.value)) {
        regexMsg.textContent = 'Invalid regular expression';
        devices = [];
        renderTable();
        renderPagination();
        return;
      }
      console.log('[DEBUG] Calling fetchDevices for name filter');
      fetchDevices('name', filterValue.value);
    } else if (filterType.value === 'location' && filterValue.value.length >= 3) {
      console.log('[DEBUG] Calling fetchDevices for location filter');
      fetchDevices('location', filterValue.value);
    } else if (filterType.value === 'prefix' && filterValue.value.length > 0) {
      if (!isValidCIDR(filterValue.value)) {
        regexMsg.textContent = 'Invalid IPv4 prefix (CIDR notation required, e.g. 192.168.1.0/24)';
        devices = [];
        renderTable();
        renderPagination();
        return;
      } else {
        regexMsg.textContent = '';
        // Only send request on Enter, not on every input
      }
    } else if ((filterType.value === 'name' || filterType.value === 'location') && filterValue.value.length < 3) {
      devices = [];
      renderTable();
      renderPagination();
    } else if (filterType.value === 'prefix' && filterValue.value.length === 0) {
      devices = [];
      renderTable();
      renderPagination();
    }
  }
  if (filterType && filterValue) {
    filterType.addEventListener('change', handleFilter);
    filterValue.addEventListener('input', handleFilter);
    filterValue.addEventListener('keydown', function(e) {
      if (filterType.value === 'prefix' && e.key === 'Enter' && isValidCIDR(filterValue.value)) {
        fetchDevices('prefix', filterValue.value);
      }
    });
  }
});

// Ensure tables have the same height by applying a CSS class
document.addEventListener('DOMContentLoaded', () => {
  const leftTable = document.getElementById('left-table');
  const rightTable = document.getElementById('right-table');
  if (leftTable && rightTable) {
    leftTable.classList.add('sync-table');
    rightTable.classList.add('sync-table');
  }
});
document.getElementById('sync-network-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  const status = document.getElementById('sync-status').value;
  const namespace = document.getElementById('sync-namespace').value;
  const syncCables = document.getElementById('sync-cables').checked;
  const syncSoftware = document.getElementById('sync-software-version').checked;
  const syncVlans = document.getElementById('sync-vlans').checked;
  const syncVrfs = document.getElementById('sync-vrfs').checked;
  // Collect selected device IDs from right table (Nautobot needs UUIDs, not names)
  const rightTableBody = document.getElementById('right-table-body');
  const deviceIds = [];
  
  // Get device IDs from the right table rows
  Array.from(rightTableBody.querySelectorAll('tr')).forEach(row => {
    const checkbox = row.querySelector('input[type="checkbox"]');
    if (checkbox && checkbox.getAttribute('data-device-id')) {
      deviceIds.push(checkbox.getAttribute('data-device-id'));
    }
  });
  
  if (deviceIds.length === 0) {
    alert('Please select at least one device to sync.');
    return;
  }
  
  console.log('[DEBUG] Device IDs to sync:', deviceIds);
  
  const data = {
    devices: deviceIds, // Send device UUIDs, not names
    default_prefix_status: status,
    interface_status: status,
    ip_address_status: status,
    namespace: namespace,
    sync_cables: syncCables,
    sync_software_version: syncSoftware,
    sync_vlans: syncVlans,
    sync_vrfs: syncVrfs
  };
  try {
    console.log('[DEBUG] Sending sync request with data:', { data });
    const result = await window.authManager.apiRequest('/api/nautobot/sync-network-data', {
      method: 'POST',
      body: JSON.stringify({ data })
    });
    console.log('[DEBUG] Sync request result:', result);
    
    if (result.success) {
      alert(`Sync request sent successfully! Job ID: ${result.job_id}`);
    } else {
      alert('Sync request failed: ' + (result.message || 'Unknown error'));
    }
  } catch (err) {
    console.error('[ERROR] Sync request failed:', err);
    alert('Sync failed: ' + err.message);
  }
});
