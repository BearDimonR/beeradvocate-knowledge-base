from py2neo import Graph, Node, Relationship


class Neo4jDataManager:
    def __init__(self, uri, username, password):
        self.graph = Graph(uri, auth=(username, password))

    def clear_database(self):
        self.graph.delete_all()

    def create_node(self, label, **properties):
        node = Node(label, **properties)
        self.graph.create(node)
        return node

    def create_relationship(self, start_node, rel_type, end_node):
        relationship = Relationship(start_node, rel_type, end_node)
        self.graph.create(relationship)

    def find_node_by_id(self, label, _id):
        return self.graph.nodes.match(label, ID=_id).first()

    def create_nodes(self, label, entities):
        nodes = []
        for entity in entities:
            node = Node(label, **entity)
            self.graph.create(node)
            nodes.append(node)
        return nodes

    def create_relationships(self, start_nodes, rel_type, end_nodes):
        relationships = []
        for start_node, end_node in zip(start_nodes, end_nodes):
            relationship = Relationship(start_node, rel_type, end_node)
            self.graph.create(relationship)
            relationships.append(relationship)
        return relationships
