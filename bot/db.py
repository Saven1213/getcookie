import sqlite3
from cgitb import reset
from os.path import curdir
import uuid
import logging
from venv import logger


def get_item(item_id):
    """
    :param item_id: ID товара
    :return: все данные о товаре
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE id = ?', (item_id,))
    results = cursor.fetchone()
    conn.close()

    return results


def get_name(item_id):
    """
    :param item_id: ID товара
    :return: название товара
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM item WHERE id = ?', (item_id,))
    results = cursor.fetchone()
    conn.close()

    return results[0]

def get_id(user_id):
    """

    :param user_id: id
    :return: ID user
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT tg_id FROM users WHERE tg_id = ?', (user_id,))
    results = cursor.fetchone()
    conn.close()

    return results

def insert_data(tg_id, name, number, location):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (tg_id, name, number, location) VALUES (?,?,?, ?)', (tg_id, name, number, location))
    conn.commit()
    conn.close()



def add_req(tg_id, count, item_name, description, amount, bool_info):
    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    basket_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO basket (id, count, item_name, description, amount, tg_id, bool) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (basket_id, count, item_name, description, amount, tg_id, bool_info))
    conn.commit()
    conn.close()

def get_basket_info():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM basket")
    all_reqs = cursor.fetchall()
    conn.close()

    if not all_reqs:
        return None
    else:
        return all_reqs

def get_basket_card(init_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM basket WHERE id = ? 
    """, (init_id,))
    info = cursor.fetchall()
    conn.close()
    return info

def get_user_info(tg_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM users WHERE tg_id = ?
    """, (tg_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_category_list():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM categories
    """)
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_item(name, description, price, category_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO item (name, description, price, category) VALUES (?, ?, ?, ?)
        """, (name, description, price, category_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка базы данных (add_item): {e}")
    finally:
        conn.close()

def get_category_with_name(category_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = cursor.fetchone()
        return result[0] if result else None #Возвращаем id если он есть, иначе None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных (get_category_with_name): {e}")
        return None
    finally:
        conn.close()

def add_new_category(new_id, name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO categories (id, name) VALUES (?,?)
    """, (new_id, name))
    conn.commit()
    conn.close()

def delete_item_bd(id_):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:

        cursor.execute("DELETE FROM item WHERE id = ?", (id_,))
        conn.commit()
        rows_affected = cursor.rowcount # количество затронутых строк
        return rows_affected > 0 # True, если что-то удалено, иначе False
    except sqlite3.Error as e:
        print(f"Ошибка базы данных (delete_item_bd): {e}")
        return False
    finally:
        conn.close()

def get_items():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, name FROM item
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def get_itemsos():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM item
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def add_basket_bool(id_):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    bool_value = 'False'
    try:

        cursor.execute("""
                    UPDATE basket SET "bool" = ? WHERE id = ?
                """, (bool_value, id_))
        conn.commit()
        conn.close()
        return True
    except:
        return False
