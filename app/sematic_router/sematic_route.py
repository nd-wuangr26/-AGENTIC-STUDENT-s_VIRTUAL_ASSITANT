import numpy as np

class SematicRouter():
    def __init__(self, embeding, routes):
        self.routes = routes
        self.embeding = embeding
        self.RouteEmbeding = {}
        
        # Encode samples và lưu trước        
        for route in self.routes:
            self.RouteEmbeding[route.name] = self.embeding.encode(route.samples)
        
    def get_routes(self):
        return self.routes
    
    def guide(self, query):
        QueryEmbeding = self.embeding.encode([query])
        QueryEmbeding = QueryEmbeding/np.linalg.norm(QueryEmbeding)
        scores = []
        for route in self.routes:
            RoutesEmbeding = self.RouteEmbeding[route.name]
            # Chuẩn hóa từng vector trong route
            RoutesEmbeding = RoutesEmbeding / np.linalg.norm(RoutesEmbeding, axis=1, keepdims=True)
            
            # Cosine similarity: dot product vì vector đã chuẩn hóa
            similarities = np.dot(RoutesEmbeding, QueryEmbeding)
            max_score = np.max(similarities)
            #avg_score = np.mean(similarities)
            
            scores.append((max_score, route.name))
            
        scores.sort(reverse = True)
        print('score: ', scores)
        return scores[0]
        