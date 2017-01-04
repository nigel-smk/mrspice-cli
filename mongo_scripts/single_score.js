conn = new Mongo()
db = conn.getDB("yummly")

ingredients = ['avocado', 'lime', 'cilantro', 'cooked quinoa']

and_count = db.recipes.find({
    ingredients: {$all: ingredients}
}).count()

or_count = db.recipes.find({
    ingredients: {$in: ingredients}
}).count()

print(and_count / or_count)
