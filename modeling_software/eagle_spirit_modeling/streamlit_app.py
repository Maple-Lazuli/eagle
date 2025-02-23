import streamlit as st
import network_plot as np
import datetime
import plot_functions as pf
import utilities as u

if "department" not in st.session_state:
    st.session_state.department = None

if "division" not in st.session_state:
    st.session_state.division = None

if "selected_division" not in st.session_state:
    st.session_state.selected_division = None

if "selected_section" not in st.session_state:
    st.session_state.selected_section = None

if "section" not in st.session_state:
    st.session_state.section = None

if "departments" not in st.session_state:
    st.session_state.departments = u.get_departments()

if "metrics_ready" not in st.session_state:
    st.session_state.metrics_ready = None

if "start_date" not in st.session_state:
    st.session_state.start_date = None

if "end_date" not in st.session_state:
    st.session_state.end_date = None


def filter_logs():
    logs = st.session_state.logs
    start = datetime.datetime.combine(st.session_state.start_date, datetime.time(0, 0, 0)).timestamp()
    end = datetime.datetime.combine(st.session_state.stop_date, datetime.time(0, 0, 0)).timestamp()

    return [l for l in logs if start <= l['scaled_timestamp'].timestamp() <= end]


@st.cache_data
def interactions_line_plot(logs):
    return pf.get_employee_interactions_line_plot(logs)


@st.cache_data
def authorization_line_plot(logs):
    return pf.get_employee_interactions_by_employee_by_authorization(logs)


@st.cache_data
def interactions_histogram(logs):
    return pf.employee_hour_histogram(logs)


# Select the department
st.session_state.selected_department = st.selectbox(
    "Select A department",
    [None] + [d[1] for d in st.session_state.departments])

# Get the ID of the selected department to start looking for sections
if st.session_state.selected_department is not None:

    for department in st.session_state.departments:
        if department[1] == st.session_state.selected_department:
            st.session_state.department = department[0]
            break

# Select the division from the department
if st.session_state.department is not None:
    st.session_state.divisions = u.get_divisions(st.session_state.department)

    st.session_state.selected_division = st.selectbox(
        "Select A division",
        [None] + [d[1] for d in st.session_state.divisions])

# Get the division ID.
if st.session_state.selected_division is not None:

    for division in st.session_state.divisions:
        if division[1] == st.session_state.selected_division:
            st.session_state.division = division[0]
            break

# Select the section from the division
if st.session_state.division is not None:
    st.session_state.sections = u.get_sections(st.session_state.division)

    st.session_state.selected_section = st.selectbox(
        "Select A section",
        [None] + [d[1] for d in st.session_state.sections])

# Get the section ID
if st.session_state.selected_section is not None:

    for section in st.session_state.sections:
        if section[1] == st.session_state.selected_section:
            st.session_state.section = section[0]
            break

# Get section details
if st.session_state.section is not None:
    st.session_state.section_details = u.get_section(st.session_state.section)
    sel_sec = st.session_state.selected_section
    sel_div = st.session_state.selected_division
    sel_dep = st.session_state.selected_department

    st.markdown("***")
    st.markdown(f"## {sel_dep} ")
    st.markdown(f"### {sel_div} > {sel_sec}")

    team_lead = u.get_employee(st.session_state.section_details['lead_id'])
    st.markdown(f"**Team Lead**: {team_lead['first_name']} {team_lead['last_name']}")
    st.markdown(f"**Work Day(s)**: {u.get_workdays_str(st.session_state.section_details)}")
    st.markdown(f"**Start Time**: {int(st.session_state.section_details['start_hour']) * 100} ")

    section_employees = u.get_employees(st.session_state.section)

    st.markdown("**Employees**:")
    for idx, employee in enumerate(section_employees):
        if employee['id'] != team_lead['id']:
            st.markdown(f"{idx}. {employee['first_name']} {employee['last_name']}")

    st.session_state.metrics_ready = True

if st.session_state.metrics_ready is not None:
    st.session_state.logs = u.get_logs_by_employee(st.session_state.section)

    min_time_stamp = min([l['scaled_timestamp'].timestamp() for l in st.session_state.logs])
    max_time_stamp = max([l['scaled_timestamp'].timestamp() for l in st.session_state.logs])

    st.session_state.start_date = st.date_input(
        "Start Date",
        value=None,
        min_value=datetime.datetime.fromtimestamp(min_time_stamp),
        max_value=datetime.datetime.fromtimestamp(max_time_stamp),
    )
if st.session_state.start_date is not None:
    min_time_stamp = min([l['scaled_timestamp'].timestamp() for l in st.session_state.logs])
    max_time_stamp = max([l['scaled_timestamp'].timestamp() for l in st.session_state.logs])

    st.session_state.stop_date = st.date_input(
        "End Date",
        value=None,
        min_value=st.session_state.start_date,
        max_value=datetime.datetime.fromtimestamp(max_time_stamp),
    )

if (st.session_state.start_date is not None) and (st.session_state.stop_date is not None):
    logs = filter_logs()
    st.plotly_chart(interactions_line_plot(logs))
    st.plotly_chart(authorization_line_plot(logs))
    st.plotly_chart(interactions_histogram(logs))
    st.write("Team Resource Usage")
    selected_employee = st.selectbox(
        "Select An Employee To Highlight",
        [None] + list(set([l['emp_id'] for l in logs])))
    st.plotly_chart(np.create_plotly_plot(logs, selected_member=selected_employee))

