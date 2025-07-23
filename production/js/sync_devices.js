import { CONFIG } from '../../src/config.js';

const BACKEND_API = `${CONFIG.API.BASE_URL}${CONFIG.API.ENDPOINTS.DEVICES}`;
const PAGE_SIZE = CONFIG.UI.PAGE_SIZE;
let currentPage = 1;
let devices = [];
let rightTableDevices = [];

const leftTableBody = document.getElementById('left-table-body');
const rightTableBody = document.getElementById('right-table-body');
const toRightBtn = document.getElementById('to-right');
const toLeftBtn = document.getElementById('to-left');

async function fetchDevices(filterType = null, filterValue = null) {
  try {
    let url = BACKEND_API;
    if (filterType === 'name' && filterValue && filterValue.length >= 3) {
      url = BACKEND_API + '?filter_type=name&filter_value=' + encodeURIComponent(filterValue);
    } else if (filterType === 'location' && filterValue && filterValue.length >= 3) {
      url = BACKEND_API + '?filter_type=location&filter_value=' + encodeURIComponent(filterValue);
    } else if (filterType === 'prefix' && filterValue && filterValue.length > 0) {
      url = BACKEND_API + '?filter_type=prefix&filter_value=' + encodeURIComponent(filterValue);
    }
    
    // Use authenticated API request
    const data = await window.authManager.apiRequest(url.replace('http://localhost:8000/api', ''));
    console.log('[DEBUG] Received data from backend:', data);
    
    if (!data.devices) {
      showError('No device data returned from backend.');
      devices = [];
    } else {
      devices = data.devices;
      console.log('[DEBUG] Devices array:', devices);
    }
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
    selectAllLeft.checked = false;
    selectAllLeft.addEventListener('change', function() {
      const checkboxes = leftTableBody.querySelectorAll('.row-checkbox-left');
      checkboxes.forEach(cb => { cb.checked = selectAllLeft.checked; });
    });
  }
}

function renderRightTable() {
  if (!rightTableBody) return;
  rightTableBody.innerHTML = '';
  const pageDevices = rightTableDevices.slice(0, PAGE_SIZE);
  if (pageDevices.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = `<td colspan="5" style="text-align:center;color:#888;">No devices selected.</td>`;
    rightTableBody.appendChild(row);
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
  // Remove DataTable initialization that might interfere with content display
  // Select-all logic for right table
  const selectAllRight = document.getElementById('select-all-right');
  if (selectAllRight) {
    selectAllRight.checked = false;
    selectAllRight.addEventListener('change', function() {
      const checkboxes = rightTableBody.querySelectorAll('.row-checkbox-right');
      checkboxes.forEach(cb => { cb.checked = selectAllRight.checked; });
    });
  }
}
if (toRightBtn) {
  toRightBtn.addEventListener('click', () => {
    // Get all checked checkboxes in the left table
    const checked = leftTableBody.querySelectorAll('input[type="checkbox"]:checked');
    const selectedIds = Array.from(checked).map(cb => cb.getAttribute('data-device-id'));
    // Find device objects by id
    const selectedDevices = devices.filter(d => selectedIds.includes(d.id));
    // Add to right table if not already present
    for (const dev of selectedDevices) {
      if (!rightTableDevices.find(d => d.id === dev.id)) {
        rightTableDevices.push(dev);
      }
    }
    renderTable();
  });
}

if (toLeftBtn) {
  toLeftBtn.addEventListener('click', () => {
    // Get all checked checkboxes in the right table
    const checked = rightTableBody.querySelectorAll('input[type="checkbox"]:checked');
    const selectedIds = Array.from(checked).map(cb => cb.getAttribute('data-device-id'));
    // Remove selected devices from rightTableDevices
    rightTableDevices = rightTableDevices.filter(d => !selectedIds.includes(d.id));
    renderTable();
  });
}

function renderPagination() {
  let pagination = document.getElementById('left-pagination');
  if (!pagination) {
    // Create pagination container if it doesn't exist
    pagination = document.createElement('div');
    pagination.id = 'left-pagination';
    pagination.className = 'dataTables_paginate paging_simple_numbers';
    leftTableBody.parentElement.parentElement.appendChild(pagination);
  }
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

// Fetch statuses from backend and populate the status dropdown
async function fetchAndPopulateStatuses() {
  const statusSelect = document.getElementById('sync-status');
  if (!statusSelect) return;
  try {
    const data = await window.authManager.apiRequest('/statuses');
    if (!data.statuses) throw new Error('No statuses returned');
    statusSelect.innerHTML = '<option value="">Select status</option>';
    let activeId = null;
    for (const status of data.statuses) {
      const opt = document.createElement('option');
      opt.value = status.id;
      opt.textContent = status.name;
      if (status.name.toLowerCase() === 'active') activeId = status.id;
      statusSelect.appendChild(opt);
    }
    // Set default to Active if present
    if (activeId) statusSelect.value = activeId;
  } catch (e) {
    statusSelect.innerHTML = '<option value="">Failed to load statuses</option>';
  }
}

// Fetch namespaces from backend and populate the namespace dropdown
async function fetchAndPopulateNamespaces() {
  const nsSelect = document.getElementById('sync-namespace');
  if (!nsSelect) return;
  try {
    const data = await window.authManager.apiRequest('/namespaces');
    if (!data.namespaces) throw new Error('No namespaces returned');
    nsSelect.innerHTML = '<option value="">Select namespace</option>';
    let globalId = null;
    for (const ns of data.namespaces) {
      const opt = document.createElement('option');
      opt.value = ns.id;
      opt.textContent = ns.name;
      if (ns.name.toLowerCase() === 'global') globalId = ns.id;
      nsSelect.appendChild(opt);
    }
    // Set default to Global if present
    if (globalId) nsSelect.value = globalId;
  } catch (e) {
    nsSelect.innerHTML = '<option value="">Failed to load namespaces</option>';
  }
}

window.addEventListener('DOMContentLoaded', () => {
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
    regexMsg.textContent = '';
    if (filterType.value === 'name' && filterValue.value.length >= 3) {
      if (!isValidRegex(filterValue.value)) {
        regexMsg.textContent = 'Invalid regular expression';
        devices = [];
        renderTable();
        renderPagination();
        return;
      }
      fetchDevices('name', filterValue.value);
    } else if (filterType.value === 'location' && filterValue.value.length >= 3) {
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
  // Collect selected device IDs from right table
  const rightTableBody = document.getElementById('right-table-body');
  const deviceIds = Array.from(rightTableBody.querySelectorAll('tr')).map(row => {
    const cb = row.querySelector('input[type="checkbox"]');
    return cb ? cb.getAttribute('data-device-id') : null;
  }).filter(Boolean);
  if (deviceIds.length === 0) {
    alert('Please select at least one device to sync.');
    return;
  }
  const data = {
    devices: deviceIds,
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
    const result = await window.authManager.apiRequest('/sync-network-data', {
      method: 'POST',
      body: JSON.stringify({ data })
    });
    alert('Sync request sent successfully!');
  } catch (err) {
    alert('Sync failed: ' + err.message);
  }
});
