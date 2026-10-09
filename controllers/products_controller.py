from flask import jsonify, request

from db import cursor, conn

def create_product():
    post_data = request.form if request.form else request.json

    company_id = int(post_data.get("company_id"))
    product_name = post_data.get("product_name")
    description = post_data.get("description")
    price = float(post_data.get("price"))

    if not product_name:
        return jsonify({"message": "product name is a required field"}), 400

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_name = %s;
        """, (product_name,)
    )

    result = cursor.fetchone()

    if result:
        return jsonify({"message": "product already exists"}), 400
    
    cursor.execute("""
        INSERT INTO Products (company_id, product_name, description, price)
        VALUES (%s, %s, %s, %s);        
    """, (company_id, product_name, description, price))
    
    conn.commit()

    final_result = cursor.execute("""
            SELECT * FROM Products
            WHERE product_name = %s;
            """, (product_name,)
        )

    final_result = cursor.fetchone()
    
    return jsonify({"message": "product created", "result": final_result}), 201


def get_all_products():
    result = cursor.execute("""
        SELECT p.product_id, p.product_name, c.category_name, p.price, p.description, w.warranty_months, p.active
        FROM Products p
        LEFT JOIN ProductsCategoriesXref pc ON p.product_id = pc.product_id
        LEFT JOIN Categories c ON pc.category_id = c.category_id
        LEFT JOIN Warranties w ON w.product_id = p.product_id;
    """)

    result = cursor.fetchall()

    record_list = []

    for record in result:
        record = {
            'product_id': record[0],
            'product_name': record[1],
            'category_name': record[2],
            'price': record[3],
            'description': record[4],
            'warranty_months': record[5],
            'active': record[6]
        }

        record_list.append(record)
        
    return jsonify({"message": "products found", "results": record_list}), 200

def get_active_products():
    results = cursor.execute("""
        SELECT * FROM Products
        WHERE active = true;
    """)

    results = cursor.fetchall()

    if not results:
        return jsonify({"message": "no active products"}), 404

    return jsonify({"message": "found active products", "results": results}), 200


def get_product_by_id(product_id):
    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s;
    """, (product_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "product does not exist"}), 404

    return jsonify({"message": "product found", "result": result}), 200

def get_products_by_company(company_id):
    products_from_company = cursor.execute("""
        SELECT * FROM Products 
        WHERE company_id = %s;
    """, (company_id,))

    products_from_company = cursor.fetchall()

    record_list = []

    for record in products_from_company:
        record = {
            "product_id": record[0],
            "company_id": record[1],
            "product_name": record[2],
            "description": record[3],
            "price": record[4],
            "active": record[5]
        }

        record_list.append(record)

    return jsonify({"message": "products from company found", "results": record_list}), 200

def update_product_by_id(product_id):
    update_data = request.form if request.form else request.json

    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s;
    """, (product_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "product does not exist"}), 404

    if update_data.get("product_name"):
        product_name = update_data.get("product_name")
    else:
        product_name = result[2]

    if update_data.get("description"):
        description = update_data.get("description")
    else:
        description = result[3]

    if update_data.get("price"):
        price = update_data.get("price")
    else:
        price = result[4]

    if update_data.get("active") != result[5]:
        active = update_data.get("active")
    else:
        active = result[5]
    
    try:
        cursor.execute("""
            UPDATE Products 
            SET product_name = %s,
                description = %s,
                price = %s,
                active = %s
            WHERE product_id = %s;
        """, (product_name, description, price, active, product_id,))

    except Exception as e:
        cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}: unable to update product"}), 400

    finally:
        conn.commit()

    final_result = cursor.execute("""
        SELECT * FROM Products WHERE product_id = %s;
    """, (product_id,))

    final_result = cursor.fetchone()

    return jsonify({"message": "product updated", "result": final_result}), 200


def delete_product_by_id(product_id):
    result = cursor.execute("""
        SELECT * FROM Products
        WHERE product_id = %s;
    """, (product_id,))

    result = cursor.fetchone()

    if not result:
        return jsonify({"message": "product does not exist"}), 404

    x_ref_check = cursor.execute("""
        SELECT * FROM ProductsCategoriesXref
        WHERE product_id = %s;
    """, (product_id,))

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
            DELETE FROM Products
            WHERE product_id = %s;
        """, (product_id,))
            
    except Exception as e:
        result = cursor.execute("ROLLBACK;")
        return jsonify({"message": f"{e}:unable to delete product"}), 400
    
    finally:
        conn.commit()

    return jsonify({"message": "product deleted"}), 200