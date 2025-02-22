import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def get_employee_interactions_line_plot(logs):
    df = pd.DataFrame(logs)
    df['scaled_timestamp'] = df['scaled_timestamp'].dt.floor('D')
    df = df.groupby(['scaled_timestamp', 'emp_id']).size().reset_index(name='daily_interactions')
    fig = go.Figure()

    for emp in df['emp_id'].unique():
        emp_data = df[df['emp_id'] == emp]

        fig.add_trace(go.Scatter(
            x=emp_data['scaled_timestamp'],
            y=emp_data['daily_interactions'],
            mode='lines+markers',
            name=f'Employee {emp}'
        ))

    fig.update_layout(
        title="Employee Interactions Over Time",
        xaxis_title="Date",
        yaxis_title="Interactions",
        showlegend=True,
        xaxis=dict(tickformat='%Y-%m-%d'),
    )

    return fig


def get_employee_interactions_by_employee_by_authorization(logs):
    df = pd.DataFrame(logs)
    df['scaled_timestamp'] = df['scaled_timestamp'].dt.floor('D')
    df = df.groupby(['scaled_timestamp', 'emp_id', 'authorized']).size().reset_index(name='daily_interactions')

    emp_ids = df['emp_id'].unique()
    states = df['authorized'].unique()

    fig = make_subplots(
        rows=len(emp_ids),
        cols=len(states),
        shared_xaxes=True,
        shared_yaxes=True,
        subplot_titles=[f"Emp {emp_id} - Authorized={state}" for emp_id in emp_ids for state in states]
    )

    row = 1
    col = 1
    for emp_id in emp_ids:
        for state in states:
            product_data = df[(df['emp_id'] == emp_id) & (df['authorized'] == state)]

            trace = go.Scatter(
                x=product_data['scaled_timestamp'],
                y=product_data['daily_interactions'],
                mode='lines+markers',
                name=f'Emp {emp_id} - Authorized={state}'
            )

            fig.add_trace(trace, row=row, col=col)

            col += 1
        row += 1
        col = 1

    fig.update_layout(
        title="Authorized Interactions By Employee",
        showlegend=False,
        height=600,
        xaxis_title="Date",
        yaxis_title="Interactions",
        xaxis=dict(tickformat='%Y-%m-%d'),
        title_x=0.5
    )

    return fig
