import pandas as pd
import numpy as np
import CommonUtil
from CommonUtil import getSQliteConnection, pushToGitRepo


# Global Variables
filename = "hardware"

def main():

    # converting excel to db
    con = getSQliteConnection(filename)

    # Query to obtain distinct Group parameter
    df_group_parameters = pd.read_sql_query(
        "SELECT DISTINCT `Group` FROM `Page 1` WHERE `Logical status` = 'Operational'", con)

    # Appending AWS region parameter to Group
    df_group_parameters['Region'] = ['US-E-Nvirginia', 'Canada', 'US-E-Nvirginia', 'US-E-Nvirginia']

    # Appending forecasted hardware growth parameter
    df_group_parameters['Year1'] = [1.1, 1, 1, 0.2]
    df_group_parameters['Year2'] = [1.25, 1, 1, 0]
    df_group_parameters['Year3'] = [1.4, 1, 1, 0]

    # Query to obtain a dataframe with only Operational logical status
    df_filtered = pd.read_sql_query("SELECT `Group`,`CPU cores`,`RAM (MB)`,`Container size` FROM `Page 1` WHERE `Logical status` = 'Operational'",con)
    df_filtered.columns = df_filtered.columns.str.strip().str.replace(' ', '_').str.replace('(', '').str.replace(')','')

    print(df_group_parameters)

    con.close()

    #Converting the RAM (MB) to GB and calculate CPU to Memory Ratio
    df_filtered['RAM_GB'] = df_filtered.RAM_MB.apply(lambda x: (x/1000)).apply(np.floor)
    df_filtered['CPUtoMem_Ratio'] = df_filtered.CPU_cores / df_filtered.RAM_GB

    #create a dataframe with cost values Mapped to CPU2MemRatio
    df_cost = getCostMappingDF()

    #Calculate the cost and append to the dataframe
    for df_filteredindex, filteredrow in df_filtered.iterrows():
            for df_costindex, costrow in df_cost.iterrows():
                    if((df_filtered.loc[df_filtered.index[df_filteredindex],'Container_size'] == df_cost.loc[df_cost.index[df_costindex],'ContainerSize']) & (df_filtered.loc[df_filtered.index[df_filteredindex],'CPUtoMem_Ratio'] == df_cost.loc[df_cost.index[df_costindex],'CPUtoMemRatio'])):
                            for df_group_parametersindex, regionrow in df_group_parameters.iterrows():
                                if(df_filtered.loc[df_filtered.index[df_filteredindex],'Group'] == df_group_parameters.loc[df_group_parameters.index[df_group_parametersindex],'Group']):
                                    df_filtered.loc[df_filtered.index[df_filteredindex],'Cost'] = df_cost.loc[df_cost.index[df_costindex],df_group_parameters.loc[df_group_parameters.index[df_group_parametersindex],'Region']]


    print(df_filtered)
    writer = pd.ExcelWriter('Level2CraftDemoOutput.xlsx')
    df_filtered.to_excel(writer,'CalculationSheet')
    writer.save()


    #Sum the cost based on department
    df_series = df_filtered.groupby('Group')['Cost'].sum()

    #convert data Series to dataframe
    df_total = pd.DataFrame({'Group':df_series.index, 'CostperYear':df_series.values})

    # Calculate cost per year
    df_total['CostperYear'] = df_total['CostperYear']*24*365

    #Forecast total cost by each dept for year1,year2,year3 based on hardware growth
    for index,row in df_total.iterrows():
        df_total.loc[index,'Year1'] = df_total.loc[index,'CostperYear']*df_group_parameters.loc[index,'Year1']
        df_total.loc[index,'Year2'] = df_total.loc[index,'CostperYear']*df_group_parameters.loc[index,'Year2']
        df_total.loc[index,'Year3'] = df_total.loc[index,'CostperYear']*df_group_parameters.loc[index,'Year3']

    print(df_total)

    #Export the result to excel
    df_total.to_excel(writer,'HostingCostbyDept')
    writer.save()
    writer.close()

    pushToGitRepo("Level2CraftDemo changes")

def getCostMappingDF():
    df = pd.read_excel('costMapper.xlsx')
    return df

main()