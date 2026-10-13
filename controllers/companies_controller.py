from flask import request, jsonify

from db import cursor, conn

def create_company():
    post_data = request.form if request.form else request.json

    company_name = post_data.get("company_name")

    if not company_name:
        return jsonify({"message": "company name is a required field"}), 400

    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_name = %s;
    """, (company_name,))

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "company already exists"}), 409

    cursor.execute("""
        INSERT INTO Companies(company_name)
        VALUES (%s);
    """, (company_name,))

    conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_name = %s;
    """, (company_name,))

    final_result = cursor.fetchone()

    record = {
        "company_id": final_result[0],
        "company_name": final_result[1],
    }

    return jsonify({"message": "company created", "result": record}), 201

def get_all_companies():
    results = cursor.execute("""
        SELECT * FROM Companies;
    """)

    results = cursor.fetchall()

    record_list = []

    for record in results:
        record = {
            "company_id": record[0],
            "company_name": record[1],
        }
        record_list.append(record)

    return jsonify({"message": "companies found", "results": record_list}), 200

def get_company_by_id(company_id):
    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
    """, (company_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "company does not exist"}), 404

    record = {
        "company_id": result[0],
        "company_name": result[1],
    }

    return jsonify({"message": "company found", "result": record}), 200

def update_company_by_id(company_id):
    update_data = request.form if request.form else request.json

    company_name = update_data.get("company_name")

    record_check = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
    """, (company_id,))

    record_check = cursor.fetchone()

    if not record_check:
        return jsonify({"message": "company does not exist"}), 404

    duplication_check = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_name = %s;
    """, (company_name,))

    duplication_check = cursor.fetchone()

    if duplication_check:
        return jsonify({"message": "company already exists"}), 409

    try:
        cursor.execute("""
            UPDATE Companies SET company_name = %s
            WHERE company_id = %s;
        """, (company_name, company_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to update company"}), 400

    finally:
        conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
    """, (company_id,))

    final_result = cursor.fetchone()

    record = {
        "company_id": final_result[0],
        "company_name": final_result[1],
    }

    return jsonify({"message": "company updated", "result": record}), 200

def delete_company_by_id(company_id):
    result = cursor.execute("""
        SELECT * FROM Companies
        WHERE company_id = %s;
    """, (company_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "company does not exist"}), 404

    try:
        final_result = cursor.execute("""
            DELETE FROM Companies WHERE company_id = %s;
        """, (company_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to delete company"}), 400

    finally:
        conn.commit()

    return jsonify({"message": "company deleted"}), 200