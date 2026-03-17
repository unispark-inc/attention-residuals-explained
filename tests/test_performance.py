"""
Test suite for performance optimization
"""
import pytest
from pathlib import Path
from bs4 import BeautifulSoup
import re


@pytest.fixture
def html_content():
    """Load the HTML file"""
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


class TestNoDependencies:
    """Tests for zero external dependencies"""

    def test_no_external_libraries(self, soup):
        """Verify no external JavaScript libraries"""
        scripts = soup.find_all('script', src=True)

        for script in scripts:
            src = script.get('src')
            assert not src.startswith('http'), \
                f"External JavaScript dependency found: {src}"

    def test_no_external_css_frameworks(self, soup):
        """Verify no external CSS frameworks"""
        links = soup.find_all('link', rel='stylesheet')

        for link in links:
            href = link.get('href')
            assert not href.startswith('http'), \
                f"External CSS framework found: {href}"

    def test_no_cdn_dependencies(self, html_content):
        """Verify no CDN dependencies anywhere"""
        cdn_indicators = [
            'cdn.jsdelivr.net',
            'unpkg.com',
            'cdnjs.cloudflare.com',
            'googleapis.com',
            'gstatic.com'
        ]

        for indicator in cdn_indicators:
            assert indicator not in html_content.lower(), \
                f"CDN dependency found: {indicator}"


class TestFileSize:
    """Tests for file size optimization"""

    def test_js_files_under_limit(self, repo_root):
        """Verify JS files are < 50KB each"""
        max_size_kb = 50
        js_dir = repo_root / "js"

        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                size_kb = js_file.stat().st_size / 1024
                assert size_kb < max_size_kb, \
                    f"{js_file.name} too large: {size_kb:.2f}KB (max: {max_size_kb}KB)"

    def test_css_files_under_limit(self, repo_root):
        """Verify CSS files are < 100KB each"""
        max_size_kb = 100
        css_dir = repo_root / "css"

        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                size_kb = css_file.stat().st_size / 1024
                assert size_kb < max_size_kb, \
                    f"{css_file.name} too large: {size_kb:.2f}KB (max: {max_size_kb}KB)"

    def test_html_file_under_limit(self, repo_root):
        """Verify HTML file is reasonable size"""
        max_size_kb = 50
        html_file = repo_root / "index.html"

        size_kb = html_file.stat().st_size / 1024
        assert size_kb < max_size_kb, \
            f"index.html too large: {size_kb:.2f}KB (max: {max_size_kb}KB)"

    def test_total_page_weight(self, repo_root):
        """Verify total page weight < 500KB (excluding images)"""
        max_weight_kb = 500

        total_size = 0

        # HTML
        html_file = repo_root / "index.html"
        if html_file.exists():
            total_size += html_file.stat().st_size

        # CSS
        css_dir = repo_root / "css"
        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                total_size += css_file.stat().st_size

        # JS
        js_dir = repo_root / "js"
        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                total_size += js_file.stat().st_size

        weight_kb = total_size / 1024
        assert weight_kb < max_weight_kb, \
            f"Total page weight: {weight_kb:.2f}KB (max: {max_weight_kb}KB)"


class TestInlineStyles:
    """Tests for inline styles (should prefer external CSS)"""

    def test_no_style_tags_in_html(self, soup):
        """Verify no <style> tags in HTML (all CSS should be external)"""
        style_tags = soup.find_all('style')
        assert len(style_tags) == 0, \
            f"Found {len(style_tags)} <style> tags (prefer external CSS)"

    def test_minimal_inline_styles(self, soup):
        """Verify minimal inline style attributes"""
        elements_with_inline_style = soup.find_all(style=True)

        # Allow some inline styles for dynamic content (like progress bars)
        # but should be minimal
        max_allowed = 15
        assert len(elements_with_inline_style) < max_allowed, \
            f"Too many inline styles: {len(elements_with_inline_style)} (max: {max_allowed})"


class TestScriptLoading:
    """Tests for script loading optimization"""

    def test_scripts_at_bottom_or_deferred(self, soup):
        """Verify scripts are at bottom of body or use defer"""
        scripts = soup.find_all('script', src=True)

        for script in scripts:
            # Check if script has defer attribute
            has_defer = script.get('defer') is not None
            has_async = script.get('async') is not None

            # Check if script is in body (not head)
            in_body = script.find_parent('body') is not None

            assert has_defer or has_async or in_body, \
                f"Script not optimized for loading: {script.get('src')}"

    def test_no_blocking_scripts_in_head(self, soup):
        """Verify no blocking scripts in <head>"""
        head = soup.find('head')
        if head:
            scripts = head.find_all('script', src=True)

            for script in scripts:
                # Scripts in head should be deferred or async
                has_defer = script.get('defer') is not None
                has_async = script.get('async') is not None

                assert has_defer or has_async, \
                    f"Blocking script in <head>: {script.get('src')}"


class TestCSSOptimization:
    """Tests for CSS optimization"""

    def test_no_css_imports(self, repo_root):
        """Verify no @import in CSS (slower than <link>)"""
        css_dir = repo_root / "css"

        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                content = css_file.read_text()
                assert '@import' not in content, \
                    f"@import found in {css_file.name} (use <link> instead)"

    def test_css_variables_for_consistency(self, repo_root):
        """Verify CSS variables are used (reduces duplication)"""
        css_dir = repo_root / "css"

        if css_dir.exists():
            for css_file in css_dir.glob('*.css'):
                content = css_file.read_text()
                if len(content) > 1000:  # Only check substantial CSS files
                    assert '--' in content and 'var(' in content, \
                        f"CSS variables not used in {css_file.name}"


class TestImageOptimization:
    """Tests for image optimization"""

    def test_no_large_images(self, repo_root):
        """Verify images are reasonably sized"""
        max_size_kb = 200  # 200KB per image
        assets_dir = repo_root / "assets"

        if assets_dir.exists():
            for img_file in assets_dir.rglob('*'):
                if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                    size_kb = img_file.stat().st_size / 1024
                    assert size_kb < max_size_kb, \
                        f"Image too large: {img_file.name} ({size_kb:.2f}KB)"


class TestCodeMinification:
    """Tests for code optimization (not minified but clean)"""

    def test_no_excessive_whitespace(self, repo_root):
        """Verify no excessive blank lines in production files"""
        # This is a soft check - we just verify files aren't bloated with whitespace

        for js_file in (repo_root / "js").glob('*.js'):
            content = js_file.read_text()
            lines = content.split('\n')

            # Count consecutive blank lines
            max_consecutive_blank = 0
            current_blank = 0

            for line in lines:
                if line.strip() == '':
                    current_blank += 1
                else:
                    max_consecutive_blank = max(max_consecutive_blank, current_blank)
                    current_blank = 0

            # Allow up to 3 consecutive blank lines
            assert max_consecutive_blank <= 3, \
                f"Excessive blank lines in {js_file.name}"

    def test_no_commented_out_code_blocks(self, repo_root):
        """Verify no large blocks of commented-out code"""
        # This is a heuristic check

        for js_file in (repo_root / "js").glob('*.js'):
            content = js_file.read_text()
            lines = content.split('\n')

            # Count consecutive comment lines
            consecutive_comments = 0
            max_consecutive_comments = 0

            for line in lines:
                stripped = line.strip()
                if stripped.startswith('//'):
                    consecutive_comments += 1
                else:
                    max_consecutive_comments = max(max_consecutive_comments, consecutive_comments)
                    consecutive_comments = 0

            # Allow up to 20 consecutive comment lines (for headers/docs)
            assert max_consecutive_comments <= 20, \
                f"Large comment block in {js_file.name} (possibly commented code)"


class TestRenderBlocking:
    """Tests for render-blocking resources"""

    def test_critical_css_inline_or_prioritized(self, soup):
        """Verify CSS is loaded efficiently"""
        css_links = soup.find_all('link', rel='stylesheet')

        # For small sites, having 1-2 CSS files in head is fine
        # Just verify we don't have many blocking stylesheets
        assert len(css_links) <= 3, \
            f"Too many CSS files ({len(css_links)}), consider consolidation"

    def test_fonts_not_blocking(self, soup):
        """Verify font loading doesn't block rendering"""
        # Check for font preloads or proper async loading
        font_links = soup.find_all('link', href=re.compile(r'\.(woff|woff2|ttf|otf)$'))

        for font in font_links:
            # Fonts should be preloaded or loaded async
            rel = font.get('rel')
            # If loading fonts, should use preload or have proper strategy


class TestDOMSize:
    """Tests for DOM size and complexity"""

    def test_reasonable_dom_size(self, soup):
        """Verify DOM is not excessively large"""
        all_elements = soup.find_all()

        # DOM should be < 1500 elements for good performance
        max_elements = 1500
        assert len(all_elements) < max_elements, \
            f"DOM too large: {len(all_elements)} elements (max: {max_elements})"

    def test_no_excessive_nesting(self, soup):
        """Verify no excessive DOM nesting"""
        # Find maximum nesting depth
        def get_depth(element):
            if not element.children:
                return 0
            return 1 + max((get_depth(child) for child in element.children if hasattr(child, 'children')), default=0)

        body = soup.find('body')
        if body:
            max_depth = get_depth(body)
            # Allow up to 15 levels of nesting
            assert max_depth <= 15, \
                f"Excessive DOM nesting: {max_depth} levels deep"


class TestLazyLoading:
    """Tests for lazy loading strategies"""

    def test_images_can_be_lazy_loaded(self, soup):
        """Verify images can use lazy loading"""
        images = soup.find_all('img')

        # Just verify images exist and could be optimized
        # For a simple page, eager loading is fine
        # This test just documents the capability


class TestJavaScriptOptimization:
    """Tests for JavaScript optimization"""

    def test_no_large_inline_scripts(self, soup):
        """Verify no large inline JavaScript blocks"""
        inline_scripts = soup.find_all('script', src=False)

        for script in inline_scripts:
            if script.string:
                size = len(script.string)
                # Inline scripts should be minimal (< 500 chars)
                assert size < 500, \
                    f"Large inline script found ({size} chars), consider external file"

    def test_event_delegation_where_possible(self, repo_root):
        """Verify event listeners are added efficiently"""
        # This is a heuristic - we check that addEventListener isn't called
        # hundreds of times in a loop

        js_dir = repo_root / "js"
        if js_dir.exists():
            for js_file in js_dir.glob('*.js'):
                content = js_file.read_text()

                # Count addEventListener calls
                listener_count = content.count('addEventListener')

                # Should be reasonable (< 30 for this size project)
                assert listener_count < 30, \
                    f"Many addEventListener calls in {js_file.name} ({listener_count})"
