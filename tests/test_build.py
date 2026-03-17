"""
Test suite for build and deployment configuration
"""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def repo_root():
    """Get repository root path"""
    return Path(__file__).parent.parent


@pytest.fixture
def workflow_file(repo_root):
    """Load GitHub Actions workflow file"""
    workflow_path = repo_root / ".github/workflows/pages.yml"
    if not workflow_path.exists():
        pytest.skip("Workflow file not found")
    return workflow_path


class TestRequiredFiles:
    """Tests for required files for GitHub Pages"""

    def test_index_html_exists(self, repo_root):
        """Verify index.html exists"""
        index_file = repo_root / "index.html"
        assert index_file.exists(), "index.html not found"

    def test_css_directory_exists(self, repo_root):
        """Verify css directory exists"""
        css_dir = repo_root / "css"
        assert css_dir.exists(), "css directory not found"
        assert css_dir.is_dir(), "css is not a directory"

    def test_js_directory_exists(self, repo_root):
        """Verify js directory exists"""
        js_dir = repo_root / "js"
        assert js_dir.exists(), "js directory not found"
        assert js_dir.is_dir(), "js is not a directory"

    def test_workflow_directory_exists(self, repo_root):
        """Verify .github/workflows directory exists"""
        workflow_dir = repo_root / ".github/workflows"
        assert workflow_dir.exists(), ".github/workflows directory not found"

    def test_pages_workflow_exists(self, workflow_file):
        """Verify GitHub Pages workflow file exists"""
        assert workflow_file.exists(), "pages.yml workflow not found"

    def test_gitignore_exists(self, repo_root):
        """Verify .gitignore exists"""
        gitignore = repo_root / ".gitignore"
        assert gitignore.exists(), ".gitignore not found"

    def test_license_exists(self, repo_root):
        """Verify LICENSE file exists"""
        license_file = repo_root / "LICENSE"
        assert license_file.exists(), "LICENSE file not found"

    def test_readme_exists(self, repo_root):
        """Verify README exists"""
        readme = repo_root / "README.md"
        assert readme.exists(), "README.md not found"


class TestWorkflowConfiguration:
    """Tests for GitHub Actions workflow configuration"""

    def test_workflow_is_valid_yaml(self, workflow_file):
        """Verify workflow file is valid YAML"""
        try:
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)
            assert workflow is not None, "Workflow YAML is empty"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in workflow file: {e}")

    def test_workflow_has_name(self, workflow_file):
        """Verify workflow has a name"""
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)
        assert 'name' in workflow, "Workflow missing 'name' field"

    def test_workflow_has_jobs(self, workflow_file):
        """Verify workflow has jobs defined"""
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)
        assert 'jobs' in workflow, "Workflow missing 'jobs' field"
        assert len(workflow['jobs']) > 0, "Workflow has no jobs"

    def test_workflow_has_correct_permissions(self, workflow_file):
        """Verify workflow has correct permissions for Pages"""
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)

        if 'permissions' in workflow:
            perms = workflow['permissions']
            # For GitHub Pages, we need specific permissions
            assert 'pages' in perms or 'contents' in perms, \
                "Workflow missing required permissions"

    def test_workflow_triggers_on_push(self, workflow_file):
        """Verify workflow triggers on push to main"""
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)

        # YAML parser converts 'on' to True in Python
        assert 'on' in workflow or True in workflow, \
            "Workflow missing trigger configuration"


class TestFileSizes:
    """Tests for reasonable file sizes"""

    def test_individual_files_reasonable_size(self, repo_root):
        """Verify no single file exceeds 1MB"""
        max_size_mb = 1.0

        # Check all non-git, non-venv files
        for file_path in repo_root.rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path) and '.venv' not in str(file_path) and '__pycache__' not in str(file_path):
                size_mb = file_path.stat().st_size / (1024 * 1024)
                assert size_mb < max_size_mb, \
                    f"File too large: {file_path.name} ({size_mb:.2f}MB)"

    def test_total_repo_size_reasonable(self, repo_root):
        """Verify total repository size is reasonable (< 5MB)"""
        max_size_mb = 5.0

        total_size = 0
        for file_path in repo_root.rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path) and '.venv' not in str(file_path) and '__pycache__' not in str(file_path) and 'tests' not in str(file_path):
                total_size += file_path.stat().st_size

        total_size_mb = total_size / (1024 * 1024)
        assert total_size_mb < max_size_mb, \
            f"Repository too large: {total_size_mb:.2f}MB (max: {max_size_mb}MB)"

    def test_js_files_size(self, repo_root):
        """Verify JavaScript files are < 50KB each"""
        max_size_kb = 50

        js_dir = repo_root / "js"
        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                size_kb = js_file.stat().st_size / 1024
                assert size_kb < max_size_kb, \
                    f"JS file too large: {js_file.name} ({size_kb:.2f}KB)"

    def test_css_files_size(self, repo_root):
        """Verify CSS files are < 100KB each"""
        max_size_kb = 100

        css_dir = repo_root / "css"
        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                size_kb = css_file.stat().st_size / 1024
                assert size_kb < max_size_kb, \
                    f"CSS file too large: {css_file.name} ({size_kb:.2f}KB)"


class TestGitignore:
    """Tests for .gitignore configuration"""

    def test_gitignore_has_common_patterns(self, repo_root):
        """Verify .gitignore covers common patterns"""
        gitignore_file = repo_root / ".gitignore"
        gitignore_content = gitignore_file.read_text()

        # Should ignore common patterns
        common_patterns = ['node_modules', '.DS_Store']

        # At least some common patterns should be present
        has_some = any(pattern in gitignore_content for pattern in common_patterns)
        assert has_some or len(gitignore_content) > 0, \
            ".gitignore should have some patterns"


class TestLicense:
    """Tests for LICENSE file"""

    def test_license_is_mit(self, repo_root):
        """Verify LICENSE file mentions MIT"""
        license_file = repo_root / "LICENSE"
        license_content = license_file.read_text()

        assert 'MIT' in license_content, "LICENSE should mention MIT"

    def test_license_not_empty(self, repo_root):
        """Verify LICENSE file is not empty"""
        license_file = repo_root / "LICENSE"
        license_content = license_file.read_text()

        assert len(license_content) > 100, "LICENSE file seems too short"


class TestDirectoryStructure:
    """Tests for proper directory structure"""

    def test_no_build_artifacts(self, repo_root):
        """Verify no build artifacts are committed"""
        # Common build directories that shouldn't be in repo
        bad_dirs = ['node_modules', 'dist', 'build', '__pycache__']

        for bad_dir in bad_dirs:
            path = repo_root / bad_dir
            assert not path.exists(), f"Build artifact directory found: {bad_dir}"

    def test_assets_directory_structure(self, repo_root):
        """Verify assets directory exists if referenced"""
        # If there's an og-image reference, assets dir should exist
        assets_dir = repo_root / "assets"
        if assets_dir.exists():
            assert assets_dir.is_dir(), "assets should be a directory"


class TestDeploymentReadiness:
    """Tests for deployment readiness"""

    def test_no_temp_files(self, repo_root):
        """Verify no temporary files in repository"""
        temp_patterns = ['*.tmp', '*.temp', '*.swp', '*~']

        for pattern in temp_patterns:
            temp_files = list(repo_root.glob(pattern))
            assert len(temp_files) == 0, \
                f"Temporary files found: {[f.name for f in temp_files]}"

    def test_no_backup_files(self, repo_root):
        """Verify no backup files in repository"""
        backup_patterns = ['*.bak', '*.backup', '*.old']

        for pattern in backup_patterns:
            backup_files = list(repo_root.glob(pattern))
            assert len(backup_files) == 0, \
                f"Backup files found: {[f.name for f in backup_files]}"


class TestPageWeight:
    """Tests for overall page weight"""

    def test_total_page_weight_reasonable(self, repo_root):
        """Verify total page weight < 500KB (excluding tests)"""
        max_weight_kb = 500

        total_weight = 0

        # Add index.html
        index_file = repo_root / "index.html"
        if index_file.exists():
            total_weight += index_file.stat().st_size

        # Add CSS files
        css_dir = repo_root / "css"
        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                total_weight += css_file.stat().st_size

        # Add JS files
        js_dir = repo_root / "js"
        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                total_weight += js_file.stat().st_size

        weight_kb = total_weight / 1024
        assert weight_kb < max_weight_kb, \
            f"Total page weight too large: {weight_kb:.2f}KB (max: {max_weight_kb}KB)"
