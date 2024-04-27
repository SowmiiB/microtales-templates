import pyotp, base64
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile, UserCredentials, Scribes, SavedScribes, LikedScribes, FavouriteAuthor
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from otpauth import TOTP
from tales import constants_and_gadgets as cg
from django.core.files.base import ContentFile
from docx import Document
import io



# Create your views here.

def homepage(request):
    return render(request, 'homepage.html')


def reader_home(request):
    #if request.user.is_authenticated():

    search_query = request.GET.get('search', '')
    print(f'search_query : {search_query}')
    userid = request.session.get('userid')
    if not userid:
        return render(request, 'homepage.html')

    if search_query:
        scribes = Scribes.objects.filter(
            title__icontains=search_query
            )
        if not scribes:
            scribes = Scribes.objects.filter(
            genre__icontains = search_query)

        if not scribes:
            scribes = Scribes.objects.filter(
            language__icontains = search_query)


        print("Filtered Scribes:", scribes)

    else:
        scribes = Scribes.objects.all()

    savedScribes = {}
    for scribe in scribes:
        scribeid = scribe.id
        scribe.saved = SavedScribes.objects.filter(scribeId = scribeid, userId = userid).exists()
    context = {
        'username': request.session.get('username'),
        'userid' : request.session.get('userid'),
        'scribes': scribes,
        'savedScribes' : savedScribes
    }
    return render(request, 'reader_home.html',context )
    #else:
        #messages.info(request, 'User is not yet authenticated!')
        #return redirect('homepage')


def writer_home(request):

    userid = request.session.get('userid')
    if not userid:
        return render(request, 'homepage.html')

    scribes = Scribes.objects.filter(userId=userid)

    context = {
        'username': request.session.get('username'),
        'scribes' : scribes
    }
    return render(request, 'writer_home.html', context)
    #else:
      #  messages.info(request, 'User is not yet authenticated!')
      #  return redirect('homepage')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('confirm_password', '')
        role = request.POST.get('role', '')
        phone = request.POST.get('phone', '')
        credentialid = f'{username}_{email}_{role}'
        if password == password2:
            if not UserCredentials.objects.filter(role=role,username=username).exists():
                if not UserCredentials.objects.filter(role=role,email=email).exists():

                    user = UserCredentials.objects.create_user(
                        email=email,
                        username=username,
                        password=password,
                        role=role,
                        phone=phone,
                        credentialId=credentialid
                    )

                    userid = f'U{user.id}'
                    userprofile = UserProfile(userId=userid,credentialId=user)
                    userprofile.save()

                    login(request, user)

                    request.session['username'] = username
                    request.session['userid'] = userid

                    if user.role == 'writer':
                        return render(request,'writer_home.html')
                    elif user.role == 'reader':
                        return render(request, 'success.html')
                    else:
                        return render(request, 'success.html')

                else:
                    messages.info(request,'Email ID already registered!')
                    return render(request,'register.html')

            else:
                messages.info(request, 'Username already registered!')
                return render(request, 'register.html')
        else:
            messages.info(request, 'Password Mismatch!')
            return render(request, 'register.html')
    else:
        return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = UserCredentials.objects.get(username=username, role=role)
        userid = UserProfile.objects.get(credentialId=user.credentialId)


        if user:
            if user.check_password(password):

                login(request, user)

                otp_secret = pyotp.random_base32()
                otp_secret_bytes = base64.b32encode(otp_secret.encode())
                totp = TOTP(secret=otp_secret_bytes,period=180)
                otp = totp.generate()

                request.session['otp_secret'] = otp
                request.session['username'] = username
                request.session['userid'] = userid.userId

                subject = 'Login OTP'
                html_message = render_to_string('otp_email.html', {'otp': otp})
                plain_message = strip_tags(html_message)
                from_email = 'microtales00@gmail.com'
                to_email = [user.email]
                send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

                return redirect('otp_verification',role,username)
            else:
                messages.error(request, 'Invalid Password!')
                return render(request, 'login.html')

        else:
            messages.error(request, 'Invalid UserName or Role!')
            return render(request, 'login.html')

    return render(request, 'login.html')


def otp_verification(request, role,username):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        otp_secret = request.session.get('otp_secret')

        if not otp_secret:
            return HttpResponse('Invalid request')

        if str(entered_otp) == str(otp_secret):

            if role == 'writer':
                return redirect('writer_home')
            elif role == 'reader':
                return redirect('reader_home')
            else:
                messages.error(request, 'Unknown Role!')
                return render(request, 'login.html')
        else:
            # OTP verification failed
            messages.error(request, 'Invalid OTP. Please try again.')

            return render(request, 'otp_verification.html')

    return render(request, 'otp_verification.html')


def publish_page(request, scribeid = None):
    if scribeid:
        scribe = get_object_or_404(Scribes, id=scribeid)
    else:
        scribe = None
    context = {
        'languages': cg.MOST_SPOKEN_LANGUAGES,
        'genres': cg.GENRES,
        'scribe': scribe,
    }

    return render(request, 'publish.html',context)


def add_book_to_db(request, scribeid=None):
    if request.method == 'POST':
        username = request.session.get('username')
        userid = request.session.get('userid')
        title = request.POST.get('title')
        thumbnail = request.FILES.get('thumbnail')
        write_content = request.POST.get('content')
        doc_upload = request.FILES.get('ebook')
        audio = request.FILES.get('audio')
        genre = request.POST.get('genre')
        language = request.POST.get('language')

        processed_audio = audio


        user = UserProfile.objects.get(userId=userid)

        if scribeid:

            scribe = Scribes.objects.get(id=scribeid)
        else:

            scribe = Scribes()
        print(write_content)
        if not doc_upload and write_content:
            # Convert write content to a document
            doc = Document()
            doc.add_paragraph(write_content)
            doc_bytes = io.BytesIO()
            doc.save(doc_bytes)
            doc_file = ContentFile(doc_bytes.getvalue(), name=f"{title}.docx")
            ebook = doc_file
        else:
            ebook = doc_upload

        scribe.userId = user
        scribe.title = title
        scribe.thumbnail = thumbnail
        scribe.ebook = ebook
        scribe.audio = processed_audio
        scribe.genre = genre
        scribe.language = language

        scribe.save()

        if scribeid:
            messages.info(request, f'Hey! Your scribe "{title}" have been successfully Republished!!')

        else:
            messages.info(request, f'Hey! Your scribe have been successfully Published!!')

        return redirect('writer_home')

    else:
        return redirect('publish_book')


def content_view(request, scribeid=None):
    scribe = Scribes.objects.get(id=scribeid)
    username = request.session.get("username")
    ebook_raw = f'media/{scribe.ebook}'
    text_content, html_content = cg.convert_to_html(f'media/{scribe.ebook}')
    audio_content = cg.audio_manipulator(scribe.audio)
    context = {
        'scribe': scribe,
        'ebook': html_content,
        'audio':audio_content,
        'ebook_raw' : ebook_raw,
    }

    return render(request, 'content.html', context)


def save_for_later(request, scribeid=None):

    user = UserProfile.objects.get(userId=request.session['userid'])
    scribe = Scribes.objects.get(id = scribeid)
    saved_for_later = SavedScribes(scribeId = scribe, userId = user)
    saved_for_later.save()

    return redirect('reader_home')


def add_author_to_fav(request, scribe_id=None):
    print('add_author_to_fav view method started')
    user = UserProfile.objects.get(userId=request.session['userid'])
    authorid = Scribes.objects.get(id=scribe_id).userId.userId
    scribeid = Scribes.objects.get(id=scribe_id)
    print(f'scribeid : {scribeid}')
    already_added = FavouriteAuthor.objects.filter(scribeId=scribeid,readerId=user, authorId=authorid).exists()
    print(f'already_added : {already_added}')

    if already_added:
        fav_author = FavouriteAuthor.objects.get(scribeId=scribe_id,readerId=user, authorId=authorid)
        fav_author.delete()
        return JsonResponse({'added_fav': False})
    else:
        add_to_fav = FavouriteAuthor(scribeId=scribeid,readerId=user, authorId=authorid)
        add_to_fav.save()
        return JsonResponse({'added_fav': True})


def like_scribe(request, scribe_id):

    user = UserProfile.objects.get(userId=request.session['userid'])
    scribe = Scribes.objects.get(id=scribe_id)
    already_liked = LikedScribes.objects.filter(scribeId=scribe, userId=user).exists()
    if already_liked:
        scribe.likes -= 1 if scribe.likes > 0 else 0
        scribe.save()
        liked_scribe = LikedScribes.objects.get(scribeId=scribe, userId=user)
        liked_scribe.delete()
        print(f'scribe likes decremented : {scribe.likes}')
        return JsonResponse({'likes': scribe.likes, 'added_like' : False})

    else:
        scribe.likes += 1
        scribe.save()
        liked_scribe = LikedScribes(scribeId=scribe, userId=user)
        liked_scribe.save()
        print(f'scribe likes incremented : {scribe.likes}')
        return JsonResponse({'likes': scribe.likes, 'added_like' : True})


def view_author(request, scribe_id):
    scribe = Scribes.objects.get(id=scribe_id)
    author = scribe.userId
    print(f'author details : {author.about}')
    context = {
        'author': author
    }

    print(f'user details : {context}')
    return render(request, 'view_author.html',context)


def logout_view(request):
    logout(request)
    return render(request, 'logout.html')


