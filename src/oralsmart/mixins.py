"""
Mixins for oralsmart project views.
Provides reusable functionality for common view patterns.
"""
from django.urls import reverse, NoReverseMatch
from urllib.parse import urlparse
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BackUrlMixin:
    """
    Mixin to provide back_url in view context.
    Use this when you need more control over the back URL logic per view.
    
    Usage:
        class MyDetailView(BackUrlMixin, DetailView):
            model = MyModel
            default_back_url = 'my_list_view'  # Optional specific fallback
    
    Note: This mixin should be used with Django class-based views that have
    request attribute and get_context_data method.
    """
    default_back_url: Optional[str] = None  # Override in your view for specific fallback
    
    def get_back_url(self) -> str:
        """
        Get the back URL for this view.
        
        Returns:
            str: URL to navigate back to
        """
        # Type ignore because this mixin is designed to be used with Django views
        request = getattr(self, 'request', None)  # type: ignore
        if not request:
            return self.get_safe_home_url()
            
        referer = request.META.get('HTTP_REFERER')
        
        if referer:
            try:
                # Security check - same domain only
                referer_parsed = urlparse(referer)
                request_parsed = urlparse(request.build_absolute_uri())
                
                if referer_parsed.netloc == request_parsed.netloc:
                    return referer
            except Exception as e:
                logger.warning(f"Error processing referer: {e}")
        
        # Use view-specific fallback if available
        if self.default_back_url:
            try:
                return reverse(self.default_back_url)
            except NoReverseMatch:
                logger.warning(f"Could not reverse URL name: {self.default_back_url}")
        
        # Fall back to safe home URL
        return self.get_safe_home_url()
    
    def get_safe_home_url(self) -> str:
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
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Add back_url to context data.
        """
        # Get context from parent class
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(**kwargs)  # type: ignore
        else:
            context = {}
            
        context['back_url'] = self.get_back_url()
        return context


class NavigationHistoryMixin:
    """
    Mixin to track navigation history in session.
    Provides more reliable back navigation by storing URL history.
    
    Usage:
        class MyView(NavigationHistoryMixin, TemplateView):
            template_name = 'my_template.html'
    
    Note: This mixin should be used with Django class-based views that have
    request attribute, dispatch method, and get_context_data method.
    """
    
    def dispatch(self, request, *args: Any, **kwargs: Any):
        """
        Track navigation history before processing the view.
        """
        # Don't track AJAX requests, static files, or admin
        if (not request.headers.get('X-Requested-With') == 'XMLHttpRequest' and 
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/') and
            not request.path.startswith('/admin/')):
            
            # Initialize history if not exists
            if 'nav_history' not in request.session:
                request.session['nav_history'] = []
            
            # Add current URL to history (max 5 entries for memory efficiency)
            history = request.session['nav_history']
            current_url = request.get_full_path()
            
            # Don't add duplicate consecutive URLs
            if not history or history[-1] != current_url:
                history.append(current_url)
                if len(history) > 5:
                    history.pop(0)
                request.session['nav_history'] = history
                request.session.modified = True
        
        # Call parent dispatch method
        if hasattr(super(), 'dispatch'):
            return super().dispatch(request, *args, **kwargs)  # type: ignore
        else:
            # Fallback for when used incorrectly
            from django.http import HttpResponse
            return HttpResponse("This mixin requires a Django view class")
    
    def get_back_url_from_history(self) -> Optional[str]:
        """
        Get back URL from session history.
        
        Returns:
            str or None: Previous URL from history or None if not available
        """
        request = getattr(self, 'request', None)
        if not request:
            return None
            
        history = request.session.get('nav_history', [])
        if len(history) >= 2:
            return history[-2]  # Previous page (second to last)
        return None
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Add navigation context to template.
        """
        # Get context from parent class
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(**kwargs)  # type: ignore
        else:
            context = {}
        
        # Try history first, then fallback to referer
        back_url = self.get_back_url_from_history()
        if not back_url and hasattr(self, 'get_back_url'):
            back_url = getattr(self, 'get_back_url')()  # type: ignore
        elif not back_url:
            # Use the context processor function directly
            from oralsmart.context_processors import get_safe_home_url
            back_url = get_safe_home_url()
        
        context['back_url'] = back_url
        
        # Add navigation history to context
        request = getattr(self, 'request', None)
        if request:
            context['nav_history'] = request.session.get('nav_history', [])
        else:
            context['nav_history'] = []
            
        return context