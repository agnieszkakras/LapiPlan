"""LapiPlan Streamlit app. Start: streamlit run app.py"""
from __future__ import annotations

import io
import calendar
from datetime import date, datetime, time, timedelta
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from lapiplan import db
from lapiplan.calendar_rules import REGIONS, calendar_window, holidays_between, weekend
from lapiplan.demo import seed_schedule
from lapiplan.i18n import translate
from lapiplan.subscription import trial_status
from lapiplan.logic import (
    age_on, completion_rate, conflicts, duration_minutes, suggested_focus_minutes,
    week_bounds,
)

st.set_page_config(page_title="LapiPlan | planowanie nauki na 6.", page_icon=str(Path(__file__).parent / "assets" / "lapiplan_icon_192.png"), layout="wide")
db.init_db()
db.init_assessments()

if "locale" not in st.session_state:
    st.session_state.locale = "PL"
locale = st.sidebar.selectbox("Language / Język", ["PL", "EN"], key="locale")
t = lambda key: translate(locale, key)

if "region" not in st.session_state:
    st.session_state.region = "PL"
if "theme" not in st.session_state:
    st.session_state.theme = "blue"
region = st.sidebar.selectbox(t("country"), REGIONS, format_func=lambda r: t("region_map")[r], key="region")
themes = {"blue":"theme_blue", "teal":"theme_teal", "lilac":"theme_lilac"}
theme = st.sidebar.selectbox(t("theme"), list(themes), format_func=lambda x:t(themes[x]), key="theme")
PALETTES = {
    "blue":("#EAF4FF", "#FFD54F", "#2155F5", "#103357", "#F8FBFF"),
    "teal":("#E5FFFA", "#EFDCC2", "#00A6A6", "#124B56", "#F8FFFD"),
    "lilac":("#F2ECFF", "#D4F7DA", "#8A4DFF", "#2E2350", "#FCFAFF"),
}
base, secondary, accent, ink, surface = PALETTES[theme]
st.markdown(f"""<style>
:root{{--sp-bg:{base};--sp-second:{secondary};--sp-accent:{accent};--sp-ink:{ink};--sp-surface:{surface};}}
html, body, [class*='css'] {{font-family:'Segoe UI',Verdana,Arial,sans-serif;}}
.stApp {{background:radial-gradient(circle at top right, {secondary}22 0%, transparent 26%), linear-gradient(135deg, {surface} 0%, {base} 58%, white 100%);color:{ink};font-size:16px;}}
h1,h2,h3 {{font-weight:900!important;color:{ink}!important;text-decoration:underline;text-decoration-color:{accent};text-underline-offset:7px;letter-spacing:-0.02em;}}
[data-testid='stSidebar'] {{background:linear-gradient(180deg, {secondary} 0%, {base} 100%);border-right:2px solid {accent}33;}}
[data-testid='stMetric'],[data-testid='stForm'],[data-testid='stExpander'],div[data-testid='stVerticalBlockBorderWrapper'], div[data-testid='stAlert'] {{border:1.5px solid {accent}55!important;border-radius:18px!important;box-shadow:0 8px 20px rgba(16,51,87,0.08)!important;}}
[data-testid='stMetric'] {{background:white; padding:10px 12px;}}
.stButton button[kind='primary'] {{background:linear-gradient(90deg, {accent}, {ink});color:white;font-weight:800;border-radius:12px;border:none;}}
.stButton button {{font-weight:700;border-color:{accent};border-radius:12px;}}
.stButton button:hover {{border-color:{ink}; color:{ink};}}
.stSelectbox label, .stRadio label, .stCheckbox label, .stTextInput label, .stDateInput label, .stTimeInput label, .stTextArea label {{font-weight:700!important;color:{ink}!important;}}
[data-testid='stCaptionContainer'] {{color:{ink}!important;}}
.sp-legend {{display:inline-block;border-radius:999px;padding:6px 12px;margin:3px;border:1px solid {accent};font-weight:700;color:{ink};background:white;}}
.lp-hero {{background:linear-gradient(90deg, white 0%, {base} 100%);border:2px solid {accent}33;border-radius:24px;padding:20px 24px;box-shadow:0 12px 30px rgba(16,51,87,0.10);}}
.lp-hero-title {{font-size:2.35rem;font-weight:900;color:{ink};line-height:1.1;margin-bottom:6px;text-decoration:underline;text-decoration-color:{accent};text-underline-offset:8px;}}
.lp-hero-sub {{font-size:1.08rem;font-weight:600;color:{ink};opacity:0.82;}}
.lp-highlight {{background:linear-gradient(90deg, {accent}12, {secondary}42);border-left:6px solid {accent};border-radius:16px;padding:14px 16px;margin:8px 0 16px 0;font-weight:700;color:{ink};}}
</style>""",unsafe_allow_html=True)
title_left, title_right = st.columns([1, 6], vertical_alignment="center")
with title_left:
    st.image(str(Path(__file__).parent / "assets" / "lapiplan_icon_192.png"), width=88)
with title_right:
    st.markdown(f"<div class='lp-hero'><div class='lp-hero-title'>{t('app')}</div><div class='lp-hero-sub'>{t('tagline')}</div></div>", unsafe_allow_html=True)

trial = trial_status()
if trial["active"]:
    st.sidebar.info(t("trial_active").format(days=trial["days_left"]))
else:
    st.sidebar.warning(t("trial_expired"))
st.sidebar.caption(t("subscription_price"))
st.sidebar.caption(t("trial_demo"))


# Local-only trial gate: no real payment collection or production-grade entitlement.
# Users may still export their data after expiry. Secure SaaS deployment requires
# authentication, payment provider webhooks and account-bound entitlements.
if not trial["active"]:
    st.warning(t("trial_expired"))
    st.markdown("**" + t("subscription_price") + "**")
    payment_url = os.getenv("LAPIPLAN_PAYMENT_URL", "").strip()
    if payment_url.startswith("https://"):
        st.link_button(t("subscribe"), payment_url)
    else:
        st.info(t("billing_unavailable"))
    st.info(t("export_after_trial"))
    for profile in db.list_children():
        with st.expander(f"{t('trial_data')}: {profile['nickname']}"):
            for name, dataset in [("events", db.list_events(profile["id"])),
                                  ("sessions", db.list_sessions(profile["id"])),
                                  ("tasks", db.list_tasks(profile["id"])),
                                  ("assessments", db.list_assessments(profile["id"]))]:
                csv = pd.DataFrame(dataset).to_csv(index=False).encode("utf-8-sig")
                st.download_button(f"{t('download')}: {name}", csv, f"lapiplan_{profile['id']}_{name}.csv", "text/csv", key=f"trial_{profile['id']}_{name}")
    st.stop()

profiles = db.list_children()
page = st.sidebar.radio("LapiPlan", [t("dashboard"), t("calendar"), t("assessments"), t("schedule"), t("sessions"), t("tasks"), t("profiles"), t("settings")], captions=[t("dashboard_caption"), t("calendar_caption"), t("assessments_caption"), t("schedule_caption"), t("sessions_caption"), t("tasks_caption"), t("profiles_caption"), t("settings_caption")])

with st.sidebar.expander(t("new_child"), expanded=not bool(profiles)):
    with st.form("new_child_form"):
        nickname = st.text_input(t("name"), max_chars=50)
        birthdate = st.date_input(t("birthdate"), value=date(2014, 1, 1), min_value=date(1990, 1, 1), max_value=date.today())
        focus = st.number_input(t("focus"), 5, 180, value=suggested_focus_minutes(age_on(birthdate.isoformat())))
        st.caption(t("focus_help"))
        if st.form_submit_button(t("save")):
            try:
                db.add_child(nickname, birthdate.isoformat(), int(focus))
                st.success(t("profile_created"))
                st.rerun()
            except ValueError as exc:
                st.error(f"{t('invalid')} {exc}")

if not profiles:
    st.markdown(f"<div class='lp-highlight'>{t('no_profiles')}</div>", unsafe_allow_html=True)
    st.stop()

options = {f"{p['nickname']} (#{p['id']})": p for p in profiles}
selected_label = st.sidebar.selectbox(t("choose_child"), list(options))
child = options[selected_label]
child_id = child["id"]
age = age_on(child["birthdate"])
st.sidebar.caption(f"{t('age')}: {age} | {t('focus')}: {child['focus_minutes']}")


def csv_bytes(data: list[dict]) -> bytes:
    return pd.DataFrame(data).to_csv(index=False).encode("utf-8-sig")


def show_schedule():
    st.subheader(t("event_list"))
    events = db.list_events(child_id)
    if not events:
        st.info(t("no_events"))
    else:
        table = pd.DataFrame([{
            "ID": e["id"], t("day"): t("days")[e["weekday"]],
            t("start"): e["start_time"], t("end"): e["end_time"],
            t("title"): e["title"], t("kind"): t("kinds")[e["kind"]],
            t("notes"): e["notes"] or ""
        } for e in events])
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.download_button(t("download"), csv_bytes(events), f"lapiplan_schedule_{child_id}.csv", "text/csv")
    with st.expander(t("add_event"), expanded=True):
        with st.form("add_event_form"):
            a, b, c = st.columns(3)
            day = a.selectbox(t("day"), list(range(7)), format_func=lambda d: t("days")[d])
            start = b.time_input(t("start"), value=time(16, 0), step=900)
            end = c.time_input(t("end"), value=time(17, 0), step=900)
            title = st.text_input(t("title"), placeholder=t("event_placeholder"))
            kind = st.selectbox(t("kind"), list(t("kinds")), format_func=lambda k: t("kinds")[k])
            notes = st.text_input(t("notes"))
            if st.form_submit_button(t("save")):
                start_s, end_s = start.strftime("%H:%M"), end.strftime("%H:%M")
                try:
                    found = conflicts(events, day, start_s, end_s)
                    if found:
                        st.error(t("conflict") + " " + ", ".join(x["title"] for x in found))
                    else:
                        db.add_event(child_id, day, start_s, end_s, title, kind, notes)
                        st.success(t("event_added"))
                        st.rerun()
                except ValueError as exc:
                    st.error(f"{t('invalid')} {exc}")
    if events:
        with st.expander(t("remove_event")):
            labels = {f"#{e['id']} {t('days')[e['weekday']]} {e['start_time']} {e['title']}": e["id"] for e in events}
            selected = st.selectbox(t("choose"), list(labels), key="remove_event_choice")
            if st.button(t("remove"), key="remove_event_button"):
                db.delete_event(labels[selected], child_id)
                st.rerun()
    if st.button(t("demo")):
        if seed_schedule(child_id):
            st.success(t("demo_success"))
            st.rerun()
        else:
            st.warning(t("existing_demo"))


def show_sessions():
    st.subheader(t("sessions"))
    with st.form("add_session_form"):
        a, b = st.columns(2)
        on_date = a.date_input(t("date"), date.today(), key="session_date")
        subject = b.text_input(t("subject"), placeholder=t("subject_placeholder"))
        c, d = st.columns(2)
        minutes = c.number_input(t("minutes"), min_value=1, max_value=600, value=int(child["focus_minutes"]))
        confidence = d.slider(t("confidence"), 1, 5, 3)
        notes = st.text_input(t("notes"), key="session_notes")
        if st.form_submit_button(t("save")):
            try:
                db.add_session(child_id, on_date.isoformat(), subject, int(minutes), confidence, notes)
                st.success(t("created"))
                st.rerun()
            except ValueError as exc:
                st.error(f"{t('invalid')} {exc}")
    sessions = db.list_sessions(child_id)
    if sessions:
        st.subheader(t("record_history"))
        st.dataframe(pd.DataFrame(sessions).drop(columns=["child_id"], errors="ignore"), hide_index=True, use_container_width=True)
        st.download_button(t("download"), csv_bytes(sessions), f"lapiplan_study_{child_id}.csv", "text/csv")
    else:
        st.info(t("no_sessions"))


def show_tasks():
    st.subheader(t("tasks"))
    with st.form("add_task_form"):
        title = st.text_input(t("title"), placeholder=t("task_placeholder"))
        a, b = st.columns(2)
        due = a.date_input(t("due"), date.today())
        subject = b.text_input(t("subject"), key="task_subject")
        if st.form_submit_button(t("save")):
            try:
                db.add_task(child_id, title, due.isoformat(), subject)
                st.success(t("saved_task"))
                st.rerun()
            except ValueError as exc:
                st.error(f"{t('invalid')} {exc}")
    tasks = db.list_tasks(child_id)
    if not tasks:
        st.info(t("no_tasks"))
    for task in tasks:
        a, b = st.columns([8, 1])
        new_value = a.checkbox(f"{task['title']} — {task['due_date']} ({task['subject']})", value=bool(task["completed"]), key=f"task_{child_id}_{task['id']}")
        if new_value != bool(task["completed"]):
            db.set_task_completed(task["id"], child_id, new_value)
            st.rerun()
        if b.button("×", key=f"delete_task_{child_id}_{task['id']}", help=t("delete_task")):
            db.delete_task(task["id"], child_id)
            st.rerun()
    if tasks:
        st.download_button(t("download"), csv_bytes(tasks), f"lapiplan_tasks_{child_id}.csv", "text/csv")


def show_dashboard():
    monday, sunday = week_bounds(date.today())
    st.subheader(f"{t('report')}: {monday.isoformat()} — {sunday.isoformat()}")
    st.markdown(f"<div class='lp-highlight'>{t('dashboard_welcome').format(name=child['nickname'])}</div>", unsafe_allow_html=True)
    sessions = db.list_sessions(child_id, monday.isoformat(), sunday.isoformat())
    events = db.list_events(child_id)
    tasks = db.list_tasks(child_id)
    total_minutes = sum(s["minutes"] for s in sessions)
    done = sum(bool(x["completed"]) for x in tasks)
    family_free = sum(e["kind"] in ("family", "free") for e in events)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t("weekly_minutes"), total_minutes)
    c2.metric(t("week_sessions"), len(sessions))
    c3.metric(t("task_completion"), f"{completion_rate(done, len(tasks))}%")
    c4.metric(t("free_blocks"), family_free)
    st.info(t("suggestion_text").format(m=child["focus_minutes"]))
    if sessions:
        by_subject = pd.DataFrame(sessions).groupby("subject")["minutes"].sum().sort_values(ascending=False)
        st.markdown("**" + t("charts") + "**")
        st.bar_chart(by_subject)
    else:
        st.caption(t("no_week"))
    if events:
        schedule = pd.DataFrame([{"kind": t("kinds")[e["kind"]], "hours":duration_minutes(e["start_time"], e["end_time"])/60} for e in events])
        st.markdown("**" + t("balance") + "**")
        st.bar_chart(schedule.groupby("kind")["hours"].sum())




def show_assessments():
    st.subheader(t("assessments"))
    first, last = calendar_window()
    with st.form("assessment_form"):
        a,b = st.columns(2)
        event_date = a.date_input(t("assessment_date"), value=date.today(), min_value=first, max_value=last)
        category = b.selectbox(t("assessment_type"), list(t("type_map")), format_func=lambda key:t("type_map")[key])
        a,b = st.columns(2)
        title = a.text_input(t("assessment_title"), max_chars=160)
        subject = b.text_input(t("assessment_subject"), max_chars=80)
        a,b = st.columns(2)
        has_time = a.checkbox(t("assessment_time"), value=False)
        event_time = b.time_input(t("start"), value=time(9,0), disabled=not has_time)
        notes = st.text_area(t("assessment_notes"), max_chars=2000)
        if st.form_submit_button(t("add_assessment")):
            try:
                db.add_assessment(child_id, event_date.isoformat(), category, title, subject,
                                  event_time.strftime("%H:%M") if has_time else "", notes)
                st.success(t("add_assessment_ok"))
                st.rerun()
            except ValueError as exc:
                st.error(f"{t('invalid')} {exc}")
    assessments = db.list_assessments(child_id)
    st.markdown("**"+t("upcoming")+"**")
    upcoming = [a for a in assessments if a["event_date"] >= date.today().isoformat() and not a["completed"]]
    if upcoming:
        st.dataframe(pd.DataFrame([{
            "ID": a["id"],t("date"):a["event_date"],t("start"):a["event_time"],
            t("assessment_type"):t("type_map")[a["category"]],t("title"):a["title"],
            t("subject"):a["subject"],t("notes"):a["notes"]
        } for a in upcoming]),hide_index=True,use_container_width=True)
    else:
        st.info(t("none_day"))
    st.markdown("**"+t("history")+"**")
    for entry in assessments:
        a,b,c=st.columns([8,1,1])
        title_text = f"{entry['event_date']} | {t('type_map')[entry['category']]} | {entry['title']} ({entry['subject']})"
        marked=a.checkbox(title_text,value=bool(entry['completed']),key=f"assess_done_{child_id}_{entry['id']}")
        if marked != bool(entry['completed']):
            db.set_assessment_completed(entry['id'], child_id, marked)
            st.rerun()
        if c.button("×",key=f"assess_delete_{child_id}_{entry['id']}",help=t("delete_assessment")):
            db.delete_assessment(entry['id'],child_id)
            st.rerun()
        if entry['notes']:
            st.caption(entry['notes'])
    if assessments:
        st.download_button(t("assessment_export"),csv_bytes(assessments),f"lapiplan_assessments_{child_id}.csv","text/csv")


def show_calendar():
    st.subheader(t("calendar"))
    first,last=calendar_window()
    st.caption(f"{t('ten_years')}: {first.isoformat()} — {last.isoformat()}")
    if "calendar_selected" not in st.session_state or not(first<=st.session_state.calendar_selected<=last):
        st.session_state.calendar_selected=first
    years=list(range(first.year,last.year+1))
    if "calendar_year" not in st.session_state or st.session_state.calendar_year not in years:
        st.session_state.calendar_year=first.year
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month=first.month
    a,b=st.columns(2)
    year=a.selectbox(t("year"),years,key="calendar_year")
    month=b.selectbox(t("month"),list(range(1,13)),format_func=lambda m:t("month_names")[m-1],key="calendar_month")
    month_start=date(year,month,1)
    month_end=date(year,month,calendar.monthrange(year,month)[1])
    holiday_dates=holidays_between(month_start,month_end,region,locale)
    entries=db.list_assessments(child_id,month_start.isoformat(),month_end.isoformat())
    per_date={}
    for entry in entries:
        per_date.setdefault(entry['event_date'],[]).append(entry)
    weekly=db.list_events(child_id)
    st.markdown(
        f'<span class="sp-legend" style="background:{secondary}">{t("weekend")}</span>'
        f'<span class="sp-legend" style="background:#ffdf84">{t("holiday")}</span>'
        f'<span class="sp-legend" style="background:{base}">{t("planned")}</span>',
        unsafe_allow_html=True)
    st.caption(t("calendar_note"))
    headers=st.columns(7)
    for i,column in enumerate(headers):
        column.markdown("**"+t("days")[i][:3]+"**")
    grid=calendar.Calendar(firstweekday=0).monthdatescalendar(year,month)
    for row in grid:
        columns=st.columns(7,gap="small")
        for col,current in zip(columns,row):
            if current.month!=month or not(first <= current <= last):
                col.markdown("　")
                continue
            holiday=holiday_dates.get(current)
            num=len(per_date.get(current.isoformat(),[]))
            marker=" •" if num else ""
            icon="✦ " if holiday else ("◼ " if weekend(current) else "")
            label=f"{icon}{current.day}{marker}"
            if col.button(label,key=f"day_{current.isoformat()}",use_container_width=True,
                          help=(holiday or t("select_day")),type="primary" if current==st.session_state.calendar_selected else "secondary"):
                st.session_state.calendar_selected=current
                st.rerun()
            if holiday:
                col.caption(holiday)
            if num:
                col.caption(f"{num} × {t('planned').lower()}")
    chosen=st.session_state.calendar_selected
    st.markdown(f"### {t('event_details')}: {chosen.strftime('%d.%m.%Y')}")
    chosen_holidays=holidays_between(chosen,chosen,region,locale)
    if weekend(chosen):
        st.info(t("weekend"))
    if chosen in chosen_holidays:
        st.warning(chosen_holidays[chosen])
    daily= [e for e in weekly if e['weekday']==chosen.weekday()]
    if daily:
        st.markdown("**"+t("day_events")+"**")
        for event in daily:
            st.write(f"{event['start_time']}–{event['end_time']} · {t('kinds')[event['kind']]} · **{event['title']}**")
        if chosen in chosen_holidays:
            st.caption(t("school_warning"))
    assessment_on_day=db.list_assessments(child_id,chosen.isoformat(),chosen.isoformat())
    if assessment_on_day:
        st.markdown("**"+t("assessments")+"**")
        for event in assessment_on_day:
            st.write(f"{'✅ ' if event['completed'] else '📌 '}{t('type_map')[event['category']]} · **{event['title']}** · {event['subject']} {event['event_time']}")
            if event['notes']:
                st.caption(event['notes'])
    if not daily and not assessment_on_day:
        st.caption(t("none_day"))


if page == t("dashboard"):
    show_dashboard()
elif page == t("calendar"):
    show_calendar()
elif page == t("assessments"):
    show_assessments()
elif page == t("schedule"):
    show_schedule()
elif page == t("sessions"):
    show_sessions()
elif page == t("tasks"):
    show_tasks()
elif page == t("profiles"):
    st.subheader(t("profiles"))
    st.dataframe(pd.DataFrame(profiles)[["nickname", "birthdate", "focus_minutes"]], hide_index=True, use_container_width=True)
    st.info(t("suggestion_text").format(m=suggested_focus_minutes(age)))
elif page == t("settings"):
    st.subheader(t("settings"))
    st.warning(t("privacy"))
    with st.expander(t("all_data")):
        for name, dataset in [("events", db.list_events(child_id)), ("sessions", db.list_sessions(child_id)), ("tasks", db.list_tasks(child_id)), ("assessments", db.list_assessments(child_id))]:
            st.download_button(f"{t('download')}: {name}", csv_bytes(dataset), f"lapiplan_{child_id}_{name}.csv", "text/csv", key=f"export_{name}")
    st.divider()
    st.error(t("delete_warning"))
    confirm = st.checkbox(t("delete_confirm"))
    if st.button(t("delete_profile"), disabled=not confirm):
        db.delete_child(child_id)
        st.rerun()
