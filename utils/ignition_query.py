
import psycopg2
import datetime

connection = psycopg2.connect(user="dcs_reader",
                                  password="qcd56RUc",
                                  host="ifdb09",
                                  port="5456",
                                  database="sbnd_online_prd")

query = """SELECT d.tagid, COALESCE((d.intvalue::numeric)::text, (trunc(d.floatvalue::numeric,3))::text), d.t_stamp
FROM cryo_prd.sqlt_data_1_2024_{} d, cryo_prd.sqlth_te s
WHERE d.tagid=s.id
AND s.tagpath LIKE '%sbnd%'
AND s.tagpath LIKE '%{}%'
AND s.tagpath LIKE '%{}%'
ORDER BY d.t_stamp DESC 
LIMIT 10""".format('02', '', 'te-8101a')

print('query:', query)

cursor = connection.cursor()

cursor.execute(query)

dbrows = cursor.fetchall()

cursor.close()

formatted = []
for row in dbrows:
    # try:
    time = datetime.datetime.fromtimestamp(row[2]/1000) # ms since epoch
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    print('->', time)
    # except:
    #     time = row[2]
    #     print(time)
    formatted.append((row[0], row[1], row[2]))

print('len:', len(formatted))
print(formatted)