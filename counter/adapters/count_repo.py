from typing import List

from pymongo import MongoClient
import psycopg2

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)

class CountPostgresRepo(ObjectCountRepo):

    def __init__(self, host, port, database, username, password):
        self.__host = host
        self.__port = port
        self.__database = database
        self.__username = username
        self.__password = password

    def __get_counter_client(self):
        client = psycopg2.connect(host=self.__host,
                                port=self.__port,
                                user=self.__username,
                                password=self.__password,
                                dbname=self.__database)
        return client

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_client = self.__get_counter_client()
        counter_curr = counter_client.cursor()
        object_counts = []
        if object_classes:
            placeholders = ', '.join(['%s'] * len(object_classes))
            sql_query = f"SELECT object_class, count FROM object_counter WHERE object_class IN ({placeholders});"
            counter_curr.execute(sql_query, tuple(object_classes))
            counters = counter_curr.fetchall()
            for counter in counters:
                object_counts.append(ObjectCount(counter[0], counter[1]))
        counter_client.commit()
        counter_client.close()
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_client = self.__get_counter_client()
        counter_curr = counter_client.cursor()
        upsert_query = """
            INSERT INTO object_counter (object_class, count)
            VALUES (%s, %s)
            ON CONFLICT (object_class)
            DO UPDATE SET count = object_counter.count + EXCLUDED.count;
            """
        for value in new_values:
            counter_curr.execute(upsert_query,(value.object_class, value.count))
        counter_client.commit()
        counter_client.close()