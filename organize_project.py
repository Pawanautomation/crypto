import os
import shutil
from pathlib import Path

def reorganize_project():
    # Get project root directory
    project_root = Path("C:/Users/pawan/Documents/Workspace/crypto-trading-bot")
    
    # Define the correct structure
    structure = {
        'src': {
            'files': [
                'market_data.py',
                'websocket_manager.py',
                'ai_analyzer.py',
                'bot_manager.py',
            ],
            'utils': {
                'files': [
                    'logging_utils.py',
                    'time_utils.py',
                    'trading_utils.py',
                    '__init__.py'
                ]
            }
        },
        'tests': {
            'files': [
                'test_ai_analyzer.py',
                'test_websocket.py',
                'test_setup.py',
                'service_test.py',
                'conftest.py',
                '__init__.py'
            ]
        },
        'config': {
            'files': [
                'config.py',
                'pytest.ini'
            ]
        }
    }

    # Create directories and move files
    for main_dir, contents in structure.items():
        dir_path = project_root / main_dir
        dir_path.mkdir(exist_ok=True)
        
        # Handle files in the main directory
        if 'files' in contents:
            for file in contents['files']:
                # Check all possible source locations
                possible_sources = [
                    project_root / file,
                    project_root / 'src' / file,
                    project_root / 'src' / 'tests' / file,
                    project_root / 'tests' / file
                ]
                
                for src_path in possible_sources:
                    if src_path.exists():
                        dest_path = dir_path / file
                        print(f"Moving {src_path} to {dest_path}")
                        try:
                            shutil.move(str(src_path), str(dest_path))
                            break
                        except Exception as e:
                            print(f"Error moving {file}: {str(e)}")
        
        # Handle subdirectories
        for sub_dir, sub_contents in contents.items():
            if sub_dir != 'files':
                sub_path = dir_path / sub_dir
                sub_path.mkdir(exist_ok=True)
                
                if 'files' in sub_contents:
                    for file in sub_contents['files']:
                        # Check all possible source locations
                        possible_sources = [
                            project_root / file,
                            project_root / 'src' / file,
                            project_root / 'src' / sub_dir / file,
                            project_root / sub_dir / file
                        ]
                        
                        for src_path in possible_sources:
                            if src_path.exists():
                                dest_path = sub_path / file
                                print(f"Moving {src_path} to {dest_path}")
                                try:
                                    shutil.move(str(src_path), str(dest_path))
                                    break
                                except Exception as e:
                                    print(f"Error moving {file}: {str(e)}")

    # Frontend directory is already correctly structured, no need to modify it
    
    print("\nFinal structure verification:")
    for path in sorted(project_root.rglob('*')):
        if path.is_file() and 'node_modules' not in str(path) and '__pycache__' not in str(path):
            print(path.relative_to(project_root))

if __name__ == "__main__":
    reorganize_project()