#!/usr/bin/env python3
"""
Demo script to showcase the enhanced CLASS VISION interface
Run this to see the new attractive front-end design
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the main attendance application
    import attendance
    print("🚀 Starting CLASS VISION - Enhanced Attendance Management System")
    print("✨ Features:")
    print("   • Modern gradient backgrounds")
    print("   • Card-based UI design")
    print("   • Hover effects and animations")
    print("   • Professional typography")
    print("   • Color-coded attendance reports")
    print("   • Responsive layout")
    print("\n🎯 Launching application...")
    
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install tkinter pillow pandas opencv-python pyttsx3")
except Exception as e:
    print(f"❌ Error starting application: {e}")