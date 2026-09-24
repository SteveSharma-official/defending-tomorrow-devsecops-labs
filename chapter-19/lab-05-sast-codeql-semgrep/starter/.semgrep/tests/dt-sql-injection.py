import sqlite3

conn = sqlite3.connect(":memory:")


def unsafe(customer, limit):
    # ruleid: dt-python-sql-built-from-string
    conn.execute(f"SELECT * FROM orders WHERE customer = '{customer}' LIMIT {limit}")
    # ruleid: dt-python-sql-built-from-string
    conn.execute("SELECT * FROM orders WHERE customer = '" + customer + "'")
    # ruleid: dt-python-sql-built-from-string
    conn.execute("SELECT * FROM orders WHERE customer = '%s'" % customer)
    # ruleid: dt-python-sql-built-from-string
    conn.execute("SELECT * FROM orders WHERE customer = '{}'".format(customer))


def safe(customer, limit):
    # ok: dt-python-sql-built-from-string
    conn.execute("SELECT * FROM orders WHERE customer = ? LIMIT ?", (customer, limit))


def more_unsafe(customer):
    query = "SELECT * FROM orders WHERE customer = '" + customer + "'"
    # todoruleid: dt-python-sql-built-from-string
    conn.execute(query)
