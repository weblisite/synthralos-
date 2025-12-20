"""
Selector Auto-Fix

Automatically fixes broken CSS/XPath selectors in scraping and browser automation tasks.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class SelectorAutoFix:
    """
    Selector auto-fix service for repairing broken selectors.

    Provides:
    - CSS selector validation and repair
    - XPath selector validation and repair
    - Alternative selector generation
    - Selector fallback strategies
    """

    def __init__(self):
        """Initialize selector auto-fix service."""
        pass

    def fix_selector(
        self,
        selector: str,
        selector_type: str = "css",
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Attempt to fix a broken selector.

        Args:
            selector: The broken selector
            selector_type: "css" or "xpath"
            context: Optional context (HTML, page structure, etc.)

        Returns:
            Dictionary with fixed selector and alternatives
        """
        if selector_type == "css":
            return self._fix_css_selector(selector, context)
        elif selector_type == "xpath":
            return self._fix_xpath_selector(selector, context)
        else:
            return {
                "success": False,
                "reason": f"Unknown selector type: {selector_type}",
            }

    def _fix_css_selector(
        self,
        selector: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Fix a broken CSS selector.

        Args:
            selector: Broken CSS selector
            context: Optional context

        Returns:
            Fixed selector result
        """
        fixed = selector
        alternatives = []

        # Common CSS selector fixes
        # Remove invalid characters
        fixed = re.sub(r"[^\w\s\-_\[\]\(\):\.#]", "", fixed)

        # Fix common issues
        # Remove leading/trailing spaces
        fixed = fixed.strip()

        # Ensure proper format for common patterns
        if fixed.startswith("//"):
            # Looks like XPath, convert to CSS
            fixed = self._xpath_to_css(fixed)

        # Generate alternatives
        alternatives = self._generate_css_alternatives(fixed, context)

        return {
            "success": True,
            "fixed_selector": fixed,
            "alternatives": alternatives,
            "original": selector,
        }

    def _fix_xpath_selector(
        self,
        selector: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Fix a broken XPath selector.

        Args:
            selector: Broken XPath selector
            context: Optional context

        Returns:
            Fixed selector result
        """
        fixed = selector
        alternatives = []

        # Common XPath fixes
        # Ensure starts with // or /
        if not fixed.startswith(("//", "/", ".//")):
            fixed = f"//{fixed}"

        # Remove invalid characters (keep XPath syntax)
        fixed = re.sub(r"[^\w\s\-_\[\]\(\):@\.\/=]", "", fixed)

        # Generate alternatives
        alternatives = self._generate_xpath_alternatives(fixed, context)

        return {
            "success": True,
            "fixed_selector": fixed,
            "alternatives": alternatives,
            "original": selector,
        }

    def _xpath_to_css(self, xpath: str) -> str:
        """
        Convert XPath to CSS selector (simplified).

        Args:
            xpath: XPath selector

        Returns:
            CSS selector
        """
        # Simplified conversion - full implementation would handle all XPath patterns
        css = xpath

        # Replace common XPath patterns with CSS equivalents
        css = css.replace("//", "")
        css = css.replace("/", " > ")
        css = css.replace("[@", "[")
        css = css.replace("text()", "")

        return css.strip()

    def _generate_css_alternatives(
        self,
        selector: str,
        context: dict[str, Any] | None = None,
    ) -> list[str]:
        """
        Generate alternative CSS selectors.

        Args:
            selector: Original selector
            context: Optional context

        Returns:
            List of alternative selectors
        """
        alternatives = []

        # Strategy 1: More specific selector
        if not selector.startswith("#") and not selector.startswith("."):
            # Try adding common class/id patterns
            alternatives.append(f"[data-testid='{selector}']")
            alternatives.append(f".{selector.replace(' ', '-')}")

        # Strategy 2: Less specific selector (parent)
        parts = selector.split(" > ")
        if len(parts) > 1:
            alternatives.append(parts[-1])  # Just the last part

        # Strategy 3: Attribute-based selector
        if "[" not in selector:
            alternatives.append(f"[id*='{selector}']")
            alternatives.append(f"[class*='{selector}']")

        return alternatives[:3]  # Return top 3 alternatives

    def _generate_xpath_alternatives(
        self,
        selector: str,
        context: dict[str, Any] | None = None,
    ) -> list[str]:
        """
        Generate alternative XPath selectors.

        Args:
            selector: Original selector
            context: Optional context

        Returns:
            List of alternative selectors
        """
        alternatives = []

        # Strategy 1: More generic XPath
        if "//" in selector:
            # Try with contains() for partial matching
            element = selector.split("//")[-1].split("[")[0]
            alternatives.append(f"//{element}[contains(@class, '{element}')]")
            alternatives.append(f"//{element}[contains(@id, '{element}')]")

        # Strategy 2: Text-based XPath
        alternatives.append(f"//*[contains(text(), '{selector.split('//')[-1]}')]")

        return alternatives[:3]  # Return top 3 alternatives

    def validate_selector(
        self,
        selector: str,
        selector_type: str = "css",
    ) -> tuple[bool, str | None]:
        """
        Validate a selector format.

        Args:
            selector: Selector to validate
            selector_type: "css" or "xpath"

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selector or not selector.strip():
            return False, "Selector is empty"

        if selector_type == "css":
            # Basic CSS validation
            # Check for balanced brackets
            if selector.count("[") != selector.count("]"):
                return False, "Unbalanced brackets in CSS selector"
            if selector.count("(") != selector.count(")"):
                return False, "Unbalanced parentheses in CSS selector"

        elif selector_type == "xpath":
            # Basic XPath validation
            if not selector.startswith(("//", "/", ".//", "@")):
                return False, "Invalid XPath format (must start with //, /, .//, or @)"

        return True, None
