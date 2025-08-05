# devices by name

    query devices_by_name($name_filter: [String]) {
        devices(name__ire: $name_filter) {
            id
            name
            primary_ip4 {
            address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }

# devices by location

    query devices_by_location ($location_filter: [String]) {
        locations (name__re: $location_filter) {
            name
            devices {
                id
                name
                role {
                    name
                }
                location {
                    name
                }
                primary_ip4 {
                    address
                }
                status {
                    name
                }
            }
        }
    }

# devices by role

    query devices_by_role($role_filter: [String]) {
        devices(role: $role_filter) {
            id
            name
            primary_ip4 {
                address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }
# devices by tag

    query devices_by_tag($tag_filter: [String]) {
        devices(tags: $tag_filter) {
            id
            name
            primary_ip4 {
                address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }

# devices by device_type

    query devices_by_devicetype($devicetype_filter: [String]) {
        devices(device_type: $devicetype_filter) {
            id
            name
            primary_ip4 {
                address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }
# devices by manufacturer

    query devices_by_manufacturer($manufacturer_filter: [String]) {
        devices(manufacturer: $manufacturer_filter) {
            id
            name
            primary_ip4 {
                address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }

# devices by platform

    query devices_by_platform($platform_filter: [String]) {
        devices(platform: $platform_filter) {
            id
            name
            primary_ip4 {
                address
            }
            status {
                name
            }
            device_type {
                model
            }
        }
    }