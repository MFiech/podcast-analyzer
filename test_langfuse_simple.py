#!/usr/bin/env python3
"""
Simple test script to verify Langfuse integration imports and basic functionality.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all Langfuse imports work correctly."""
    try:
        from langfuse import Langfuse, observe
        print("✅ Langfuse imports successful!")
        return True
    except Exception as e:
        print(f"❌ Langfuse imports failed: {e}")
        return False

def test_langfuse_initialization():
    """Test Langfuse client initialization."""
    try:
        from langfuse import Langfuse
        
        langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'http://localhost:4000')
        )
        
        print("✅ Langfuse client initialization successful!")
        return True
    except Exception as e:
        print(f"❌ Langfuse client initialization failed: {e}")
        return False

def test_decorator_functionality():
    """Test that the @observe decorator can be applied to functions."""
    try:
        from langfuse import observe
        
        @observe(as_type="generation")
        def test_function():
            return "test output"
        
        result = test_function()
        print(f"✅ @observe decorator test successful! Result: {result}")
        return True
    except Exception as e:
        print(f"❌ @observe decorator test failed: {e}")
        return False

def test_file_modifications():
    """Test that the modified files can be imported without syntax errors."""
    try:
        # Test that the files can be imported (even if they fail at runtime due to missing API keys)
        import ast
        
        files_to_check = ['summarizer.py', 'cleaner.py', 'tasks.py']
        
        for file_path in files_to_check:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the file to check for syntax errors
            ast.parse(content)
            print(f"✅ {file_path} syntax check passed")
        
        print("✅ All modified files have valid syntax!")
        return True
    except Exception as e:
        print(f"❌ File syntax check failed: {e}")
        return False

def main():
    """Run all simple integration tests."""
    print("🚀 Starting simple Langfuse integration tests...\n")
    
    # Check environment variables
    required_env_vars = ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY', 'LANGFUSE_HOST']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment.")
        return False
    
    print("✅ Environment variables found")
    
    # Run tests
    tests = [
        test_imports,
        test_langfuse_initialization,
        test_decorator_functionality,
        test_file_modifications
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All simple tests passed! Langfuse integration is ready.")
        print("\nNext steps:")
        print("1. Set your OPENAI_API_KEY in the .env file")
        print("2. Start your Langfuse server at http://localhost:4000")
        print("3. Run your normal podcast analysis tasks")
        print("4. View traces in your Langfuse dashboard")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
