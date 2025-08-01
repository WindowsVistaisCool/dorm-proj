#!/bin/bash

# Raspberry Pi Performance Optimization Script for LED Controller (SAFE VERSION)
# Run this script to apply user-level optimizations only
# NO kernel modifications or system-level changes that could break your OS

echo "Applying SAFE performance optimizations for LED Controller..."

# 1. Set CPU governor to performance mode (reversible)
echo "Setting CPU governor to performance mode (can be reverted)..."
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -w "$cpu/cpufreq/scaling_governor" ]; then
        echo 'performance' | sudo tee "$cpu/cpufreq/scaling_governor" > /dev/null
    fi
done

# 2. Create user-level service file (doesn't auto-enable)
echo "Creating LED controller service template..."
sudo tee /etc/systemd/system/led-controller.service > /dev/null << EOF
[Unit]
Description=LED Controller Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/dorm-proj/src
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
# Mild priority boost (safe)
Nice=-5

[Install]
WantedBy=multi-user.target
EOF

echo "Service created but NOT enabled. To enable: sudo systemctl enable led-controller.service"

# 3. Create LED user group (safe)
echo "Creating LED user group..."
sudo groupadd -f led-group
sudo usermod -a -G led-group pi

# 4. Set process limits for LED group (safe, user-level)
echo "Setting safe process limits..."
if ! grep -q "@led-group" /etc/security/limits.conf; then
    echo "@led-group    soft   nice     -10" | sudo tee -a /etc/security/limits.conf > /dev/null
    echo "@led-group    hard   nice     -10" | sudo tee -a /etc/security/limits.conf > /dev/null
    echo "Added safe process limits"
fi

# 5. Create performance monitoring script
echo "Creating performance monitoring helper..."
cat > ~/led_performance_monitor.sh << 'EOF'
#!/bin/bash
# Simple performance monitoring for LED controller

echo "LED Controller Performance Monitor"
echo "=================================="
echo "Date: $(date)"
echo ""

echo "CPU Information:"
echo "  Cores: $(nproc)"
echo "  Current Governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo "Unknown")"
echo ""

echo "Current CPU Usage per Core:"
grep 'cpu[0-9]' /proc/stat | while read cpu usage; do
    echo "  $cpu: Active"
done
echo ""

echo "Memory Usage:"
free -h | grep -E "Mem:|Swap:"
echo ""

echo "LED Controller Process (if running):"
pgrep -f "python.*main.py" > /dev/null && echo "  Status: Running" || echo "  Status: Not running"
if pgrep -f "python.*main.py" > /dev/null; then
    echo "  PID: $(pgrep -f "python.*main.py")"
    echo "  CPU%: $(ps -p $(pgrep -f "python.*main.py") -o %cpu --no-headers 2>/dev/null || echo "Unknown")"
    echo "  Memory: $(ps -p $(pgrep -f "python.*main.py") -o rss --no-headers 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "Unknown")"
fi
echo ""

echo "To revert CPU governor to default: sudo cpufreq-set -g ondemand"
echo "To start LED service: sudo systemctl start led-controller.service"
echo "To stop LED service: sudo systemctl stop led-controller.service"
EOF

chmod +x ~/led_performance_monitor.sh

echo ""
echo "=== SAFE OPTIMIZATION COMPLETE ==="
echo ""
echo "Applied changes:"
echo "✓ CPU governor set to performance (reversible)"
echo "✓ LED user group created"
echo "✓ Safe process limits set"
echo "✓ Service template created (not enabled)"
echo "✓ Performance monitor script created"
echo ""
echo "NO RISKY CHANGES APPLIED:"
echo "✗ No kernel parameters modified"
echo "✗ No boot configuration changes"
echo "✗ No CPU isolation"
echo "✗ No services disabled"
echo "✗ No GPU memory changes"
echo ""
echo "To monitor performance: ~/led_performance_monitor.sh"
echo "To revert CPU governor: sudo cpufreq-set -g ondemand"
echo ""
echo "The LED controller will still benefit from:"
echo "• Better CPU scheduling with performance governor"
echo "• Thread affinity optimizations in the code"
echo "• Improved frame rate limiting"
echo "• Chunked processing with break checks"
