conn = new Mongo()
db = conn.getDB("yummly")

cursor = db.combinations50k.aggregate(
	[
        {
		$match: {
             r: 2,
             ingredients: { 
                $all: ['avocado']
            }
        }
        },
        {
        $project: {
            score: {
                $divide: ["$and_count", "$or_count"]
            },
            pairing: {
                $arrayElemAt: [
                    { $setDifference: ["$ingredients", ['avocado']] } ,
                    0
                ]
            }
        }
        },
        {
        $sort: {
            score: 1
        }
        }   
    ]
)

while ( cursor.hasNext() ) {
    printjson( cursor.next() );
}
