
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.utils import timezone

from datetime import date, timedelta
from .models import User, Session, Subject
from .forms import SessionForm, SubjectForm


# --------------------
# Main Views
# --------------------

@login_required
def dashboard(request):

    # Select the study period and filter the current user's sessions.
    today = timezone.localdate()
    period = request.GET.get("period", "week")

    sessions = Session.objects.filter(owner=request.user)

    if period == "week":
        start_date = today - timedelta(days=today.weekday())
        sessions = sessions.filter(
            date__range=(start_date, today)
        )

    elif period == "month":
        start_date = date(today.year, today.month, 1)
        sessions = sessions.filter(
            date__range=(start_date, today)
        )

    elif period == "all":
        pass

    else:
        period = "week"
        start_date = today - timedelta(days=today.weekday())
        sessions = sessions.filter(
            date__range=(start_date, today)
        )

    # Calculate total study time and number of sessions.
    total_minutes = sessions.aggregate(
        total=Sum("duration_minutes")
    )["total"] or 0

    session_count = sessions.count()

    # Group study time by subject, with the most studied subject first.
    study_time = (
        sessions
        .values("subject_id", "subject__name")
        .annotate(total_minutes=Sum("duration_minutes"))
        .order_by("-total_minutes", "subject_id")
    )

    most_studied = study_time.first()

    # Prepare subject names and durations for the pie chart.
    chart_data = {
        "labels": [],
        "minutes": []
    }

    for subject in study_time:
        chart_data["labels"].append(subject["subject__name"])
        chart_data["minutes"].append(subject["total_minutes"])

    # Return JSON for JavaScript requests; otherwise render the dashboard.
    if request.GET.get("format") == "json":
        return JsonResponse({
            "total_minutes": total_minutes,
            "session_count": session_count,
            "most_studied": (
                most_studied["subject__name"]
                if most_studied else None
            ),
            "most_studied_minutes": (
                most_studied["total_minutes"]
                if most_studied else 0
            ),
            "chart_data": chart_data,
        })

    return render(request, "study/dashboard.html", {
        "period": period,
        "total_minutes": total_minutes,
        "session_count": session_count,
        "study_time": study_time,
        "most_studied": most_studied,
        "chart_data": chart_data,
    })


# --------------------
# Authentication Views
# --------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        # Authenticate the submitted credentials.
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "study/login.html", {
                "message": "Invalid username and/or password."
            })

    else:
        return render(request, "study/login.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Check that both password fields match.
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "study/register.html", {
                "message": "Passwords must match."
            })

        # Create the user and log them in.
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "study/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return redirect("dashboard")

    else:
        return render(request, "study/register.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# --------------------
# Subject Views
# --------------------

@login_required
def subjects(request):

    # Display only subjects belonging to the current user.
    subjects = Subject.objects.filter(
        owner=request.user,
    )

    return render(request, "study/subjects.html", {
        "subjects": subjects,
    })


@login_required
def subjects_new(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)

        if form.is_valid():
            # Assign the current user before saving the subject.
            subject = form.save(commit=False)
            subject.owner = request.user
            subject.save()

            return redirect("subjects")

    else:
        form = SubjectForm()

    return render(request, "study/subjects_new.html", {
        "form": form
    })


@login_required
def subjects_edit(request, id):

    # Return 404 if the subject does not belong to the current user.
    subject = get_object_or_404(
        Subject,
        id=id,
        owner=request.user
    )

    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            return redirect("subjects")

    else:
        form = SubjectForm(instance=subject)

    return render(request, "study/subjects_edit.html", {
        "form": form
    })


@login_required
def subjects_delete(request, id):
    subject = get_object_or_404(
        Subject,
        id=id,
        owner=request.user,
    )

    # Delete only after the confirmation form is submitted.
    if request.method == "POST":
        subject.delete()
        return redirect("subjects")

    return render(request, "study/subjects_delete.html", {
        "subject": subject,
    })


# --------------------
# Session Views
# --------------------

@login_required
def sessions(request):

    # Start with the current user's sessions and available subjects.
    sessions = Session.objects.filter(
        owner=request.user,
    )

    subjects = Subject.objects.filter(owner=request.user)

    # Read optional filters from the URL.
    subject = request.GET.get("subject")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    search = request.GET.get("search")

    if subject:
        sessions = sessions.filter(subject_id=subject)

    if date_from:
        sessions = sessions.filter(date__gte=date_from)

    if date_to:
        sessions = sessions.filter(date__lte=date_to)

    if search:
        sessions = sessions.filter(notes__icontains=search)

    return render(request, "study/sessions.html", {
        "sessions": sessions,
        "subjects": subjects,
        "selected_subject": subject,
    })


@login_required
def sessions_new(request):
    if request.method == "POST":

        # Pass the user so the form offers only their subjects.
        form = SessionForm(request.POST, user=request.user)

        if form.is_valid():
            session = form.save(commit=False)
            session.owner = request.user
            session.save()

            return redirect("sessions")

    else:
        form = SessionForm(user=request.user)

    return render(request, "study/sessions_new.html", {
        "form": form
    })


@login_required
def sessions_edit(request, id):

    # Restrict editing to sessions owned by the current user.
    session = get_object_or_404(
        Session,
        id=id,
        owner=request.user
    )

    if request.method == "POST":
        form = SessionForm(
            request.POST,
            user=request.user,
            instance=session
        )

        if form.is_valid():
            form.save()
            return redirect("sessions")

    else:
        form = SessionForm(user=request.user, instance=session)

    return render(request, "study/sessions_edit.html", {
        "form": form
    })


@login_required
def sessions_delete(request, id):
    session = get_object_or_404(
        Session,
        id=id,
        owner=request.user,
    )

    # Show a confirmation page before deleting the session.
    if request.method == "POST":
        session.delete()
        return redirect("sessions")

    return render(request, "study/sessions_delete.html", {
        "session": session,
    })
