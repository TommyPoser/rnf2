from django.db import connection


def execute_query(**kwargs):
    with connection.cursor() as cursor:
        cursor.execute(kwargs["query"], kwargs["params"])
        return None


def get_array(**kwargs):
    with connection.cursor() as cursor:
        cursor.execute(kwargs["query"], kwargs["params"])
        return cursor.fetchall()
