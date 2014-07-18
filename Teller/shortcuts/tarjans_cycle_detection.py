import pprint
from Teller.models import Tale, TalePart, TaleLink


class TarjansCycleDetection:
    def __init__(self, tale_id, tale=None):
        self.tale = tale
        if self.tale is None:
            self.tale = Tale.objects.get(id=tale_id)
        self.V = TalePart.objects.filter(tale=self.tale)
        self.E = TaleLink.objects.filter(tale=self.tale)
        self.index = {}
        self.lowlink = {}
        self.i = 0
        self.S = []
        self.SCC = []
        self.hasCycle = False

    def strong_connect(self, v):
        self.index[v.id] = self.i
        self.lowlink[v.id] = self.i
        self.i += 1
        self.S.append(v.id)
        successors = self.E.filter(source=v).values_list('destination', flat=True)
        for w in successors:
            w = self.V.get(id=w)
            if w.id not in self.index:
                self.strong_connect(w)
                self.lowlink[v.id] = min(self.lowlink[v.id], self.lowlink[w.id])
            elif w.id in self.S:
                self.lowlink[v.id] = min(self.lowlink[v.id], self.index[w.id])

        if self.lowlink[v.id] == self.index[v.id]:
            new_scc = []
            w = None
            while w != v.id:
                w = self.S.pop()
                new_scc.append(w)
            self.SCC.append(new_scc)

    def detect_cycles(self):
        """
        Uses Tarjan's algorithm to find cycles in directed graph
        """

        for v in self.V:
            if v.id not in self.index:
                self.strong_connect(v)

        for sc in self.SCC:
            if len(sc) > 1:
                return True
        return False
