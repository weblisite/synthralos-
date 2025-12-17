"""
Behavioral Stealth Layer

Implements stealth techniques for web scraping:
- User-Agent rotation
- Timing randomness
- Fingerprint spoofing
- Ghost cursor simulation
- Browser fingerprint randomization
"""

import random
import time
from typing import Any

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except Exception:
    pass


class StealthConfig:
    """
    Configuration for stealth behavior.
    """
    
    def __init__(
        self,
        enable_ua_rotation: bool = True,
        enable_timing_randomness: bool = True,
        enable_fingerprint_spoofing: bool = True,
        enable_ghost_cursor: bool = True,
        min_delay_seconds: float = 1.0,
        max_delay_seconds: float = 3.0,
        ua_rotation_pool_size: int = 50,
    ):
        self.enable_ua_rotation = enable_ua_rotation
        self.enable_timing_randomness = enable_timing_randomness
        self.enable_fingerprint_spoofing = enable_fingerprint_spoofing
        self.enable_ghost_cursor = enable_ghost_cursor
        self.min_delay_seconds = min_delay_seconds
        self.max_delay_seconds = max_delay_seconds
        self.ua_rotation_pool_size = ua_rotation_pool_size


class UserAgentRotator:
    """
    User-Agent rotation service.
    Maintains a pool of realistic user agents and rotates them.
    """
    
    def __init__(self):
        """Initialize user agent rotator."""
        self._user_agents = self._load_user_agents()
        self._current_index = 0
    
    def _load_user_agents(self) -> list[str]:
        """
        Load realistic user agents.
        Includes Chrome, Firefox, Safari, Edge on various platforms.
        """
        return [
            # Chrome on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            
            # Chrome on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Chrome on Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            
            # Firefox on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Firefox on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            
            # Firefox on Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
            
            # Safari on macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            
            # Edge on Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            
            # Mobile Chrome (Android)
            "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            
            # Mobile Safari (iOS)
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        ]
    
    def get_user_agent(self) -> str:
        """
        Get a random user agent from the pool.
        
        Returns:
            User agent string
        """
        return random.choice(self._user_agents)
    
    def rotate_user_agent(self) -> str:
        """
        Rotate to the next user agent in sequence.
        
        Returns:
            User agent string
        """
        self._current_index = (self._current_index + 1) % len(self._user_agents)
        return self._user_agents[self._current_index]


class TimingRandomizer:
    """
    Timing randomization service.
    Adds random delays to mimic human behavior.
    """
    
    def __init__(self, config: StealthConfig):
        """
        Initialize timing randomizer.
        
        Args:
            config: Stealth configuration
        """
        self.config = config
    
    def random_delay(self) -> None:
        """
        Apply a random delay between min and max delay seconds.
        """
        if not self.config.enable_timing_randomness:
            return
        
        delay = random.uniform(
            self.config.min_delay_seconds,
            self.config.max_delay_seconds,
        )
        time.sleep(delay)
    
    def human_like_delay(self, base_seconds: float = 2.0, variance: float = 0.5) -> None:
        """
        Apply a human-like delay with normal distribution.
        
        Args:
            base_seconds: Base delay in seconds
            variance: Variance for normal distribution
        """
        if not self.config.enable_timing_randomness:
            return
        
        delay = max(0.1, random.gauss(base_seconds, variance))
        time.sleep(delay)
    
    def random_idle_time(self, min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
        """
        Random idle time before action (e.g., before clicking).
        
        Args:
            min_seconds: Minimum idle time
            max_seconds: Maximum idle time
        """
        if not self.config.enable_timing_randomness:
            return
        
        idle_time = random.uniform(min_seconds, max_seconds)
        time.sleep(idle_time)


class FingerprintSpoofer:
    """
    Browser fingerprint spoofing service.
    Generates realistic browser fingerprints.
    """
    
    def __init__(self):
        """Initialize fingerprint spoofer."""
        self._screen_resolutions = [
            (1920, 1080),
            (1366, 768),
            (1536, 864),
            (1440, 900),
            (1280, 720),
            (1600, 900),
        ]
        self._timezones = [
            "America/New_York",
            "America/Los_Angeles",
            "America/Chicago",
            "Europe/London",
            "Europe/Paris",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Australia/Sydney",
        ]
        self._languages = [
            "en-US",
            "en-GB",
            "en-CA",
            "fr-FR",
            "de-DE",
            "es-ES",
            "ja-JP",
            "zh-CN",
        ]
    
    def generate_fingerprint(self) -> dict[str, Any]:
        """
        Generate a random browser fingerprint.
        
        Returns:
            Fingerprint dictionary
        """
        width, height = random.choice(self._screen_resolutions)
        
        return {
            "screen_width": width,
            "screen_height": height,
            "timezone": random.choice(self._timezones),
            "language": random.choice(self._languages),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "hardware_concurrency": random.choice([4, 8, 12, 16]),
            "device_memory": random.choice([4, 8, 16]),
            "color_depth": random.choice([24, 32]),
        }
    
    def get_headers(self, user_agent: str, fingerprint: dict[str, Any] | None = None) -> dict[str, str]:
        """
        Generate HTTP headers with fingerprint spoofing.
        
        Args:
            user_agent: User agent string
            fingerprint: Optional fingerprint dictionary
            
        Returns:
            HTTP headers dictionary
        """
        if fingerprint is None:
            fingerprint = self.generate_fingerprint()
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": fingerprint["language"],
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        return headers


class GhostCursorSimulator:
    """
    Ghost cursor simulation service.
    Simulates mouse movements and interactions.
    """
    
    def __init__(self, config: StealthConfig):
        """
        Initialize ghost cursor simulator.
        
        Args:
            config: Stealth configuration
        """
        self.config = config
    
    def simulate_mouse_movement(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        steps: int = 10,
    ) -> list[tuple[int, int]]:
        """
        Generate mouse movement path.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            steps: Number of steps in the path
            
        Returns:
            List of (x, y) coordinates
        """
        if not self.config.enable_ghost_cursor:
            return [(end_x, end_y)]
        
        path = []
        for i in range(steps + 1):
            t = i / steps
            # Use Bezier curve for natural movement
            x = int(start_x + (end_x - start_x) * t)
            y = int(start_y + (end_y - start_y) * t)
            # Add slight randomness
            x += random.randint(-2, 2)
            y += random.randint(-2, 2)
            path.append((x, y))
        
        return path
    
    def simulate_hover(self, element_x: int, element_y: int) -> list[tuple[int, int]]:
        """
        Simulate hovering over an element.
        
        Args:
            element_x: Element X coordinate
            element_y: Element Y coordinate
            
        Returns:
            List of (x, y) coordinates for hover path
        """
        if not self.config.enable_ghost_cursor:
            return [(element_x, element_y)]
        
        # Small random movements around the element
        hover_path = []
        for _ in range(3):
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            hover_path.append((element_x + offset_x, element_y + offset_y))
        
        return hover_path
    
    def simulate_click_preparation(
        self,
        target_x: int,
        target_y: int,
    ) -> list[tuple[int, int]]:
        """
        Simulate mouse movement before clicking.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            List of (x, y) coordinates
        """
        if not self.config.enable_ghost_cursor:
            return [(target_x, target_y)]
        
        # Approach the target with slight overshoot and correction
        approach_x = target_x + random.randint(-3, 3)
        approach_y = target_y + random.randint(-3, 3)
        
        return [
            (approach_x, approach_y),
            (target_x, target_y),
        ]


class StealthService:
    """
    Main stealth service that combines all stealth techniques.
    """
    
    def __init__(self, config: StealthConfig | None = None):
        """
        Initialize stealth service.
        
        Args:
            config: Optional stealth configuration
        """
        self.config = config or StealthConfig()
        self.ua_rotator = UserAgentRotator()
        self.timing_randomizer = TimingRandomizer(self.config)
        self.fingerprint_spoofer = FingerprintSpoofer()
        self.ghost_cursor = GhostCursorSimulator(self.config)
        self._current_fingerprint: dict[str, Any] | None = None
    
    def get_stealth_headers(self) -> dict[str, str]:
        """
        Get HTTP headers with stealth features applied.
        
        Returns:
            HTTP headers dictionary
        """
        user_agent = self.ua_rotator.get_user_agent() if self.config.enable_ua_rotation else self.ua_rotator._user_agents[0]
        
        if self._current_fingerprint is None or self.config.enable_fingerprint_spoofing:
            self._current_fingerprint = self.fingerprint_spoofer.generate_fingerprint()
        
        return self.fingerprint_spoofer.get_headers(user_agent, self._current_fingerprint)
    
    def apply_timing_delay(self) -> None:
        """Apply random timing delay."""
        self.timing_randomizer.random_delay()
    
    def apply_idle_time(self, min_seconds: float = 0.5, max_seconds: float = 2.0) -> None:
        """
        Apply random idle time.
        
        Args:
            min_seconds: Minimum idle time
            max_seconds: Maximum idle time
        """
        self.timing_randomizer.random_idle_time(min_seconds, max_seconds)
    
    def get_mouse_movement_path(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
    ) -> list[tuple[int, int]]:
        """
        Get mouse movement path for ghost cursor simulation.
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            
        Returns:
            List of (x, y) coordinates
        """
        return self.ghost_cursor.simulate_mouse_movement(start_x, start_y, end_x, end_y)
    
    def get_click_preparation_path(self, target_x: int, target_y: int) -> list[tuple[int, int]]:
        """
        Get mouse path for click preparation.
        
        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            
        Returns:
            List of (x, y) coordinates
        """
        return self.ghost_cursor.simulate_click_preparation(target_x, target_y)
    
    def get_fingerprint(self) -> dict[str, Any]:
        """
        Get current browser fingerprint.
        
        Returns:
            Fingerprint dictionary
        """
        if self._current_fingerprint is None:
            self._current_fingerprint = self.fingerprint_spoofer.generate_fingerprint()
        return self._current_fingerprint.copy()
    
    def rotate_user_agent(self) -> str:
        """
        Rotate to next user agent.
        
        Returns:
            New user agent string
        """
        return self.ua_rotator.rotate_user_agent()
    
    def reset_fingerprint(self) -> None:
        """Reset fingerprint (will generate new one on next use)."""
        self._current_fingerprint = None


# Default stealth service instance
default_stealth_service = StealthService()

