import pandas as pd
import numpy as np
import seaborn as sns
import io
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter

st.title("Ohio Checkbook Reader")

st.header("Import")

data = st.file_uploader("Upload a File", type=["csv", "xlsx", "xls"])

if data is not None:

    st.header("Dataframe")

    if data.name.endswith(".csv"):
        df = pd.read_csv(data)
    elif data.name.endswith ((".xls", ".xlsx")):
        df = pd.read_excel(data)
    df.columns = df.columns.str.title()
    df["Account"] = df["Account"].astype(str)
    searchquery = st.text_input("Search by Account Number")
    if searchquery:
        df = df[df["Account"].str.contains(search_query, case=False, na=False)]
    minamount = st.number_input("Minimum Payment", value=df["Payment_Amount"].min())
    maxamount = st.number_input("Maximum Payment", value=df["Payment_Amount"].max())
    df = df[(df["Payment_Amount"]>=minamount) & (df["Payment_Amount"]<=maxamount)]
    selecteddepartment = st.multiselect("Filter by Department", options=df["Department_Description"].unique(), default=df["Department_Description"].unique())
    filtered_df = df[df["Department_Description"].isin(selecteddepartment)]
    st.dataframe(filtered_df, width="stretch")
    
    st.header("Benford Analysis")

    benforddf = df.copy()
    
    lead1 = abs(benforddf["Payment_Amount"].astype(float)*1000000).astype(int).astype(str).str.slice(0, 1).astype(int)
    lead2 = abs(benforddf["Payment_Amount"].astype(float)*1000000).astype(int).astype(str).str.slice(0, 2).astype(int)
    
    cnt1a = Counter(lead1)
    cnt2a = Counter(lead2)
    cnt1b = {}
    for i in range(0, 10):
        cnt1b[i] = cnt1a[i]
    cnt2b = {}
    for i in range(10, 100):
        cnt2b[i] = cnt2a[i]
    
    p1 = cnt1b.copy()
    for i in p1:
        p1[i] = cnt1b[i] / sum(cnt1b.values())
    p2 = cnt2b.copy()
    for i in p2:
        p2[i] = cnt2b[i] / sum(cnt2b.values())
    
    benford1 = {}
    benford1[0] = 0
    for i in range(1, 10):
        benford1[i] = float(np.log10(1+1/i))
    benford2 = {}
    for i in range(10, 100):
        benford2[i] = float(np.log10(1+1/i))
    
    dif1 = {}
    for i in p1:
        dif1[i]= (p1[i] - benford1[i])
    dif2 = {}
    for i in p2:
        dif2[i]= (p2[i] - benford2[i])
    
    leaddigit1 = {}
    for i in range(0, 10):
        leaddigit1[i] = i
    leaddigit2 = {}
    for i in range(10,100):
        leaddigit2[i] = i

    st.write("Leading Digit vs Benford Probabilities")
    benfordadf1 = pd.DataFrame({'Leading_Digit': leaddigit1,
                    'Count': cnt1b,
                    'Proportion': p1,
                    'Benford': benford1,
                    'Difference': dif1})
    st.dataframe(benfordadf1, width="stretch")
    cum_diff1 = np.cumsum(benfordadf1['Proportion'].values) - np.cumsum(benfordadf1['Benford'].values)
    max_diff1 = np.max(np.abs(cum_diff1))
    st.write('Maximum Difference:', max_diff1)
    critical_value1 = 1.36 / np.sqrt(benfordadf1['Count'].sum())
    st.write('Critical value for KS test at alpha=0.05:', critical_value1)
    
    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=False).encode("utf-8")

    benfordadfcsv1 = convert_df_to_csv(benfordadf1)
    
    st.download_button(
        label="Download Benford Analysis as CSV",
        data=benfordadfcsv1,
        file_name="Leading Digit Benford Analysis.csv",
        mime="text/csv",
        icon=":material/download:")
    
    st.space()
    st.write("Leading Two Digits vs Benford Probabilities")
    benfordadf2 = pd.DataFrame({'Leading_Digits': leaddigit2,
                    'Count': cnt2b,
                    'Proportion': p2,
                    'Benford': benford2,
                    'Difference': dif2})
    st.dataframe(benfordadf2, width="stretch")
    cum_diff2 = np.cumsum(benfordadf2['Proportion'].values) - np.cumsum(benfordadf2['Benford'].values)
    max_diff2 = np.max(np.abs(cum_diff2))
    st.write('Maximum Difference:', max_diff2)
    critical_value1 = 1.36 / np.sqrt(benfordadf2['Count'].sum())
    st.write('Critical value for KS test at alpha=0.05:', critical_value1)

    def convert_df_to_csv(dataframe):
            return dataframe.to_csv(index=False).encode("utf-8")
    
    benfordadfcsv2 = convert_df_to_csv(benfordadf2)
    
    st.download_button(
    label="Download Benford Analysis as CSV",
    data=benfordadfcsv2,
    file_name="Leading Two Digits Benford Analysis.csv",
    mime="text/csv",
    icon=":material/download:")

    st.header("Benford Analysis Visualization")

    sns.set_theme(style="darkgrid", font_scale=1.8)

    benfordplot1 = {}
    benfordplot1['Leading Digit'] = benfordadf1['Leading_Digit']
    benfordplot1['Observed'] = benfordadf1['Proportion']
    benfordplot1['Benford'] = benfordadf1['Benford']

    benfordplot2 = {}
    benfordplot2['Leading Digits'] = benfordadf2['Leading_Digits']
    benfordplot2['Observed'] = benfordadf2['Proportion']
    benfordplot2['Benford'] = benfordadf2['Benford']

    fig1, ax1 = plt.subplots(figsize=(30, 16))
    sns.barplot(data=benfordplot1, x="Leading Digit", y="Observed", label="Observed", ax=ax1)
    sns.lineplot(data=benfordplot1, x="Leading Digit", y="Benford", color="red", label="Benford", ax=ax1)
    ax1.set_ylabel('Observed vs Benford')
    ax1.set_title('Leading Digit vs Benford Probabilities')
    st.pyplot(fig1)

    chart1 = io.BytesIO()
    fig1.savefig(chart1, format="png", dpi=300, bbox_inches="tight")
    chart1.seek(0)
    
    st.download_button(
        label="Download Graph",
        data=chart1,
        file_name="Leading Digit vs Benford Graph.png",
        mime="image/png")

    fig2, ax2 = plt.subplots(figsize=(30, 16))
    sns.barplot(data=benfordplot2, x="Leading Digits", y="Observed", native_scale=True, label="Observed", ax=ax2, gap=0.2)
    sns.lineplot(data=benfordplot2, x="Leading Digits", y="Benford", color="red", label="Benford", ax=ax2)
    ax2.xaxis.set_major_locator(ticker.MultipleLocator(5))
    ax2.set_ylabel('Observed vs Benford')
    ax2.set_title('Leading Digits vs Benford Probabilities')
    st.pyplot(fig2)

    chart2 = io.BytesIO()
    fig2.savefig(chart2, format="png", dpi=300, bbox_inches="tight")
    chart2.seek(0)

    st.download_button(
        label="Download Graph",
        data=chart2,
        file_name="Leading Two Digits vs Benford Graph.png",
        mime="image/png")

    st.header("Statistical Analysis")

    stats = df.describe()
    st.write("File Summary Statistics")
    st.dataframe(stats)

    def convert_df_to_csv(dataframe):
        return dataframe.to_csv(index=True).encode("utf-8")
       
    statscsv = convert_df_to_csv(stats)
       
    st.download_button(
        label="Download Summary Statistics as CSV",
        data=statscsv,
        file_name="Summary Statistics.csv",
        mime="text/csv",
        icon=":material/download:")