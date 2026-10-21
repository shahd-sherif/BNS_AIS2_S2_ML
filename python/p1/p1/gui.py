import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import ShuffleSplit, GridSearchCV
from sklearn.metrics import r2_score, make_scorer

st.set_page_config(
    page_title="Boston Housing Analytics Dashboard",
    page_icon="🏘️",
    layout="wide"
)

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "housing.csv")
    if not os.path.exists(file_path):
        file_path = os.path.join(base_dir, "..", "housing.csv")
    data = pd.read_csv(file_path)
    features = data[['RM', 'LSTAT', 'PTRATIO']]
    prices = data['MEDV']
    return data, features, prices

@st.cache_resource
def train_model(features, prices):
    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
    regressor = DecisionTreeRegressor()
    params = {'max_depth': list(range(1, 11))}
    scoring_fnc = make_scorer(r2_score)
    
    grid = GridSearchCV(regressor, params, scoring=scoring_fnc, cv=cv)
    grid.fit(features, prices)
    return grid.best_estimator_, grid.cv_results_

data, features, prices = load_data()
model, cv_results = train_model(features, prices)

st.sidebar.header("🏠 Property Attributes")
rm = st.sidebar.slider("Number of Rooms (RM)", float(features['RM'].min()), float(features['RM'].max()), float(round(features['RM'].median(), 1)), 0.1)
lstat = st.sidebar.slider("Neighborhood Poverty % (LSTAT)", float(features['LSTAT'].min()), float(features['LSTAT'].max()), float(round(features['LSTAT'].median(), 1)), 0.5)
ptratio = st.sidebar.slider("Pupil-Teacher Ratio (PTRATIO)", float(features['PTRATIO'].min()), float(features['PTRATIO'].max()), float(round(features['PTRATIO'].median(), 1)), 0.5)

input_sample = pd.DataFrame([[rm, lstat, ptratio]], columns=['RM', 'LSTAT', 'PTRATIO'])
predicted_price = model.predict(input_sample)[0]

st.title("🏘️ Boston Housing Market & Valuation Dashboard")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Predicted Home Price", f"${predicted_price:,.2f}")
m2.metric("Optimal Tree Depth", f"{model.get_params()['max_depth']}")
m3.metric("Dataset Median Price", f"${prices.median():,.2f}")
m4.metric("Total Records", f"{len(data)}")

tab_pred, tab_eda, tab_model, tab_batch = st.tabs([
    "Prediction & Context", 
    "Market Trends (EDA)", 
    "Model Diagnostics", 
    "Batch Predictor"
])

with tab_pred:
    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.subheader("Price Estimation Breakdown")
        st.write(f"- **Rooms**: {rm}")
        st.write(f"- **Poverty Rate**: {lstat}%")
        st.write(f"- **Student/Teacher**: {ptratio}:1")
        diff = predicted_price - prices.median()
        st.write(f"- **vs Median Home**: {'+$' if diff >= 0 else '-$'}{abs(diff):,.2f}")
    
    with col_right:
        fig_dist = px.histogram(data, x="MEDV", nbins=30, title="Price Distribution with Your Prediction", labels={"MEDV": "Selling Price ($)"})
        fig_dist.add_vline(x=predicted_price, line_width=3, line_dash="dash", line_color="red", annotation_text="Your Property", annotation_position="top left")
        st.plotly_chart(fig_dist, use_container_width=True)

with tab_eda:
    st.subheader("Interactive Feature Correlations")
    scatter_feature = st.selectbox("Compare Price Against:", ["RM", "LSTAT", "PTRATIO"], index=1)
    
    fig_scatter = px.scatter(
        data, 
        x=scatter_feature, 
        y="MEDV", 
        title=f"Relationship between {scatter_feature} and MEDV",
        labels={"MEDV": "Selling Price ($)"}
    )
    
    curr_x = rm if scatter_feature == "RM" else (lstat if scatter_feature == "LSTAT" else ptratio)
    fig_scatter.add_trace(go.Scatter(
        x=[curr_x], y=[predicted_price],
        mode="markers",
        marker=dict(size=14, color="crimson", symbol="star"),
        name="Current Query"
    ))
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab_model:
    col_diag1, col_diag2 = st.columns(2)
    with col_diag1:
        st.subheader("Feature Importance")
        feat_df = pd.DataFrame({
            'Feature': ['RM', 'LSTAT', 'PTRATIO'],
            'Importance': model.feature_importances_
        }).sort_values(by='Importance', ascending=True)
        fig_feat = px.bar(feat_df, x='Importance', y='Feature', orientation='h', title="Feature Importance Weight")
        st.plotly_chart(fig_feat, use_container_width=True)
        
    with col_diag2:
        st.subheader("Grid Search Validation Curve")
        depths = list(range(1, 11))
        scores = cv_results['mean_test_score']
        fig_curve = px.line(x=depths, y=scores, markers=True, labels={'x': 'Tree Max Depth', 'y': 'Mean R2 Validation Score'}, title="Max Depth vs Model Performance")
        fig_curve.add_vline(x=model.get_params()['max_depth'], line_dash="dot", line_color="green", annotation_text="Selected Depth")
        st.plotly_chart(fig_curve, use_container_width=True)

with tab_batch:
    st.subheader("Upload CSV for Bulk Prediction")
    st.write("Upload a CSV file containing columns: `RM`, `LSTAT`, and `PTRATIO`.")
    uploaded_file = st.file_uploader("Upload property list", type=["csv"])
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        if all(col in batch_df.columns for col in ['RM', 'LSTAT', 'PTRATIO']):
            batch_df['Predicted_MEDV'] = model.predict(batch_df[['RM', 'LSTAT', 'PTRATIO']])
            batch_df['Predicted_MEDV_Formatted'] = batch_df['Predicted_MEDV'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(batch_df, use_container_width=True)
            
            csv_export = batch_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Predictions CSV", data=csv_export, file_name="predictions.csv", mime="text/csv")
        else:
            st.error("Uploaded CSV must contain columns: RM, LSTAT, PTRATIO")