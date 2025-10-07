"""
Context processors for oralsmart project.
Provides common template variables across all views.
"""
from django.urls import reverse, NoReverseMatch
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


def back_url_processor(request):
    """
    Context processor to provide a reliable back URL for templates.
    Uses HTTP_REFERER when available and safe, falls back to home page.
    
    Returns:
        dict: Context dictionary with 'back_url' key
    """
    # Get the referer URL
    referer = request.META.get('HTTP_REFERER')
    back_url = None
    
    if referer:
        try:
            # Parse the referer to ensure it's from the same domain
            referer_parsed = urlparse(referer)
            request_parsed = urlparse(request.build_absolute_uri())
            
            # Only use referer if it's from the same domain (security)
            if referer_parsed.netloc == request_parsed.netloc:
                back_url = referer
        except Exception as e:
            logger.warning(f"Error parsing referer URL: {e}")
    
    # If no valid referer, fall back to home page
    if not back_url:
        back_url = get_safe_home_url()
    
    return {'back_url': back_url}


def get_safe_home_url():
    """
    Get a safe home URL with fallback options.
    
    Returns:
        str: URL to redirect to (home, landing, or root)
    """
    # Try home page first (main authenticated page)
    try:
        return reverse('home')
    except NoReverseMatch:
        pass
    
    # Try landing page (public entry point)
    try:
        return reverse('landing')
    except NoReverseMatch:
        pass
    
    # Ultimate fallback - root path
    return '/'