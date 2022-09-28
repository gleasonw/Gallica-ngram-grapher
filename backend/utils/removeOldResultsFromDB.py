from psqlconn import PSQLconn


def removeOldResultsFromDB():
    print('Removing old results from DB...')
    conn = PSQLconn().getConn()
    cur = conn.cursor()
    cur.execute("""
    DELETE FROM results 
    WHERE created < NOW() - INTERVAL '1 hour'
    AND requestid > 0;
    """)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    removeOldResultsFromDB()
