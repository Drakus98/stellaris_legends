from os import system
import galaxy_objects as ob
import numpy as np
import skimage.draw as dw
import skimage.io as aiyo
import skimage.segmentation as seg

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
            type = "None"
            starbase_ID = system_find_starbase_ID(line_number,gamestate)
            connections = system_find_connections(ID,line_number,gamestate)
            closest = False
            
            #Object creation
            system_list.append(ob.system(line_number,ID,name,x_coord,y_coord,owner_ID,starbase_ID,connections,closest,type))
            #Line increment for speed
            current_line = line_number
        elif "starbase_mgr={" in gamestate[line_number]:
            break
    star_dist = (([np.sqrt(s.x_coord**2+s.y_coord**2) for s in system_list]))
    closest_star_index = min(range(len(star_dist)), key=star_dist.__getitem__)
    system_list[closest_star_index].closest = True
    return system_list


def system_find_starbase_ID(line_number,gamestate):
    for sub_line_number in range(line_number + 1, line_number + 100):
        if " starbase=" in gamestate[sub_line_number]:
            return int(gamestate[sub_line_number][17:])
    return -1


def system_find_connections(ID,line_number,gamestate):
    connections = []
    for sub_line_number in range(line_number + 1, line_number + 100):
        if "coordinate={" in gamestate[sub_line_number]:
            break        
        if "to=" in gamestate[sub_line_number]:
            target = int(gamestate[sub_line_number][19:])
            if target > ID:
                connections.append(target)
    return connections


def system__find_starbase_type(line_number,gamestate):
    if "modules=" in gamestate[line_number + 1]:
        if "shipyard" in gamestate[line_number + 2]:
            return "Shipyard"
        elif "trade_hub" in gamestate[line_number + 2]:
            return "Trade Hub"
        elif "battery" in gamestate[line_number + 2]:
            return "Bastion"
        else:
            return "Empty"
    return "Basic"


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
            type = system__find_starbase_type(line_number,gamestate)
            #Object creation
            starbase_list.append(ob.starbase(line_number,ID,level,owner_ID,modules,buildings,type))
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


def system_find_starbase_info(system_list,starbase_list):
    for system in system_list:
        for starbase in starbase_list:
            if system.starbase_ID == starbase.ID:
                system.owner_ID = starbase.owner_ID
                system.starbase_type = starbase.type
                break
    return None


def system_coord_conv(system_list,img_size,multiplier):
    for system in system_list:
        system.x_coord = ((system.x_coord * multiplier) + int((img_size/2)))
        system.y_coord = ((system.y_coord * multiplier) + int((img_size/2)))
    return None


def colorify(fig):
    """Given a 2D array, returns that array stacked thrice over (i.e. converts greyscale to color)"""
    return np.stack((fig,fig,fig),axis=-1)


def draw_core(map_file,system_list):
    center_x = len(map_file)/2
    center_y = len(map_file)/2
    nearest_x_y = [0,0]
    for system in system_list:
        if system.closest == True:
            nearest_x_y[0] = system.x_coord
            nearest_x_y[1] = system.y_coord
    radius = int(np.sqrt((center_x-nearest_x_y[0])**2+(center_y-nearest_x_y[1])**2))-10
    center_info = [center_x,center_y,]

    rr,cc = dw.disk((center_x,center_y),radius = radius)
    map_file[rr,cc] = np.random.randint(230,high=255)
    return None


def draw_territories(map_file,system_list,color_dict):
    #Draws increasingly bigger colored circles from each system
    for size in range(0,120,1):
        for system in system_list:
            rr,cc = dw.circle_perimeter(system.x_coord,system.y_coord,size, method="andres", shape=(map_file.shape))
            map_file[rr,cc] = np.where(map_file[rr,cc]==(255,255,255),color_dict[system.owner_ID],map_file[rr,cc])
    
    map_file[:,:] = np.where(map_file==[254,254,254],[255,255,255],map_file)
    borders = (seg.find_boundaries(map_file[:,:,0],mode='thick')
              |seg.find_boundaries(map_file[:,:,1],mode='thick')
              |seg.find_boundaries(map_file[:,:,2],mode='thick'))
    map_file[borders] = 0
    return None


def color_assignment(system_list):
    color_dict={}
    for system in system_list:
        if system.owner_ID not in color_dict:
            if system.owner_ID == -1:
                color_dict[system.owner_ID] = (254,254,254)
            else:
                color_dict[system.owner_ID] = np.random.randint(120,high=229,size=3)
    return color_dict


def draw_lines(map_file,system_list):
    for origin in system_list:              #origin is first object
        targets = origin.connections                #targets is IDs of second object
        for target_ID in targets:#target is single ID of object
            target=system_list[target_ID]
            rr, cc, val = dw.line_aa(origin.x_coord,origin.y_coord
                                    ,target.x_coord,target.y_coord)
            val = np.abs(val-max(val))
            map_file[rr,cc] = colorify(val)*map_file[rr,cc]
    return map_file


def draw_systems(map_file,system_list):
    for system in system_list:
        map_file[dw.disk((system.x_coord,system.y_coord),4)]=(230,30,37)
    return None


nebula_list, system_list, starbase_list = save_reader(gamestate)
system_find_starbase_info(system_list,starbase_list)


img_size = 4000
multiplier = 4


map_file=np.full([img_size,img_size,3],fill_value=255,dtype=np.uint8)

color_dict = color_assignment(system_list)
system_coord_conv(system_list,img_size,multiplier)
draw_core(map_file,system_list)
print("Drawn Core")
draw_territories(map_file,system_list,color_dict)
print("Drawn Territories")
draw_lines(map_file,system_list)
print("Drawn Hyperlanes")
draw_systems(map_file, system_list)
print("Drawn Systems")

map_file = np.rot90(map_file,k=3).astype(np.uint8)
aiyo.imsave("test.png",map_file)