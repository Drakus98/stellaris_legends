import galaxy_objects as ob
import numpy as np
import skimage.draw as dw
import skimage.io as aiyo

gamestate = open("gamestate").read().replace("\t","    ").splitlines()

def save_reader(gamestate):
    current_line = 0
    nebula_list = nebula_organizer(current_line,gamestate)
    system_list = system_organizer(current_line,gamestate)
    starbase_list = starbase_organizer(current_line,gamestate)
    return nebula_list, system_list, starbase_list


def nebula_organizer(current_line,gamestate):
    nebula_list = []
    for line_number in range(current_line,len(gamestate)):
        if "nebula={" in gamestate[line_number]:
            #Attribute collection
            ID = len(nebula_list)
            name = gamestate[line_number + 7][11:-1]
            x_coord = int(float(gamestate[line_number + 2][10:]))
            y_coord = int(float(gamestate[line_number + 3][10:]))
            radius = int(gamestate[line_number + 8][11:])
            #Object creation
            nebula_list.append(ob.nebula(line_number,ID,name,x_coord,y_coord,radius))
            #Line increment for speed
            current_line = line_number
        elif "construction={" in gamestate[line_number]:
            break
    return nebula_list


def system_organizer(current_line,gamestate):
    system_list = []
    for line_number in range(current_line,len(gamestate)):
        if ("type=star" in gamestate[line_number]) and ("type=starbase" not in gamestate[line_number]):
            #Attribute collection
            ID = len(system_list)
            name = gamestate[line_number+1][14:-1]
            x_coord = int(float(gamestate[line_number - 5][14:]))
            y_coord = int(float(gamestate[line_number - 4][14:]))
            owner_ID = -1
            starbase_ID = system_find_starbase_ID(line_number,gamestate)
            connections = system_find_connections(ID,line_number,gamestate)
            #Object creation
            system_list.append(ob.system(line_number,ID,name,x_coord,y_coord,owner_ID,starbase_ID,connections))
            #Line increment for speed
            current_line = line_number
        elif "starbase_mgr={" in gamestate[line_number]:
            break
    return system_list

def system_find_starbase_ID(line_number,gamestate):
    for sub_line_number in range(line_number + 1, line_number + 100):
        if ("starbase=" in gamestate[sub_line_number]) and ("dpe_recent_talent" not in gamestate[sub_line_number]):
            return int(gamestate[sub_line_number][17:])
    return -1

def system_find_connections(ID,line_number,gamestate):
    connections = []
    for sub_line_number in range(line_number + 1, line_number + 100):
        if "to=" in gamestate[sub_line_number]:
            target = int(gamestate[sub_line_number][19:])
            if target > ID:
                connections.append(target)
    return connections

def starbase_organizer(current_line,gamestate):
    starbase_list = []
    for line_number in range(current_line,len(gamestate)):
        if 'level="starbase_level' in gamestate[line_number]:
            #Attribute collection
            ID = int(gamestate[line_number - 1][8:-2])
            level = gamestate[line_number][34:-1]
            owner_ID = starbase_find_owner_ID(line_number,gamestate)
            modules = "None"
            buildings = "None"
            #Object creation
            starbase_list.append(ob.starbase(line_number,ID,level,owner_ID,modules,buildings))
            #Line increment for speed
            current_line = line_number
        elif "planets={" in gamestate[line_number]:
            break
    return starbase_list

def starbase_find_owner_ID(line_number,gamestate):
    for sub_line_number in range(line_number + 5, line_number + 10):
        if "owner=" in gamestate[sub_line_number]:
            return int(gamestate[sub_line_number][18:])
    return -1

def system_find_owner(system_list,starbase_list):
    for system in system_list:
        for starbase in starbase_list:
            if system.starbase_ID == starbase.ID:
                system.owner_ID = starbase.owner_ID
                break

def system_coord_conv(system_list,img_size,multiplier):
    for system in system_list:
        system.x_coord = ((system.x_coord * multiplier) + int((img_size/2)))
        system.y_coord = ((system.y_coord * multiplier) + int((img_size/2)))

def colorify(fig):
    """Given a 2D array, returns that array stacked thrice over (i.e. converts greyscale to color)"""
    return np.stack((fig,fig,fig),axis=-1)


def draw_systems(map_file,system_list):
    count = 0
    for system in system_list:
        map_file[dw.disk((system.x_coord,system.y_coord),2.5)]=(230,30,37)


def draw_lines(map_file,system_list,img_size,multiplier):
    for origin in system_list:              #origin is first object
        targets = origin.connections                #targets is IDs of second object
        for target_ID in targets:#target is single ID of object
            target=system_list[target_ID]
            rr, cc, val = dw.line_aa(origin.x_coord,origin.y_coord
                                    ,target.x_coord,target.y_coord)
            val = np.abs(val-max(val))
            map_file[rr,cc] = colorify(val)*(132,213,243)
    return map_file
    
nebula_list, system_list, starbase_list = save_reader(gamestate)
system_find_owner(system_list,starbase_list)


img_size = 4000 #max coord is just below 500, multiplier is therefore 4.
multiplier = 4
system_coord_conv(system_list,img_size,multiplier)


map_file=np.full([img_size,img_size,3],fill_value=255,dtype=np.uint8)
draw_systems(map_file, system_list)
draw_lines(map_file,system_list,img_size,multiplier)
map_file = np.rot90(map_file,k=3)
aiyo.imsave("test.png",map_file)