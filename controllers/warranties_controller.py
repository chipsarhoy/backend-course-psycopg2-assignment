from flask import request, jsonify

from db import conn, cursor

def create_warranty():
    form_data = request.form if request.form else request.json

    product_id = form_data.get("product_id")
    warranty_months = form_data.get("warranty_months")

    if not product_id:
        return jsonify({"message": "product id is a required field"}), 400

    if not warranty_months:
        return jsonify({"message": "warranty months is a required field"}), 400


    cursor.execute("""
        INSERT INTO Warranties (product_id, warranty_months)
        VALUES (%s, %s);
    """, (product_id, warranty_months,))

    conn.commit()

    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = (SELECT MAX(warranty_id) FROM Warranties);
    """)

    result = cursor.fetchone()

    return jsonify({"message": "warranty created", "result": result}), 201

def get_warranty_by_id(warranty_id):
    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
    """, (warranty_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "warranty does not exist"}), 404

    return jsonify({"message": "warranty found", "result": result}), 200

def update_warranty_by_id(warranty_id):
    update_data = request.form if request.form else request.json

    result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
    """, (warranty_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "warranty does not exist"}), 404

    product_id = update_data.get("product_id")
    warranty_months = update_data.get("warranty_months")

    if not product_id:
        product_id = result[1]

    if not warranty_months:
        warranty_months = result[2]

    try:
        cursor.execute("""
            UPDATE Warranties 
            SET product_id = %s, 
                warranty_months = %s
            WHERE warranty_id = %s;
        """, (product_id, warranty_months, warranty_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to update warranty"}), 400

    finally:
        conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
    """, (warranty_id,))

    final_result = cursor.fetchone()

    return jsonify({"message": "warranty updated", "result": final_result}), 200

def delete_warranty_by_id(warranty_id):
    check = cursor.execute("""
        SELECT * FROM Warranties
        WHERE warranty_id = %s;
    """, (warranty_id,))

    check = cursor.fetchone()

    if not check:
        return jsonify({"message": "warranty does not exist"}), 404

    try:
        cursor.execute("""
            DELETE FROM Warranties
            WHERE warranty_id = %s;
        """, (warranty_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to delete warranty"}), 400

    finally:
        conn.commit()

    return jsonify({"message": "warranty deleted"}), 200