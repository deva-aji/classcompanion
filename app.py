import streamlit as st

import json

import os

import calendar

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

# -------------------------

# TITLE

# -------------------------

st.title("🎓 Student Assistant")

st.write("Your personal class and timetable assistant")

st.divider()

# -------------------------

# ADD CLASS

# -------------------------

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

# -------------------------

# SCHEDULE CONFLICT ALERT

# -------------------------

st.header("⚠️ Schedule Conflict Alert")

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

conflicts = []

classes = st.session_state.classes

for i in range(len(classes)):

    for j in range(

        i + 1,

        len(classes)

    ):

        class_1 = classes[i]

        class_2 = classes[j]

        # Ignore a specific-date class if the

        # weekly class was deleted on that date

        if (

            class_1.get("type") == "weekly"

            and class_2.get("type") == "specific"

        ):

            specific_date = datetime.strptime(

                class_2["date"],

                "%Y-%m-%d"

            ).date()

            if (

                specific_date.strftime("%Y-%m-%d")

                in class_1.get("deleted_dates", [])

            ):

                continue

        if (

            class_1.get("type") == "specific"

            and class_2.get("type") == "weekly"

        ):

            specific_date = datetime.strptime(

                class_1["date"],

                "%Y-%m-%d"

            ).date()

            if (

                specific_date.strftime("%Y-%m-%d")

                in class_2.get("deleted_dates", [])

            ):

                continue

        # Check whether both classes

        # can occur on the same day

        if not same_schedule_day(

            class_1,

            class_2

        ):

            continue

        # Check whether their

        # times overlap

        if not classes_overlap(

            class_1,

            class_2

        ):

            continue

        # Calculate exact overlap

        overlap_start, overlap_end = (

            get_overlap_time(

                class_1,

                class_2

            )

        )

        conflict_day = get_conflict_day(

            class_1,

            class_2

        )

        conflicts.append({

            "class_1": class_1,

            "class_2": class_2,

            "day": conflict_day,

            "overlap_start": overlap_start,

            "overlap_end": overlap_end

        })

# -------------------------

# DISPLAY RESULTS

# -------------------------

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

# -------------------------

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

            for c in all_classes:

                st.caption(

                    f"📚 {c['subject']}\n\n"

                    f"🕐 {c['start']}\n\n"

                    f"🏫 {c['room']}"

                )

st.divider()

# -------------------------

# UPCOMING CLASSES

# -------------------------

st.header("🔔 Upcoming Classes")

today = date.today()

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

            upcoming_classes.append({

                "date": current_date,

                "subject": c["subject"],

                "room": c["room"],

                "start": c["start"],

                "end": c["end"]

            })

        # Specific-date classes

        elif (

            c.get("type") == "specific"

            and c.get("date") == current_date.strftime("%Y-%m-%d")

        ):

            upcoming_classes.append({

                "date": current_date,

                "subject": c["subject"],

                "room": c["room"],

                "start": c["start"],

                "end": c["end"]

            })

# Sort by date and time

upcoming_classes.sort(

    key=lambda x: (x["date"], time_to_minutes(x["start"]) if time_to_minutes(x["start"]) is not None else 0)

)

if upcoming_classes:

    # Next class

    next_class = upcoming_classes[0]

    st.subheader("⭐ Next Class")

    st.info(

        f"📚 **{next_class['subject']}**\n\n"

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

st.divider()

# -------------------------

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

                    not in c.get("deleted_dates",[])

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

        key=lambda x: (x["date"], time_to_minutes(x["start"]) if time_to_minutes(x["start"]) is not None else 0)

    )

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

            start_month

            + timedelta(days=i)

        )

        day_number = str(

            possible_date.day

        )

        month_name = (

            possible_date

            .strftime("%B")

            .lower()

        )

        if (

            day_number in q

            and month_name in q

        ):

            reference_date = possible_date

            break

    # =====================================================

    # NEW FEATURE 1

    # HOW MANY CLASSES?

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

            week_end = week_start + timedelta(

                days=6

            )

            matching = [

                c for c in upcoming

                if (

                    week_start

                    <= c["date"]

                    <= week_end

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

                    c["date"].month

                    == today.month

                    and c["date"].year

                    == today.year

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

    # NEW FEATURE 2

    # FIRST CLASS

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

    # NEW FEATURE 3

    # LAST CLASS

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

    # NEW FEATURE 4

    # BUSIEST DAY

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

                day_name = c["date"].strftime(

                    "%A"

                )

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

    # NEW FEATURE 6

    # CLASSES IN A SPECIFIC WEEK OF A MONTH

    # =====================================================

    elif (

        (

            "week" in q

            or "weeks" in q

        )

        and any(

            ordinal in q

            for ordinal in [

                "1st",

                "2nd",

                "3rd",

                "4th",

                "5th",

                "first",

                "second",

                "third",

                "fourth",

                "fifth"

            ]

        )

        and any(

            month in q

            for month in [

                "january",

                "february",

                "march",

                "april",

                "may",

                "june",

                "july",

                "august",

                "september",

                "october",

                "november",

                "december"

            ]

        )

    ):

        # -------------------------

        # FIND WEEK NUMBER

        # -------------------------

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

        # -------------------------

        # FIND MONTH

        # -------------------------

        requested_month = None

        for month_number in range(1, 13):

            month_name = (

                calendar.month_name[month_number]

                .lower()

            )

            if month_name in q:

                requested_month = month_number

                break

        # -------------------------

        # FIND YEAR

        # -------------------------

        requested_year = today.year

        # If a year is mentioned, use it

        for year in range(

            today.year - 5,

            today.year + 6

        ):

            if str(year) in q:

                requested_year = year

                break

        # -------------------------

        # FIND CALENDAR WEEK DATES

        # Monday - Sunday

        # -------------------------

        first_day = date(

            requested_year,

            requested_month,

            1

        )

        # Find the Monday of the first calendar week

        first_monday = (

            first_day

            - timedelta(days=first_day.weekday())

        )

        # Find the requested Monday

        week_start = (

            first_monday

            + timedelta(days=(week_number - 1) * 7)

        )

        # Sunday of that calendar week

        week_end = week_start + timedelta(days=6)

        # -------------------------

        # FIND CLASSES

        # -------------------------

        week_classes = []

        current_week_date = week_start

        while current_week_date <= week_end:

            current_day = (

                current_week_date.strftime("%A")

            )

            date_string = (

                current_week_date.strftime("%Y-%m-%d")

            )

            for c in st.session_state.classes:

                # WEEKLY CLASS

                if (

                    c.get("type") == "weekly"

                    and c.get("day") == current_day

                    and date_string

                        not in c.get(

                            "deleted_dates",

                            []

                        )

                ):

                    week_classes.append({

                        "date": current_week_date,

                        "subject": c["subject"],

                        "room": c["room"],

                        "start": c["start"],

                        "end": c["end"]

                    })

                # SPECIFIC-DATE CLASS

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

        # -------------------------

        # FILTER SUBJECT

        # -------------------------

        if matched_subject:

            week_classes = [

                c for c in week_classes

                if c["subject"].lower()

                == matched_subject.lower()

            ]

        # -------------------------

        # SORT CLASSES

        # -------------------------

        week_classes.sort(

            key=lambda x: (

                x["date"],

                x["start"]

            )

        )

        # -------------------------

        # DISPLAY

        # -------------------------

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

    # NEW FEATURE 5

    # CLASSES THIS WEEK

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

        week_start = today - timedelta(

            days=today.weekday()

        )

        week_end = week_start + timedelta(

            days=6

        )

        week_classes = [

            c for c in upcoming

            if (

                week_start

                <= c["date"]

                <= week_end

            )

        ]

        if matched_subject:

            week_classes = [

                c for c in week_classes

                if c["subject"].lower()

                == matched_subject.lower()

            ]

        if week_classes:

            st.success(

                "Here are your classes this week:"

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

                "You don't have any classes this week."

            )

    # =====================================================

    # NEW FEATURE 6

    # SUBJECTS THIS WEEK

    # =====================================================

    elif (

        "subjects" in q

        and (

            "this week" in q

            or "week" in q

        )

    ):

        week_start = today - timedelta(

            days=today.weekday()

        )

        week_end = week_start + timedelta(

            days=6

        )

        week_classes = [

            c for c in upcoming

            if (

                week_start

                <= c["date"]

                <= week_end

            )

        ]

        unique_subjects = []

        for c in week_classes:

            if c["subject"] not in unique_subjects:

                unique_subjects.append(

                    c["subject"]

                )

        if unique_subjects:

            st.success(

                "Your subjects this week are:"

            )

            for subject in unique_subjects:

                st.write(

                    f"📚 **{subject}**"

                )

        else:

            st.info(

                "You don't have any classes this week."

            )

    # =====================================================

    # NEW FEATURE 7

    # WHAT COMES AFTER A SUBJECT?

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

                    c["subject"].lower()

                    == matched_subject.lower()

                    and c["date"] >= today

                )

            ]

            if subject_classes:

                reference_class = subject_classes[0]

                following_classes = [

                    c for c in upcoming

                    if (

                        c["date"]

                        > reference_class["date"]

                        or (

                            c["date"]

                            == reference_class["date"]

                            and time_to_minutes(c["start"]) > time_to_minutes(reference_class["start"])

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

                    st.info(

                        "I couldn't find another class after that."

                    )

            else:

                st.info(

                    f"I couldn't find an upcoming "

                    f"**{matched_subject}** class."

                )

        else:

            st.info(

                "Please mention the subject you want "

                "to find the following class for."

            )

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

                if c["subject"].lower()

                == matched_subject.lower()

            ]

        if today_classes:

            for c in today_classes:

                st.write(

                    f"📚 **{c['subject']}** — "

                    f"🕐 {c['start']} — "

                    f"🏫 {c['room']}"

                )

        else:

            st.info(

                "You don't have any matching classes today."

            )

    # =====================================================

    # BEFORE DATE

    # =====================================================

    elif "before" in q:

        if matched_subject:

            matching_classes = [

                c for c in upcoming

                if (

                    c["subject"].lower()

                    == matched_subject.lower()

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

                    c["subject"].lower()

                    == matched_subject.lower()

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

                if c["subject"].lower()

                == matched_subject.lower()

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

            "january",

            "february",

            "march",

            "april",

            "may",

            "june",

            "july",

            "august",

            "september",

            "october",

            "november",

            "december"

        ]

    ):

        requested_month = None

        for month_number in range(1, 13):

            month_name = (

                calendar.month_name[month_number]

                .lower()

            )

            if month_name in q:

                requested_month = month_number

                break

        month_classes = [

            c for c in upcoming

            if c["date"].month

            == requested_month

        ]

        if matched_subject:

            month_classes = [

                c for c in month_classes

                if c["subject"].lower()

                == matched_subject.lower()

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

                if c["subject"].lower()

                == matched_subject.lower()

            ]

        if tomorrow_classes:

            for c in tomorrow_classes:

                st.write(

                    f"📚 **{c['subject']}** — "

                    f"🕐 {c['start']} — "

                    f"🏫 {c['room']}"

                )

        else:

            st.info(

                "You don't have any matching classes tomorrow."

            )

    # =====================================================

    # NEXT CLASS

    # =====================================================

    elif "next" in q and "class" in q:

        if matched_subject:

            matching_classes = [

                c for c in upcoming

                if (

                    c["subject"].lower()

                    == matched_subject.lower()

                    and c["date"] >= today

                )

            ]

            if matching_classes:

                c = matching_classes[0]

                st.success(

                    f"Your next **{c['subject']}** class is on "

                    f"**{c['date'].strftime('%A, %d %B')}** "

                    f"at **{c['start']}** in **{c['room']}**."

                )

            else:

                st.info(

                    f"I couldn't find any upcoming "

                    f"**{matched_subject}** classes."

                )

        else:

            future_classes = [

                c for c in upcoming

                if c["date"] >= today

            ]

            if future_classes:

                c = future_classes[0]

                st.success(

                    f"Your next class is **{c['subject']}** "

                    f"on **{c['date'].strftime('%A, %d %B')}** "

                    f"at **{c['start']}** in **{c['room']}**."

                )

            else:

                st.info(

                    "You don't have any upcoming classes."

                )

    # =====================================================

    # WHERE / ROOM

    # =====================================================

    elif "where" in q or "room" in q:

        found = False

        if matched_subject:

            for c in upcoming:

                if (

                    c["subject"].lower()

                    == matched_subject.lower()

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

            st.info(

                "I couldn't find that subject in your timetable."

            )

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