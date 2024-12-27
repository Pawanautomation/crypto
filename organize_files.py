import os
import shutil
from pathlib import Path

def reorganize_files():
    # Project root
    root = Path("C:/Users/pawan/Documents/Workspace/crypto-trading-bot")
    
    # Create necessary directories
    directories = ['src/utils', 'tests', 'config', 'docs']
    for dir_path in directories:
        (root / dir_path).mkdir(parents=True, exist_ok=True)

    # Move source files
    source_files = [
        'market_data.py',
        'market_data.py.bak',
        'ai_analyzer.py', 
        'bot_manager.py',
        'websocket_manager.py'
    ]
    for file in source_files:
        if (root / file).exists():
            shutil.move(str(root / file), str(root / 'src' / file))
    
    # Move util files
    util_files = [
        'logging_utils.py',
        'time_utils.py',
        'trading_utils.py'
    ]
    for file in util_files:
        if (root / 'src' / 'utils' / file).exists():
            src_path = root / 'src' / file
            dest_path = root / 'src' / 'utils' / file
            if src_path.exists():
                shutil.move(str(src_path), str(dest_path))
    
    # Move test files
    test_files = [
        'test_ai_analyzer.py',
        'test_websocket.py',
        'test_setup.py',
        'service_test.py',
        'conftest.py'
    ]
    for file in test_files:
        if (root / file).exists():
            shutil.move(str(root / file), str(root / 'tests' / file))
    
    # Move config files
    if (root / 'pytest.ini').exists():
        shutil.move(str(root / 'pytest.ini'), str(root / 'config' / 'pytest.ini'))
    
    # Move documentation files
    doc_files = [
        'chat-gpt.md',
        'gemini.md',
        'knowledgeBase.md'
    ]
    for file in doc_files:
        if (root / file).exists():
            shutil.move(str(root / file), str(root / 'docs' / file))
    
    # Create __init__.py files
    init_dirs = ['src', 'src/utils', 'tests']
    for dir_path in init_dirs:
        init_file = root / dir_path / '__init__.py'
        if not init_file.exists():
            init_file.touch()

    print("Project reorganization complete!")
    
    # Print final structure
    print("\nFinal project structure:")
    for path in sorted(root.rglob('*')):
        if path.is_file() and 'venv' not in str(path) and '__pycache__' not in str(path):
            print(path.relative_to(root))

if __name__ == "__main__":
    reorganize_files()