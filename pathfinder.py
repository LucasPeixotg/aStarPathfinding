from time import sleep
from math import sqrt, floor

class Path:
    def __init__(self, father_pos:tuple, gcost:int, hcost:int, pos:tuple):
        self.pos = pos
        self.father_pos = father_pos
        self.gcost = gcost
        self.hcost = hcost
        self.fcost = gcost + hcost
        self.locked = False

class PathFinder:
    def __init__(self, width, height, delay=0):
        self.width = width
        self.height = height
        self.delay = delay
        self.initial = ()
        self.target = ()
        self.grid = []
        for i in range(width):
            self.grid.append([])
            for j in range(height):
                self.grid[i].append(0)


    def set_initial(self, col, row):
        try:
            if not self.grid[col][row] or self.grid[col][row] == 'obstacle':
                self.grid[col][row] = 'initial'
                self.initial = (col, row)

                return False
            else:
                return True
        except IndexError:
            return True

    def set_target(self, col, row):
        try:
            if not self.grid[col][row] or self.grid[col][row] == 'obstacle':
                self.grid[col][row] = 'target'
                self.target = (col, row)
                
                return False
            else:
                return True
        except IndexError:
            return True

    def set_obstacle(self, col, row):
        try:
            if not self.grid[col][row]:
                self.grid[col][row] = 'obstacle'
        except IndexError:
            pass

    def remove(self, col, row):
        if not self.grid[col][row]:
            return None
        elif self.grid[col][row] == 'initial':
            self.initial = ()
            self.grid[col][row] = None
            return 'initial'
        elif self.grid[col][row] == 'target':
            self.target = ()
            self.grid[col][row] = None
            return 'target'
        else:
            self.grid[col][row] = None
            return 'obstacle'

    def ready(self):
        return self.initial and self.target

    def calculate_costs(self, pos, fatherpos, fathergcost):
        gcost = floor( (sqrt(((pos[0] - fatherpos[0])**2 )+((pos[1] - fatherpos[1])**2)))* 10) + fathergcost
        hcost = floor( (sqrt(((pos[0] - self.target[0])**2 )+((pos[1] - self.target[1])**2)))* 10 )

        return gcost, hcost    

    def start(self):
        if not self.ready():
            return 
        
        self.path_list = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i != 0 or j != 0:
                    pos = (self.initial[0]+i, self.initial[1]+j)
                    if pos != self.initial and pos[0] >= 0 and pos[0] < self.width and pos[1] >= 0 and pos[1] < self.height: 
                        gcost, hcost = self.calculate_costs(pos, self.initial, 0)
                        path = Path(self.initial, gcost, hcost, pos)

                        if not self.grid[pos[0]][pos[1]]:
                            self.path_list.append(path)
                            self.grid[pos[0]][pos[1]] = path
                        
                        elif self.grid[pos[0]][pos[1]] == 'target':
                            self.target_found(path)

        self.path_list = sorted(self.path_list, key=lambda path: (path.fcost, path.hcost))
        sleep(self.delay)
        
        while True:
            try:
                father = self.path_list[0]
            except IndexError:
                return
            if not father:
                return

            father.locked = True
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:
                        pos = (father.pos[0]+i, father.pos[1]+j)
                        if pos != father.pos and pos[0] >= 0 and pos[0] < self.width and pos[1] >= 0 and pos[1] < self.height: 
                            gcost, hcost = self.calculate_costs(pos, father.pos, father.gcost)


                            path = Path(father.pos, gcost, hcost, pos)

                            if not self.grid[pos[0]][pos[1]]:
                                self.path_list.append(path)
                                self.grid[pos[0]][pos[1]] = path

                            elif type(self.grid[pos[0]][pos[1]]) == Path:
                                if self.grid[pos[0]][pos[1]].fcost > path.fcost and not self.grid[pos[0]][pos[1]].locked:
                                    self.path_list.append(path)
                                    self.grid[pos[0]][pos[1]] = path
                            
                            elif self.grid[pos[0]][pos[1]] == 'target':
                                self.target_found(father)
                                return

            self.path_list.remove(father)
            self.path_list = sorted(self.path_list, key=lambda path: (path.fcost, path.hcost))
            sleep(self.delay)


    def target_found(self, path):
        current = path
        while current != 'initial':
            sleep(self.delay)
            self.grid[current.pos[0]][current.pos[1]] = 'success'
            current = self.grid[current.father_pos[0]][current.father_pos[1]]
        return
