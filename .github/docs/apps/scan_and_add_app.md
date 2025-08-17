# Scan and Add App Wizard – Implementation Instructions

## Overview

This app is a two-step wizard for discovering devices on local networks, authenticating with them, and either onboarding them via Nautobot or adding them to an inventory file. It leverages the existing Credentials Settings app for credential selection.

---

## Wizard Step 1: Settings

### UI Requirements

1. - Add the Menu "Scan & Add" to the menu Onboarding.
   - The Navigation Bar MUST be adjusted so that ALL apps use the same navigation bar.
2. **Network Input**
   - Allow user to enter one or more networks in CIDR format (e.g., `192.168.1.0/24`).
   - Support adding/removing multiple network entries.
3. **Credential Selection**
   - Allow user to select one or more credentials from the existing Credentials Settings app.
   - Display credential names for selection (multi-select dropdown or list).
4. **Scan Network Button**
   - Add a button labeled **Scan Network**.
   - On click, send the entered networks and selected credentials to the backend for scanning.
   - The backend should:
     - Scan all provided networks for alive hosts.
     - Attempt to log in to each alive host using the selected credentials.
     - For each successful login, collect the IP address and the credential used.
     - The backend MUST use the library napalm for device login and detection.
     - The backend must try to identify the type of device. It is either a network device (cisco) or a linux server.
   - After scan completes, proceed to Step 2 and display the results.

---

## Wizard Step 2: Summary

### UI Requirements

1. \*\*Menu
   - The filename of the app is scan-and-add.py, scan-and-add.html and so on
   - Desired Menu Label: Scan & Add
2. **Results Table**
   - Display a table listing all discovered IP addresses and the credentials that worked for each.
   - The first column must be a checkbox for each row (to select devices for onboarding).
3. **Onboard Button**
   - Add a button labeled **Onboard** below the table.
   - When clicked, send the selected devices (IP + credential) to the backend for onboarding.
   - The backend should onboard each selected device via the Nautobot onboard app.
4. Use Bootstrap as UI/UX Library.

---

## Backend Requirements

- Provide endpoints for:
  - Scanning networks with provided credentials (returns list of alive/logged-in devices).
  - Onboarding selected devices (accepts list of IPs and credentials, calls Nautobot onboard or adds to inventory file).
- Use the credentials from the Credentials Settings app (do not store plaintext passwords in the frontend).

## Network Scan Behaviour

- ICMP Ping is used to check if a device is alive
- Overlapping / duplicate CIDRs should be de-duplicated automatically
- The Max Network Size of a CIDR is /22

## Concurrency & Performance

- Limit the number of hosts probe to 10
- Implement separate timeouts: ping_timeout=1500ms, login_timeout=5s
- An abort Mechanism is not needed

## Credential Trial Logic

- Credentials are used in the provided order
- If a credentials work stop on first and use this credential

## Device Type Detection

- First use ios then nxos and then iosxr
- Use paramiko to check if the device is a linux server and run uname
- A device is a linux server if a login was successfull the app sees a prompt and uname was executed successfully.

## Napalm Usage

- Use the napalm driver ios, nxos_ssh and iosxr
- Failures should not fallback
- Add python dependencies

## Result Data Model

- Fields per discovered device: {ip, credential_id, device_type, hostname, platform}
- For linux map: hostname=uname -n, platform=linux
- Do not include unreachable devices

## Step Transition UX

- While scan runs: Switch to Step 2 with streaming updates
- Single blocking request is acceptable; Do a Simple blocking + periodic frontend polling

## Long-Running Job Handling

- It is not necessary to do a polling.

## Onboarding Action

- Add a table with the following columns: Hostname, IP-Address, Platform, Location, Namespace, Role, Status, Interface Status, IP Status
- The values are all editable cells with dropdowns (see the onboarding app and use this dropdown)
- The location should be editable. Look att the onboarding app. THere is a nice looking filter mechanism.

### Cisco

- Set default values "Active" for Status, Interface Status, IP Status
- Set default value "Global" for Namespace
- Set default value "network" for role

### Linux

- Add a table with the following columns: Location, Role, Status
- Set default values "Active" for Status
- Set default value "server" for role

### Onboarding

- To onboard a cisco device use the the api /api/nautobot/devices/onboard of the backend to onboard a device. Run it asynchronously with a job ID
- To onboard a Linux server add the server to an inventory.yaml

## Inventory File Option

- To add a host to the inventory use a template that the user has specified in the "Settings Templates" App. All the linux hosts are added to a python dictionary named "all_devices". Use this dict to render the specified template.
- Inventory file path: ./data/inventory/inventory\_{jobid}.yaml (create folder if missing)

## Validation & Error Messaging

- Reject invalid CIDR early (client-side)
- Limit count of networks to 10

## Security

- Credential decryption strictly backend (already).
- No rate limiting or audit logging needed
- Send store scan results to frontend only

## Retry Logic

- Retry failed connection attempts: 3 for each device

## Device Uniqueness

- If same IP appears via multiple networks (overlap), ensure only one entry

## Sorting & Filtering in Summary

- Client-side search/filter are needed? Sorting by IP should be implemented.

## UX Polishing

- Show counts: total hosts scanned, alive, authenticated.
- Show progress bar. The progress bar should be determinate (percent complete) based on total candidate IP count

## Failure Classification

- Distinguish “host unreachable” vs “auth failed” vs “driver not supported”
- Add a counter for failures (auth failed / unreachable) and display it. Include summary counts.

## Error Codes (API)

- Standardize: 400 (bad input), 422 (validation), 504 (scan timeout)

## Rate of Napalm Driver Attempts

- For each IP use a prioritized list: ios -> nxos -> iosxr -> linux until success or failure.

## Logging

- Logging must not be stored but printed to the console

## Cleanup

- Job/result expiration policy: Discard after 24 hours.

## Frontend Tech Constraints

- Reuse existing AuthManager + relative /api calls

## File Naming / Routing

- Proposed new HTML: production/scan-and-add.html

---

## Notes

- The wizard should be user-friendly and robust against invalid input.
- All network and credential operations must be secure; never expose passwords to the frontend.
- The app should be accessible from the main navigation.

---

## Deliverables

- Frontend: Two-page wizard UI as described above.
- Backend: Endpoints for scanning and onboarding as described above.
- Integration: Use existing credentials infrastructure for secure authentication.
