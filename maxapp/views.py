# views.py
import os
import requests
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Count
from django.contrib.auth.models import User
import urllib.parse

from .models import SearchHistory

# --- API Imports ---
from googleapiclient.discovery import build

# --- Groq AI Helper Functions ---

def get_groq_chat_response(query):
    """Calls the Groq API for a conversational response."""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.GROQ_API_KEY}'
        }
        
        payload = {
            'model': 'llama-3.1-8b-instant',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are Max, a friendly and helpful AI assistant with a playful personality like Stitch. Respond in a casual, conversational way with occasional humor. Keep responses concise and engaging.'
                },
                {
                    'role': 'user',
                    'content': query
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1024
        }
        
        response = requests.post(
            settings.GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"!!! GROQ CHAT ERROR: {response.status_code} - {response.text} !!!")
            return "Ohana means family! 🌺 I'm having a little trouble connecting right now. Try again?"
            
    except Exception as e:
        print(f"!!! GROQ CHAT ERROR: {e} !!!")
        return "Aloha! 🌺 Max here! I'm currently experiencing some cosmic interference. Try again in a moment!"

def get_groq_summary(query):
    """Calls the Groq API for a search summary."""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.GROQ_API_KEY}'
        }
        
        payload = {
            'model': 'llama-3.1-8b-instant',
            'messages': [
                {
                    'role': 'user',
                    'content': f"Provide a fun, concise summary of this search query in one short paragraph with a touch of personality:\n\n{query}"
                }
            ],
            'temperature': 0.3,
            'max_tokens': 512
        }
        
        response = requests.post(
            settings.GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"!!! GROQ SUMMARY ERROR: {response.status_code} - {response.text} !!!")
            return "Let me help you explore this through the search results below! 🌟"
            
    except Exception as e:
        print(f"!!! GROQ SUMMARY ERROR: {e} !!!")
        return "Let me help you explore this through the search results below! 🌟"


# --- Google Search Function with Images ---
def search_google(query, search_type='web'):
    """Calls the Google Search API and returns results with images."""
    try:
        service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
        
        if search_type == 'images':
            res = service.cse().list(
                q=query, 
                cx=settings.GOOGLE_CSE_ID, 
                num=8,
                searchType='image'
            ).execute()
        else:
            res = service.cse().list(
                q=query, 
                cx=settings.GOOGLE_CSE_ID, 
                num=5
            ).execute()
            
        return res
    except Exception as e:
        print(f"!!! GOOGLE API ERROR: {e} !!!")
        return {}


# --- Enhanced App Command Function ---
def handle_app_command(query):
    """Checks if the query is a command to open a web app or play music."""
    query = query.lower().strip()
    
    app_commands = {
        'open youtube': 'https://www.youtube.com',
        'open netflix': 'https://www.netflix.com',
        'open spotify': 'https://open.spotify.com',
        'open google': 'https://www.google.com',
        'open github': 'https://www.github.com',
        'open twitter': 'https://twitter.com',
        'open facebook': 'https://facebook.com',
        'open instagram': 'https://instagram.com',
        'open amazon': 'https://amazon.com',
        'open prime video': 'https://primevideo.com',
        'open hotstar': 'https://hotstar.com',
        'open linkedin': 'https://linkedin.com',
        'open whatsapp': 'https://web.whatsapp.com',
        'open gmail': 'https://gmail.com',
        'open drive': 'https://drive.google.com',
        'open maps': 'https://maps.google.com',
        'open calendar': 'https://calendar.google.com',
        'open chatgpt': 'https://chatgpt.com',
    }

    # Special commands that show content instead of redirecting
    special_commands = {
        'chikaico': 'chikaico',
        'show chikaico': 'chikaico',
        'chika ico': 'chikaico',
    }
    
    music_keywords = ['play', 'song', 'music']
    
    # Check for special commands first
    if query in special_commands:
        return special_commands[query]

    # Check for basic app commands
    if query in app_commands:
        return redirect(app_commands[query])

    # Check for "go to" commands
    if query.startswith('go to '):
        url = query.split('go to ')[-1]
        if not url.startswith('http'):
            url = 'https://' + url
        return redirect(url)

    # Check for "open" commands
    if query.startswith('open '):
        site_name = query.split('open ')[-1]
        if site_name in app_commands:
            return redirect(app_commands[site_name])
        elif site_name in special_commands:
            return special_commands[site_name]
        else:
            # Try to open any website
            if '.' not in site_name:
                site_name = site_name + '.com'
            if not site_name.startswith('http'):
                site_name = 'https://' + site_name
            return redirect(site_name)

    # Check for music commands - FIXED: Only redirect, don't search
    if any(keyword in query for keyword in music_keywords):
        # Extract song name from query
        music_query = query
        
        # Remove common prefixes
        prefixes = ['play', 'play song', 'play music', 'search for', 'find']
        for prefix in prefixes:
            if music_query.startswith(prefix):
                music_query = music_query[len(prefix):].strip()
        
        # Remove "on youtube" suffix
        if music_query.endswith('on youtube'):
            music_query = music_query[:-10].strip()
        
        # Create YouTube search URL - ONLY REDIRECT, DON'T SEARCH
        if music_query:
            youtube_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(music_query)}"
            return redirect(youtube_url)

    return None


# --- Authentication Views ---
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Aloha! 🌺 Registration successful! Welcome to Max AI!')
            return redirect('index')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Aloha, {username}! 🌺 Welcome back to Max AI!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Mahalo! 🌺 You have been logged out successfully.')
    return redirect('login')


# --- Main App View ---
@login_required
def index(request):
    context = {}
    
    # Get user's search history
    user_searches = SearchHistory.objects.filter(user=request.user).order_by('-timestamp')[:10]
    context['user_searches'] = user_searches

    if request.method == 'POST':
        query = request.POST.get('query')
        search_type = request.POST.get('search_type', 'web')
        
        if not query:
            context['error'] = "Please enter a search query."
        else:
            chat_triggers = ['hello', 'hi max', 'hi', 'hello max', 'hey max', 'hey', 'max', 'how are you', 'aloha']
            clean_query = query.lower().strip()

            # --- CHAT LOGIC ---
            if clean_query in chat_triggers:
                SearchHistory.objects.create(query=query, user=request.user)
                context['chat_response'] = get_groq_chat_response(query)
                context['query'] = query
                context['is_chat'] = True

            else:
                # --- APP COMMAND & MUSIC - FIXED: Only redirect, don't search
                app_redirect = handle_app_command(query)
                
                if app_redirect == 'chikaico':
                    # Show ChikaICO image instead of redirecting
                    context['show_chikaico'] = True
                    context['query'] = query
                    SearchHistory.objects.create(query=query, user=request.user)
                    
                elif app_redirect and hasattr(app_redirect, 'url'):
                    # It's a redirect object
                    return app_redirect
                    
                else:
                    # --- NORMAL SEARCH ---
                    SearchHistory.objects.create(query=query, user=request.user)
                    
                    if search_type == 'images':
                        google_results_raw = search_google(query, search_type='images')
                        image_results = []
                        
                        if 'items' in google_results_raw:
                            for item in google_results_raw.get('items', []):
                                image_results.append({
                                    'title': item.get('title'),
                                    'link': item.get('link'),
                                    'thumbnail': item.get('link'),
                                    'image_url': item.get('link'),
                                    'context_link': item.get('image', {}).get('contextLink', '#'),
                                    'display_link': item.get('displayLink', '')
                                })
                        
                        context['image_results'] = image_results
                        context['is_image_search'] = True
                        
                    else:
                        google_results_raw = search_google(query, search_type='web')
                        google_links = []

                        if 'items' in google_results_raw:
                            for item in google_results_raw.get('items', []):
                                thumbnail_url = None
                                if 'pagemap' in item:
                                    if 'cse_thumbnail' in item['pagemap']:
                                        thumbnail_url = item['pagemap']['cse_thumbnail'][0]['src']
                                    elif 'cse_image' in item['pagemap']:
                                        thumbnail_url = item['pagemap']['cse_image'][0]['src']

                                google_links.append({
                                    'title': item.get('title'),
                                    'link': item.get('link'),
                                    'thumbnail': thumbnail_url,
                                    'snippet': item.get('snippet', '')[:200] + '...' if item.get('snippet') else ''
                                })

                        context['google_links'] = google_links
                        context['is_web_search'] = True

                    context['chatgpt_solution'] = get_groq_summary(query)
                    context['query'] = query

    return render(request, 'index.html', context)


# --- Clear History View ---
@login_required
def clear_history(request):
    """Clear user's search history"""
    if request.method == 'POST':
        SearchHistory.objects.filter(user=request.user).delete()
        messages.success(request, 'Search history cleared! 🌟')
    return redirect('index')


# --- Admin View ---
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    all_users = User.objects.annotate(search_count=Count('searchhistory'))
    all_searches = SearchHistory.objects.order_by('-timestamp').select_related('user')[:50]
    total_searches = SearchHistory.objects.count()
    total_users = User.objects.count()

    context = {
        'all_users': all_users,
        'all_searches': all_searches,
        'total_searches': total_searches,
        'total_users': total_users,
    }
    return render(request, 'maxapp/admin_dashboard.html', context)


# --- New Chat View ---
@login_required
def new_chat(request):
    """Clear current chat context and start fresh"""
    messages.info(request, 'Started a new chat! 🌟')
    return redirect('index')