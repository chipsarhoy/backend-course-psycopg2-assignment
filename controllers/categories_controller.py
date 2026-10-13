from flask import jsonify, request

from db import cursor, conn

def create_category():
    post_data = request.form if request.form else request.json

    category_name = post_data.get("category_name")

    if not category_name:
        return jsonify({"message": "category name is a required field"}), 400

    result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_name = %s;
        """, (category_name,))

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "category already exists"}), 409

    cursor.execute("""
        INSERT INTO Categories (category_name)
        VALUES (%s);
    """, (category_name,))

    conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_name = %s;
    """, (category_name,))

    final_result = cursor.fetchone()

    result_dict = {
        'category_id': final_result[0],
        'category_name': final_result[1]
    }

    return jsonify({"message": "category created", "result": result_dict}), 201

def get_all_categories():
    result = cursor.execute("""
        SELECT * FROM Categories;
    """)

    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'category_id': record[0],
            'category_name': record[1]
        }

        record_list.append(record)

    return jsonify({"message": "categories found", "results": record_list}), 200

def get_category_by_id(category_id):
    result = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_id = %s;
    """, (category_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "category does not exist"}), 404
  
    record = {
        'category_id': result[0],
        'category_name': result[1]
    }

    return jsonify({"message": "category found", "result": record}), 200

def update_category_by_id(category_id):
    update_data = request.form if request.form else request.json

    category_name = update_data.get("category_name")

    record_check = cursor.execute("""
        SELECT * FROM Categories
        WHERE category_id = %s;
    """, (category_id,))  

    record_check = cursor.fetchone()

    if not record_check:
        return jsonify({"message": "category does not exist"}), 404

    duplication_check = cursor.execute("""
        SELECT * FROM Categories WHERE category_name = %s;
    """, (category_name,))

    duplication_check = cursor.fetchone()

    if duplication_check:
        return jsonify({"message": "category already exists"}), 409

    try:
        cursor.execute("""
            UPDATE Categories SET category_name = %s WHERE category_id = %s;
        """, (category_name, category_id,))
    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to update category"}), 400

    finally:
        conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Categories WHERE category_id = %s;
    """, (category_id,))

    final_result = cursor.fetchone()

    record = {
        'category_id': final_result[0],
        'category_name': final_result[1]
    }

    return jsonify({"message": "category updated", "result": record}), 200

def delete_category_by_id(category_id):
    result = cursor.execute("""
        SELECT * FROM Categories WHERE category_id = %s;
    """, (category_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "category does not exist"}), 404

    x_ref_check = cursor.execute("""
    SELECT * FROM ProductsCategoriesXref
    WHERE category_id = %s;
    """, (category_id,))

    x_ref_check = cursor.fetchall()

    if x_ref_check:
        try:
            for ref in x_ref_check:
                cursor.execute("""
                    DELETE FROM ProductsCategoriesXref
                    WHERE product_id = %s;
                """, (ref[0],))
        except Exception as e:
            cursor.execute("ROLLBACK;")
            return jsonify({"message": f"{e}: unable to delete reference"}), 400

        finally:
            conn.commit()

    try:
        cursor.execute("""
            DELETE FROM Categories
            WHERE category_id = %s;
        """, (category_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}:unable to delete category"}), 400

    finally:
        conn.commit()

    return jsonify({"message": "category deleted"}), 200