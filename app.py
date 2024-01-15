import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('data/fake_data_clean.csv')

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
    data_conv = (data[['EmployeeID','RegularHours','OvertimeHours']]
             .rename(columns={'EmployeeID':'Key','RegularHours':'E_Hourly Regular_Hours','OvertimeHours':'E_Overtime_Hours'}))
    
    st.dataframe(data_conv)


#%% TAB 2: Data Visualization
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        data_viz = (
            data
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
        st.empty()


#%% TAB 3: Summary Statistics
with tab3:
    data_stats = (
        data
        .groupby(['Store'])
        .agg({'EmployeeName':'count',
            'RegularHours':'sum',
            'OvertimeHours':'sum',
            'TotalHours':'sum',
            'RegPay':'sum',
            'OverPay':'sum',
            'TotalPay':'sum',
            })
    )

    data_stats_hours = (
        data_stats[['EmployeeName','RegularHours','OvertimeHours','TotalHours']]
        .assign(ot_per = 100*round(data_stats.OvertimeHours / data_stats.TotalHours, 3))
        .rename(columns={'EmployeeName':'# Employees',
                        'RegularHours':'Total Reg Hours',
                        'OvertimeHours':'Total OT Hours',
                        'TotalHours':'Total Hours',
                        'ot_per':'% OT Hours'
                        })
    )

    data_stats_pay = (
        data_stats[['EmployeeName','RegPay','OverPay','TotalPay']]
        .assign(ot_per = 100*round(data_stats.OverPay / data_stats.TotalPay, 3))
        .rename(columns={'EmployeeName':'# Employees',
                        'RegPay':'Total Reg Pay',
                        'OverPay':'Total OT Pay',
                        'TotalPay':'Total Pay',
                        'ot_per':'% OT Pay'
                        })
    )

    st.write('Total Hours per Pay Period')
    st.dataframe(data_stats_hours)
    st.write('Total Pay per Pay Period')
    st.dataframe(data_stats_pay)




#%% TAB 3: Anomalies
with tab4:
    anomalies = (
            data
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
    fig, axs = plt.subplots(ncols=4, figsize=(12,4))
    # axs = axs.flatten()

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

