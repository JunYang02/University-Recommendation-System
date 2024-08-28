from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .forms import PreferenceForm
from system.models import University
from system.models import Major
import base64
from django.core.paginator import Paginator
from django.db.models import Q
import logging
from urllib.parse import urlencode
from django.db.models import IntegerField, Value
from django.db.models.functions import Cast
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
import openai
import os
import json
from django.conf import settings


def home(request):
    return render(request, 'homepage.html')

def Blog1(request):
    return render(request, 'Blog1.html')

def Blog2(request):
    return render(request, 'Blog2.html')

def Blog3(request):
    return render(request, 'Blog3.html')

def Blog4(request):
    return render(request, 'Blog4.html')

def Blog5(request):
    return render(request, 'Blog5.html')

def Sign_in(request):
    return render(request, 'sign_in.html')

VALID_INVITATION_CODES = ['admin001']

@csrf_protect
def admin_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            is_admin = form.cleaned_data.get('is_admin')
            invitation_code = form.cleaned_data.get('invitation_code').strip().lower()

            # Debugging output
            print(f"Received data - Username: {username}, Email: {email}, Password: {password}")
            print(f"Is Admin: {is_admin}, Invitation Code: {invitation_code}")
            print(f"Valid invitation codes: {[code.lower() for code in VALID_INVITATION_CODES]}")

            if is_admin:
                if invitation_code not in [code.lower() for code in VALID_INVITATION_CODES]:
                    form.add_error('invitation_code', 'Invalid invitation code for admin registration')
                    return render(request, 'sign_in.html', {'form': form, 'signin_signup': True})

            user = User.objects.create_user(username=username, email=email, password=password)
            if is_admin:
                user.is_staff = True
                user.is_superuser = True
            user.save()

            # Log the user in immediately after registration
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                auth_login(request, new_user)

            # Redirect based on admin status
            if is_admin:
                return redirect('/admin/')  # Redirect to the Django admin site
            else:
                return redirect('system:main_sys')  # Redirect to the main system URL
        else:
            # Debugging output
            print("Form is not valid")
            for field in form:
                for error in field.errors:
                    print(f"Error in field {field.name}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_in.html', {'form': form, 'signin_signup': True})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Log the user in immediately after registration
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                auth_login(request, new_user)

            return redirect('system:main_sys')  # Redirect to the main system URL
    else:
        form = CustomUserCreationForm()
    return render(request, 'sign_in.html', {'form': form, 'is_sign_up': True})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            if user.is_superuser:
                return redirect('/admin/')  # Redirect to Django admin site
            else:
                return redirect('system:main_sys')  # Redirect to the system frontend
        else:
            return render(request, 'sign_in.html', {'error': 'Invalid username or password'})
    return render(request, 'sign_in.html')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    success_url = reverse_lazy('system:password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('system:homepage')  # Ensure 'system:homepage' is the correct name of your homepage URL pattern

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                if user.is_superuser:
                    return redirect('/admin/')
                else:
                    return redirect('system:main_sys')
    else:
        form = AuthenticationForm()
    return render(request, 'sign_in.html', {'form': form})

def main_view(request):
    return render(request, 'main_sys.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('homepage')

def preference_view(request):
    if request.method == 'POST':
        form = PreferenceForm(request.POST)
        if form.is_valid():
            preferred_major = form.cleaned_data['preferred_major'].id  # Get the id of the selected major
            admission = form.cleaned_data['admission']
            accommodation = form.cleaned_data['accommodation']
            qualification = form.cleaned_data['qualification']
            institution_type = form.cleaned_data['institution_type']

            # Redirect to the filter_university view with the preferences as query parameters
            query_params = {
                'preferred_major': preferred_major,
                'admission': admission,
                'accommodation': accommodation,
                'qualification': qualification,
                'institution_type': institution_type
            }
            url = reverse('system:filter_university') + '?' + urlencode(query_params)
            return HttpResponseRedirect(url)
    else:
        form = PreferenceForm()

    return render(request, 'PreferenceForm.html', {'form': form})

def success_view(request):
    return render(request, 'main_sys.html')

def major_autocomplete(request):
    static_majors = [
        'Accounting', 'Agriculture', 'Applied Science', 'Architecture',
        'Aviation', 'Business', 'Computer Science', 'Education', 
        'Engineering', 'English', 'Health and Medicine', 'Law', 
        'Mass Communication', 'MBA', 'Sports Science'
    ]
    if 'term' in request.GET:
        term = request.GET.get('term').lower()
        suggestions = [major for major in static_majors if term in major.lower()]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)


def university_list(request):
    qualifications = request.GET.get('qualifications', '').split(',')
    institution_type = request.GET.get('institution_type', '')
    major_id = request.GET.get('major_id')
    admission = request.GET.get('admission', '')
    accommodation = request.GET.get('accommodation', '')
    universities = University.objects.all()

    # Adjust filtering to exclude zero values for specified qualifications
    if qualifications and qualifications != ['']:
        qualification_queries = Q()
        for qualification in qualifications:
            if qualification == 'PreU':
                qualification_queries &= Q(PreU__gt=0)
            elif qualification == 'Undergraduate':
                qualification_queries &= Q(Undergraduate__gt=0)
            elif qualification == 'Postgraduate':
                qualification_queries &= Q(Postgraduate__gt=0)
        universities = universities.filter(qualification_queries)

    if institution_type:
        universities = universities.filter(university_type=institution_type)

    if major_id:
        universities = universities.filter(majors__id=major_id)

    if admission:
        universities = universities.filter(admission__icontains=admission)

    if accommodation:
        universities = universities.filter(Accommodation__iexact=accommodation)

    university_data = []
    for university in universities:
        image_data = university.Image
        if image_data:
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            university_image = f"data:image/jpeg;base64,{image_base64}"
        else:
            university_image = None

        university_data.append({
            'name': university.name,
            'university_type': university.university_type,
            'location': university.location,
            'contact_info': university.contact_info,
            'admission': university.admission,
            'faculty': university.faculty,
            'program': university.program,
            'PreU': university.PreU,
            'Undergraduate': university.Undergraduate,
            'Postgraduate': university.Postgraduate,
            'Accommodation': university.Accommodation,
            'Image': university_image,
            'official_page': university.official_page or ''
        })

    # Apply pagination on the prepared university data
    paginator = Paginator(university_data, 20)  # Show 20 universities per page
    page_number = request.GET.get('page', 1)  # Get page number from request, default to 1
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        'universities': list(page_obj.object_list),
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
    })

def score_university(university, preferred_major, admission, accommodation, qualifications, institution_types):
    score = 0
    max_major_score = 25
    max_admission_score = 20
    max_accommodation_score = 10
    max_qualification_score = 15
    max_institution_type_score = 10
    max_ranking_score = 20

    if university.universitymajor_set.filter(major=preferred_major).exists():
        score += max_major_score

    if admission and university.admission and admission.lower() in university.admission.lower():
        score += max_admission_score

    if accommodation and university.Accommodation and accommodation.lower() == university.Accommodation.lower():
        score += max_accommodation_score

    if qualifications:
        for qual in qualifications:
            if qual.lower() in (university.PreU.lower(), university.Undergraduate.lower(), university.Postgraduate.lower()):
                score += max_qualification_score
                break

    if institution_types:
        for inst_type in institution_types:
            if university.university_type and inst_type.lower() in university.university_type.lower():
                score += max_institution_type_score
                break

    try:
        if university.Ranking is not None:
            ranking = int(university.Ranking)
            if ranking <= 1004:
                rank_score = max(100 - ((ranking - 1) / 1004 * 100), 0) * (max_ranking_score / 100)
            else:
                rank_score = 0
            score += round(rank_score, 2)
    except (ValueError, TypeError):
        pass

    if university.Ranking is None or university.Ranking == 1010:
        score = 1

    print(f"University: {university.name}, Score: {score}")

    return score

def filter_university(request):
    if request.method == 'POST':
        form = PreferenceForm(request.POST)
        if form.is_valid():
            preferred_major = form.cleaned_data['preferred_major']
            admission = form.cleaned_data['admission']
            accommodation = form.cleaned_data['accommodation']
            qualification = form.cleaned_data['qualification']
            institution_type = form.cleaned_data['institution_type']

            universities = University.objects.all()

            if qualification:
                qualification_queries = Q()
                if qualification == 'PreU':
                    qualification_queries &= Q(PreU__gt=0)
                elif qualification == 'Undergraduate':
                    qualification_queries &= Q(Undergraduate__gt=0)
                elif qualification == 'Postgraduate':
                    qualification_queries &= Q(Postgraduate__gt=0)
                universities = universities.filter(qualification_queries)

            if institution_type:
                universities = universities.filter(university_type=institution_type)

            if preferred_major:
                universities = universities.filter(majors__id=preferred_major.id)

            if admission:
                universities = universities.filter(admission__icontains=admission)

            if accommodation:
                universities = universities.filter(Accommodation__iexact=accommodation)

            university_data = []
            for university in universities:
                image_data = university.Image
                if image_data:
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    university_image = f"data:image/jpeg;base64,{image_base64}"
                else:
                    university_image = None

                score = score_university(university, preferred_major, admission, accommodation, qualification, institution_type)
                
                Recommendation = university.Recommendation

                university_data.append({
                    'name': university.name,
                    'university_type': university.university_type,
                    'location': university.location,
                    'contact_info': university.contact_info,
                    'admission': university.admission,
                    'faculty': university.faculty,
                    'program': university.program,
                    'PreU': university.PreU,
                    'Undergraduate': university.Undergraduate,
                    'Postgraduate': university.Postgraduate,
                    'Accommodation': university.Accommodation,
                    'Image': university_image,
                    'official_page': university.official_page or '',
                    'score': score,
                    'Recommendation':university.Recommendation
                })

            # Sort university data by score in descending order
            university_data.sort(key=lambda x: x['score'], reverse=True)

            paginator = Paginator(university_data, 20)  # Show 20 universities per page
            page_number = request.GET.get('page', 1)  # Get page number from request, default to 1
            page_obj = paginator.get_page(page_number)

            # Store the top universities in the session for chatbot use
            request.session['top_universities'] = list(page_obj.object_list)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'universities': list(page_obj),
                    'page': page_obj.number,
                    'num_pages': paginator.num_pages
                })
            else:
                return render(request, 'PreferenceForm.html', {'form': form, 'universities': page_obj})
    else:
        form = PreferenceForm()
        return render(request, 'PreferenceForm.html', {'form': form})

@csrf_exempt
def get_universities(request):
    file_path = os.path.join(settings.BASE_DIR, 'system', 'universities.json')
    with open(file_path, 'r') as file:
        universities = json.load(file)
    return JsonResponse({'universities': universities})
    
@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            user_message = user_message.strip().lower()
            if user_message == 'yes':
                # Fetch the top 3 universities from the session
                top_universities = request.session.get('top_universities', [])
                if not top_universities:
                    response_message = "Sorry, there are no top universities to display."
                else:
                    response_message = "Here are the details for the top 3 universities:<br>"
                    for university in top_universities[:3]:
                        response_message += f"Name: {university['name']}<br>Location: {university['location']}<br>Score: {university['score']}<br>Reason: {university['recommendation_reason']}<br>Contact Info: {university['contact_info']}<br>Admission: {university['admission']}<br><br>"
                return JsonResponse({'response': response_message})
            else:
                response_message = "I'm here to help. Please type 'yes' if you need more information about the top 3 results."
                return JsonResponse({'response': response_message})
    return JsonResponse({'response': 'Invalid request'}, status=400)