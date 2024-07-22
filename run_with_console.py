import os
import sys
import subprocess

def run_main_script():
    script_name = "PCBcoilV2.py"
    
    # Check if the script has been launched with the 'run_in_console' argument
    if len(sys.argv) > 1 and sys.argv[1] == 'run_in_console':
        sys.argv.pop(1)  # Remove the 'run_in_console' argument
        os.execv(sys.executable, ['python'] + [script_name] + sys.argv)
    else:
        # If not running in a console, open a new console window and run the script
        if sys.platform.startswith('linux'):
            subprocess.Popen(['konsole', '-e', sys.executable, __file__, 'run_in_console'] + sys.argv[1:])
        elif sys.platform.startswith('win'):
            subprocess.Popen(['cmd.exe', '/c', 'start', 'cmd.exe', '/k', sys.executable, __file__, 'run_in_console'] + sys.argv[1:])
        sys.exit()

if __name__ == "__main__":
    try:
        run_main_script()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to close the console window...")  # Keeps the console open
