class system:
    def __init__(self,line_number,ID,name,x_coord,y_coord,owner_ID,starbase_ID) -> None:
        
        #critical attributes: these are to be found
        self.ID = ID
        self.name = name
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.owner_ID = owner_ID

        #intermediate attributes: these are used to find critical attributes
        self.starbase_ID = starbase_ID

class nebula:
    def __init__(self,line_number,ID,name,x_coord,y_coord,radius) -> None:
        
        self.line_number = line_number
        self.ID = ID
        self.name = name
        self.x_coord = x_coord
        self.y_coord = y_coord
        
        #Radius is present, but appears to be a constant 30 for all nebulae. 
        self.radius = radius

class starbase:
    def __init__(self,line_number,ID,level,owner,modules,buildings) -> None:

        self.line_number = line_number
        self.ID = ID
        self.level = level
        self.owner = owner
        self.modules = modules
        self.buildings = buildings