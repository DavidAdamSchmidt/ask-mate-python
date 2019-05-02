import connection
from datetime import datetime

BASIC_TAGS = ['Python', 'CSS', 'HTML', 'JavaScript', 'Java', 'C#', 'C++', 'C']


@connection.connection_handler
def get_max_id(cursor, table):
    cursor.execute(
        f"""SELECT MAX(id) FROM {table};""")
    id = cursor.fetchone()
    return id


@connection.connection_handler
def update_vote_number(cursor, table, op_change, id_):
    cursor.execute(
        f"""UPDATE {table} SET vote_number = vote_number {op_change}
        WHERE id={id_};""")


@connection.connection_handler
def insert_new_record(cursor, table, record):
    record['submission_time'] = str(datetime.now())
    command = f"""INSERT INTO {table} {str(tuple(record.keys())).replace("'","")} VALUES("""
    for data in record.values():
        if type(data) is str:
            data = data.replace("'", "''")
        command += (f"'{data}'" if type(data) is str else f"{data}") + ', '
    command = command[:-2] + ')'
    cursor.execute(command)


@connection.connection_handler
def get_record_by_id(cursor, record_id, table):
    cursor.execute(f"SELECT * FROM {table} WHERE id={record_id}")
    record = cursor.fetchone()
    return record


@connection.connection_handler
def get_records_by_parent_id(cursor, id, table, parent_type):
    cursor.execute(f"SELECT * FROM {table} WHERE {parent_type}_id={id}")
    records = cursor.fetchall()
    return records


@connection.connection_handler
def get_parent_id_by_comment_id(cursor, comment_id):
    cursor.execute(f'''SELECT * FROM comment WHERE id={comment_id}''')
    comment = cursor.fetchall()
    return comment


@connection.connection_handler
def get_answer_by_id(cursor, id):
    cursor.execute(f"SELECT message, image, question_id FROM answer WHERE id={id}")
    answer = cursor.fetchone()
    return answer


@connection.connection_handler
def update_record_by_primary_id(cursor, table, data, id):
    command = f"UPDATE {table} SET "
    for key, value in data.items():
        command += f"{key}="
        command += (f"'{value}'" if type(value) is str else f"{value}") + ", "
    cursor.execute(command[:-2] + f" WHERE id={id}")


@connection.connection_handler
def update_answer(cursor, message, image_url, id):
    cursor.execute(
        f"""UPDATE answer SET message='{message}', image='{image_url}'
            WHERE id={id}""")


@connection.connection_handler
def update_question(cursor, title, message, image, id_):
    cursor.execute(
        f""" UPDATE question SET title='{title}', message='{message}', image='{image}'
            WHERE id={id_};""")


@connection.connection_handler
def add_comment(cursor, message, edited_count, id, parent_type):
    cursor.execute(
        f"""INSERT INTO comment
            (message, edited_count, submission_time, {parent_type + '_id'})
            VALUES
            ('{message}', {edited_count}, '{datetime.now()}', {id})""")


@connection.connection_handler
def sort_by_any(cursor, table, column, order, limit=None):
    order = 'ASC' if order is True else 'DESC'
    if limit is None:
        cursor.execute(
            f"""SELECT * FROM {table} ORDER BY {column} {order}""")
    else:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row_num = cursor.fetchone()['count']
        if row_num < limit:
            limit = row_num
        cursor.execute(
            f"""SELECT * FROM {table} ORDER BY {column} {order}
                OFFSET {row_num - limit} FETCH FIRST {limit} ROWS ONLY;""")
    ordered_table = cursor.fetchall()
    return ordered_table


@connection.connection_handler
def get_data_from_database(cursor, search_phrase):
    cursor.execute('''
                   SELECT DISTINCT ON (title) title, question.message FROM question, answer
                   WHERE title LIKE %(search_phrase)s OR question.message LIKE %(search_phrase)s
                   OR answer.message LIKE %(search_phrase)s AND question.id=question_id;
                   ''',
                   {'search_phrase': search_phrase})
    results = cursor.fetchall()
    return results


@connection.connection_handler
def delete_by_id(cursor, table, id_):
    cursor.execute(
        f"""DELETE FROM {table} WHERE id={id_};""")


@connection.connection_handler
def insert_new_tag(cursor, new_tag):
    cursor.execute(
        f""" INSERT INTO tag (name) 
        VALUES ('{new_tag['name']}')""")
    new_tag_id = get_max_id('tag')
    cursor.execute(
        f""" INSERT INTO question_tag (question_id, tag_id) 
        VALUES ('{new_tag['question_id']}', '{new_tag_id['max']}')""")


@connection.connection_handler
def delete_tags(cursor, question_id, tag):
    tag = None
    cursor.execute(f"DELETE FROM question_tag WHERE question_id={question_id};")


@connection.connection_handler
def update_tag(cursor, tag):
    cursor.execute(
                   f""" UPDATE tag SET name='{tag['name']}'
        WHERE id={tag['tag_id']};""")