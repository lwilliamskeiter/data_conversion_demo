import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

data_clean = pd.read_csv('data/fake_data_clean.csv')

#%% APP
st.set_page_config(
     page_title='Data Conversion Demo',
     layout="wide",
)
st.markdown("## Data Conversion Demo")


# tab1, tab2, tab3 = st.tabs(["Data Conversion", "Data Visualization", "Summary Statistics"])
tab1, tab2, tab3, tab4 = st.tabs(["Data Conversion", "Data Visualization", "Summary Statistics", "Anomalies"])

#%% TAB 1: Data Conversion
with tab1:
    data_conv = (data_clean[['EmployeeID','RegularHours','OvertimeHours']]
                 .rename(columns={'EmployeeID':'Key','RegularHours':'E_Hourly Regular_Hours','OvertimeHours':'E_Overtime_Hours'}))
    
    st.dataframe(data_conv)


#%% TAB 2: Data Visualization
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        data_viz = (
            data_clean
            .groupby(['EndDate'])
            .agg({'TotalHours':'mean', 'OvertimeHours':'mean',})
            .reset_index()
            .rename(columns={'TotalHours':'Total Hours','OvertimeHours':'Overtime Hours'})
        )

        # Plot
        plt1 = data_viz.plot(
            kind='bar',
            x='EndDate',
            stacked=True,
            xlabel='Pay Period End',
            ylabel='Average Pay Period Hours',
            rot=0
        )
        # Move legend outside plot
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
        plt.title('With % OT Hours',fontsize=10)
        plt.suptitle('Average Hours Worked by all Employees per Pay Period',x=.46,y=.95)
        plt.tight_layout()

        # Add text labels
        for x in plt1.containers:
            # Only create labels on OT hours part
            labels = [str(100*round(data_viz['Overtime Hours']/data_viz['Total Hours'],3)[i])+'%' if 0 < v.get_height() < 60 else '' for i,v in enumerate(x)]
            # Add label to bar
            plt1.bar_label(x, labels=labels, label_type='center')
        
        st.pyplot(plt1.figure)

    with col2:
        anomalies = (
            data_clean
            .groupby(['Store','Description'])
            .agg({'EmployeeName':'count'})
            .reset_index()
            # .rename(columns={'EmployeeName'})
        )

        # Unique categories
        categories = anomalies['Description'].unique()
        stores = anomalies['Store'].unique()
        colors = {'Store A': 'lightblue', 'Store B': 'green', 'Store C': 'purple', 'Store D': 'darkblue', 'Store E': 'pink', 'Store F': 'orange', 'Store G': 'indigo'}

        # Create a figure and axes
        fig, axs = plt.subplots(nrows=2 ,ncols=2, figsize=(6,6))
        axs = axs.flatten()

        # Iterate over each category and create a plot
        for ax, category in zip(axs, categories):
            # Select Employee type and fill in 0s if a store does not have any of that employee type
            sub_df = (anomalies[anomalies['Description'] == category]
                    .set_index('Store').reindex(stores).fillna(value={'EmployeeName':0}).ffill().reset_index())
            # Create sublplot
            sub_df.plot(x='Store', y='EmployeeName', kind='bar', ax=ax, title=category, 
                        color=[colors[x] for x in sub_df['Store']],ylim=(0,10),legend=False,xlabel='')
        
        plt.suptitle('Number of Employees per Position per Store')
        plt.tight_layout()

        st.pyplot(fig)


#%% TAB 3: Summary Statistics
with tab3:
    col1,col2 = st.columns([1.25,2],gap='small')
    
    data_stats = (
        data_clean
        .drop(columns=['EmployeeID','TimeCard','EmployeeName','EmployeeExtRef','ShortDescription','ExternalReference','RegPay','OverPay','TotalPay'])
    )

    with col1:
        st.write('Summary Statistics')
        st.dataframe(data_stats[data_stats.columns[[str(x)!='object' for x in data_stats.dtypes]]].describe().round(2))

    with col2:
        st.write('Categorical Frequencies')
        st.dataframe(data_stats[data_stats.columns[[str(x)=='object' for x in data_stats.dtypes]]].describe())


#%% TAB 4: Anomalies
with tab4:
    # col1, col2 = st.columns([3,3])
    data_stats2 = data_clean.drop(columns=['TimeCard','EmployeeName','EmployeeExtRef','ShortDescription','ExternalReference','RegPay','OverPay','TotalPay'])
    
    # with col1:
    st.write('Pay Periods Worked for Employees with Missing Break Time')
    st.dataframe((data_stats2[data_stats2.BreakTime.isna() & (data_stats2.RateTimeFrame!='Monthly')]
                  [['EmployeeID','Store','Description','Minor','RateType','RateTimeFrame',
                    'BeginDate','EndDate','RegularHours','OvertimeHours','TotalHours','BreakTime']]))

    # with col2:
    if any(data_clean.groupby(['EmployeeID']).Store.count() < len(data_clean[['BeginDate','EndDate']].drop_duplicates())):
        missing_weeks_emps = (
            data_clean.groupby(['EmployeeID']).Store.count()
            [data_clean.groupby(['EmployeeID']).Store.count() < len(data_clean[['BeginDate','EndDate']].drop_duplicates())]
            .reset_index()['EmployeeID'].values
        )
        
        st.write('Pay Periods Worked for Employees with Missing Pay Periods')
        st.dataframe((data_stats2[data_stats2['EmployeeID'].isin(missing_weeks_emps)]
                      [['EmployeeID','Store','Description','Minor','RateType','RateTimeFrame',
                        'BeginDate','EndDate','RegularHours','OvertimeHours','TotalHours']]))
    else:
        st.empty()
        

    

