
import math
import copy
import search
import sokoban
from sokoban import find_2D_iterator


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [ (10887601, 'Timothy', 'Jeoung'), (10569294, 'Sooraj', 'Chirangara Narayanan'), (10660381, 'Naga Kaushik', 'Jandhayala') ]
    


def offset_direction(offset):
    if offset == (0, 1):
        return "Down"
    elif offset == (0, -1):
        return "Up"
    elif offset == (1, 0):
        return "Right"
    elif offset == (-1, 0):
        return "Left"
    else:
        raise ValueError("offset state is not known")


def direction_offset(direction):
    if direction == "Down":
        return 0, 1
    elif direction == "Up":
        return 0, -1
    elif direction == "Right":
        return 1, 0
    elif direction == "Left":
        return -1, 0
    else:
        raise ValueError("direction is not known")


def worker_goal_path(box, push_direction):
    """
    Search the goal paths for worker with directions with a box
    """
    offset = (0, 0)
    if push_direction == "Left":
        offset = (1, 0)
    elif push_direction == "Right":
        offset = (-1, 0)
    elif push_direction == "Up":
        offset = (0, 1)
    elif push_direction == "Down":
        offset = (0, -1)
    return tuple_addition(box, offset)


def tuple_addition(tuple1, tuple2):
    return tuple1[0] + tuple2[0], tuple1[1] + tuple2[1]

def turn_tuples(a):
    return a[1], a[0]

def manhattan_dist(a, b): #Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse. A "taboo cell" is by definition
    a cell inside a warehouse such that whenever a box get pushed on such 
    a cell then the puzzle becomes unsolvable. 
    
    Cells outside the warehouse are not taboo. It is a fail to tag one as taboo.
    
    When determining the taboo cells, you must ignore all the existing boxes, 
    only consider the walls and the target  cells.  
    Use only the following rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.
    
    @param warehouse: 
        a Warehouse object with a worker inside the warehouse

    @return
       A string representing the warehouse with only the wall cells marked with 
       a '#' and the taboo cells marked with a 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''

    # constants for representing warehoue
    squares_to_eliminate = ['$', '@']
    desired_squares = ['.', '!', '*']
    wall_square = '#'
    taboo_square = 'X'

    def check_for_corner(warehouse, x, y, wall=0):
       # a cell can be considered as corner cell if there is a  walls with in one unit distanceance below/up
       #from the cell and  walls in left/right with in one unit distanceance from the cell 
        walls_up_down_cell = 0
        walls_lef_right_cell = 0
        # cheking if wall present with in one unit distanceance of the cell in up and down direction
        #addind and sucrating one unit distanceance to cell's y cordinate and checking is the new cordinates 
        #is a wall squre
        #if wall squre detected in either up or down side then 'walls_up_down_cell' will be incrimented
        for (d_x, d_y) in [(0, 1), (0, -1)]:
            if warehouse[y + d_y][x + d_x] == wall_square:
                walls_up_down_cell += 1
        # cheking if wall present with in one unit distanceance of the cell in left and right direction
        #addind and sucrating one unit distanceance to cell's x cordinate and checking is the new cordinates 
        #is a wall squre
        #if wall squre detected in either left or right side then 'walls_lef_right_cell' will be incrimented
        for (d_x, d_y) in [(1, 0), (-1, 0)]:
            if warehouse[y + d_y][x + d_x] == wall_square:
                walls_lef_right_cell += 1
        if wall:
            return (walls_up_down_cell >= 1) or (walls_lef_right_cell >= 1)
        else:
            return (walls_up_down_cell >= 1) and (walls_lef_right_cell >= 1)

    # converting warehouse object into string format
    warehouse_str = str(warehouse)

    # worker and boxes in warehouse can be removed because in a given warehouse' initial state boxes will not be 
    #placed in taboo cells 
    # replacing worker and box with empty space
    for sqr_remove in squares_to_eliminate:
        warehouse_str = warehouse_str.replace(sqr_remove, ' ')

    # convert warehouse string into 2D array
    array_warehouse = [list(line) for line in warehouse_str.split('\n')]

    # apply rule 1: if a cell is a corner and not a target, then it is a taboo cell
    for y in range(len(array_warehouse) - 1):
        inside = False
        for x in range(len(array_warehouse[0]) - 1):
            # checking the reachability inside the warehouse
            # moving through cells untill an occurance of a wall 
            if not inside:
                if array_warehouse[y][x] == wall_square:
                    inside = True
            else:
                # checking is the cell is outside of the warehouse
                # checking is the cells on right side of the walls are empty and applying rule no:1
                
                if all([cell == ' ' for cell in array_warehouse[y][x:]]):
                    break
                if array_warehouse[y][x] not in desired_squares:
                    if array_warehouse[y][x] != wall_square:
                        if check_for_corner(array_warehouse, x, y):
                            array_warehouse[y][x] = taboo_square

# apply rule 2: all the cells between two corners along a wall are taboo if none of 
#these cells is a target
    for y in range(1, len(array_warehouse) - 1):
        for x in range(1, len(array_warehouse[0]) - 1):
            if array_warehouse[y][x] == taboo_square \
                    and check_for_corner(array_warehouse, x, y):
                row = array_warehouse[y][x + 1:]
                col = [row[x] for row in array_warehouse[y + 1:][:]]
                # populating taboo cells with cells which are right to the corner taboo cell
                for x2 in range(len(row)):
                    if row[x2] in desired_squares or row[x2] == wall_square:
                        break
                    if row[x2] == taboo_square \
                            and check_for_corner(array_warehouse, x2 + x + 1, y):
                        if all([check_for_corner(array_warehouse, x3, y, 1)
                                for x3 in range(x + 1, x2 + x + 1)]):
                            for x4 in range(x + 1, x2 + x + 1):
                                array_warehouse[y][x4] = 'X'
                # moving down from the corner taboo cella and adding cells which are not belong to target to
                #taboo cells
                for y2 in range(len(col)):
                    if col[y2] in desired_squares or col[y2] == wall_square:
                        break
                    if col[y2] == taboo_square \
                            and check_for_corner(array_warehouse, x, y2 + y + 1):
                        if all([check_for_corner(array_warehouse, x, y3, 1)
                                for y3 in range(y + 1, y2 + y + 1)]):
                            for y4 in range(y + 1, y2 + y + 1):
                                array_warehouse[y4][x] = 'X'

    #compute original string format of 2 dimensional array
    warehouse_str = '\n'.join([''.join(line) for line in array_warehouse])

    # replacing target squres with empy space
    for t_sqrs in desired_squares:
        warehouse_str = warehouse_str.replace(t_sqrs, ' ')
    return warehouse_str


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    '''

    def __init__(self, initial, goal):
        self.initial = (((-1, -1), "None"), initial)
        self.goal = goal.replace("@", " ")

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.
        
        As specified in the header comment of this class, the attributes
        'self.allow_taboo_push' and 'self.macro' should be tested to determine
        what type of list of actions is to be returned.
        """
        
        # Extracting the warehouse from the recent state.
        
        global negative_cell 
        
        present_wh = sokoban.Warehouse()
        present_wh.extract_locations(state[1].split(sep="\n"))
        

        if negative_cell is None:
            # Compute the taboo cells when the taboo cells have not computed. 
            # It is only required once for the optimization
            
            negative_cell = set(find_2D_iterator(taboo_cells(present_wh)
                                             .split("\n"), "X"))
        
        for box in present_wh.boxes:
            for offset in offset_states:
                position_of_player = turn_tuples((box[0] + (offset[0] * -1),
                                              box[1] + (offset[1] * -1)))
                position_of_newbox = tuple_addition(box, offset)
                if worker_paths(present_wh, position_of_player) \
                        and position_of_newbox not in negative_cell \
                        and position_of_newbox not in present_wh.walls \
                        and position_of_newbox not in present_wh.boxes:
                    yield (box, offset_direction(offset))
        # Search every boxes and directions that can be pushed

    def result(self, state, action):
        present_wh = sokoban.Warehouse()
        present_wh.extract_locations(state[1].split(sep="\n"))
        box = action[0]
        if box in present_wh.boxes:
        # Extracting the warehouse from the present state.
            
            # Old box being removed and new box to the position with worker
            offset = direction_offset(action[1])
            present_wh.worker = box
            present_wh.boxes.remove(box)
            present_wh.boxes.append(tuple_addition(box, offset))
            return action, str(present_wh)
        else: #When the box is out of range
            print(str(present_wh)) 
            print(box)
            print(present_wh.boxes)
            raise ValueError("Error! the box is out of the warehouse!")
    
    def value(self, state):
        #The changes will have a cost = 1
        return 1 
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
   # path cost consists is the combined cost of moving a worker and pushing a box, the cost
   #depends on the weight of the box. 
   #For moving a box with W units to  one unit distance, total cost will be W+1 
        global ls
        cos=0
        push_direction=action[1]
        new_=tuple_addition(action[0],direction_offset(push_direction))
    
 #    For each state transition, position and 
 #weight of the box stored into a list for referencing in next state transition
        l= len(ls)
            
        if (ls[l-2][0]==action[0]):
            
            cos=ls[l-2][1]
            nls=[new_,cos]
            ls.append(nls)
            ls.append(ls[l-1])
            
        elif(ls[l-1][0]==action[0]):
            cos=ls[l-1][1]
            nls=[new_,cos]
            ls.append(nls)
            ls.append(ls[l-2])
       
        return c+cos+1

    def goal_test(self, state):
       
        return state[1].replace("@", " ") == self.goal
        # Test to see the state warehouse goals are filled



class SearchProblemPath(search.Problem):
    
    def __init__(self, initial, warehouse, goal=None):
        self.initial = initial
        self.goal = goal
        self.warehouse = warehouse

    def actions(self, state):
        #testing the area is not wall or a box
        for offset in offset_states:
            n_states = tuple_addition(state, offset) #newstate
            if n_states not in self.warehouse.boxes \
                    and n_states not in self.warehouse.walls:
                yield offset
                
    def result(self, state, action):
            n_states = tuple_addition(state, action) #new state
            return n_states      
    
    def value(self, state):
           # A single movement of cost = 1
           return 1  

                

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        
                
                
def check_elem_action_seq(warehouse, action_seq):
    '''
    
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''
    # calling warehouse worker to get location of worker and warehouse.boxes for locations
    global x, y
    
    x = warehouse.worker[0]
    y = warehouse.worker[1]

    # String constant to be returnet in case of failedSequence 
    failed_sequence = 'Impossible'

   
    #Validating each move action_seq by iterating through every moves in it
    def left(x,y):
         
            # next location for left
            
         next_x = x - 1
         next_y = y
            # checking movement in in left direction
         if (next_x, next_y) in warehouse.walls:
             return failed_sequence  # failed to move
         elif (next_x, next_y) in warehouse.boxes:
                if (next_x - 1, next_y) not in warehouse.walls and (
                        next_x, next_y) in warehouse.boxes:
                    #movement possible
                    warehouse.boxes.remove((next_x, next_y))
                    warehouse.boxes.append((next_x - 1, next_y))
                    x = next_x
                else:
                    return failed_sequence  # box was blocked
         else:
                x = next_x
                return x
    def right(x,y):
            #checking movement in right direction
            next_x = x + 1
            next_y = y
            if (next_x, next_y) in warehouse.walls:
                return failed_sequence  # impossible move
            elif (next_x, next_y) in warehouse.boxes:
                if (next_x + 1, next_y) not in warehouse.walls \
                        and (next_x, next_y) in warehouse.boxes:
                    # can move the box!
                    # move successful
                    warehouse.boxes.remove((next_x, next_y))
                    warehouse.boxes.append((next_x + 1, next_y))
                    x = next_x
                else:
                    return failed_sequence  # box was blocked
            else:
                x = next_x
                return x
        
    def up(x,y):
        #checking movement to Up direction
        next_y = y - 1
        next_x = x
        if (next_x, next_y) in warehouse.walls:
            return failed_sequence  # impossible move
        elif (next_x, next_y) in warehouse.boxes:
                if (next_x, next_y - 1) not in warehouse.walls \
                        and (next_x, next_y) in warehouse.boxes:
                    # movement posible
                    
                    warehouse.boxes.remove((next_x, next_y))
                    warehouse.boxes.append((next_x, next_y - 1))
                    y = next_y
                else:
                    return failed_sequence  # box was blocked
        else:
                y = next_y
                return y
    def down(x,y):
        #checking for down movement
        next_y = y + 1
        next_x = x
        if (next_x, next_y) in warehouse.walls:
            return failed_sequence  # movement not possible
        elif (next_x, next_y) in warehouse.boxes:
                if (next_x, next_y + 1) not in warehouse.walls \
                        and (next_x, next_y) in warehouse.boxes:
                    # sucessfull movement
                    
                    warehouse.boxes.remove((next_x, next_y))
                    warehouse.boxes.append((next_x, next_y + 1))
                    y = next_y
                else:
                    return failed_sequence  # failed by block
        else:
                y = next_y
                return y
      
   # move_list=['left','right','up','down']    
    for data in action_seq:
        if(data=='Left'):
            x=left(x,y)
            if(x =='Impossible'):
                return failed_sequence
            
        elif(data=='Right'):
             x=right(x,y)
             if(x =='Impossible'):
                return failed_sequence 
                 
             
        elif(data=='Up'):
            y=up(x,y)
            if(y =='Impossible'):
                return failed_sequence
            
        elif(data=='Down'):
            y=down(x,y)
            if(y =='Impossible'):
                return failed_sequence
        else:
            raise ValueError("Invalid action sequence; action sequence must be combination of Right,Left,Up, and Down")
        
#    applicable_sequence = 'Yes'
#    print(applicable_sequence)

    # implement change character information for updating
    warehouse.worker = x, y                                
  # the code below are from sokoban.py for creating warehoue string from a warehouse object
    X, Y = zip(*warehouse.walls)
    x_size, y_size = 1 + max(X), 1 + max(Y)

    vis = [[" "] * x_size for z in range(y_size)]
    for (x, y) in warehouse.walls:
        vis[y][x] = "#"
    for (x, y) in warehouse.targets:
        vis[y][x] = "."

    if vis[warehouse.worker[1]][warehouse.worker[0]] == ".":
        vis[warehouse.worker[1]][warehouse.worker[0]] = "!"
    else:
        vis[warehouse.worker[1]][warehouse.worker[0]] = "@"
    for (x, y) in warehouse.boxes:
        if vis[y][x] == ".":  # if on target
            vis[y][x] = "*"
        else:
            vis[y][x] = "$"
    warehouse = "\n".join(["".join(line) for line in vis])
   # A warehouse string after perfoming given action sequence will be returned    
    return str(warehouse)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def solve_weighted_sokoban(warehouse):
    '''
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.
    
    @param 
     warehouse: a valid Warehouse object

    @return
    
        If puzzle cannot be solved 
            return 'Impossible', None
        
        If a solution was found, 
            return S, C 
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C

    '''
    
    # f(n) = g(n) + h(n)    
      # specify the goal
    warehouse_stringing = str(warehouse)
    goal = warehouse_stringing.replace("$", " ").replace(".", "*")
    global ls
    # Creating a dictionary to keep movement and weight of the box consistant
    #Initialising the dictionary with initial position of boxes and coresponding weights
    wd={}
    l= []
    for box in warehouse.boxes:
        try:
            w_1=warehouse.weights[warehouse.boxes.index((box[0],box[1]))]
        except:
            w_1 = 0    
        wd[box]=w_1
        l.append([box,w_1])
    ls=l 

    # specifying heuristic
    def h(n):
        # Manhattan distanceance heuristic
        state = n.state[1]
        wh = sokoban.Warehouse()
        wh.extract_locations(state.split('\n'))
        num_targets = len(wh.targets)
        heuristic = 0
        for box in wh.boxes:
            distance = 0
            for target in wh.targets:
                distance+= manhattan_dist(box, target)
            heuristic += (distance/num_targets)
#           
        return heuristic

    # using astar_graph_search
    L = search.astar_graph_search(SokobanPuzzle(warehouse_stringing, goal),h)
                                      
    # when the puzzle cannot be solved SokobanPuzzle returns 'None'
    if L is None:
        return ['Impossible']

    # take the returned action and it's paths to get theres
    location_actions = L.path()
        
    # extract the action data from the node data
    location_actions = [e.action for e in location_actions]
    # extract the state data from the node data
    state_check = L.path()
    state_check = [b.state for b in state_check]

    obj = copy.deepcopy(warehouse)

    # check if already solved
    if len(location_actions) == 0:
        return location_actions

    S = [] 
    C = 0
    for location_action in location_actions[1:]:
        target_box = location_action[0]
        push_direction = location_action[1]
        worker_goal = worker_goal_path(target_box, push_direction)

        def heuristic(n):
            state = n.state
            return math.sqrt(((state[1] - worker_goal[1]) ** 2)
                             + ((state[0] - worker_goal[0]) ** 2))

        nodes = search.astar_graph_search(SearchProblemPath(obj.worker, obj,
                                            worker_goal), heuristic)
        
        if nodes is None:
            return ['Impossible']
        
        # build list of actions to get worker next to target box
        for node in nodes.path()[1:]:
            S.append(offset_direction(node.action))
            C=C+1
        # add the actual push action
        S.append(push_direction)
        new_pos=tuple_addition(location_action[0],direction_offset(push_direction))
        wd[new_pos]=wd.get(location_action[0])
        C=C+1+wd.get(location_action[0])
        
        # move target box to new position
        obj.boxes.remove(target_box)
        obj.boxes.append(
            tuple_addition(target_box, direction_offset(push_direction)))

        # move worker to new position
        obj.worker = target_box
        
    
    return S, C

    

#raise NotImplementedError()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


offset_states = [(-1, 0), (1, 0), (0, -1), (0, 1)]
negative_cell = None


def worker_paths(warehouse, location):
    #Finding the nodes which are reachable by worker without pushing the box

    def heuristic(n):
        state = n.state
        distance = manhattan_dist(state,location)
#        return math.sqrt(((state[1] - location[1]) ** 2)
#                         + ((state[0] - location[0]) ** 2))
        return distance

    location = (location[1], location[0])  # Destination is given in (row,col), not (x,y)

    # Use an A* graph search on the SearchProblemPath search
    node = search.astar_graph_search(SearchProblemPath(warehouse.worker, warehouse, location),
                       heuristic)

    # If a node was found, this is a valid destination
    return node is not None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
