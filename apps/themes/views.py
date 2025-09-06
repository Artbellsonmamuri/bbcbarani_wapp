from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import SiteTheme, ColorPalette, FontFamily, ThemeCustomization
from .forms import SiteThemeForm, ColorPaletteForm, ThemeCustomizationForm


@staff_member_required
def theme_editor(request):
    """Visual theme editor interface"""

    active_theme = SiteTheme.objects.filter(is_active=True).first()
    all_themes = SiteTheme.objects.all().order_by('name')
    color_palettes = ColorPalette.objects.filter(is_active=True).order_by('name')
    font_families = FontFamily.objects.filter(is_active=True).order_by('category', 'name')

    context = {
        'active_theme': active_theme,
        'all_themes': all_themes,
        'color_palettes': color_palettes,
        'font_families': font_families,
    }
    return render(request, 'themes/editor.html', context)


@staff_member_required
def create_theme(request):
    """Create a new theme"""

    if request.method == 'POST':
        form = SiteThemeForm(request.POST, request.FILES)
        if form.is_valid():
            theme = form.save(commit=False)
            theme.created_by = request.user
            theme.save()

            messages.success(request, f'Theme "{theme.name}" created successfully!')
            return redirect('themes:editor')
    else:
        form = SiteThemeForm()

    context = {
        'form': form,
        'color_palettes': ColorPalette.objects.filter(is_active=True),
    }
    return render(request, 'themes/create.html', context)


@staff_member_required
def edit_theme(request, theme_id):
    """Edit an existing theme"""

    theme = get_object_or_404(SiteTheme, id=theme_id)

    if request.method == 'POST':
        form = SiteThemeForm(request.POST, request.FILES, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, f'Theme "{theme.name}" updated successfully!')
            return redirect('themes:editor')
    else:
        form = SiteThemeForm(instance=theme)

    context = {
        'form': form,
        'theme': theme,
        'color_palettes': ColorPalette.objects.filter(is_active=True),
    }
    return render(request, 'themes/edit.html', context)


@staff_member_required
def activate_theme(request, theme_id):
    """Activate a theme"""

    theme = get_object_or_404(SiteTheme, id=theme_id)
    theme.activate()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Theme "{theme.name}" activated successfully!',
            'theme_css': theme.get_compiled_css()
        })

    messages.success(request, f'Theme "{theme.name}" has been activated!')
    return redirect('themes:editor')


@staff_member_required
@csrf_exempt
def save_theme_settings(request):
    """Save theme CSS settings via AJAX"""

    if request.method == 'POST':
        theme_id = request.POST.get('theme_id')
        css_settings = request.POST.get('css_settings')
        custom_css = request.POST.get('custom_css', '')

        try:
            theme = SiteTheme.objects.get(id=theme_id)

            # Parse CSS settings JSON
            if css_settings:
                import json
                theme.css_settings = json.loads(css_settings)

            theme.custom_css = custom_css
            theme.save()

            return JsonResponse({
                'success': True,
                'message': 'Theme settings saved!',
                'compiled_css': theme.get_compiled_css()
            })

        except (SiteTheme.DoesNotExist, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'message': f'Error saving theme: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request'})


@staff_member_required
def theme_preview(request, theme_id):
    """Live preview of theme"""

    theme = get_object_or_404(SiteTheme, id=theme_id)

    # Get preview CSS settings from request or use theme defaults
    preview_settings = request.GET.get('settings')
    if preview_settings:
        import json
        try:
            css_settings = json.loads(preview_settings)
        except json.JSONDecodeError:
            css_settings = theme.css_settings
    else:
        css_settings = theme.css_settings

    # Create temporary theme object for preview
    preview_theme = SiteTheme(
        css_settings=css_settings,
        custom_css=theme.custom_css
    )

    context = {
        'theme': preview_theme,
        'preview_css': preview_theme.get_compiled_css(),
        'is_preview': True,
    }
    return render(request, 'themes/preview.html', context)


def get_active_theme_css(request):
    """Return CSS for the currently active theme"""

    active_theme = SiteTheme.objects.filter(is_active=True).first()

    if active_theme:
        css_content = active_theme.get_compiled_css()
    else:
        css_content = "/* No active theme */"

    from django.http import HttpResponse
    response = HttpResponse(css_content, content_type='text/css')
    response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
    return response


@login_required
def user_theme_customization(request):
    """Allow users to customize their theme preferences"""

    try:
        customization = request.user.theme_customization
    except ThemeCustomization.DoesNotExist:
        # Create default customization
        default_theme = SiteTheme.objects.filter(is_default=True).first()
        if not default_theme:
            default_theme = SiteTheme.objects.filter(is_active=True).first()

        if default_theme:
            customization = ThemeCustomization.objects.create(
                user=request.user,
                theme=default_theme
            )
        else:
            customization = None

    if request.method == 'POST':
        if customization:
            form = ThemeCustomizationForm(request.POST, instance=customization)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your theme preferences have been saved!')
                return redirect('themes:user_customization')

    form = ThemeCustomizationForm(instance=customization) if customization else None

    context = {
        'form': form,
        'customization': customization,
        'available_themes': SiteTheme.objects.all(),
    }
    return render(request, 'themes/user_customization.html', context)
