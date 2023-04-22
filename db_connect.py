import psycopg2

db = psycopg2.connect(host='localhost', dbname='postgres',user='postgres',password='1234',port=5432)

# 1. db를 선택하고 그걸 여기에 연결
# 2. method  >> db schema  id, name, 방문여부(0,1), 그간 대화내역 (system으로 입력한거, 유저로 입력한),일일보고 (dic.toString), 주간보고, 월간보고 , 분기보고
# 2-1. db를 다루는 sql 작성  당장 필요한 sql name으로 일일보고 가져오기 , name으로 방문 여부 체크 (True or False), db에 저장하는거
# 3. (주간보고 트리거) ai한테 일일보고를 하다가 특정갯수이상 (5이상 쌓이면) 사용자한테 "주간보고서를 만들까요?" >> "yes or no"
# (2번째 트리거) 수동모드 ai한테 주간보고를 만들어줘(갯수 x) >> "making report"

class Databases():
    def __init__(self):
        self.db = psycopg2.connect(host='localhost', dbname='postgres',user='postgres',password='1234',port=5432)
        self.cursor = self.db.cursor()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self,query,args={}):
        self.cursor.execute(query,args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()

class CRUD(Databases):
    def insertDB(self, schema, table, columns, data_list):
        columns_str = ", ".join(columns)
        values_str = ", ".join(["%s"] * len(data_list[0]))
        sql = "INSERT INTO {schema}.{table}({columns_str}) VALUES ({values_str})".format(schema=schema, table=table, columns_str=columns_str, values_str=values_str)
        try:
            self.cursor.executemany(sql, data_list)
            self.db.commit()
        except Exception as e:
            print("insert DB err", e)

    def readDB(self, schema, table, columns):
        columns_str = ", ".join(columns)
        sql = " SELECT {columns_str} from {schema}.{table}".format(columns_str=columns_str, schema=schema, table=table)
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)

        return result

    def updateDB(self, schema, table, columns, data_list, condition):
        set_str = ", ".join([f"{col}=%s" for col in columns])
        sql = f"UPDATE {schema}.{table} SET {set_str} WHERE {condition}"
        try:
            self.cursor.executemany(sql, data_list)
            self.db.commit()
        except Exception as e:
            print("update DB err", e)

    def deleteDB(self, schema, table, condition):
        sql = " delete from {schema}.{table} where {condition} ; ".format(schema=schema, table=table,
                                                                          condition=condition)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("delete DB err", e)


if __name__ == "__main__":
    db = CRUD()
    schema = 'public'
    table = 'userstatus'
#     columns = ['id','name','visit_yn']
#     data_list = [
#     ("1", "고명섭", 0),
#     ("2", "곽재혁", 1),
# ]
#     db.insertDB(schema=schema, table=table, columns=columns, data_list=data_list)
#     print(db.readDB(schema=schema, table=table, columns=columns))
    db.updateDB(schema=schema, table=table, columns=['id','visit_yn'], data_list=[('1',1)], condition="name='고명섭'")
    # db.deleteDB(schema=schema, table=table, condition="id != 'd'")