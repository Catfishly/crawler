# -*- coding: utf-8 -*-

from db.mysql.connection import get_cursor


_cursor = get_cursor()


def find_one(sql, fields):
    """
    SELECT FUNCTION
    return fetchall()[0]
    """

    def result():
        _cursor.execute(sql, fields)
        return _cursor.fetchall()[0]

    return result()


def find(sql, fields):
    """
    SELECT FUNCTION
    return fetchall()
    """

    def result():
        _cursor.execute(sql, fields)
        return _cursor.fetchall()

    return result()


def save(sql, fields):
    """
    INSERT FUNCTION 
    """

    def insert():
        _cursor.execute(sql, fields)

    insert()