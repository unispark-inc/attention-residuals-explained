"""
Test suite for HTML validation and structure
"""
import pytest
from bs4 import BeautifulSoup
from pathlib import Path
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


class TestHTMLStructure:
    """Tests for basic HTML structure and validity"""

    def test_html5_doctype(self, html_content):
        """Verify HTML5 doctype is present"""
        assert html_content.strip().startswith('<!DOCTYPE html>'), "Missing HTML5 doctype"

    def test_html_lang_attribute(self, soup):
        """Verify <html> has lang attribute"""
        html_tag = soup.find('html')
        assert html_tag is not None, "No <html> tag found"
        assert html_tag.get('lang'), "<html> tag missing lang attribute"
        assert html_tag.get('lang') == 'en', "Expected lang='en'"

    def test_meta_charset(self, soup):
        """Verify charset meta tag exists"""
        charset_meta = soup.find('meta', attrs={'charset': True})
        assert charset_meta is not None, "Missing charset meta tag"
        assert charset_meta.get('charset').upper() == 'UTF-8', "Expected UTF-8 charset"

    def test_meta_viewport(self, soup):
        """Verify viewport meta tag exists"""
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        assert viewport_meta is not None, "Missing viewport meta tag"
        assert viewport_meta.get('content'), "Viewport meta tag has no content"

    def test_title_tag(self, soup):
        """Verify title tag exists and is not empty"""
        title = soup.find('title')
        assert title is not None, "Missing <title> tag"
        assert title.string, "Title tag is empty"
        assert len(title.string.strip()) > 0, "Title tag contains only whitespace"

    def test_og_meta_tags(self, soup):
        """Verify Open Graph meta tags exist"""
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_image = soup.find('meta', property='og:image')
        og_type = soup.find('meta', property='og:type')

        assert og_title is not None, "Missing og:title meta tag"
        assert og_description is not None, "Missing og:description meta tag"
        assert og_image is not None, "Missing og:image meta tag"
        assert og_type is not None, "Missing og:type meta tag"

        assert og_title.get('content'), "og:title has no content"
        assert og_description.get('content'), "og:description has no content"
        assert og_image.get('content'), "og:image has no content"


class TestSections:
    """Tests for main sections and content structure"""

    def test_all_sections_present(self, soup):
        """Verify all required sections exist"""
        required_sections = [
            'hero',
            'problem',
            'insight',
            'how-it-works',
            'block-attnres',
            'results'
        ]

        for section_id in required_sections:
            section = soup.find(id=section_id)
            assert section is not None, f"Missing section with id='{section_id}'"

    def test_section_ids_unique(self, soup):
        """Verify all IDs are unique"""
        elements_with_id = soup.find_all(id=True)
        ids = [elem.get('id') for elem in elements_with_id]
        duplicates = [id for id in ids if ids.count(id) > 1]
        assert len(duplicates) == 0, f"Duplicate IDs found: {set(duplicates)}"

    def test_no_empty_sections(self, soup):
        """Verify sections have content"""
        sections = soup.find_all('section')
        for section in sections:
            text_content = section.get_text(strip=True)
            assert len(text_content) > 0, f"Empty section found: {section.get('id') or section.get('class')}"

    def test_main_tag_exists(self, soup):
        """Verify semantic <main> tag exists"""
        main_tag = soup.find('main')
        assert main_tag is not None, "Missing <main> semantic tag"

    def test_footer_exists(self, soup):
        """Verify footer exists"""
        footer = soup.find('footer')
        assert footer is not None, "Missing <footer> tag"


class TestLinks:
    """Tests for internal and external links"""

    def test_internal_links_valid(self, soup):
        """Verify internal links (#...) point to existing IDs"""
        all_ids = {elem.get('id') for elem in soup.find_all(id=True)}
        internal_links = soup.find_all('a', href=re.compile(r'^#'))

        for link in internal_links:
            href = link.get('href')
            if href == '#':
                continue  # Skip empty hash links
            target_id = href[1:]  # Remove the '#'
            assert target_id in all_ids, f"Internal link #{target_id} points to non-existent ID"

    def test_external_links_are_https(self, soup):
        """Verify external links use HTTPS"""
        external_links = soup.find_all('a', href=re.compile(r'^http'))

        for link in external_links:
            href = link.get('href')
            assert href.startswith('https://'), f"Non-HTTPS external link: {href}"

    def test_paper_link_exists(self, soup):
        """Verify link to paper exists"""
        paper_links = soup.find_all('a', href=re.compile(r'arxiv\.org'))
        assert len(paper_links) > 0, "No link to arXiv paper found"

    def test_github_repo_link_exists(self, soup):
        """Verify GitHub repository link exists"""
        github_links = soup.find_all('a', href=re.compile(r'github\.com'))
        assert len(github_links) > 0, "No GitHub repository link found"


class TestResources:
    """Tests for resource references (CSS, JS, images)"""

    def test_css_references_exist(self, soup):
        """Verify CSS files referenced in HTML exist"""
        css_links = soup.find_all('link', rel='stylesheet')

        for link in css_links:
            href = link.get('href')
            if href and not href.startswith('http'):
                css_path = Path(__file__).parent.parent / href
                assert css_path.exists(), f"CSS file not found: {href}"

    def test_js_references_exist(self, soup):
        """Verify JS files referenced in HTML exist"""
        scripts = soup.find_all('script', src=True)

        for script in scripts:
            src = script.get('src')
            if src and not src.startswith('http'):
                js_path = Path(__file__).parent.parent / src
                assert js_path.exists(), f"JS file not found: {src}"

    def test_og_image_exists(self, soup):
        """Verify OG image file exists"""
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_path = og_image.get('content')
            if image_path and not image_path.startswith('http'):
                # Remove leading './'
                image_path = image_path.lstrip('./')
                img_file = Path(__file__).parent.parent / image_path
                assert img_file.exists(), f"OG image not found: {image_path}"


class TestAccessibility:
    """Tests for accessibility features"""

    def test_images_have_alt_text(self, soup):
        """Verify all images have alt attributes"""
        images = soup.find_all('img')
        for img in images:
            assert img.has_attr('alt'), f"Image missing alt attribute: {img.get('src', 'unknown')}"

    def test_theme_toggle_has_aria_label(self, soup):
        """Verify theme toggle button has aria-label"""
        theme_toggle = soup.find('button', class_='theme-toggle')
        assert theme_toggle is not None, "Theme toggle button not found"
        assert theme_toggle.get('aria-label'), "Theme toggle missing aria-label"

    def test_slider_inputs_have_labels(self, soup):
        """Verify slider inputs have associated labels"""
        sliders = soup.find_all('input', type='range')

        for slider in sliders:
            slider_id = slider.get('id')
            if slider_id:
                label = soup.find('label', attrs={'for': slider_id})
                if not label:
                    # Check if input is inside a label
                    parent = slider.parent
                    assert parent.name == 'label', f"Slider {slider_id} has no associated label"


class TestHeadingHierarchy:
    """Tests for proper heading structure"""

    def test_single_h1(self, soup):
        """Verify there is exactly one h1 tag"""
        h1_tags = soup.find_all('h1')
        assert len(h1_tags) == 1, f"Expected 1 h1 tag, found {len(h1_tags)}"

    def test_heading_hierarchy(self, soup):
        """Verify headings follow proper hierarchy (no skipping levels)"""
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        if not headings:
            return

        levels = [int(h.name[1]) for h in headings]

        # First heading should be h1
        assert levels[0] == 1, "First heading should be h1"

        # Check for skipped levels
        for i in range(1, len(levels)):
            diff = levels[i] - levels[i-1]
            assert diff <= 1, f"Heading level skipped: {headings[i-1].name} → {headings[i].name}"


class TestSVGDiagrams:
    """Tests for SVG diagram containers"""

    def test_svg_elements_exist(self, soup):
        """Verify SVG elements are present in HTML"""
        svgs = soup.find_all('svg')
        assert len(svgs) > 0, "No SVG elements found"

    def test_svg_diagrams_have_viewbox(self, soup):
        """Verify SVG diagrams use viewBox for scalability"""
        svgs = soup.find_all('svg')

        for svg in svgs:
            # BeautifulSoup is case-insensitive for HTML attributes
            viewbox = svg.get('viewBox') or svg.get('viewbox')
            assert viewbox, f"SVG missing viewBox attribute: {svg.get('id', 'unknown')}"

    def test_required_svg_ids_exist(self, soup):
        """Verify required SVG diagram IDs exist"""
        required_svg_ids = [
            'standard-residual-diagram',
            'comparison-diagram',
            'mechanism-diagram',
            'block-diagram'
        ]

        for svg_id in required_svg_ids:
            svg = soup.find('svg', id=svg_id)
            assert svg is not None, f"Missing SVG with id='{svg_id}'"
