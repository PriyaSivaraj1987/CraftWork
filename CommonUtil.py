import pandas as pd
import sqlite3
import git
from git import Repo

def getSQliteConnection(filename):
    con = sqlite3.connect(filename + ".db")
    try:
        wb = pd.ExcelFile(filename + '.xlsx')
        for sheet in wb.sheet_names:
            df = pd.read_excel(filename + '.xlsx', sheet_name=sheet)
            df.to_sql(sheet, con, index=False, if_exists="replace")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)
    con.commit()
    return con

def pushToGitRepo(commitMessage):
    repo = git.Repo()
    repo.git.add('--all')
    repo.index.commit(commitMessage)
    origin = repo.remote('origin')
    origin.push()
