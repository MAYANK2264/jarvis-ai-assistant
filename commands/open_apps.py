import os
import winreg
import glob
from typing import Optional, List, Dict
import subprocess
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicationManager:
    def __init__(self):
        # Common program installation directories
        self.program_dirs = [
            os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
            os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
            os.environ.get('LOCALAPPDATA', ''),
            os.environ.get('APPDATA', ''),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
            "C:\\Windows\\System32"
        ]
        
        # Common executable extensions
        self.exec_extensions = ['.exe', '.msi', '.bat', '.cmd']
        
        # Common document extensions
        self.doc_extensions = [
            '.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.csv', '.rtf', '.odt'
        ]
        
        # Initialize app cache
        self.app_cache: Dict[str, str] = self._get_default_apps()
        self.refresh_app_cache()

    def _get_default_apps(self) -> Dict[str, str]:
        """Get default Windows applications."""
        return {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "wordpad": "wordpad.exe",
            "cmd": "cmd.exe",
            "explorer": "explorer.exe",
            "control": "control.exe",
            "task manager": "taskmgr.exe",
            "powershell": "powershell.exe",
            "terminal": "wt.exe"
        }

    def _get_start_menu_programs(self) -> List[str]:
        """Get programs from Start Menu."""
        start_menu_paths = [
            os.path.join(os.environ.get('PROGRAMDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
            os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs')
        ]
        
        programs = []
        for start_menu in start_menu_paths:
            if os.path.exists(start_menu):
                for root, _, files in os.walk(start_menu):
                    for file in files:
                        if file.endswith('.lnk'):
                            programs.append(os.path.join(root, file))
        return programs

    def _get_installed_programs_from_registry(self) -> Dict[str, str]:
        """Get installed programs from Windows Registry."""
        programs = {}
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for reg_hkey, reg_path in reg_paths:
            try:
                reg_key = winreg.OpenKey(reg_hkey, reg_path, 0, winreg.KEY_READ)
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        app_name = winreg.EnumKey(reg_key, i)
                        app_key = winreg.OpenKey(reg_key, app_name)
                        try:
                            path = winreg.QueryValue(app_key, None)
                            if path and path.endswith('.exe'):
                                name = app_name.replace('.exe', '').lower()
                                programs[name] = path
                        except:
                            pass
                        winreg.CloseKey(app_key)
                    except:
                        continue
                winreg.CloseKey(reg_key)
            except:
                continue
        return programs

    def refresh_app_cache(self):
        """Refresh the cache of available applications."""
        # Add registry programs
        self.app_cache.update(self._get_installed_programs_from_registry())
        
        # Search common program directories
        for directory in self.program_dirs:
            if os.path.exists(directory):
                for ext in self.exec_extensions:
                    for file in glob.glob(os.path.join(directory, f'**/*{ext}'), recursive=True):
                        name = os.path.basename(file).lower().replace(ext, '')
                        self.app_cache[name] = file

    def find_file(self, query: str) -> Optional[str]:
        """Find a file in common locations."""
        # Common locations to search
        search_locations = [
            os.path.expanduser('~'),
            os.path.join(os.path.expanduser('~'), 'Documents'),
            os.path.join(os.path.expanduser('~'), 'Downloads'),
            os.path.join(os.path.expanduser('~'), 'Desktop')
        ]
        
        query = query.lower()
        for location in search_locations:
            if os.path.exists(location):
                # Search for exact matches first
                for root, _, files in os.walk(location):
                    for file in files:
                        if query == file.lower():
                            return os.path.join(root, file)
                
                # Then search for partial matches
                for root, _, files in os.walk(location):
                    for file in files:
                        if query in file.lower():
                            return os.path.join(root, file)
        return None

    def open_item(self, query: str) -> str:
        """Open an application or file based on the query."""
        try:
            query = query.lower().strip()
            
            # Check if it's a known application
            for app_name, app_path in self.app_cache.items():
                if query in app_name and os.path.exists(app_path):
                    try:
                        os.startfile(app_path)
                        return f"Opening {app_name}"
                    except Exception as e:
                        logger.error(f"Error opening {app_name}: {str(e)}")
                        continue

            # Try to find and open as a file
            file_path = self.find_file(query)
            if file_path and os.path.exists(file_path):
                try:
                    os.startfile(file_path)
                    return f"Opening file: {os.path.basename(file_path)}"
                except Exception as e:
                    logger.error(f"Error opening file {file_path}: {str(e)}")
                    return f"Error opening file: {str(e)}"

            # If not found, try to open as a URL
            if any(query.startswith(prefix) for prefix in ['http://', 'https://', 'www.']):
                if not query.startswith(('http://', 'https://')):
                    query = 'https://' + query
                os.startfile(query)
                return f"Opening URL: {query}"

            return f"Could not find '{query}'. Please check if the name is correct."

        except Exception as e:
            logger.error(f"Error in open_item: {str(e)}")
            return f"Error: {str(e)}"

# Initialize the application manager
app_manager = ApplicationManager()

def open_application(command: str) -> str:
    """Open an application or file based on the command."""
    # Extract the application/file name from the command
    words = command.lower().split()
    if len(words) <= 1:
        return "Please specify what you want to open."
        
    # Remove common command words
    common_words = ['open', 'run', 'start', 'launch', 'execute']
    query = ' '.join(word for word in words if word not in common_words)
    
    return app_manager.open_item(query)

def refresh_application_cache():
    """Refresh the cache of available applications."""
    app_manager.refresh_app_cache()
    return "Application cache has been refreshed."
