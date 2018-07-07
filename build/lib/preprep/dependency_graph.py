

class Node():
    def __init__(self,value,edges):
        self.value = value
        self.edges = edges

    def add(self,node):
        self.edges.append(node)


def resolve_dependency(node,resolved,seen):
    for edge in node.edges:
        if edge not in resolved:
            resolve_dependency(edge,resolved)
    resolved.append(node)
    return resolved

if __name__ == "__main__":
    a = Node("a", edges = [])
    b = Node("b", edges = [])
    c = Node("c", edges = [])
    d = Node("d", edges = [])
    e = Node("e", edges = [])

    a.add(b)
    a.add(d)
    b.add(c)
    b.add(e)
    c.add(d)
    c.add(e)
    resolve_dependency(a,[])
