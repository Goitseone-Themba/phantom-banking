#!/usr/bin/env python3
"""
Helper script to stop all Django development servers.

This script will find and terminate any running Django development servers
to prevent port conflicts when starting a new server.
"""

import subprocess
import signal
import sys
import time

def find_django_processes():
    """Find all Django development server processes."""
    try:
        # Find processes running Django development servers
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, 
            text=True
        )
        
        django_processes = []
        for line in result.stdout.split('\n'):
            if ('manage.py' in line and 'runserver' in line) or 'dev_server.py' in line:
                if 'grep' not in line:  # Exclude grep processes
                    parts = line.split()
                    if len(parts) >= 2:
                        pid = parts[1]
                        django_processes.append((pid, line.strip()))
        
        return django_processes
    except Exception as e:
        print(f"Error finding Django processes: {e}")
        return []

def stop_processes(processes):
    """Stop the given processes gracefully."""
    if not processes:
        print("🟢 No Django development servers found running.")
        return
    
    print(f"🔍 Found {len(processes)} Django server process(es):")
    for pid, description in processes:
        print(f"   PID {pid}: {description}")
    
    print("\n🛑 Stopping Django servers...")
    
    # First try graceful termination
    for pid, _ in processes:
        try:
            subprocess.run(['kill', '-TERM', pid], check=False)
            print(f"   Sent SIGTERM to PID {pid}")
        except Exception as e:
            print(f"   Error sending SIGTERM to PID {pid}: {e}")
    
    # Wait a bit for graceful shutdown
    time.sleep(2)
    
    # Check if any processes are still running
    remaining = find_django_processes()
    
    if remaining:
        print("\n⚠️  Some processes didn't stop gracefully, forcing termination...")
        for pid, _ in remaining:
            try:
                subprocess.run(['kill', '-KILL', pid], check=False)
                print(f"   Sent SIGKILL to PID {pid}")
            except Exception as e:
                print(f"   Error sending SIGKILL to PID {pid}: {e}")
        
        time.sleep(1)
    
    # Final check
    final_check = find_django_processes()
    if not final_check:
        print("\n✅ All Django development servers stopped successfully!")
    else:
        print(f"\n❌ {len(final_check)} process(es) still running:")
        for pid, description in final_check:
            print(f"   PID {pid}: {description}")

def check_port_8000():
    """Check if port 8000 is free."""
    try:
        result = subprocess.run(
            ['ss', '-tlnp'], 
            capture_output=True, 
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if ':8000' in line:
                return False, line.strip()
        
        return True, None
    except Exception as e:
        print(f"Error checking port 8000: {e}")
        return False, None

def main():
    print("🏦 Phantom Banking - Django Server Stopper")
    print("=" * 50)
    
    # Find and stop Django processes
    processes = find_django_processes()
    stop_processes(processes)
    
    # Check port 8000 status
    print("\n🔍 Checking port 8000 status...")
    port_free, port_info = check_port_8000()
    
    if port_free:
        print("✅ Port 8000 is free and ready for use!")
    else:
        print("❌ Port 8000 is still in use:")
        print(f"   {port_info}")
        print("\n💡 You may need to manually stop the process using the port.")

if __name__ == '__main__':
    main()

