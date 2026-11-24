# LapiPlan — bilingual study & family planner / Plan nauki i rodziny

**Portfolio:** Junior Data Engineer | Python · SQL · SQLite · Pandas · Streamlit · Pytest · GitHub Actions

LapiPlan is a *local-first* bilingual PL/EN application that helps families plan school classes, extracurricular activities, self-study, family time and free time. It also tracks assignments and study sessions, showing weekly analytics. This is an original sample implementation, not a production-grade multi-tenant SaaS.

LapiPlan to dwujęzyczna aplikacja PL/EN do lokalnego planowania tygodnia: plan lekcji, zajęcia dodatkowe, nauka własna, rodzinne aktywności i wolny czas. Rejestruje zadania i sesje nauki, prezentując tygodniową analizę. Projekt portfolio, nie gotowa publiczna usługa przechowująca dane dzieci.

## Features / Funkcje

- Multiple child profiles / Wiele profili dzieci
- Age-dependent **editable** focus block suggestion / Dostosowywana podpowiedź czasu nauki zależna od wieku
- Recurring Monday–Sunday schedule with conflict detection / Tygodniowy plan z wykrywaniem kolizji
- School, extracurricular, study, family, free and other time blocks / Kategorie aktywności
- Task tracking, study logs and weekly charts / Zadania, dziennik nauki i wykresy
- PL/EN selector / Przełącznik języka
- CSV export, SQLite persistence / Eksport CSV i lokalna baza danych
- Automated Pytest workflow / Automatyczne testy

## Quick start / Uruchomienie

Requires Python 3.11+ (3.12 recommended).

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**. Add a child *nickname* and birthdate. For testing, use fictional data. Open **Weekly schedule / Plan tygodnia** and optionally click **Load demo timetable / Załaduj przykładowy plan**.

### Docker (optional)

```bash
docker compose up --build
```

Data is persisted in the local `data/` folder (excluded from Git).

## Tests / Testy

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

## Data model / Model danych

- `children(id, nickname, birthdate, focus_minutes)`
- `events(id, child_id, weekday, start_time, end_time, title, kind, notes)`
- `study_sessions(id, child_id, session_date, subject, minutes, confidence, notes)`
- `tasks(id, child_id, title, due_date, subject, completed)`

Relationships: `children 1:N events`, `children 1:N study_sessions`, `children 1:N tasks`. Foreign keys and cascaded profile deletion are enabled.

## Data engineering portfolio angle / Kompetencje Data Engineer

- Structured SQL schema, relational constraints, indexes, parametrized statements
- ETL-like pipeline: form inputs → validation → SQLite → Pandas aggregation → charts/CSV
- Data quality validation: durations, allowed category, focus boundaries, duplicate time conflicts at UI level
- Tests, CI, README, synthetic demo schedule

Next steps: CSV lesson import and schema mapping; import error log; Azure Blob for synthetic files; PostgreSQL; scheduled transformations; dbt/SQL transformation tests; anonymized monitoring.

## Privacy, limitations / Prywatność i ograniczenia

**Important:** This is a **single-device demo** without authentication or user separation. **Do not deploy publicly with children's personal data.** The CSV exports and database can contain sensitive family schedules. Use pseudonyms, protect your device, and never commit `data/` to GitHub. A production SaaS would need secure login, per-account authorization, encrypted traffic, backups, retention and deletion policies, and applicable privacy compliance (including GDPR/RODO).

The schedule is a recurring weekly template, not a calendar with exceptions/holidays. It prevents conflicting new events in the UI, but does not prevent clashes with independently logged study sessions or external calendars. All suggested study block lengths are configurable examples, not scientific or clinical recommendations. No AI models are used; the “smart” element is deterministic analytics.

## Roadmap / Rozwój komercyjny

1. MVP: current local-first edition
2. Import/export school timetables and exceptions, account permissions
3. PostgreSQL + secure accounts and tenant isolation
4. Optional Azure pipeline and paid family reports / reminders

## License

MIT — see `LICENSE`.

## Version 2 — ten-year calendar, school assessments and visual themes

- Configurable **Polish / English** UI. Language and holiday country are selected **independently**.
- Calendar dynamically displays the next **10 years starting today** (including all Saturdays and Sundays).
- Holiday regions: **Poland**, **UK England and Wales**, **UK Scotland**, **UK Northern Ireland**, and **US federal** holidays.
- Public-holiday names localized PL/EN; standard recurring holidays, weekend substitutes in UK and observed US federal dates.
- Academic events: quizzes, tests, class exams, group projects, subject olympiads, presentations, assignment deadlines, other events. Dates, optional times, subjects, notes, completion state, CSV export.
- Three selectable design themes: **sky blue/yellow**, **turquoise/beige**, **light green/lilac**; strong headings and readable interface.
- Your existing profiles, study sessions, homework and weekly schedule remain available. Assessment tables are added without deleting the original SQLite tables.

### Important calendar limitations

- UK calendars are distinct by constituent nation. The US calendar lists **federal** holidays, not state or school district holidays. Poland lists statutory dates, but does **not** invent a fixed employer-specific day off in exchange for a Saturday holiday.
- School terms, local school closures, half terms, vacations, teacher-training days and local holidays are **not automatically inferred**. Enter these as custom events / adapt the weekly timetable as needed. The recurring weekly timetable is shown on holidays for reference, **not** as a claim that classes are held on holidays.
- The rules are valid for the known recurring framework as of **17 November 2026**. Governments can announce exceptional bank holidays or change laws in future years. Review the official sources periodically. This is a planning calendar, not a legal guarantee of future days off.
- Polish Easter-related movable feasts use Gregorian Easter. UK substitute holidays and US federal observances are computed programmatically.
- Browser calendar does not synchronize with Google Calendar / Outlook. Local SQLite is not suitable for a publicly available multi-user deployment without login and authorization.

### Official sources to verify changes

- Poland legal holiday statute: https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20250000296/O/D20250296.pdf
- UK bank holidays: https://www.gov.uk/bank-holidays
- US federal holidays: https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/

### Tests

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
```

## LapiPlan pricing / Cennik i wersja przeglądarkowa

- **Browser app / Aplikacja przeglądarkowa:** Streamlit on localhost (NOT an Android APK).
- **Trial / Okres próbny:** 30 days from first launch, stored in local SQLite.
- **Planned premium:** PLN 14.99 per month after 30 days. This is a planned price, not an active subscription.
- **Payments:** Not enabled. The optional `LAPIPLAN_PAYMENT_URL` environment variable can show an HTTPS provider-hosted checkout link, but **does not activate access automatically**. Do not publish a paid version until authentication, Stripe/Paddle or another provider webhook verification, and server-side per-account entitlements are implemented.
- **Security:** Local SQLite trial timestamp can be changed/reset. It is explicitly a pricing UX prototype, not tamper-proof licensing.
- **Export:** Data can still be exported after the 30-day trial; stored records are not erased.
- **Logo:** User-provided icon in `assets/`, also used in Streamlit browser tab and header. No phone home-screen icon is guaranteed unless the user manually adds a browser shortcut.
- **Migration:** If updating a previous install, stop the app, create a backup, and copy `StudyPulse_v2/data/studypulse.sqlite3` (if present) to `LapiPlan_PL_EN/data/lapiplan.sqlite3`. Existing entries are preserved.
