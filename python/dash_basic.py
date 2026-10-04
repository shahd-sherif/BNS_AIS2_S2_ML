from dash import Dash, html, dcc, Input, Output
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

df=pd.read_excel(r'C:\Users\MOBI LAP\BNS_AIS2_S2_ML\python\data1.xlsx')
app= Dash()
app.title="Interactive Dashboard"
num_cols=df.select_dtypes(include='number').columns
app.layout=html.Div([
    html.H1("Interative Dashboard with pie plot"),
    html.Label("select a value to show in the pie chart"),
    dcc.Dropdown(id='column-dropdown',
    options=[{'label':col,'value':col} for col in num_cols],
    value=num_cols[0]),
    dcc.Graph(id='pie-plot')

])
@app.callback(Output('pie-plot','figure'),
              Input('column-dropdown','value'))
def update_pie_plot(selected_col):
    grouped=df.groupby('Area')[selected_col].sum().reset_index()
    fig=px.pie(grouped,names='Area',values=selected_col,title=f"distribution of {selected_col} by area",hole=0.4,color_discrete_sequence=px.colors.qualitative.Set2)
    return fig





if __name__=='__main__':
    app.run(debug=True)