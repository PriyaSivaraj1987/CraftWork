import sqlite3
import pandas as pd
import git
from git import Repo

def main():
    filename = "hardware"
    con = sqlite3.connect(filename+".db")
    wb = pd.ExcelFile(filename+'.xlsx')
    for sheet in wb.sheet_names:
        df = pd.read_excel(filename+'.xlsx',sheet_name=sheet)
        df.to_sql(sheet, con, index=False, if_exists="replace")
    con.commit()
    writer = pd.ExcelWriter('Level1CraftDemoOutput.xlsx')
    getDepartmentList(pd,con,writer)
    getApplicationList(pd,con,writer)
    getCPUandMemoryUsageByDept(pd,con,writer)
    getCPUandMemoryUsageByApp(pd,con,writer)
    getCPUandMemoryUsageByDataCenter(pd,con,writer)
    writer.close()
    con.close()
    pushToGitRepo()

def getDepartmentList(pd,con,writer):
    df_listofdep = pd.read_sql_query("SELECT DISTINCT `Group` FROM `Page 1` WHERE `Logical status` = 'Operational'",con)
    print(df_listofdep)
    df_listofdep.to_excel(writer, 'List of Departments')
    writer.save()

def getApplicationList(pd,con,writer):
    print("List of applications for each department")
    df_app_each_dept = pd.read_sql_query( "SELECT DISTINCT `Group`,Application FROM `Page 1` ORDER BY `Group`,Application", con)
    print(df_app_each_dept)
    df_app_each_dept.to_excel(writer, 'List of applications')
    writer.save()

def getCPUandMemoryUsageByDept(pd,con,writer):
    print("Sum CPU and Memory used by each dept")
    df_sum_cpu_memory_dept = pd.read_sql_query( "SELECT `Group`,SUM(`CPU cores`),SUM(`RAM (MB)`) FROM `Page 1` WHERE `Logical status` = 'Operational' GROUP BY `Group`",con)
    print(df_sum_cpu_memory_dept)
    df_sum_cpu_memory_dept.to_excel(writer, 'CPU and Memory Usage by dept')
    writer.save()

def getCPUandMemoryUsageByApp(pd,con,writer):
    print("Sum CPU and Memory used by each application")
    df_sum_cpu_memory_app = pd.read_sql_query("SELECT Application ,SUM(`CPU cores`),SUM(`RAM (MB)`) FROM `Page 1` WHERE `Logical status` = 'Operational' GROUP BY Application",con)
    print(df_sum_cpu_memory_app)
    df_sum_cpu_memory_app.to_excel(writer, 'CPU and Memory Usage by app')
    writer.save()

def getCPUandMemoryUsageByDataCenter(pd,con,writer):
    print("Sum CPU and Memory used by each dataCenter")
    df_sum_cpu_memory_site = pd.read_sql_query("SELECT Site,SUM(`CPU cores`),SUM(`RAM (MB)`) FROM `Page 1` WHERE `Logical status` = 'Operational' GROUP BY Site",con)
    print(df_sum_cpu_memory_site)
    df_sum_cpu_memory_site.to_excel(writer, 'CPU and Memory Usage by DC')
    writer.save()

def pushToGitRepo():
    repo = git.Repo()
    commit_message = 'Push results to Git Repo'
    repo.git.add('--all')
    repo.index.commit(commit_message)
    origin = repo.remote('origin')
    origin.push()

main()