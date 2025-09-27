#!/usr/bin/env python3
"""
Log Viewer for DD and Sons Website
This script helps you view and monitor application logs
"""

import os
import time
import subprocess
from datetime import datetime

def show_log_files():
    """Show available log files"""
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        print("❌ No logs directory found. Run the application first to generate logs.")
        return []
    
    log_files = []
    for file in os.listdir(logs_dir):
        if file.endswith('.log'):
            file_path = os.path.join(logs_dir, file)
            size = os.path.getsize(file_path)
            modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            log_files.append({
                'name': file,
                'path': file_path,
                'size': size,
                'modified': modified
            })
    
    print("📋 Available Log Files:")
    print("=" * 60)
    for i, log_file in enumerate(log_files, 1):
        size_mb = log_file['size'] / (1024 * 1024)
        print(f"{i}. {log_file['name']}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Modified: {log_file['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    return log_files

def view_log_file(file_path, lines=50):
    """View the last N lines of a log file"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ Log file not found: {file_path}")
            return
        
        # Use tail command to get last N lines
        result = subprocess.run(['tail', '-n', str(lines), file_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"📄 Last {lines} lines of {os.path.basename(file_path)}:")
            print("=" * 80)
            print(result.stdout)
        else:
            print(f"❌ Error reading log file: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def follow_log_file(file_path):
    """Follow a log file in real-time"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ Log file not found: {file_path}")
            return
        
        print(f"👀 Following {os.path.basename(file_path)} (Press Ctrl+C to stop):")
        print("=" * 80)
        
        # Use tail -f to follow the file
        process = subprocess.Popen(['tail', '-f', file_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
        except KeyboardInterrupt:
            print("\n🛑 Stopped following log file")
        finally:
            process.terminate()
            
    except Exception as e:
        print(f"❌ Error: {e}")

def search_logs(search_term, log_files=None):
    """Search for a term in log files"""
    if log_files is None:
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            print("❌ No logs directory found.")
            return
        
        log_files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]
    
    print(f"🔍 Searching for '{search_term}' in log files:")
    print("=" * 60)
    
    found_results = False
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            matching_lines = []
            for i, line in enumerate(lines, 1):
                if search_term.lower() in line.lower():
                    matching_lines.append((i, line.strip()))
            
            if matching_lines:
                found_results = True
                print(f"\n📄 {os.path.basename(log_file)}:")
                for line_num, line_content in matching_lines:
                    print(f"  Line {line_num}: {line_content}")
                    
        except Exception as e:
            print(f"❌ Error reading {log_file}: {e}")
    
    if not found_results:
        print(f"No results found for '{search_term}'")

def show_recent_activity():
    """Show recent login attempts and errors"""
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        print("❌ No logs directory found.")
        return
    
    main_log = os.path.join(logs_dir, 'dd_sons.log')
    error_log = os.path.join(logs_dir, 'errors.log')
    
    print("📊 Recent Activity Summary:")
    print("=" * 50)
    
    # Show recent login attempts
    if os.path.exists(main_log):
        try:
            result = subprocess.run(['grep', '-i', 'login', main_log], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                login_lines = result.stdout.strip().split('\n')
                recent_logins = login_lines[-10:] if len(login_lines) > 10 else login_lines
                
                print("🔐 Recent Login Activity:")
                for line in recent_logins:
                    if line.strip():
                        print(f"  {line}")
                print()
        except:
            pass
    
    # Show recent errors
    if os.path.exists(error_log):
        try:
            result = subprocess.run(['tail', '-n', '10', error_log], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print("❌ Recent Errors:")
                print(result.stdout)
        except:
            pass

def main():
    """Main log viewer function"""
    while True:
        print("\n📋 DD and Sons - Log Viewer")
        print("=" * 40)
        print("1. Show log files")
        print("2. View log file (last 50 lines)")
        print("3. Follow log file (real-time)")
        print("4. Search logs")
        print("5. Show recent activity")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            show_log_files()
            
        elif choice == '2':
            log_files = show_log_files()
            if log_files:
                try:
                    file_num = int(input("Enter file number: ")) - 1
                    if 0 <= file_num < len(log_files):
                        lines = input("Number of lines to show (default 50): ").strip()
                        lines = int(lines) if lines.isdigit() else 50
                        view_log_file(log_files[file_num]['path'], lines)
                    else:
                        print("❌ Invalid file number")
                except ValueError:
                    print("❌ Please enter a valid number")
                    
        elif choice == '3':
            log_files = show_log_files()
            if log_files:
                try:
                    file_num = int(input("Enter file number: ")) - 1
                    if 0 <= file_num < len(log_files):
                        follow_log_file(log_files[file_num]['path'])
                    else:
                        print("❌ Invalid file number")
                except ValueError:
                    print("❌ Please enter a valid number")
                    
        elif choice == '4':
            search_term = input("Enter search term: ").strip()
            if search_term:
                search_logs(search_term)
            else:
                print("❌ Please enter a search term")
                
        elif choice == '5':
            show_recent_activity()
            
        elif choice == '6':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()

