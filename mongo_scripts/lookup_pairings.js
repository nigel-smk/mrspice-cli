conn = new Mongo()
db = conn.getDB("yummly")

_id = 'butter::pepper::salt'

cursor = db.combinations1k.aggregate([
    {
        $match: {
            _id: _id
        }
    },
    {
        $project: {
            _id: 0,
            pairings: '$links'
        }
    }
//    {
//        $unwind: '$links'
//    },
//    {
//        $lookup: {
//            from: 'combinations1k',
//            localField: 'links.ref_id',
//            foreignField: '_id',
//            as: 'pairings'
//        }
//    }
//    {
//        $unwind: '$pairings'
//    },
//    {
//        $project: {
//            _id: 0,
//            pairings: {
//                ref_id: '$links.ref_id',
//                name: '$links.candidate',
//                score: {
//                    $divide: ['$pairings.and_count', '$pairings.or_count']
//                }
//            }
//        }
//    },
//    {
//        $sort: {
//            'pairings.score': -1
//        }
//    },
//    {
//        $group: {
//            _id: null,
//            pairings: {
//                $push: '$pairings'
//            }
//        }
//    },
//    {
//        $project: {
//            _id: 0,
//            pairings: 1
//        }
//    }
]);

printjson( cursor.next() );
