# General Instructions

## Technology Stack

This App should be integrated into the existing Cockpit application.

## File reference

Look in .github/docs/nautobot_graphql_queries.md to get all the queries you need for the backend.

## Navigation integration

Integrate this App into the existing Cockpit navigation system. The agent can see in the repository.

This app the is Inventory App. The Menu of this App is called "Ansible", the submenu is called "Inventory". the navigation bar at the left side must be modified so that the app is reachable using the link "Ansible/Inventory"

## Nautobot Integration

Use the existing Nautobot integration. There is a python based backend that contains some but not all graphql calls to nautobot. Add the missing graphql queries to the backend. 

## UI Framework

Follow the existing Cockpit UI patterns that you find.

## Authentication

Use the existing Cockpit authentication system.

## File Structure

1. The frontend should be placed in the production directory and named "ansible-inventory.html". The backend exists at ./backend and must be expanded. The backend has a model directory as well as a routers directory.

# What the Application does

* The app provides a user interface for constructing an Ansible inventory.
* Users can add hosts, groups, and variables using logical operations (AND, OR, NOT, etc.).
* Users can use the following data from nautobot as input fields for the logical operations: name, location, role, tag, device_type, manufacturer, platform
* The interface allows users to define rules and conditions for including hosts in groups or assigning variables.
* When the user clicks the "Result" button, the app processes all logical operations and rules to generate the final Ansible inventory in YAML or INI format.
* The generated inventory is displayed to the user and can be downloaded.
* The app should validate user input and provide error messages for invalid logic or missing required fields.
* The app should be modular, allowing easy extension for new logical operations or inventory features.

# How to get the list of devices as result

GraphQL does not provide a built-in mechanism for combining logical operations (AND, OR, NOT) within a single query. Therefore, the app MUST use a separate GraphQL query for each logical operation defined by the user.

For example, if the user wants to retrieve devices from a location named "lab", the app must use the query `devices_by_name` as specified in the file `nautobot_graphql_queries.md`. Each logical condition (such as filtering by location, role, or tag) requires its own query, and the app should combine the results according to the user's logical rules.

This approach ensures that every logical operation is executed as an individual query, and the app processes and merges the results to build the final device list for the Ansible inventory.

To implement an "AND NOT" logical operation, the app must:
- Execute a GraphQL query to retrieve all devices that match the logical operation specified by the user.
- Remove (subtract) these devices from the current result set, effectively excluding them from the final device list.

For example, if the user wants all devices in location "lab" AND NOT with role "router", the app should:
1. Query for devices in location "lab".
2. Query for devices with role "router".
3. Remove all devices with role "router" from the set of devices in location "lab".

This ensures that the result set contains only devices that satisfy the AND condition and do not match the NOT condition.

To implement logical operations:

**AND Operation:**
- For each condition in the AND chain, execute a separate GraphQL query to retrieve the matching devices.
- The app must compute the intersection of all device result sets, so only devices present in every set are included in the final result.
- Devices should be uniquely identified (e.g., by device name or ID) to ensure correct intersection.

**OR Operation:**
- For each condition in the OR chain, execute a separate GraphQL query to retrieve the matching devices.
- The app must compute the union of all device result sets, combining all devices and removing duplicates.
- Devices should be uniquely identified to avoid duplicate entries in the final result.

**Complex/Nested Logical Operations:**
- The app must parse and evaluate complex logical expressions (e.g., (A AND B) OR (C AND NOT D)) using a tree or stack-based approach.
- Each leaf node (condition) triggers a GraphQL query, and the app combines results according to the logical structure (using intersection, union, and subtraction as described above).

**Device Identification:**
- Devices must be uniquely identified (by name, ID, or another unique field) when performing set operations (intersection, union, subtraction).

**Query Mapping:**
- The app must map each user-selected field and logical operation to the correct GraphQL query as defined in `nautobot_graphql_queries.md`.
- For example, filtering by location uses the `devices_by_location` query, filtering by role uses the `devices_by_role` query, etc.
- The app should be able to dynamically select and execute the appropriate query for each condition.

**Error Handling:**
- If a query returns no results or a logical operation results in an empty set, the app should display a clear error or warning to the user.
- The app must validate all logical expressions before execution and provide feedback for invalid or incomplete logic.

# The Application looks like

* At the top of the application, there are input fields and controls where the user can build logical operations for the Ansible inventory. These include dropdowns, text fields, and buttons to add hosts, groups, variables, and logical operators (AND, OR, NOT, etc.). Users can chain multiple conditions and rules visually.

* Below the input section, there is a dynamic table that executes the defined logical operation. This table displays the resulting inventory structure, showing which hosts belong to which groups, assigned variables, and any computed results. The table updates in real time as the user modifies the logical operations.

* At the bottom, there is a "Result" button. When clicked, the app processes all inputs and displays the final Ansible inventory in YAML or INI format, with options to download or copy the result. Error messages and validation feedback are shown inline if needed.

# Ansible Inventory Format

This app has the ability to use jinja2 templates (Settings / templates). To build the final inventory this app must ask the user for the template name and the category (name and category are part of each template). To build the inventory do this:
    
    1. Build a dict "all_devices" that includes the final result that is shown in the table. all_devices must incude the following data: 
        * name
        * uuid of the device
        * location
        * role
        * all tags
        * device_type
        * manufacturer
        * platform
    2. Render the jinja2 template using this dict and show it the user. 
    3. Add a Download Inventory Button to the output. If the user clicks this button the inventory is downloaded named inventory.yaml

# Real-time Table Update

The result should only be updated if the user clicks the "Preview" Button.
