import streamlit as st
import json
import os
import calendar
import uuid
from datetime import date,datetime,timedelta,time
st.set_page_config(
    page_title="Student Assistant",
    page_icon="🎓",
    layout="wide"
)
DATA_FILE = "classes.json"
# -------------------------
# LOAD SAVED CLASSES
# -------------------------
if "classes" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            st.session_state.classes = json.load(file)
    else:
        st.session_state.classes = []
# -------------------------
# CHECK IF CLASS IS ACTIVE ON A DATE
# -------------------------
def is_class_active_on_date(c, current_date):
    date_string = current_date.strftime("%Y-%m-%d")
    # SPECIFIC DATE CLASS
    if c.get("type") == "specific":
        return (
            c.get("date") == date_string
        )
    # WEEKLY CLASS
    if c.get("type") == "weekly":
        return (
            c.get("day") == current_date.strftime("%A")
            and date_string not in c.get(
                "deleted_dates",
                []
            )
        )
    return False
def save_classes():
    with open(DATA_FILE, "w") as file:
        json.dump(st.session_state.classes, file, indent=4)

# Add attendance fields to classes already saved in classes.json.
# This is a one-time migration and does not remove or replace existing class data.
missing_attendance_fields = False
for saved_class in st.session_state.classes:
    if not saved_class.get("attendance_id"):
        saved_class["attendance_id"] = uuid.uuid4().hex
        missing_attendance_fields = True
    if "attended_dates" not in saved_class:
        saved_class["attended_dates"] = []
        missing_attendance_fields = True
if missing_attendance_fields:
    save_classes()

def update_attendance(class_id, occurrence_date, widget_key):
    """Save attendance for one class occurrence and sync both views."""
    checked = bool(st.session_state.get(widget_key, False))
    occurrence_dates = []
    for saved_class in st.session_state.classes:
        if saved_class.get("attendance_id") == class_id:
            occurrence_dates = saved_class.setdefault("attended_dates", [])
            break
    if checked and occurrence_date not in occurrence_dates:
        occurrence_dates.append(occurrence_date)
    elif not checked and occurrence_date in occurrence_dates:
        occurrence_dates.remove(occurrence_date)
    save_classes()

# -------------------------
# TITLE
# -------------------------

# -------------------------
# CLASS COMPASS — VISUAL THEME
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&family=Space+Mono:wght@400;700&display=swap');
:root {
  --cc-ink: #243b39;
  --cc-green: #28645b;
  --cc-green-soft: #e6eee5;
  --cc-paper: #f7f5ed;
  --cc-card: #fffaf0;
  --cc-line: #e4dfd1;
  --cc-muted: #78837c;
}
.stApp { background: radial-gradient(ellipse at 88% 4%, #e8ecdf 0, transparent 28%), var(--cc-paper); color: var(--cc-ink); }
.block-container { max-width: 1600px; padding-top: 1.4rem; padding-bottom: 3rem; }
html, body, [class*="css"], [data-testid="stMarkdownContainer"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3, [data-testid="stHeading"] { font-family: 'Playfair Display', Georgia, serif !important; color: var(--cc-ink) !important; letter-spacing: -0.025em; }
h1 { font-size: clamp(2.3rem, 4vw, 4rem) !important; line-height: 1.04 !important; }
h2 { font-size: 1.8rem !important; }
h3 { font-size: 1.25rem !important; }
[data-testid="stCaptionContainer"], label, .cc-eyebrow { color: var(--cc-muted); }
[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,250,240,.72); border: 1px solid var(--cc-line); border-radius: 20px; padding: 1rem; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button { border-radius: 12px; border: 1px solid #d9e0d5; font-weight: 600; min-height: 2.6rem; }
[data-testid="stButton"] button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] { background: var(--cc-green); color: white; border-color: var(--cc-green); }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] div[data-baseweb="select"], [data-testid="stDateInput"] input, [data-testid="stTimeInput"] input, textarea { background: #f8f6ee !important; border-color: var(--cc-line) !important; border-radius: 11px !important; }
[data-testid="stAlert"] { border-radius: 14px; }
hr { border-color: var(--cc-line); }
.cc-brand { display:flex; align-items:center; gap:12px; font-weight:700; font-size:1.05rem; color:var(--cc-ink); margin-bottom:2.2rem; }
.cc-brand-icon { display:inline-flex; align-items:center; justify-content:center; width:42px; height:42px; border-radius:14px; background:var(--cc-green); color:white; font-size:1.25rem; }
.cc-eyebrow { font-family:'Space Mono', monospace; text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:700; color:#568177; margin-bottom:.7rem; }
.cc-intro { color:#75817a; font-size:1rem; max-width:390px; padding-top:3.2rem; line-height:1.7; }
.cc-date-pill { display:inline-block; border:1px solid var(--cc-line); background:rgba(255,250,240,.8); border-radius:99px; padding:.6rem 1rem; color:#6c7a72; font-size:.85rem; }
@media(max-width: 900px) { .cc-intro { padding-top:0; } .block-container { padding-left:1rem; padding-right:1rem; } }
</style>
""", unsafe_allow_html=True)
st.markdown(
    '<div class="cc-brand"><span class="cc-brand-icon">▦</span> class compass</div>'
    '<div class="cc-eyebrow">YOUR WEEK, IN ONE PLACE</div>',
    unsafe_allow_html=True
)
st.title("A little more room to think.")
st.markdown(
    '<p style="color:#75817a;max-width:540px;font-size:1rem;line-height:1.7;margin-top:-.5rem;margin-bottom:1.6rem;">Your classes, the next place to be, and a clearer view of the week ahead. One less thing to keep in your head.</p>',
    unsafe_allow_html=True
)


# -------------------------
# SCHEDULE CONFLICT ALERT
# -------------------------
# -------------------------
# CONVERT TIME TO MINUTES
# -------------------------
def time_to_minutes(time_string):
    try:
        time_obj = datetime.strptime(
            time_string,
            "%I:%M %p"
        ).time()
        return (
            time_obj.hour * 60
            + time_obj.minute
        )
    except ValueError:
        return None
# -------------------------
# CHECK TIME OVERLAP
# -------------------------
def classes_overlap(class_1, class_2):
    start_1 = time_to_minutes(
        class_1["start"]
    )
    end_1 = time_to_minutes(
        class_1["end"]
    )
    start_2 = time_to_minutes(
        class_2["start"]
    )
    end_2 = time_to_minutes(
        class_2["end"]
    )
    if None in (
        start_1,
        end_1,
        start_2,
        end_2
    ):
        return False
    return (
        start_1 < end_2
        and start_2 < end_1
    )
# -------------------------
# FIND OVERLAPPING PERIOD
# -------------------------
def get_overlap_time(
    class_1,
    class_2
):
    start_1 = time_to_minutes(
        class_1["start"]
    )
    end_1 = time_to_minutes(
        class_1["end"]
    )
    start_2 = time_to_minutes(
        class_2["start"]
    )
    end_2 = time_to_minutes(
        class_2["end"]
    )
    overlap_start = max(
        start_1,
        start_2
    )
    overlap_end = min(
        end_1,
        end_2
    )
    start_time = (
        datetime.min
        + timedelta(
            minutes=overlap_start
        )
    ).strftime("%I:%M %p")
    end_time = (
        datetime.min
        + timedelta(
            minutes=overlap_end
        )
    ).strftime("%I:%M %p")
    return start_time, end_time
# -------------------------
# CHECK WHETHER CLASSES
# CAN OCCUR ON SAME DAY
# -------------------------
def same_schedule_day(
    class_1,
    class_2
):
    type_1 = class_1.get("type")
    type_2 = class_2.get("type")
    # BOTH WEEKLY
    if (
        type_1 == "weekly"
        and type_2 == "weekly"
    ):
        return (
            class_1.get("day")
            == class_2.get("day")
        )
    # BOTH SPECIFIC DATE
    if (
        type_1 == "specific"
        and type_2 == "specific"
    ):
        return (
            class_1.get("date")
            == class_2.get("date")
        )
    # WEEKLY + SPECIFIC DATE
    if (
        type_1 == "weekly"
        and type_2 == "specific"
    ):
        try:
            specific_date = (
                datetime.strptime(
                    class_2["date"],
                    "%Y-%m-%d"
                ).date()
            )
            return (
                class_1.get("day")
                == specific_date.strftime("%A")
            )
        except ValueError:
            return False
    # SPECIFIC DATE + WEEKLY
    if (
        type_1 == "specific"
        and type_2 == "weekly"
    ):
        try:
            specific_date = (
                datetime.strptime(
                    class_1["date"],
                    "%Y-%m-%d"
                ).date()
            )
            return (
                specific_date.strftime("%A")
                == class_2.get("day")
            )
        except ValueError:
            return False
    return False
# -------------------------
# GET CONFLICT DAY
# -------------------------
def get_conflict_day(
    class_1,
    class_2
):
    type_1 = class_1.get("type")
    type_2 = class_2.get("type")
    # SPECIFIC + SPECIFIC
    if (
        type_1 == "specific"
        and type_2 == "specific"
    ):
        try:
            conflict_date = (
                datetime.strptime(
                    class_1["date"],
                    "%Y-%m-%d"
                ).date()
            )
            return conflict_date.strftime(
                "%A, %d %B %Y"
            )
        except ValueError:
            return "the same date"
    # WEEKLY + SPECIFIC
    if (
        type_1 == "weekly"
        and type_2 == "specific"
    ):
        try:
            conflict_date = (
                datetime.strptime(
                    class_2["date"],
                    "%Y-%m-%d"
                ).date()
            )
            return conflict_date.strftime(
                "%A, %d %B %Y"
            )
        except ValueError:
            return class_1.get(
                "day",
                "the same day"
            )
    # SPECIFIC + WEEKLY
    if (
        type_1 == "specific"
        and type_2 == "weekly"
    ):
        try:
            conflict_date = (
                datetime.strptime(
                    class_1["date"],
                    "%Y-%m-%d"
                ).date()
            )
            return conflict_date.strftime(
                "%A, %d %B %Y"
            )
        except ValueError:
            return class_2.get(
                "day",
                "the same day"
            )
    # BOTH WEEKLY
    if (
        type_1 == "weekly"
        and type_2 == "weekly"
    ):
        return class_1.get(
            "day",
            "the same day"
        )
    return "the same day"
# -------------------------
# FIND ALL CONFLICTS
# -------------------------
def get_candidate_dates(class_1, class_2):
    """Dates on which these two classes could clash."""
    specific_dates = []
    for c in (class_1, class_2):
        if c.get("type") == "specific":
            try:
                specific_dates.append(
                    datetime.strptime(c["date"], "%Y-%m-%d").date()
                )
            except (KeyError, ValueError, TypeError):
                return []
    # At least one class is a one-time class: only its date matters.
    if specific_dates:
        return [specific_dates[0]]
    # Both weekly: look at the next 12 weeks, starting today.
    start_day = date.today()
    return [start_day + timedelta(days=i) for i in range(84)]


def find_conflicts():
    """Return only conflicts whose overlapping time has not finished yet."""
    now = datetime.now()
    found = []
    all_classes = st.session_state.classes
    for i in range(len(all_classes)):
        for j in range(i + 1, len(all_classes)):
            class_1 = all_classes[i]
            class_2 = all_classes[j]
            if not classes_overlap(class_1, class_2):
                continue
            overlap_start, overlap_end = get_overlap_time(class_1, class_2)
            overlap_end_minutes = min(
                time_to_minutes(class_1["end"]),
                time_to_minutes(class_2["end"])
            )
            for candidate in get_candidate_dates(class_1, class_2):
                # Respects weekdays, specific dates and deleted dates
                if not (
                    is_class_active_on_date(class_1, candidate)
                    and is_class_active_on_date(class_2, candidate)
                ):
                    continue
                overlap_finish = (
                    datetime.combine(candidate, time(0, 0))
                    + timedelta(minutes=overlap_end_minutes)
                )
                # Conflict is already over, so look at the next occurrence
                if overlap_finish <= now:
                    continue
                found.append({
                    "class_1": class_1,
                    "class_2": class_2,
                    "day": candidate.strftime("%A, %d %B %Y"),
                    "overlap_start": overlap_start,
                    "overlap_end": overlap_end,
                    "overlap_finish": overlap_finish
                })
                break  # only the next upcoming occurrence
    found.sort(key=lambda x: x["overlap_finish"])
    return found

def render_add_class():
    st.header("➕ Add a Class")
    schedule_type = st.radio(
        "How often does this class occur?",
        ["🔁 Every week", "📌 Specific date"],
        horizontal=True
    )
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input(
            "📚 Subject",
            placeholder="Example: Artificial Intelligence"
        )
        room = st.text_input(
            "🏫 Classroom",
            placeholder="Example: Room 201"
        )
    with col2:
        st.markdown("**🕐 Start Time**")
        start_hour_col, start_min_col, start_period_col = st.columns(3)
        with start_hour_col:
            start_hour = st.selectbox("Hour", list(range(1, 13)), index=8, key="start_hour")
        with start_min_col:
            start_minute = st.selectbox("Minute", list(range(0, 60)), index=0, format_func=lambda m: f"{m:02d}", key="start_minute")
        with start_period_col:
            start_period = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="start_period")
        st.markdown("**🕐 End Time**")
        end_hour_col, end_min_col, end_period_col = st.columns(3)
        with end_hour_col:
            end_hour = st.selectbox("Hour", list(range(1, 13)), index=9, key="end_hour")
        with end_min_col:
            end_minute = st.selectbox("Minute", list(range(0, 60)), index=0, format_func=lambda m: f"{m:02d}", key="end_minute")
        with end_period_col:
            end_period = st.selectbox("AM/PM", ["AM", "PM"], index=0, key="end_period")
    start_time = time((start_hour % 12) + (12 if start_period == "PM" else 0), start_minute)
    end_time = time((end_hour % 12) + (12 if end_period == "PM" else 0), end_minute)
    if schedule_type == "🔁 Every week":
        day = st.selectbox(
            "📅 Day",
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday"
            ]
        )
    else:
        selected_date = st.date_input(
        "📅 Class Date",
        value=date.today(),
        min_value=date(2020, 1, 1),
        max_value=date(2035, 12, 31)
    )
        day = selected_date.strftime("%A")
    if st.button("➕ Add Class"):
        if not subject.strip() or not room.strip():
            st.warning("Please enter the subject and classroom.")
        elif end_time <= start_time:
            st.error("End time must be later than start time. Please correct the time before adding this class.")
        else:
            new_class = {
                "attendance_id": uuid.uuid4().hex,
                "attended_dates": [],
                "subject": subject,
                "room": room,
                "start": start_time.strftime("%I:%M %p"),
                "end": end_time.strftime("%I:%M %p"),
                "type": "weekly" if schedule_type == "🔁 Every week" else "specific"
            }
            if schedule_type == "🔁 Every week":
                new_class["day"] = day
            else:
                new_class["date"] = selected_date.strftime("%Y-%m-%d")
                new_class["day"] = day
            st.session_state.classes.append(new_class)
            save_classes()
            st.success(f"✅ {subject} added successfully!")
    st.divider()


def render_conflict_display():
    @st.fragment(run_every="30s")
    def show_conflicts():
        conflicts = find_conflicts()
        st.header("⚠️ Schedule Conflict Alert")
        if conflicts:
            st.warning(
                f"⚠️ **{len(conflicts)} "
                f"schedule conflict(s) detected.**"
            )
            for conflict in conflicts:
                class_1 = conflict["class_1"]
                class_2 = conflict["class_2"]
                st.error(
                    f"📅 **{conflict['day']}**\n\n"
                    f"📚 **{class_1['subject']}**  \n"
                    f"🕐 {class_1['start']} – "
                    f"{class_1['end']}  \n"
                    f"🏫 {class_1['room']}  \n\n"
                    f"📚 **{class_2['subject']}**  \n"
                    f"🕐 {class_2['start']} – "
                    f"{class_2['end']}  \n"
                    f"🏫 {class_2['room']}  \n\n"
                    f"⏰ **Conflicting time: "
                    f"{conflict['overlap_start']} – "
                    f"{conflict['overlap_end']}**"
                )
            st.info(
                "💡 These classes have been saved "
                "normally. Review the conflicts and "
                "decide how you want to handle them."
            )
        else:
            st.success(
                "✅ **No schedule conflicts detected!**"
            )

    show_conflicts()


def render_weekly_timetable():
    # WEEK VIEWER
    # -------------------------
    st.header("📅 Weekly Timetable")
    today = date.today()
    # -------------------------------------------------
    # CREATE AVAILABLE WEEKS
    # -------------------------------------------------
    range_start = date(
        today.year - 1,
        today.month,
        1
    )
    range_end = date(
        today.year + 1,
        today.month,
        28
    )
    range_start = (
        range_start
        - timedelta(days=range_start.weekday())
    )
    available_weeks = []
    current_week = range_start
    while current_week <= range_end:
        available_weeks.append(
            current_week
        )
        current_week += timedelta(days=7)
    # -------------------------------------------------
    # MONTH SELECTION
    # -------------------------------------------------
    month_options = []
    for week_start in available_weeks:
        month_key = (
            week_start.year,
            week_start.month
        )
        if month_key not in month_options:
            month_options.append(
                month_key
            )
    month_labels = [
        date(year, month, 1).strftime(
            "%B %Y"
        )
        for year, month in month_options
    ]
    current_month_label = date(
        today.year,
        today.month,
        1
    ).strftime("%B %Y")
    selected_month_label = st.selectbox(
        "📆 Choose a month",
        month_labels,
        index=month_labels.index(
            current_month_label
        )
    )
    selected_month_index = (
        month_labels.index(
            selected_month_label
        )
    )
    selected_year, selected_month = (
        month_options[selected_month_index]
    )
    # -------------------------------------------------
    # WEEKS FOR SELECTED MONTH
    # -------------------------------------------------
    month_weeks = [
        week
        for week in available_weeks
        if (
            week.month == selected_month
            and week.year == selected_year
        )
    ]
    week_labels = []
    for i, week_start in enumerate(
        month_weeks
    ):
        week_end = (
            week_start
            + timedelta(days=6)
        )
        week_labels.append(
            f"Week {i + 1}: "
            f"{week_start.strftime('%d %b')} – "
            f"{week_end.strftime('%d %b')}"
        )
    # -------------------------------------------------
    # SELECT WEEK
    # -------------------------------------------------
    selected_week_label = st.selectbox(
        "🗓️ Choose a week",
        week_labels
    )
    selected_week_index = (
        week_labels.index(
            selected_week_label
        )
    )
    selected_week_start = (
        month_weeks[selected_week_index]
    )
    selected_week_end = (
        selected_week_start
        + timedelta(days=6)
    )
    st.caption(
        f"Showing classes from "
        f"**{selected_week_start.strftime('%A, %d %B %Y')}** "
        f"to "
        f"**{selected_week_end.strftime('%A, %d %B %Y')}**"
    )
    # -------------------------------------------------
    # DELETE THIS OCCURRENCE
    # -------------------------------------------------
    def delete_class_occurrence(
        class_to_delete,
        occurrence_date
    ):
        # WEEKLY CLASS
        if class_to_delete.get("type") == "weekly":
            date_string = (
                occurrence_date.strftime(
                    "%Y-%m-%d"
                )
            )
            if "deleted_dates" not in class_to_delete:
                class_to_delete["deleted_dates"] = []
            if date_string not in (
                class_to_delete["deleted_dates"]
            ):
                class_to_delete[
                    "deleted_dates"
                ].append(date_string)
        # SPECIFIC DATE CLASS
        else:
            st.session_state.classes.remove(
                class_to_delete
            )
        save_classes()
        st.rerun()
    # -------------------------------------------------
    # DELETE RECURRING CLASS
    # -------------------------------------------------
    def delete_recurring_class(
        class_to_delete
    ):
        st.session_state.classes.remove(
            class_to_delete
        )
        save_classes()
        st.rerun()
    # -------------------------------------------------
    # DISPLAY SELECTED WEEK
    # -------------------------------------------------
    for day_offset in range(7):
        current_date = (
            selected_week_start
            + timedelta(days=day_offset)
        )
        current_day = (
            current_date.strftime("%A")
        )
        # -------------------------------------------------
        # FIND CLASSES FOR THIS DATE
        # -------------------------------------------------
        day_classes = []
        for c in st.session_state.classes:
            if is_class_active_on_date(
                c,
                current_date
            ):
                day_classes.append(c)
        # Sort by starting time
        day_classes.sort(
            key=lambda x: x["start"]
        )
        # -------------------------------------------------
        # DAY HEADER
        # -------------------------------------------------
        if current_date == today:
            st.subheader(
                f"📍 Today — "
                f"{current_date.strftime('%A, %d %B')}"
            )
        else:
            st.subheader(
                current_date.strftime(
                    "%A, %d %B"
                )
            )
        # -------------------------------------------------
        # DISPLAY CLASSES
        # -------------------------------------------------
        if day_classes:
            for index, c in enumerate(
                day_classes
            ):
                # -----------------------------------------
                # CLASS INFORMATION
                # -----------------------------------------
                if c.get("type") == "weekly":
                    class_label = "🔁 Weekly"
                else:
                    class_label = "📌 One-time"
                col1, col2 = st.columns(
                    [5, 2]
                )
                with col1:
                    st.write(
                        f"📚 **{c['subject']}**  \n"
                        f"🕐 {c['start']} – "
                        f"{c['end']}  \n"
                        f"🏫 {c['room']}  \n"
                        f"{class_label}"
                    )
                    attendance_key = (
                        f"attendance_week_{c['attendance_id']}_{current_date.isoformat()}"
                    )
                    attended_dates = c.setdefault("attended_dates", [])
                    st.checkbox(
                        "Class attended",
                        value=current_date.isoformat() in attended_dates,
                        key=attendance_key,
                        on_change=update_attendance,
                        args=(c["attendance_id"], current_date.isoformat(), attendance_key)
                    )
                with col2:
                    # -----------------------------------------
                    # WEEKLY CLASS
                    # -----------------------------------------
                    if c.get("type") == "weekly":
                        if st.button(
                            "🗑️ Delete this class",
                            key=(
                                f"delete_occurrence_"
                                f"{selected_week_start}_"
                                f"{current_date}_"
                                f"{index}_"
                                f"{c['subject']}"
                            )
                        ):
                            delete_class_occurrence(
                                c,
                                current_date
                            )
                        if st.button(
                            "🗑️ Delete recurring",
                            key=(
                                f"delete_recurring_"
                                f"{selected_week_start}_"
                                f"{current_date}_"
                                f"{index}_"
                                f"{c['subject']}"
                            )
                        ):
                            delete_recurring_class(c)
                    # -----------------------------------------
                    # SPECIFIC DATE CLASS
                    # -----------------------------------------
                    else:
                        if st.button(
                            "🗑️ Delete",
                            key=(
                                f"delete_specific_"
                                f"{selected_week_start}_"
                                f"{current_date}_"
                                f"{index}_"
                                f"{c['subject']}"
                            )
                        ):
                            delete_class_occurrence(
                                c,
                                current_date
                            )
        else:
            st.caption(
                "No classes scheduled."
            )
    # -------------------------


def render_month_calendar():
    # MONTH CALENDAR
    # -------------------------
    st.header("🗓️ Calendar")
    today = date.today()
    # Month navigation
    if "calendar_year" not in st.session_state:
        st.session_state.calendar_year = today.year
    if "calendar_month" not in st.session_state:
        st.session_state.calendar_month = today.month
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous Month"):
            if st.session_state.calendar_month == 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            else:
                st.session_state.calendar_month -= 1
            st.rerun()
    with col2:
        month_name = calendar.month_name[
            st.session_state.calendar_month
        ]
        st.markdown(
            f"<h2 style='text-align:center'>{month_name} "
            f"{st.session_state.calendar_year}</h2>",
            unsafe_allow_html=True
        )
    with col3:
        if st.button("Next Month ➡️"):
            if st.session_state.calendar_month == 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            else:
                st.session_state.calendar_month += 1
            st.rerun()
    # Calendar grid
    month_calendar = calendar.monthcalendar(
        st.session_state.calendar_year,
        st.session_state.calendar_month
    )
    week_days = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]
    header_cols = st.columns(7)
    for i, day_name in enumerate(week_days):
        with header_cols[i]:
            st.markdown(f"**{day_name}**")
    for week in month_calendar:
        cols = st.columns(7)
        for i, day_number in enumerate(week):
            with cols[i]:
                if day_number == 0:
                    st.write("")
                    continue
                current_date = date(
                    st.session_state.calendar_year,
                    st.session_state.calendar_month,
                    day_number
                )
                st.markdown(
                    f"**{day_number}**"
                )
                current_day_name = current_date.strftime("%A")
                # Weekly classes
                weekly_classes = [
                    c for c in st.session_state.classes
                    if c.get("type") == "weekly"
                    and c.get("day") == current_day_name
                    and current_date.strftime("%Y-%m-%d")
                        not in c.get("deleted_dates",[])
                ]
                # Specific-date classes
                specific_classes = [
                    c for c in st.session_state.classes
                    if c.get("type") == "specific"
                    and c.get("date") == current_date.strftime("%Y-%m-%d")
                ]
                all_classes = weekly_classes + specific_classes
                for class_index, c in enumerate(all_classes):
                    st.caption(
                        f"📚 {c['subject']}\n\n"
                        f"🕐 {c['start']}\n\n"
                        f"🏫 {c['room']}"
                    )
                    attendance_key = (
                        f"attendance_calendar_{c['attendance_id']}_{current_date.isoformat()}"
                    )
                    attended_dates = c.setdefault("attended_dates", [])
                    st.checkbox(
                        "Attended",
                        value=current_date.isoformat() in attended_dates,
                        key=attendance_key,
                        on_change=update_attendance,
                        args=(c["attendance_id"], current_date.isoformat(), attendance_key)
                    )
    st.divider()


def render_upcoming_classes():
    # -------------------------
    # UPCOMING CLASSES
    # -------------------------
    @st.fragment(run_every="30s")
    def show_upcoming_classes():
        st.header("🔔 Upcoming Classes")
        now = datetime.now()
        today = now.date()
        upcoming_classes = []
        # Look ahead 14 days
        for i in range(14):
            current_date = today + timedelta(days=i)
            current_day = current_date.strftime("%A")
            # Weekly classes
            for c in st.session_state.classes:
                if (
                    c.get("type") == "weekly"
                    and c.get("day") == current_day
                    and current_date.strftime("%Y-%m-%d")
                        not in c.get("deleted_dates", [])
                ):
                    try:
                        end_clock = datetime.strptime(c["end"], "%I:%M %p").time()
                        end_datetime = datetime.combine(current_date, end_clock)
                        start_clock = datetime.strptime(c["start"], "%I:%M %p").time()
                        start_datetime = datetime.combine(current_date, start_clock)
                    except (KeyError, TypeError, ValueError):
                        continue
                    # Remove classes after their scheduled end time.
                    if end_datetime <= now:
                        continue
                    upcoming_classes.append({
                        "date": current_date,
                        "subject": c["subject"],
                        "room": c["room"],
                        "start": c["start"],
                        "end": c["end"],
                        "start_datetime": start_datetime,
                        "end_datetime": end_datetime
                    })
                # Specific-date classes
                elif (
                    c.get("type") == "specific"
                    and c.get("date") == current_date.strftime("%Y-%m-%d")
                ):
                    try:
                        end_clock = datetime.strptime(c["end"], "%I:%M %p").time()
                        end_datetime = datetime.combine(current_date, end_clock)
                        start_clock = datetime.strptime(c["start"], "%I:%M %p").time()
                        start_datetime = datetime.combine(current_date, start_clock)
                    except (KeyError, TypeError, ValueError):
                        continue
                    # Remove classes after their scheduled end time.
                    if end_datetime <= now:
                        continue
                    upcoming_classes.append({
                        "date": current_date,
                        "subject": c["subject"],
                        "room": c["room"],
                        "start": c["start"],
                        "end": c["end"],
                        "start_datetime": start_datetime,
                        "end_datetime": end_datetime
                    })
        # Sort by date and time
        upcoming_classes.sort(
            key=lambda x: (x["date"], time_to_minutes(x["start"]) if time_to_minutes(x["start"]) is not None else 0)
        )
        if upcoming_classes:
            # Next class
            next_class = upcoming_classes[0]
            st.subheader("⭐ Next Class")
            if next_class["start_datetime"] <= now < next_class["end_datetime"]:
                next_status = "**Class in progress**\n\n"
            else:
                next_status = ""
            st.info(
                f"{next_status}📚 **{next_class['subject']}**\n\n"
                f"📅 {next_class['date'].strftime('%A, %d %B %Y')}\n\n"
                f"🕐 {next_class['start']} - {next_class['end']}\n\n"
                f"🏫 {next_class['room']}"
            )
            st.subheader("📋 Upcoming Classes")
            for c in upcoming_classes[:10]:
                st.write(
                    f"📅 **{c['date'].strftime('%a, %d %b')}**  |  "
                    f"🕐 **{c['start']}**  |  "
                    f"📚 **{c['subject']}**  |  "
                    f"🏫 {c['room']}"
                )
        else:
            st.success("🎉 No upcoming classes scheduled!")

    show_upcoming_classes()
    st.divider()
    # -------------------------


def render_smart_reminder():
    # PROACTIVE CLASS REMINDER
    # -------------------------
    @st.fragment(run_every="30s")
    def proactive_class_reminder():
        now = datetime.now()
        today = date.today()
        upcoming_today = []
        for c in st.session_state.classes:
            # -------------------------
            # WEEKLY CLASS
            # -------------------------
            if (
                c.get("type") == "weekly"
                and c.get("day") == today.strftime("%A")
                and today.strftime("%Y-%m-%d")
                    not in c.get("deleted_dates",[])
            ):
                try:
                    start_time = datetime.strptime(
                        c["start"],
                        "%I:%M %p"
                    ).time()
                    class_datetime = datetime.combine(
                        today,
                        start_time
                    )
                    if class_datetime >= now:
                        upcoming_today.append({
                            "subject": c["subject"],
                            "room": c["room"],
                            "start": c["start"],
                            "datetime": class_datetime
                        })
                except ValueError:
                    pass
            # -------------------------
            # SPECIFIC DATE CLASS
            # -------------------------
            elif (
                c.get("type") == "specific"
                and c.get("date")
                == today.strftime("%Y-%m-%d")
            ):
                try:
                    start_time = datetime.strptime(
                        c["start"],
                        "%I:%M %p"
                    ).time()
                    class_datetime = datetime.combine(
                        today,
                        start_time
                    )
                    if class_datetime >= now:
                        upcoming_today.append({
                            "subject": c["subject"],
                            "room": c["room"],
                            "start": c["start"],
                            "datetime": class_datetime
                        })
                except ValueError:
                    pass
        # Sort by time
        upcoming_today.sort(
            key=lambda x: x["datetime"]
        )
        st.subheader("🔔 Smart Class Reminder")
        # -------------------------
        # NO CLASSES TODAY
        # -------------------------
        if not upcoming_today:
            st.success(
                "✅ You have no more classes scheduled for today."
            )
        else:
            next_class = upcoming_today[0]
            time_difference = (
                next_class["datetime"] - now
            )
            total_seconds = int(
                time_difference.total_seconds()
            )
            minutes = total_seconds // 60
            hours = minutes // 60
            remaining_minutes = minutes % 60
            # -------------------------
            # CLASS STARTING SOON
            # -------------------------
            if minutes <= 30:
                if minutes <= 1:
                    time_message = "starting now"
                else:
                    time_message = (
                        f"starting in {minutes} minutes"
                    )
                st.warning(
                    f"🔔 **Upcoming Class!**\n\n"
                    f"**{next_class['subject']}** is "
                    f"**{time_message}**.\n\n"
                    f"🕐 {next_class['start']}  "
                    f"🏫 {next_class['room']}"
                )
            # -------------------------
            # CLASS LATER TODAY
            # -------------------------
            else:
                if hours > 0:
                    if remaining_minutes > 0:
                        time_message = (
                            f"{hours} hour(s) "
                            f"{remaining_minutes} minute(s)"
                        )
                    else:
                        time_message = (
                            f"{hours} hour(s)"
                        )
                else:
                    time_message = (
                        f"{minutes} minutes"
                    )
                st.info(
                    f"📚 **Your next class**\n\n"
                    f"**{next_class['subject']}** "
                    f"at **{next_class['start']}** "
                    f"in **{next_class['room']}**.\n\n"
                    f"Starts in **{time_message}**."
                )
            # -------------------------
            # TODAY'S REMAINING CLASSES
            # -------------------------
            if len(upcoming_today) > 1:
                with st.expander(
                    "📋 View today's remaining classes"
                ):
                    for c in upcoming_today:
                        st.write(
                            f"📚 **{c['subject']}** — "
                            f"🕐 {c['start']} — "
                            f"🏫 {c['room']}"
                        )
    proactive_class_reminder()
    # -------------------------


def render_ai_assistant():
    # AI STUDENT ASSISTANT
    # -------------------------
    st.header("🤖 Ask Your Student Assistant")
    question = st.text_input(
        "Ask something about your timetable:",
        placeholder="Example: When is my next class?"
    )
    if question:
        q = question.lower()
        # -------------------------
        # HELPER: ADD MONTHS
        # -------------------------
        def add_months(original_date, months):
            month = original_date.month - 1 + months
            year = original_date.year + month // 12
            month = month % 12 + 1
            return date(year, month, 1)
        # -------------------------
        # DATE RANGE
        # -------------------------
        today = date.today()
        start_month = add_months(
            date(today.year, today.month, 1),
            -2
        )
        end_month = add_months(
            date(today.year, today.month, 1),
            2
        )
        end_date = (
            end_month
            + timedelta(
                days=calendar.monthrange(
                    end_month.year,
                    end_month.month
                )[1] - 1
            )
        )
        # -------------------------
        # BUILD UPCOMING CLASSES
        # -------------------------
        upcoming = []
        current_date = start_month
        while current_date <= end_date:
            current_day = current_date.strftime("%A")
            for c in st.session_state.classes:
                # Weekly classes
                if (
                    c.get("type") == "weekly"
                    and c.get("day") == current_day
                    and current_date.strftime("%Y-%m-%d")
                        not in c.get("deleted_dates", [])
                ):
                    upcoming.append({
                        "date": current_date,
                        "subject": c["subject"],
                        "room": c["room"],
                        "start": c["start"],
                        "end": c["end"]
                    })
                # Specific-date classes
                elif (
                    c.get("type") == "specific"
                    and c.get("date")
                        == current_date.strftime("%Y-%m-%d")
                ):
                    upcoming.append({
                        "date": current_date,
                        "subject": c["subject"],
                        "room": c["room"],
                        "start": c["start"],
                        "end": c["end"]
                    })
            current_date += timedelta(days=1)
        upcoming.sort(
            key=lambda x: (
                x["date"],
                time_to_minutes(x["start"])
                if time_to_minutes(x["start"]) is not None
                else 0
            )
        )
        # -------------------------
        # CURRENT TIME
        # -------------------------
        from datetime import datetime
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        # -------------------------
        # FIND SUBJECT
        # -------------------------
        matched_subject = None
        subjects = list(
            set(
                c["subject"]
                for c in st.session_state.classes
            )
        )
        subjects.sort(
            key=len,
            reverse=True
        )
        for subject in subjects:
            if subject.lower() in q:
                matched_subject = subject
                break
        # -------------------------
        # FIND DATE
        # -------------------------
        reference_date = today
        for i in range(
            (end_date - start_month).days + 1
        ):
            possible_date = (
                start_month + timedelta(days=i)
            )
            day_number = str(possible_date.day)
            month_name = (
                possible_date.strftime("%B").lower()
            )
            if (
                day_number in q
                and month_name in q
            ):
                reference_date = possible_date
                break
        # =====================================================
        # FEATURE 1: HOW MANY CLASSES?
        # =====================================================
        if (
            "how many" in q
            and "class" in q
        ):
            # TODAY
            if "today" in q:
                matching = [
                    c for c in upcoming
                    if c["date"] == today
                ]
                if matched_subject:
                    matching = [
                        c for c in matching
                        if c["subject"].lower()
                        == matched_subject.lower()
                    ]
                st.success(
                    f"You have **{len(matching)}** "
                    f"{matched_subject + ' ' if matched_subject else ''}"
                    f"class(es) today."
                )
            # THIS WEEK
            elif "this week" in q:
                week_start = today - timedelta(
                    days=today.weekday()
                )
                week_end = week_start + timedelta(days=6)
                matching = [
                    c for c in upcoming
                    if week_start <= c["date"] <= week_end
                ]
                if matched_subject:
                    matching = [
                        c for c in matching
                        if c["subject"].lower()
                        == matched_subject.lower()
                    ]
                st.success(
                    f"You have **{len(matching)}** "
                    f"{matched_subject + ' ' if matched_subject else ''}"
                    f"class(es) this week."
                )
            # THIS MONTH
            elif (
                "this month" in q
                or "month" in q
            ):
                matching = [
                    c for c in upcoming
                    if (
                        c["date"].month == today.month
                        and c["date"].year == today.year
                    )
                ]
                if matched_subject:
                    matching = [
                        c for c in matching
                        if c["subject"].lower()
                        == matched_subject.lower()
                    ]
                st.success(
                    f"You have **{len(matching)}** "
                    f"{matched_subject + ' ' if matched_subject else ''}"
                    f"class(es) this month."
                )
        # =====================================================
        # FEATURE 2: FIRST CLASS
        # =====================================================
        elif (
            "first class" in q
            or "first class today" in q
        ):
            matching = [
                c for c in upcoming
                if c["date"] == today
            ]
            if matched_subject:
                matching = [
                    c for c in matching
                    if c["subject"].lower()
                    == matched_subject.lower()
                ]
            if matching:
                c = matching[0]
                st.success(
                    f"Your first class today is "
                    f"**{c['subject']}** at **{c['start']}** "
                    f"in **{c['room']}**."
                )
            else:
                st.info(
                    "You don't have any matching classes today."
                )
        # =====================================================
        # FEATURE 3: LAST CLASS
        # =====================================================
        elif (
            "last class" in q
            or "last class today" in q
        ):
            matching = [
                c for c in upcoming
                if c["date"] == today
            ]
            if matched_subject:
                matching = [
                    c for c in matching
                    if c["subject"].lower()
                    == matched_subject.lower()
                ]
            if matching:
                c = matching[-1]
                st.success(
                    f"Your last class today is "
                    f"**{c['subject']}** at **{c['start']}** "
                    f"in **{c['room']}**."
                )
            else:
                st.info(
                    "You don't have any matching classes today."
                )
        # =====================================================
        # FEATURE 4: BUSIEST DAY
        # =====================================================
        elif (
            "busiest day" in q
            or "busy day" in q
        ):
            day_counts = {}
            for c in upcoming:
                if (
                    c["date"] >= today
                    and c["date"] < today + timedelta(days=7)
                ):
                    day_name = c["date"].strftime("%A")
                    day_counts[day_name] = (
                        day_counts.get(day_name, 0) + 1
                    )
            if day_counts:
                busiest_day = max(
                    day_counts,
                    key=day_counts.get
                )
                count = day_counts[busiest_day]
                st.success(
                    f"Your busiest day this week is "
                    f"**{busiest_day}** with "
                    f"**{count} classes**."
                )
            else:
                st.info(
                    "I couldn't find enough classes "
                    "to determine your busiest day."
                )
        # =====================================================
        # FEATURE 5: CLASSES IN A SPECIFIC WEEK OF A MONTH
        # =====================================================
        elif (
            (
                "week" in q
                or "weeks" in q
            )
            and any(
                ordinal in q
                for ordinal in [
                    "1st", "2nd", "3rd", "4th", "5th",
                    "first", "second", "third", "fourth", "fifth"
                ]
            )
            and any(
                month in q
                for month in [
                    "january", "february", "march", "april",
                    "may", "june", "july", "august",
                    "september", "october", "november", "december"
                ]
            )
        ):
            week_number = None
            if "1st" in q or "first" in q:
                week_number = 1
            elif "2nd" in q or "second" in q:
                week_number = 2
            elif "3rd" in q or "third" in q:
                week_number = 3
            elif "4th" in q or "fourth" in q:
                week_number = 4
            elif "5th" in q or "fifth" in q:
                week_number = 5
            requested_month = None
            for month_number in range(1, 13):
                month_name = calendar.month_name[month_number].lower()
                if month_name in q:
                    requested_month = month_number
                    break
            requested_year = today.year
            for year in range(today.year - 5, today.year + 6):
                if str(year) in q:
                    requested_year = year
                    break
            first_day = date(
                requested_year,
                requested_month,
                1
            )
            first_monday = (
                first_day - timedelta(days=first_day.weekday())
            )
            week_start = (
                first_monday + timedelta(days=(week_number - 1) * 7)
            )
            week_end = week_start + timedelta(days=6)
            week_classes = []
            current_week_date = week_start
            while current_week_date <= week_end:
                current_day = current_week_date.strftime("%A")
                date_string = current_week_date.strftime("%Y-%m-%d")
                for c in st.session_state.classes:
                    if (
                        c.get("type") == "weekly"
                        and c.get("day") == current_day
                        and date_string not in c.get("deleted_dates", [])
                    ):
                        week_classes.append({
                            "date": current_week_date,
                            "subject": c["subject"],
                            "room": c["room"],
                            "start": c["start"],
                            "end": c["end"]
                        })
                    elif (
                        c.get("type") == "specific"
                        and c.get("date") == date_string
                    ):
                        week_classes.append({
                            "date": current_week_date,
                            "subject": c["subject"],
                            "room": c["room"],
                            "start": c["start"],
                            "end": c["end"]
                        })
                current_week_date += timedelta(days=1)
            if matched_subject:
                week_classes = [
                    c for c in week_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            week_classes.sort(
                key=lambda x: (
                    x["date"],
                    time_to_minutes(x["start"])
                    if time_to_minutes(x["start"]) is not None
                    else 0
                )
            )
            if week_classes:
                st.success(
                    f"Here are your classes for the "
                    f"{week_number}th week of "
                    f"{calendar.month_name[requested_month]} "
                    f"{requested_year}:"
                )
                for c in week_classes:
                    st.write(
                        f"📅 **{c['date'].strftime('%A, %d %B')}** — "
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} – {c['end']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                st.info(
                    f"You don't have any classes in the "
                    f"{week_number}th week of "
                    f"{calendar.month_name[requested_month]} "
                    f"{requested_year}."
                )
        # =====================================================
        # FEATURE 6: CLASSES THIS WEEK
        # =====================================================
        elif (
            (
                "what classes" in q
                or "which classes" in q
                or "classes this week" in q
                or "class this week" in q
            )
            and (
                "week" in q
                or "this week" in q
            )
        ):
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_classes = [
                c for c in upcoming
                if week_start <= c["date"] <= week_end
            ]
            if matched_subject:
                week_classes = [
                    c for c in week_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if week_classes:
                st.success("Here are your classes this week:")
                for c in week_classes:
                    st.write(
                        f"📅 **{c['date'].strftime('%A, %d %B')}** — "
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} – {c['end']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                st.info("You don't have any classes this week.")
        # =====================================================
        # FEATURE 7: SUBJECTS THIS WEEK
        # =====================================================
        elif (
            "subjects" in q
            and (
                "this week" in q
                or "week" in q
            )
        ):
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            week_classes = [
                c for c in upcoming
                if week_start <= c["date"] <= week_end
            ]
            unique_subjects = []
            for c in week_classes:
                if c["subject"] not in unique_subjects:
                    unique_subjects.append(c["subject"])
            if unique_subjects:
                st.success("Your subjects this week are:")
                for subject in unique_subjects:
                    st.write(f"📚 **{subject}**")
            else:
                st.info("You don't have any classes this week.")
        # =====================================================
        # FEATURE 8: WHAT COMES AFTER A SUBJECT?
        # =====================================================
        elif (
            "what comes after" in q
            or "what is after" in q
            or "what's after" in q
        ):
            if matched_subject:
                subject_classes = [
                    c for c in upcoming
                    if (
                        c["subject"].lower() == matched_subject.lower()
                        and (
                            c["date"] > today
                            or (
                                c["date"] == today
                                and time_to_minutes(c["start"]) is not None
                                and time_to_minutes(c["start"]) > current_minutes
                            )
                        )
                    )
                ]
                if subject_classes:
                    reference_class = subject_classes[0]
                    following_classes = [
                        c for c in upcoming
                        if (
                            c["date"] > reference_class["date"]
                            or (
                                c["date"] == reference_class["date"]
                                and time_to_minutes(c["start"]) is not None
                                and time_to_minutes(reference_class["start"]) is not None
                                and time_to_minutes(c["start"])
                                    > time_to_minutes(reference_class["start"])
                            )
                        )
                    ]
                    if following_classes:
                        c = following_classes[0]
                        st.success(
                            f"After your **{matched_subject}** class, "
                            f"you have **{c['subject']}** on "
                            f"**{c['date'].strftime('%A, %d %B')}** "
                            f"at **{c['start']}** in **{c['room']}**."
                        )
                    else:
                        st.info("I couldn't find another class after that.")
                else:
                    st.info(
                        f"I couldn't find an upcoming **{matched_subject}** class."
                    )
            else:
                st.info(
                    "Please mention the subject you want "
                    "to find the following class for."
                )
        # =====================================================
        # NEXT CLASS — DATE AND CURRENT TIME
        # This comes BEFORE the general TODAY handler.
        # =====================================================
        elif "next" in q and "class" in q:
            future_classes = [
                c for c in upcoming
                if (
                    c["date"] > today
                    or (
                        c["date"] == today
                        and time_to_minutes(c["start"]) is not None
                        and time_to_minutes(c["start"]) > current_minutes
                    )
                )
            ]
            if matched_subject:
                future_classes = [
                    c for c in future_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if future_classes:
                c = future_classes[0]
                st.success(
                    f"Your next {matched_subject + ' ' if matched_subject else ''}"
                    f"class is **{c['subject']}** on "
                    f"**{c['date'].strftime('%A, %d %B')}** "
                    f"at **{c['start']}** in **{c['room']}**."
                )
            else:
                if matched_subject:
                    st.info(
                        f"No upcoming {matched_subject} classes were found."
                    )
                else:
                    st.info("You don't have any upcoming classes.")
        # =====================================================
        # TODAY
        # =====================================================
        elif (
            "today" in q
            or "my class is today" in q
        ):
            today_classes = [
                c for c in upcoming
                if c["date"] == today
            ]
            if matched_subject:
                today_classes = [
                    c for c in today_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if today_classes:
                for c in today_classes:
                    st.write(
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                st.info("You don't have any matching classes today.")
        # =====================================================
        # BEFORE DATE
        # =====================================================
        elif "before" in q:
            if matched_subject:
                matching_classes = [
                    c for c in upcoming
                    if (
                        c["subject"].lower() == matched_subject.lower()
                        and c["date"] < reference_date
                    )
                ]
                if matching_classes:
                    c = matching_classes[-1]
                    st.success(
                        f"Your previous **{c['subject']}** class before "
                        f"**{reference_date.strftime('%d %B')}** was on "
                        f"**{c['date'].strftime('%A, %d %B')}** "
                        f"at **{c['start']}** in **{c['room']}**."
                    )
                else:
                    st.info(
                        f"I couldn't find a **{matched_subject}** class before "
                        f"{reference_date.strftime('%d %B')}."
                    )
            else:
                matching_classes = [
                    c for c in upcoming
                    if c["date"] < reference_date
                ]
                if matching_classes:
                    c = matching_classes[-1]
                    st.success(
                        f"The class immediately before "
                        f"**{reference_date.strftime('%d %B')}** is "
                        f"**{c['subject']}** on "
                        f"**{c['date'].strftime('%A, %d %B')}** "
                        f"at **{c['start']}** in **{c['room']}**."
                    )
                else:
                    st.info(
                        f"I couldn't find any classes before "
                        f"{reference_date.strftime('%d %B')}."
                    )
        # =====================================================
        # AFTER DATE
        # =====================================================
        elif "after" in q:
            if matched_subject:
                matching_classes = [
                    c for c in upcoming
                    if (
                        c["subject"].lower() == matched_subject.lower()
                        and c["date"] > reference_date
                    )
                ]
                if matching_classes:
                    c = matching_classes[0]
                    st.success(
                        f"Your next **{c['subject']}** class after "
                        f"**{reference_date.strftime('%d %B')}** is on "
                        f"**{c['date'].strftime('%A, %d %B')}** "
                        f"at **{c['start']}** in **{c['room']}**."
                    )
                else:
                    st.info(
                        f"I couldn't find another **{matched_subject}** class after "
                        f"{reference_date.strftime('%d %B')}."
                    )
            else:
                matching_classes = [
                    c for c in upcoming
                    if c["date"] > reference_date
                ]
                if matching_classes:
                    c = matching_classes[0]
                    st.success(
                        f"The first class after "
                        f"**{reference_date.strftime('%d %B')}** is "
                        f"**{c['subject']}** on "
                        f"**{c['date'].strftime('%A, %d %B')}** "
                        f"at **{c['start']}** in **{c['room']}**."
                    )
                else:
                    st.info(
                        f"I couldn't find any classes after "
                        f"{reference_date.strftime('%d %B')}."
                    )
        # =====================================================
        # SPECIFIC DATE
        # =====================================================
        elif reference_date != today:
            date_classes = [
                c for c in upcoming
                if c["date"] == reference_date
            ]
            if matched_subject:
                date_classes = [
                    c for c in date_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if date_classes:
                for c in date_classes:
                    st.write(
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                st.info(
                    f"I couldn't find any classes on "
                    f"{reference_date.strftime('%d %B')}."
                )
        # =====================================================
        # MONTH SEARCH
        # =====================================================
        elif any(
            month in q
            for month in [
                "january", "february", "march", "april",
                "may", "june", "july", "august",
                "september", "october", "november", "december"
            ]
        ):
            requested_month = None
            for month_number in range(1, 13):
                month_name = calendar.month_name[month_number].lower()
                if month_name in q:
                    requested_month = month_number
                    break
            month_classes = [
                c for c in upcoming
                if c["date"].month == requested_month
            ]
            if matched_subject:
                month_classes = [
                    c for c in month_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if month_classes:
                for c in month_classes:
                    st.write(
                        f"📅 **{c['date'].strftime('%A, %d %B')}** — "
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                if matched_subject:
                    st.info(
                        f"I couldn't find any **{matched_subject}** classes "
                        f"in {calendar.month_name[requested_month]}."
                    )
                else:
                    st.info(
                        f"You don't have any classes in "
                        f"{calendar.month_name[requested_month]}."
                    )
        # =====================================================
        # TOMORROW
        # =====================================================
        elif "tomorrow" in q:
            tomorrow = today + timedelta(days=1)
            tomorrow_classes = [
                c for c in upcoming
                if c["date"] == tomorrow
            ]
            if matched_subject:
                tomorrow_classes = [
                    c for c in tomorrow_classes
                    if c["subject"].lower() == matched_subject.lower()
                ]
            if tomorrow_classes:
                for c in tomorrow_classes:
                    st.write(
                        f"📚 **{c['subject']}** — "
                        f"🕐 {c['start']} — "
                        f"🏫 {c['room']}"
                    )
            else:
                st.info("You don't have any matching classes tomorrow.")
        # =====================================================
        # WHERE / ROOM
        # =====================================================
        elif "where" in q or "room" in q:
            found = False
            if matched_subject:
                for c in upcoming:
                    if (
                        c["subject"].lower() == matched_subject.lower()
                        and c["date"] >= today
                    ):
                        st.success(
                            f"Your **{c['subject']}** class is in "
                            f"**{c['room']}** on "
                            f"**{c['date'].strftime('%A, %d %B')}** "
                            f"at **{c['start']}**."
                        )
                        found = True
                        break
            if not found:
                st.info("I couldn't find that subject in your timetable.")
        # =====================================================
        # DEFAULT
        # =====================================================
        else:
            st.info(
                "Try asking about your next class, "
                "a subject, a classroom, today, tomorrow, "
                "a specific date, a month, "
                "class counts, your busiest day, "
                "or a class before or after a specific date."
            )


# -------------------------
# COMPACT LAYOUT (calendar on the right)
# -------------------------
st.markdown("""
<style>
.block-container { padding-top: 4.5rem !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stVerticalBlockBorderWrapper"] { padding: .8rem 1rem; }
[data-testid="stHeading"] h2 { font-size: 1.45rem !important; margin-bottom: .2rem; }
[data-testid="stHeading"] h3 { font-size: 1.05rem !important; }
[data-testid="stVerticalBlock"] { gap: .6rem; }
hr { margin: .6rem 0 !important; }
[data-testid="stAlert"] { padding: .6rem .8rem; }
</style>
""", unsafe_allow_html=True)

# Row 1: reminder + add class + upcoming (side column) | calendar (wide, right)
side_col, calendar_col = st.columns([1, 2.1], gap="medium", vertical_alignment="top")

with side_col:
    with st.container(border=True):
        render_smart_reminder()
    with st.container(border=True):
        render_add_class()
    with st.container(border=True):
        render_upcoming_classes()

with calendar_col:
    with st.container(border=True):
        calendar_view = st.radio(
            "Calendar view",
            ["📅 Week", "🗓️ Month"],
            horizontal=True,
            key="calendar_view",
            label_visibility="collapsed"
        )
        if calendar_view == "📅 Week":
            render_weekly_timetable()
        else:
            render_month_calendar()

# Row 2: conflicts | assistant
conflict_col, assistant_col = st.columns(2, gap="medium", vertical_alignment="top")

with conflict_col:
    with st.container(border=True):
        render_conflict_display()

with assistant_col:
    with st.container(border=True):
        render_ai_assistant()