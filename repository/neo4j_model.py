from py2neo import Graph, Node, Relationship, Subgraph
import os
import copy

url = os.environ.get('GRAPHENEDB_URL', 'http://neo4j:1234@localhost:7474/db/data')

#graph = Graph(url + '/db/data/', username=username, password=password)
graph = Graph(url)

#general queries
def reset_graph():
    graph.delete_all()

'''
Return dictionary of every ingredient and the count of recipes that ingredient is in.
Wheres are ingredients that the recipes must require.
'''
def get_all_recipes_require_ingredient_counts(*wheres):
    query = "MATCH "
    for where in wheres:
        query += "(r:Recipe)-[:REQUIRES]->(:Ingredient{{name:'{0}'}}), ".format(where.node['name'])
    query += "(i:Ingredient)<-[:REQUIRES]-(r:Recipe) RETURN i.name AS name, count(r) AS total"
    recordList = graph.cypher.execute(query)
    #dictionary comprehension
    return {record['name']: record['total'] for record in recordList}

#classes for manipulating nodes
class Recipe:

    def __init__(self, id, **kwargs):
        self.node = Node('Recipe', id=id, **kwargs)
        self.node.__primarylabel__ = 'Recipe'
        self.node.__primarykey__ = 'id'

    def get_node(self):
        return self.node

    def find(self):
        recipe = graph.find_one('Recipe', self.node.__primarykey__, self.node[self.node.__primarykey__])
        if recipe:
            self.node = recipe
        return recipe

    def add(self):
        self.node = graph.merge_one(self.node.__primarylabel__, self.node.__primarykey__, self.node[self.node.__primarykey__])
        return self.node

    def merge(self):
        graph.merge(self.node, 'Recipe', self.node[self.node.__primarykey__])

    def require_ingredient(self, ingredient):
        rel = Relationship(self.node, 'REQUIRES', ingredient.node)
        graph.create(rel)

    def require_ingredients(self, ingredients):
        for ingredient in ingredients:
            iNode = ingredient.add()
            rel = Relationship(self.node, 'REQUIRES', iNode)
            graph.create_unique(rel)

    def get_meta_data(self):
        #retrieve metadata from mongo
        pass


class Ingredient:

    def __init__(self, name, **kwargs):
        self.node = Node('Ingredient', name=name, **kwargs)
        self.node.__primarylabel__ = 'Ingredient'
        self.node.__primarykey__ = 'name'

    def __lt__(self, other):
        self_name = self.node[self.node.__primarykey__]
        other_name = other.node[other.node.__primarykey__]
        return self_name < other_name

    def __eq__(self, other):
        self_name = self.node[self.node.__primarykey__]
        other_name = other.node[other.node.__primarykey__]
        return self_name == other_name

    def __hash__(self):
        self_name = self.node[self.node.__primarykey__]
        return hash(self_name)

    def get_node(self):
        return self.node

    def is_remote(self):
        return not self.find()

    def find(self):
        ingredient = graph.find_one('Ingredient', self.node.__primarykey__, self.node[self.node.__primarykey__])
        if ingredient:
            self.node = ingredient
        return ingredient

    def add(self):
        self.node = graph.merge_one(self.node.__primarylabel__, self.node.__primarykey__, self.node[self.node.__primarykey__])
        return self.node

    def merge(self):
        graph.merge(self.node, 'Ingredient', self.node[self.node.__primarykey__])
