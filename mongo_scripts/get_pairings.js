conn = new Mongo()
db = conn.getDB("yummly")

ingredients = ['avocado', 'lime', 'cilantro', 'cooked quinoa', 'garbanzo beans']

cursor = db.recipes.aggregate([
    {
        $match: {
            ingredients: {
                $all: ingredients
            }
        }
    },
    {
        $project: {
            ingredients: {
                $setDifference: ['$ingredients', ingredients]
            }
         }
    },
    {
        $unwind: '$ingredients'
    },
    {
        $group: {
            _id: null,
            pairings: {
                $addToSet: '$ingredients'
            }
        }
    },
    {
        $project: {
            _id: 0,
            pairings: 1
        }
    }
]);

printjson( cursor.next() );
