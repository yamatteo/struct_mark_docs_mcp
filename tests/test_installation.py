import pytest
import subprocess
import tempfile
from pathlib import Path


def get_package_name():
    """Extract package name from pyproject.toml"""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    for line in content.split('\n'):
        if line.strip().startswith('name = '):
            return line.split('=')[1].strip().strip('"')
    return None


def test_uv_add_git_installation():
    """Test that 'uv add git+https://repo-url' works for the current package"""
    repo_url = "git+https://github.com/yamatteo/struct_mark_docs_mcp"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "test_project"
        test_project.mkdir()
        
        # Initialize a new uv project
        result = subprocess.run(
            ["uv", "init"], 
            cwd=test_project, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip(f"Could not initialize uv project: {result.stderr}")
        
        # Try to add the package from git
        result = subprocess.run(
            ["uv", "add", repo_url], 
            cwd=test_project, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"Failed to install package from git: {result.stderr}")
        
        # Verify the package was installed
        result = subprocess.run(
            ["uv", "run", "struct-mark-docs-mcp", "--help"], 
            cwd=test_project, 
            capture_output=True, 
            text=True,
            timeout=5  # Don't wait forever, just verify it starts
        )
        
        # We expect this to be interrupted (timeout) but the command should exist
        # If return code is 0 or 124 (timeout), the package is working
        if result.returncode not in [0, 124]:
            pytest.fail(f"Package script not working: {result.stderr}")


def test_uvx_git_installation():
    """Test that 'uvx git+https://repo-url' works for the current package"""
    repo_url = "git+https://github.com/yamatteo/struct_mark_docs_mcp"
    
    # Try to run the package directly with uvx from git
    result = subprocess.run(
        ["uvx", repo_url, "--help"], 
        capture_output=True, 
        text=True,
        timeout=5  # Don't wait forever, just verify it starts
    )
    
    # We expect this to be interrupted (timeout) but the command should exist
    # If return code is 0 or 124 (timeout), the package is working
    if result.returncode not in [0, 124]:
        pytest.fail(f"uvx from git failed: {result.stderr}")


def test_manual_installation():
    """Test that manual installation instructions work"""
    repo_url = "https://github.com/yamatteo/struct_mark_docs_mcp"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = Path(temp_dir) / "struct_mark_docs_mcp"
        
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, str(clone_dir)], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            pytest.skip(f"Could not clone repository: {result.stderr}")
        
        # Try to sync dependencies
        result = subprocess.run(
            ["uv", "sync"], 
            cwd=clone_dir, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            pytest.fail(f"Manual installation failed: {result.stderr}")
        
        # Check if the package script is available
        result = subprocess.run(
            ["uv", "run", "struct-mark-docs-mcp", "--help"], 
            cwd=clone_dir, 
            capture_output=True, 
            text=True
        )
        
        # The command should at least start (even if it fails due to missing env)
        # We just want to verify the script exists and is executable
        assert result.returncode != 127, "Package script not found after manual installation"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
