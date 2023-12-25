import sys
from heapq import heapify, heappop, heappush
import copy
import random

class Graph:
    """ Directed multigraph with weights """
    def __init__(self, weighted = False, graph = None, json = None):
        # json comes first (create graph from json)
        if json:
            self.graph  = {}
            json_graph = json['graph']
            for key in json_graph:
                self.graph[key] = Vertex(0, json=json_graph[key])
            self.weighted = json['weighted']
        else:
            self.graph = graph if graph != None else {}
            self.weighted = weighted
    
    def __iter__(self):
        return iter(self.graph.values())

    def to_json(self):
        obj = {'weighted': self.weighted, 'graph': {}}
        for key in self.graph:
            obj['graph'][key] = self.graph[key].to_json()
        return obj

    def add_vertex(self, v, v_data = None):
        if v in self.graph:
            pass
        
        if v_data == None:
            v_data = dict()

        new_ver = Vertex(v, v_data)
        self.graph[v] = new_ver

        return new_ver

    def get_vertex(self, v, create_if_not_exists = False):
        if v in self.graph:
            return self.graph[v]
        
        if create_if_not_exists:
            return self.add_vertex(v)

        return None

    def get_vertexies(self, predicate):
        return filter(lambda v: predicate(self.graph[v]), self.graph)

    def add_edge(self, v_frm, v_to, weight = 0, e_data = {}, is_unique=False):
        if v_frm not in self.graph:
            self.add_vertex(v_frm)
        if v_to not in self.graph:
            self.add_vertex(v_to)

        if is_unique:
            # Pass if edge exists
            exist_edges = self.graph[v_frm].get_edges(v_to)
            if exist_edges:
                for edge in exist_edges:
                    if edge['weight'] == weight and edge['e_data'] == e_data:
                        return
                        
        self.graph[v_frm].add_neighbor(v_to, weight, e_data)

    def find_shortest_path(self, source, target):
        target_v = self.get_vertex(target)
        path = [{'v': target_v, 'e': None}]

        if target == source:
            return path

        source_v = self.get_vertex(source)

        if source_v.dropout or target_v.dropout:
            return []

        if self.weighted:
            self.__dijkstra(source_v, target_v)
        else:
            self.__bfs_shortest_path(source_v, target_v)
        
        prev = {'v': target_v.v_data['prev'], 'e': target_v.v_data['e_data']}

        while prev['v'] is not None:
            path.insert(0, prev)
            prev = {'v': prev['v'].v_data['prev'], 'e': prev['v'].v_data['e_data']}

        # Clean
        for v in iter(self.graph.values()):
            v.v_data.pop('prev', None)
            v.v_data.pop('e_data', None)
            v.v_data.pop('color', None)
            v.v_data.pop('d', None)
            v.v_data.pop('visited', None)        

        return path

    def copy(self):
        graph_copy = copy.deepcopy(self.graph)
        return Graph(self.weighted, graph_copy)

    """ option: 
                0 - display all
                1 - display only vertiex
                2 - display only connections (edges)"""
    def display(self, option = 0):
        if option == 1:
            self.__display_vertexies()
            return
        if option == 2:
            self.__display_connections()
            return
        
        self.__display_vertexies()
        print
        self.__display_connections()

    def __dijkstra(self, source, target):
        for v in iter(self.graph.values()):
            v.v_data['d'] = sys.maxsize
            v.v_data['e_data'] = None
            v.v_data['visited'] = False
            v.v_data['prev'] = None

        source.v_data['d'] = 0

        unvisited = [(v.v_data['d'], v) for v in iter(self.graph.values()) if not v.dropout]
        heapify(unvisited)

        while len(unvisited):
            tpl_v = heappop(unvisited)
            v = tpl_v[1]
            v.v_data['visited'] = True

            if v.id == target.id:
                return

            for u_id in v.get_neighbors():
                u = self.graph[u_id]
                
                if u.v_data['visited'] or u.dropout:
                    continue

                edge = min(v.get_edges(u_id), key=lambda e: e['weight'])
                new_d = v.v_data['d'] + edge['weight']
                # Relax
                if new_d <= u.v_data['d']:
                    u.v_data['d'] = new_d
                    u.v_data['e_data'] = edge['e_data']
                    u.v_data['prev'] = v

            unvisited = [(v.v_data['d'], v)  for v in iter(self.graph.values()) 
                                                if not v.v_data['visited'] and not v.dropout]
            heapify(unvisited)

        # Clean
        for v in iter(self.graph.values()):
            v.v_data.pop('d', None)
            v.v_data.pop('visited', None)
        

    def __bfs_shortest_path(self, source, target):
        for v in iter(self.graph.values()):
            v.v_data['d'] = sys.maxint
            v.v_data['e_data'] = None
            v.v_data['color'] = 0
            v.v_data['prev'] = None

        source.v_data['color'] = 1
        source.v_data['d'] = 0

        heap = [source]
        heapify(heap)

        while len(heap):
            v = heappop(heap) 

            if v.id == target.id:
                return

            for u_id in v.get_neighbors():
                u = self.graph[u_id]
                
                if u.v_data['color'] != 0 or u.dropout:
                    continue

                u.v_data['color'] = 1
                u.v_data['d'] = v.v_data['d'] + 1
                u.v_data['prev'] = v
                edge = random.choice(v.get_edges(u_id))
                u.v_data['e_data'] = edge['e_data']
                heappush(heap, u)
            
            v.v_data['color'] = 2


    def __display_vertexies(self):
        print 'Vertexies:'
        for v in iter(self.graph.values()):
            print v.id,', ', v.v_data, 'dropout: ', v.dropout

    def __display_connections(self):
        print 'Connections:'
        for v in iter(self.graph.values()):
            for u in v.get_neighbors():
                print "From:", v.id,', To:', u 
                print "Edges:"
                for edge in v.get_edges(u):
                    print edge['weight'], edge['e_data']

class Vertex:
    """ Vertex with weights (for implicit edges) """
    def __init__(self, id, v_data = {}, json = None):
        if json:
            self.id = json['id']
            self.v_data = json['v_data']
            self.dropout = json['dropout']
            self.neighbors = json['neighbors']
        else:
            self.id = id
            self.v_data = v_data
            self.dropout = False
            self.neighbors = {}

    def add_neighbor(self, neighbor, weight = 0, e_data = {}):
        if neighbor not in self.neighbors:
            self.neighbors[neighbor] = []
        self.neighbors[neighbor].append({'weight':weight, 'e_data': e_data})

    def get_neighbors(self):
        return self.neighbors.keys()

    def get_edges(self, neighbor):
        if neighbor not in self.neighbors:
            return None

        return self.neighbors[neighbor]

    def to_json(self):
        return {'id': self.id, 'v_data': self.v_data, 'dropout': self.dropout,\
                'neighbors': self.neighbors}
    

