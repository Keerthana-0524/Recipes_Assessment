
from flask import Flask, jsonify,render_template,request
from flask_mysqldb import MySQL
import json

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'recipe_db'

mysql = MySQL(app)

@app.route('/')
def index():
    return 'US Recipes'

@app.route('/show-json', methods=['GET'])
def import_json():
    try:
        with open('US_recipes_null.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        cur = mysql.connection.cursor()

        inserted = 0
        skipped = 0

        for key, recipe in raw_data.items():
            title = recipe.get('title')
            if not title:
                skipped += 1
                continue 

            cur.execute("""
                INSERT INTO recipe (
                    title, continent, country_state, cuisine, url, rating,
                    total_time, prep_time, cook_time, description,
                    ingredients, instructions, nutrients, serves
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                title,
                recipe.get('Contient'),
                recipe.get('Country_State'),
                recipe.get('cuisine'),
                recipe.get('URL'),
                recipe.get('rating'),
                str(recipe.get('total_time')),
                str(recipe.get('prep_time')),
                str(recipe.get('cook_time')),
                recipe.get('description'),
                json.dumps(recipe.get('ingredients')) if recipe.get('ingredients') else None,
                json.dumps(recipe.get('instructions')) if recipe.get('instructions') else None,
                json.dumps(recipe.get('nutrients')) if recipe.get('nutrients') else None,
                recipe.get('serves')
            ))
            inserted += 1

        mysql.connection.commit()
        cur.close()

        return jsonify({
            'message': f'{inserted} recipes inserted successfully',
            'skipped': skipped
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recipe/all', methods=['GET'])
def show_recipes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM recipe")
    rows = cur.fetchall()
    cur.close()

    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'title': row[1],
            'continent': row[2],
            'country_state': row[3],
            'cuisine': row[4],
            'url': row[5],
            'rating': row[6],
            'total_time': row[7],
            'prep_time': row[8],
            'cook_time': row[9],
            'description': row[10],
            'ingredients': json.loads(row[11]) if row[11] else [],
            'instructions': json.loads(row[12]) if row[12] else [],
            'nutrients': json.loads(row[13]) if row[13] else {},
            'serves': row[14]
        })
    return jsonify(result)

@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    cur = mysql.connection.cursor()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = request.args.get('sort_by', 'title')
    order = request.args.get('order', 'asc')

    offset = (page - 1) * per_page
    allowed_sort_fields = ['title', 'rating', 'total_time', 'prep_time', 'cook_time']
    if sort_by not in allowed_sort_fields:
        sort_by = 'rating'

    query = f"SELECT * FROM recipe ORDER BY {sort_by} {order.upper()} LIMIT %s OFFSET %s"
    cur.execute(query, (per_page, offset))
    rows = cur.fetchall()

    cur.close()

    recipes = []
    for row in rows:
        recipes.append({
            "id": row[0],
            "title": row[1],
            "continent": row[2],
            "country_state": row[3],
            "cuisine": row[4],
            "url": row[5],
            "rating": row[6],
            "total_time": row[7],
            "prep_time": row[8],
            "cook_time": row[9],
            "description": row[10],
            "ingredients": row[11],
            "instructions": row[12],
            "nutrients": row[13],
            "serves": row[14]
        })

    return jsonify(recipes)


@app.route('/search', methods=['GET'])
def search_recipes():
    cur = mysql.connection.cursor()

    
    title = request.args.get('title')
    cuisine = request.args.get('cuisine')
    continent = request.args.get('continent')
    country = request.args.get('country_state')

    
    base_query = "SELECT * FROM recipe WHERE 1=1"
    params = []

    if title:
        base_query += " AND title LIKE %s"
        params.append(f"%{title}%")
    if cuisine:
        base_query += " AND cuisine LIKE %s"
        params.append(f"%{cuisine}%")
    if continent:
        base_query += " AND continent LIKE %s"
        params.append(f"%{continent}%")
    if country:
        base_query += " AND country_state LIKE %s"
        params.append(f"%{country}%")

    cur.execute(base_query, tuple(params))
    rows = cur.fetchall()
    cur.close()

    recipes = []
    for row in rows:
        recipes.append({
            "id": row[0],
            "title": row[1],
            "continent": row[2],
            "country_state": row[3],
            "cuisine": row[4],
            "url": row[5],
            "rating": row[6],
            "total_time": row[7],
            "prep_time": row[8],
            "cook_time": row[9],
            "description": row[10],
            "ingredients": row[11],
            "instructions": row[12],
            "nutrients": row[13],
            "serves": row[14]
        })

    return jsonify(recipes)

if __name__ == '__main__':
    app.run(debug=True)
