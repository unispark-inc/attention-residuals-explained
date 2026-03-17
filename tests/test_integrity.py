"""
Test suite for link and reference integrity
"""
import pytest
from pathlib import Path
from bs4 import BeautifulSoup
import re


@pytest.fixture
def html_content():
    """Load the index.html file"""
    html_file = Path(__file__).parent.parent / "index.html"
    return html_file.read_text()


@pytest.fixture
def soup(html_content):
    """Parse HTML with BeautifulSoup"""
    return BeautifulSoup(html_content, 'html.parser')


@pytest.fixture
def repo_root():
    """Get repository root path"""
    return Path(__file__).parent.parent


class TestFileReferences:
    """Tests for file reference integrity"""

    def test_css_files_exist(self, soup, repo_root):
        """Verify all CSS file references resolve to existing files"""
        css_links = soup.find_all('link', rel='stylesheet')

        for link in css_links:
            href = link.get('href')
            if href and not href.startswith('http'):
                # Remove leading './'
                href = href.lstrip('./')
                css_path = repo_root / href
                assert css_path.exists(), f"CSS file not found: {href}"

    def test_js_files_exist(self, soup, repo_root):
        """Verify all JS file references resolve to existing files"""
        scripts = soup.find_all('script', src=True)

        for script in scripts:
            src = script.get('src')
            if src and not src.startswith('http'):
                # Remove leading './'
                src = src.lstrip('./')
                js_path = repo_root / src
                assert js_path.exists(), f"JavaScript file not found: {src}"

    def test_og_image_exists(self, soup, repo_root):
        """Verify OG image file exists"""
        og_image = soup.find('meta', property='og:image')
        assert og_image is not None, "OG image meta tag not found"

        image_path = og_image.get('content')
        if image_path and not image_path.startswith('http'):
            # Remove leading './'
            image_path = image_path.lstrip('./')
            img_file = repo_root / image_path
            assert img_file.exists(), f"OG image file not found: {image_path}"

    def test_all_local_resources_exist(self, soup, repo_root):
        """Verify all local resource references exist"""
        # Check images
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src and not src.startswith('http') and not src.startswith('data:'):
                src = src.lstrip('./')
                img_path = repo_root / src
                assert img_path.exists(), f"Image file not found: {src}"


class TestExternalLinks:
    """Tests for external link integrity"""

    def test_external_links_are_https(self, soup):
        """Verify all external links use HTTPS"""
        external_links = soup.find_all('a', href=re.compile(r'^http'))

        for link in external_links:
            href = link.get('href')
            assert href.startswith('https://'), \
                f"External link uses HTTP instead of HTTPS: {href}"

    def test_external_links_have_target_blank(self, soup):
        """Verify external links open in new tab"""
        external_links = soup.find_all('a', href=re.compile(r'^https?://'))

        for link in external_links:
            target = link.get('target')
            # External links should open in new tab
            assert target == '_blank', \
                f"External link missing target='_blank': {link.get('href')}"

    def test_paper_link_valid_format(self, soup):
        """Verify paper link has valid ArXiv format"""
        paper_links = soup.find_all('a', href=re.compile(r'arxiv\.org'))

        assert len(paper_links) > 0, "No ArXiv paper link found"

        for link in paper_links:
            href = link.get('href')
            # Should be arxiv.org/abs/XXXX.XXXXX format
            assert 'arxiv.org/abs/' in href, \
                f"ArXiv link has incorrect format: {href}"

    def test_github_links_valid(self, soup):
        """Verify GitHub repository links are valid"""
        github_links = soup.find_all('a', href=re.compile(r'github\.com'))

        assert len(github_links) > 0, "No GitHub links found"

        for link in github_links:
            href = link.get('href')
            # Should be github.com/username/repo format
            assert re.match(r'https://github\.com/[\w-]+/[\w-]+', href), \
                f"GitHub link has invalid format: {href}"


class TestURLPatterns:
    """Tests for URL patterns and potential 404s"""

    def test_no_broken_hash_links(self, soup):
        """Verify internal hash links point to existing IDs"""
        all_ids = {elem.get('id') for elem in soup.find_all(id=True)}
        hash_links = soup.find_all('a', href=re.compile(r'^#'))

        for link in hash_links:
            href = link.get('href')
            if href == '#':
                continue  # Skip empty hash

            target_id = href[1:]  # Remove '#'
            assert target_id in all_ids, \
                f"Hash link #{target_id} points to non-existent ID"

    def test_no_404_prone_patterns(self, html_content):
        """Verify no common 404-prone URL patterns"""
        # Check for common mistakes
        assert 'href=""' not in html_content, "Empty href found"
        assert 'src=""' not in html_content, "Empty src found"

        # Check for localhost references
        assert 'localhost' not in html_content.lower(), \
            "localhost reference found (will break in production)"
        assert '127.0.0.1' not in html_content, \
            "127.0.0.1 reference found (will break in production)"


class TestResourcePaths:
    """Tests for resource path consistency"""

    def test_relative_paths_use_forward_slash(self, html_content):
        """Verify relative paths use forward slashes (not backslashes)"""
        # Find src and href attributes
        src_attrs = re.findall(r'src=["\']([^"\']+)["\']', html_content)
        href_attrs = re.findall(r'href=["\']([^"\']+)["\']', html_content)

        all_paths = src_attrs + href_attrs

        for path in all_paths:
            if not path.startswith('http') and not path.startswith('#'):
                assert '\\' not in path, \
                    f"Path uses backslash (Windows-specific): {path}"

    def test_no_absolute_local_paths(self, html_content):
        """Verify no absolute local file paths are used"""
        # Check for common absolute path patterns
        assert 'file://' not in html_content.lower(), \
            "Absolute file:// path found"
        assert 'C:\\' not in html_content, \
            "Windows absolute path found"
        assert '/Users/' not in html_content, \
            "Unix absolute path found (potential issue)"
        assert '/home/' not in html_content, \
            "Unix absolute path found (potential issue)"


class TestCitationAndMetadata:
    """Tests for citation and metadata integrity"""

    def test_citation_block_exists(self, soup):
        """Verify citation block exists in footer"""
        citation = soup.find('pre', class_='citation')
        assert citation is not None, "Citation block not found"

        citation_text = citation.get_text()
        assert '@article' in citation_text, "Citation missing @article tag"
        assert '2025' in citation_text, "Citation missing year"

    def test_license_link_exists(self, soup):
        """Verify LICENSE link exists"""
        license_links = soup.find_all('a', href=re.compile(r'LICENSE'))
        assert len(license_links) > 0, "No LICENSE link found"


class TestNoExternalDependencies:
    """Tests for zero external dependencies philosophy"""

    def test_no_cdn_links(self, soup):
        """Verify no CDN dependencies (zero deps philosophy)"""
        # Check for common CDN patterns
        cdn_patterns = [
            'cdn.jsdelivr.net',
            'unpkg.com',
            'cdnjs.cloudflare.com',
            'cdn.plot.ly',
            'code.jquery.com',
            'stackpath.bootstrapcdn.com',
            'fonts.googleapis.com',
            'fonts.gstatic.com'
        ]

        links = soup.find_all(['link', 'script'])

        for link in links:
            href = link.get('href', '') + link.get('src', '')
            for pattern in cdn_patterns:
                assert pattern not in href.lower(), \
                    f"External CDN dependency found: {href}"

    def test_no_external_fonts(self, soup):
        """Verify no external font dependencies"""
        # Check for font imports
        links = soup.find_all('link', href=True)

        for link in links:
            href = link.get('href')
            assert 'fonts.googleapis.com' not in href, \
                "External font dependency found"
            assert 'fonts.gstatic.com' not in href, \
                "External font dependency found"

    def test_no_external_css(self, soup):
        """Verify no external CSS dependencies"""
        css_links = soup.find_all('link', rel='stylesheet')

        for link in css_links:
            href = link.get('href')
            assert not href.startswith('http'), \
                f"External CSS dependency found: {href}"

    def test_no_external_js(self, soup):
        """Verify no external JavaScript dependencies"""
        scripts = soup.find_all('script', src=True)

        for script in scripts:
            src = script.get('src')
            assert not src.startswith('http'), \
                f"External JavaScript dependency found: {src}"


class TestLinkConsistency:
    """Tests for link consistency across the page"""

    def test_github_repo_links_consistent(self, soup):
        """Verify all GitHub repo links point to same repository"""
        github_links = soup.find_all('a', href=re.compile(r'github\.com/.*Attention'))

        if len(github_links) > 1:
            # All links should be consistent
            first_href = github_links[0].get('href').rstrip('/')

            for link in github_links[1:]:
                href = link.get('href').rstrip('/')
                # Allow for /tree/main or other suffixes
                assert first_href in href or href in first_href, \
                    f"Inconsistent GitHub links: {first_href} vs {href}"

    def test_arxiv_links_consistent(self, soup):
        """Verify all ArXiv links point to same paper"""
        arxiv_links = soup.find_all('a', href=re.compile(r'arxiv\.org'))

        if len(arxiv_links) > 1:
            # Extract paper ID from all links
            paper_ids = set()
            for link in arxiv_links:
                href = link.get('href')
                match = re.search(r'(\d{4}\.\d{5})', href)
                if match:
                    paper_ids.add(match.group(1))

            assert len(paper_ids) == 1, \
                f"Inconsistent ArXiv paper IDs: {paper_ids}"
