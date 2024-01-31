import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

data_clean = pd.read_csv('data/fake_data_clean2.csv')

#%% APP
st.set_page_config(
     page_title='Data Conversion Demo',
    #  layout="wide",
)


def intro():
    st.markdown('## Data Demos')

    st.markdown("""
Select a data demo from the drop down menu to the left!
    """)


def data_conversion():
    st.markdown("## Data Conversion")

    data_conv = data_clean.rename(columns={'EmployeeID':'Key','RegularHours':'E_Hourly Regular_Hours','OvertimeHours':'E_Overtime_Hours'})
    st.dataframe(data_conv[['Key','E_Hourly Regular_Hours','E_Overtime_Hours']], hide_index=True, use_container_width=True)

def data_viz():    
    st.markdown("## Data Visualization")
    tab1, tab2 = st.tabs(['Pay Period Hours','Store Employees'])

    with tab1:
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
            rot=0,
            figsize=(6.4,4.8)
        )
        # Move legend outside plot
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
        plt.title('With % OT Hours',fontsize=10)
        plt.suptitle('Average Hours Worked by all Employees per Pay Period',x=.52,y=.95,size=15)
        plt.tight_layout()

        # Add text labels
        for x in plt1.containers:
            # Only create labels on OT hours part
            labels = [str(100*round(data_viz['Overtime Hours']/data_viz['Total Hours'],3)[i])+'%' if 0 < v.get_height() < 60 else '' for i,v in enumerate(x)]
            # Add label to bar
            plt1.bar_label(x, labels=labels, label_type='center')
        
        with st.container(border=True):
            st.pyplot(plt1.figure)
    
    with tab2:
        anomalies = (
            data_clean
            .groupby(['Store','Description'])
            .agg({'EmployeeName':'count'})
            .reset_index()
        )

        # Unique categories
        categories = anomalies['Description'].unique()
        stores = anomalies['Store'].unique()
        colors = {'Store A': 'lightblue', 'Store B': 'green', 'Store C': 'purple', 'Store D': 'darkblue', 'Store E': 'pink', 'Store F': 'orange', 'Store G': 'indigo'}

        # Create a figure and axes
        fig, axs = plt.subplots(nrows=2 ,ncols=2, sharex=True, sharey=True, figsize=(6.4,4.8))
        axs = axs.flatten()

        # Iterate over each category and create a plot
        for ax, category in zip(axs, categories):
            # Select Employee type and fill in 0s if a store does not have any of that employee type
            sub_df = (anomalies[anomalies['Description'] == category]
                      .set_index('Store').reindex(stores)
                      .fillna(value={'EmployeeName':0}).ffill().reset_index())
            # Create sublplot
            # ax.tick_params(which='both',labelbottom=False)
            sub_df.plot(x='Store', y='EmployeeName', kind='bar', ax=ax, title=category,     
                        color=[colors[x] for x in sub_df['Store']],ylim=(0,10),legend=False,xlabel='')

        # Rotate x-axis tick labels for the bottom row subplots
        for ax in axs[-2:]:  # Selects the last two axes (bottom row) for rotation
            ax.tick_params(axis='x', labelrotation=45)

        plt.suptitle('Number of Employees per Position per Store',size=15)
        # plt.tight_layout(rect=[0, 0, .95, 0.95])
        plt.tight_layout()

        legend_elements = [Patch(facecolor=col, label=cat) for col, cat in zip(colors.values(), colors.keys())]
        # fig.legend(bbox_to_anchor=(-.025, .75),handles=legend_elements, borderaxespad=0)
        # fig.legend(handles=legend_elements,ncol=len(colors),# fontsize='medium',
        #            handlelength=.5, handletextpad=0.5, columnspacing=1.25,
        #            loc='lower center',bbox_to_anchor=(.5,.86),borderaxespad=0)

        with st.container(border=True):
            st.pyplot(fig)


def summary_stats():    
    st.markdown("## Data Summary")

    tab1, tab2 = st.tabs(['Summary Statistics','Categorical Frequencies'])
    data_stats = (
        data_clean
        .drop(columns=['EmployeeID','TimeCard','EmployeeName','EmployeeExtRef','ShortDescription','ExternalReference'])
    )

    with tab1:
        # st.write('Summary Statistics')
        st.dataframe(data_stats[data_stats.columns[[str(x)!='object' for x in data_stats.dtypes]]].describe().round(2))

    with tab2:
        # st.write('Categorical Frequencies')
        st.dataframe(data_stats[data_stats.columns[[str(x)=='object' for x in data_stats.dtypes]]].describe())


def anomalies():    
    st.markdown("## Data Anomalies")
    data_stats2 = data_clean.drop(
        columns=['TimeCard','EmployeeName','EmployeeExtRef','ShortDescription','ExternalReference','RateTimeFrame']
        ).rename(columns={'OvertimeHours':'OTHours'})

    st.write('Pay Periods Worked for Employees with Missing Break Time')
    st.dataframe((data_stats2[data_stats2.BreakTime.isna() & (data_stats2.RateType!='Salary')]
                    [['EmployeeID','Store','Description','Minor','RateType',
                    'BeginDate','EndDate','RegularHours','OTHours','TotalHours','BreakTime']]),
                    hide_index=True)

    if any(data_clean.groupby(['EmployeeID']).Store.count() < len(data_clean[['BeginDate','EndDate']].drop_duplicates())):
        missing_weeks_emps = (
            data_clean.groupby(['EmployeeID']).Store.count()
            [data_clean.groupby(['EmployeeID']).Store.count() < len(data_clean[['BeginDate','EndDate']].drop_duplicates())]
            .reset_index()['EmployeeID'].values
        )
        
        st.write('Pay Periods Worked for Employees with Missing Pay Periods')
        st.dataframe((data_stats2[data_stats2['EmployeeID'].isin(missing_weeks_emps)]
                        [['EmployeeID','Store','Description','Minor','RateType',
                        'BeginDate','EndDate','RegularHours','OTHours','TotalHours']]),
                        hide_index=True)
    else: st.empty()


#%% OUTPUT
page_names_to_funcs = {
    "Select a demo":intro,
    "Data Conversion": data_conversion,
    "Data Visualization":data_viz,
    "Data Summary":summary_stats,
    "Data Anomalies":anomalies
}


demo_name = st.sidebar.selectbox("Data Demos", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
