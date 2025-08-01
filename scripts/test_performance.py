#!/usr/bin/env python3
"""
Performance Test Script for LED Controller
Tests the LED processing performance with and without optimizations
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from LEDService import LEDService
from LEDLoops import LEDThemes
from App import App

def test_led_performance():
    """Test LED processing performance"""
    print("Starting LED Performance Test...")
    print("=" * 50)
    
    # Create minimal app instance
    app = App()
    app.withdraw()  # Hide the window for testing
    
    # Test different LED themes
    themes_to_test = [
        ("twinkle", 30),     # 30 seconds
        ("rainbow", 30),     # 30 seconds  
        ("pacifica", 60),    # 60 seconds - most intensive
    ]
    
    led_service = LEDService.getInstance()
    
    for theme_name, duration in themes_to_test:
        print(f"\nTesting {theme_name} theme for {duration} seconds...")
        
        theme = LEDThemes.getTheme(theme_name)
        if not theme:
            print(f"Theme {theme_name} not found!")
            continue
            
        # Record performance metrics
        start_time = time.time()
        frame_count = 0
        
        led_service.setLoop(theme)
        
        # Monitor for specified duration
        end_time = start_time + duration
        while time.time() < end_time:
            time.sleep(0.1)  # Check every 100ms
            frame_count += 1
            
            # Print progress every 10 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 10 == 0 and elapsed > 0:
                print(f"  Progress: {elapsed:.1f}s / {duration}s")
        
        # Calculate performance
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        
        print(f"  Results for {theme_name}:")
        print(f"    Duration: {total_time:.1f}s")
        print(f"    Average FPS: {avg_fps:.1f}")
        
        # Stop the theme
        led_service.setLoop(LEDThemes.null())
        time.sleep(1)  # Brief pause between tests
    
    print("\nPerformance test complete!")
    print("Check the Debug page in the UI to see detailed performance metrics.")
    
    led_service.shutdown()
    app.destroy()

if __name__ == "__main__":
    try:
        test_led_performance()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
