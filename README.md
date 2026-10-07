# StudyLog

StudyLog is a personal study-tracking web application built with Django, JavaScript, HTML, CSS, and Bootstrap. It lets registered users organize their learning into subjects, record individual study sessions, review their history, and see how they distribute their study time. Rather than entering study totals manually, users record the duration of each session and StudyLog calculates the resulting statistics. The dashboard includes a pie chart showing the proportion of study time spent on each subject.

The application is intended for individual use: each account has its own subjects and study sessions. A user can create subjects, add dated sessions with a duration and optional notes, and return later to edit or delete those records. The session history can be filtered by subject, date range, and text contained in the notes. The dashboard can display statistics for the current week, current month, or all recorded time.

## Distinctiveness and Complexity

StudyLog focuses on a specific workflow: recording learning activities and turning them into a useful personal summary. The main interaction is to log how long a person studied, then use those entries to understand where their time went. Although the application includes create, read, update, and delete operations, those operations support a study-tracking workflow rather than being the application's only functionality.

The relationship between subjects and sessions is important to the design. Each session references one subject and stores a date, duration in minutes, and optional notes. Subjects and sessions are also associated with their owner. This makes it possible to group multiple study sessions under a subject, show the corresponding history, and calculate per-subject totals. Subject names must be unique within a single user's account, while different users can create subjects with the same name. Session durations are validated to require a positive value. The session form also limits its subject choices to subjects owned by the signed-in user.

Keeping users' data separate adds another layer beyond a shared list of records. The subject and session list views filter records by the current user, while edit and delete views look up objects using both their ID and owner. The form for adding or editing a session restricts the available subjects to the current user's subjects. These checks matter because hiding another user's records in the interface is not enough: direct requests to edit or delete URLs must also be restricted. Django's authentication system provides registration, login, logout, and protection for the private study pages.

StudyLog also performs calculations on stored data. Its dashboard filters sessions according to a selected period and uses Django database aggregation to calculate total minutes, number of sessions, and minutes grouped by subject. It identifies the subject with the highest total for that period, and it handles the case where there are no sessions. The current-week option covers Monday through today; the current-month option covers the first day of the month through today; and the all-time option includes all recorded sessions for the signed-in user.

The dashboard combines Django and client-side JavaScript rather than requiring a full reload whenever the user changes periods. A normal request renders the initial HTML and embeds the initial chart data as JSON. When the user clicks a period selector, JavaScript uses `fetch()` to request updated statistics in JSON format from the same Django view. It then replaces the displayed figures and subject breakdown, updates the selected button, and refreshes a Chart.js pie chart. The JavaScript also tracks the latest request so that an older response cannot overwrite the result of a more recent period selection. The ordinary period links remain usable if JavaScript is unavailable.

The interface uses Bootstrap's responsive grid, forms, and cards, with custom pastel colours defined in the stylesheet. Dashboard cards and session and subject cards change their arrangement according to screen width. The chart is placed in a width-limited container so that it does not fill the entire screen on large displays. Together, the relational data model, per-user access restrictions, search and date filtering, server-side calculations, and asynchronous chart updates make StudyLog more than a static page or a single CRUD form.

## Features

- **Accounts:** Register, log in, and log out using Django authentication.
- **Subjects:** Create, view, edit, and delete subjects with a name and optional description.
- **Study sessions:** Record a subject, date, duration in minutes, and optional notes; edit or delete existing sessions.
- **Session history:** Filter entries by subject, starting date, ending date, and text in their notes.
- **Dashboard:** View total study minutes, session count, most-studied subject, a per-subject breakdown, and an interactive pie chart for this week, this month, or all time.
- **Responsive interface:** Use the application on different screen sizes with Bootstrap-based layouts.

## Project Files

The following describes the files and templates used by the project. Standard Django-generated files provide the project scaffolding and configuration.

### Project-level files

- `manage.py` — Django's command-line entry point for running the development server and database commands.
- `studylog/settings.py` — Project configuration, including installed apps, templates, database, and static-file settings.
- `studylog/urls.py` — The project-level URL configuration, which connects requests to the `study` application.
- `studylog/asgi.py` and `studylog/wsgi.py` — Standard Django application entry points.
- `README.md` — Project documentation and setup instructions.
- `requirements.txt`, if included — Python packages needed to install the project in a fresh environment.

### `study/` application

- `apps.py` — Django application configuration.
- `models.py` — Defines the `Subject` and `Session` models, their ownership and relationship fields, the unique-subject constraint, and positive-duration validation.
- `forms.py` — Defines model forms for subjects and sessions, Bootstrap-compatible widgets, and the user-specific subject choices for session forms.
- `views.py` — Handles authentication, subject and session operations, session-history filters, and dashboard aggregation and JSON responses.
- `urls.py` — Maps the application's named URL routes to its views.
- `admin.py` — Django admin configuration; no custom model registration is required for the application's user-facing workflow.
- `tests.py` — Django test module; automated tests have not been added to the supplied version.
- `migrations/` — Django database migration files generated for the application models.

### `study/templates/study/`

- `layout.html` — Shared HTML document, Bootstrap and stylesheet links, navigation, and template content block.
- `dashboard.html` — Period selectors, statistics cards, per-subject totals, pie-chart canvas, and initial JSON data.
- `login.html` and `register.html` — Authentication forms.
- `subjects.html` — Subject listing and links to add, edit, or delete subjects.
- `subjects_new.html`, `subjects_edit.html`, and `subjects_delete.html` — Subject form and deletion-confirmation pages.
- `sessions.html` — Session listing and subject, date, and notes filters.
- `sessions_new.html`, `sessions_edit.html`, and `sessions_delete.html` — Session form and deletion-confirmation pages.

### `study/static/study/`

- `styles.css` — Custom pastel colours for the page, forms, cards, and buttons.
- `dashboard.js` — Creates the Chart.js pie chart, assigns slice colours, fetches period-specific data, and updates the dashboard without a page reload.

## How to Run the Application

The following commands assume Python is installed and are run from the directory containing `manage.py`.

1. Obtain the project files and open a terminal in the project directory.
2. Create and activate a virtual environment if desired:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activate it with `.venv\Scripts\activate` instead.

3. Install dependencies. If the submitted project includes `requirements.txt`, run:

   ```bash
   python -m pip install -r requirements.txt
   ```

   Otherwise, install a compatible version of Django:

   ```bash
   python -m pip install Django
   ```

4. Apply the database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start Django's development server:

   ```bash
   python manage.py runserver
   ```

6. Open the URL shown in the terminal, normally `http://127.0.0.1:8000/`. Register a user, create a subject, and add a study session to populate the dashboard.

Bootstrap and Chart.js are loaded from CDN URLs in the templates, so the browser needs an internet connection to load those assets. They are JavaScript/CSS resources, not Python packages installed using `pip`.

## Additional Notes

Study time is stored and displayed in minutes. Dashboard totals reflect the sessions belonging to the signed-in user and the selected period; the most-studied subject is calculated from those same filtered sessions. Empty periods display zero totals or an empty-state message. Deleting a subject also deletes its related sessions because the session-to-subject relationship uses Django's `CASCADE` deletion behavior; users should take that into account when confirming a subject deletion.

The application is a coursework project intended to run with Django's development server. It has no external account integration or background jobs. Its interactive dashboard uses the same Django endpoint for initial HTML and subsequent JSON requests; no separate API service is needed.
