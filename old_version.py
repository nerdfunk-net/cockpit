
@app.route("/onboard", methods=["GET", "POST"])
@login_required
def onboard_device():
    """Handle device onboarding - IP validation and device setup."""
    # Check if we're coming from an IP check or if IP is already in session
    ip_address = session.get('onboard_ip')
    
    if request.method == "POST":
        # Check if this is an IP validation request
        if 'ip_address' in request.form:
            ip_address = request.form.get("ip_address", "").strip()
            
            if not ip_address:
                flash("Please enter an IP address.", "error")
                return redirect(url_for("onboard_device"))
            
            if not validate_ip_address(ip_address):
                flash("Invalid IP address format.", "error")
                return redirect(url_for("onboard_device"))
            
            try:
                result = check_ip_address_in_nautobot(ip_address)
                
                if result['exists']:
                    device = result['device']
                    if device:
                        flash(f"✅ IP address '{ip_address}' found in Nautobot and assigned to device: {device['name']}", "success")
                        return redirect(url_for("onboard_device"))
                    else:
                        flash(f"✅ IP address '{ip_address}' found in Nautobot but not assigned to any device.", "warning")
                        return redirect(url_for("onboard_device"))
                else:
                    # Store IP address in session for the onboarding form
                    session['onboard_ip'] = ip_address
                    flash(f"IP address '{ip_address}' not found in Nautobot. Please configure the device details below.", "info")
                    return redirect(url_for("onboard_device"))
                    
            except Exception as e:
                logger.error(f"Error checking IP address: {e}")
                flash(f"Error checking IP address: {str(e)}", "error")
                return redirect(url_for("onboard_device"))
        
        # Handle device onboarding form submission
        else:
            ip_address = session.get('onboard_ip')
            if not ip_address:
                flash("No IP address to onboard. Please check an IP address first.", "error")
                return redirect(url_for("onboard_device"))
            
            # Get form data (all IDs now)
            location = request.form.get("location", "").strip()
            secret_groups = request.form.get("secret_groups", "").strip()
            role = request.form.get("role", "").strip()
            namespace = request.form.get("namespace", "").strip()
            status = request.form.get("status", "").strip()
            platform = request.form.get("platform", "").strip()
            
            # Validate required fields
            required_fields = {
                'location': location,
                'secret_groups': secret_groups,
                'role': role,
                'namespace': namespace,
                'status': status,
                'platform': platform
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                flash(f"Please fill in all required fields: {', '.join(missing_fields)}", "error")
                return redirect(url_for("onboard_device"))
            
            try:
                result = add_device_to_nautobot(
                    ip_address=ip_address,
                    location_id=location,
                    secret_groups_id=secret_groups,
                    role_id=role,
                    namespace_id=namespace,
                    status_id=status,
                    platform_id=platform
                )
                
                if result['success']:
                    flash(f"✅ Device onboarding initiated successfully!", "success")
                    flash(f"Job ID: {result['job_id']} - {result['message']}", "info")
                    # Clear the IP from session
                    session.pop('onboard_ip', None)
                    return redirect(url_for("onboard_device"))
                else:
                    flash(f"❌ Failed to onboard device: {result['error']}", "error")
                    return redirect(url_for("onboard_device"))
                    
            except Exception as e:
                logger.error(f"Error during device onboarding: {e}")
                flash(f"Error during device onboarding: {str(e)}", "error")
                return redirect(url_for("onboard_device"))
    
    # GET request - show the onboarding page
    # Fetch all data for dropdowns
    try:
        locations = get_nautobot_locations()
        namespaces = get_nautobot_namespaces()
        roles = get_nautobot_roles()
        platforms = get_nautobot_platforms()
        statuses = get_nautobot_statuses()
        secrets_groups = get_nautobot_secrets_groups()
    except Exception as e:
        logger.error(f"Error fetching data from Nautobot: {e}")
        flash(f"Error fetching data from Nautobot: {str(e)}", "error")
        locations = []
        namespaces = []
        roles = []
        platforms = []
        statuses = []
        secrets_groups = []
    
    return render_template("onboard_device.html", 
                         ip_address=ip_address, 
                         locations=locations,
                         namespaces=namespaces,
                         roles=roles,
                         platforms=platforms,
                         statuses=statuses,
                         secrets_groups=secrets_groups)

