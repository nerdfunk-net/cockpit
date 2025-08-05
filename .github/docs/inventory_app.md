# What the Application does

* The app provides a user interface for constructing an Ansible inventory.
* Users can add hosts, groups, and variables using logical operations (AND, OR, NOT, etc.).
* The interface allows users to define rules and conditions for including hosts in groups or assigning variables.
* When the user clicks the "Result" button, the app processes all logical operations and rules to generate the final Ansible inventory in YAML or INI format.
* The generated inventory is displayed to the user and can be downloaded.
* The app should validate user input and provide error messages for invalid logic or missing required fields.
* The app should be modular, allowing easy extension for new logical operations or inventory features.

# The Application looks like

* At the top of the application, there are input fields and controls where the user can build logical operations for the Ansible inventory. These include dropdowns, text fields, and buttons to add hosts, groups, variables, and logical operators (AND, OR, NOT, etc.). Users can chain multiple conditions and rules visually.

* Below the input section, there is a dynamic table that executes the defined logical operation. This table displays the resulting inventory structure, showing which hosts belong to which groups, assigned variables, and any computed results. The table updates in real time as the user modifies the logical operations.

* At the bottom, there is a "Result" button. When clicked, the app processes all inputs and displays the final Ansible inventory in YAML or INI format, with options to download or copy the result. Error messages and validation feedback are shown inline if needed.