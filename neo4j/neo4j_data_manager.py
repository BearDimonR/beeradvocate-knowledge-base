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

    def create_relationships(
        self,
        start_nodes,
        start_property_name,
        end_nodes,
        end_property_name,
        rel_type,
    ):
        for start_node in start_nodes:
            related_nodes = [
                end_node
                for end_node in end_nodes
                if end_node[end_property_name]
                == start_node[start_property_name]
            ]

            for node2 in related_nodes:
                self.create_relationship(start_node, rel_type, node2)
