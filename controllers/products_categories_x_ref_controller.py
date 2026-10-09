from flask import request, jsonify

from db import conn, cursor

def create_x_ref():
    form_data = request.form if request.form else request.json

    product_id = form_data.get("product_id")
    category_id = form_data.get("category_id")

    if not product_id:
        return jsonify({"message": "product id field is required"}), 400

    if not category_id:
        return jsonify({"message": "category id field is required"}), 400

    check = cursor.execute("""
        SELECT * FROM ProductsCategoriesXref
        WHERE product_id = %s AND category_id = %s;
    """, (product_id, category_id,))

    check = cursor.fetchone()

    if check:
        return jsonify({"message": "reference already exists"}), 400

    try:
        cursor.execute("""
            INSERT INTO ProductsCategoriesXref (product_id, category_id)
            VALUES (%s, %s);
        """, (product_id, category_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to create reference"}), 400

    conn.commit()

    verify = cursor.execute("""
        SELECT * FROM ProductsCategoriesXref
        WHERE product_id = %s AND category_id = %s;
    """, (product_id, category_id,))

    verify = cursor.fetchone()

    if not verify:
        return jsonify({"message": "unable to create the relationship"}), 400

    return jsonify({"message": "relationship created", "result": verify}), 201
