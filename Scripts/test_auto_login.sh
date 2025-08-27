#!/bin/bash
# Test script to validate auto-login configuration
# This script can be run on a HoloBox to check if auto-login is properly configured

echo "HoloBox Auto-Login Configuration Test"
echo "====================================="

# Check if pi user exists
if id pi >/dev/null 2>&1; then
    echo "✓ Pi user exists"
    echo "  User info: $(getent passwd pi)"
else
    echo "✗ Pi user does not exist"
    exit 1
fi

# Check if pi user is in sudo group
if groups pi | grep -q sudo; then
    echo "✓ Pi user has sudo privileges"
else
    echo "✗ Pi user does not have sudo privileges"
fi

# Check auto-login configuration
if [ -f /etc/systemd/system/getty@tty1.service.d/autologin.conf ]; then
    echo "✓ Auto-login configuration file exists"
    echo "  Content:"
    cat /etc/systemd/system/getty@tty1.service.d/autologin.conf | sed 's/^/    /'
else
    echo "✗ Auto-login configuration file not found"
fi

# Check if userconfig service is disabled
if ! systemctl is-enabled userconfig.service >/dev/null 2>&1; then
    echo "✓ Userconfig service is disabled"
else
    echo "✗ Userconfig service is still enabled"
fi

# Check if first-boot setup script exists
if [ -f /opt/holobox/setup-user-first-boot.sh ]; then
    echo "✓ First-boot user setup script exists"
    if [ -x /opt/holobox/setup-user-first-boot.sh ]; then
        echo "✓ First-boot user setup script is executable"
    else
        echo "✗ First-boot user setup script is not executable"
    fi
else
    echo "✗ First-boot user setup script not found"
fi

# Check if first-boot setup service exists and is configured
if [ -f /etc/systemd/system/holobox-user-setup.service ]; then
    echo "✓ First-boot user setup service exists"
    if systemctl is-enabled holobox-user-setup.service >/dev/null 2>&1; then
        echo "✓ First-boot user setup service is enabled"
    else
        echo "ℹ First-boot user setup service is disabled (expected after first run)"
    fi
else
    echo "✗ First-boot user setup service not found"
fi

# Check if first-boot setup has completed
if [ -f /opt/holobox/.user-setup-complete ]; then
    echo "✓ First-boot user setup has completed"
    echo "  Completion time: $(stat -c %y /opt/holobox/.user-setup-complete)"
else
    echo "ℹ First-boot user setup has not run yet (expected on fresh image)"
fi

# Check for setup logs
if [ -f /var/log/holobox-user-setup.log ]; then
    echo "✓ User setup log exists"
    echo "  Log size: $(wc -l < /var/log/holobox-user-setup.log) lines"
    echo "  Last 5 lines:"
    tail -5 /var/log/holobox-user-setup.log | sed 's/^/    /'
else
    echo "ℹ User setup log not found (expected if setup hasn't run)"
fi

echo ""
echo "Test completed. A properly configured HoloBox should:"
echo "- Have pi user with sudo privileges"
echo "- Have auto-login configured for tty1"
echo "- Have userconfig service disabled"
echo "- Complete first-boot setup on initial start"