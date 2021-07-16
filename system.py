import galaxy_objects as ob

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
            ID = len(nebula_list)
            name = gamestate[line_number + 7][11:-1]
            x_coord = float(gamestate[line_number + 2][10:])
            y_coord = float(gamestate[line_number + 3][10:])
            radius = int(gamestate[line_number + 8][11:])
            nebula_list.append(ob.nebula(line_number,ID,name,x_coord,y_coord,radius))
            current_line = line_number
        elif "construction={" in gamestate[line_number]:
            break
    return nebula_list


def system_organizer(current_line,gamestate):
    system_list = []
    for line_number in range(current_line,len(gamestate)):
        if ("type=star" in gamestate[line_number]) and ("type=starbase" not in gamestate[line_number]):
            ID = len(system_list)
            name = gamestate[line_number+1][14:-1]
            x_coord = float(gamestate[line_number - 5][14:])
            y_coord = float(gamestate[line_number - 4][14:])
            owner_ID = -1
            starbase_ID = -1
            for sub_line_number in range(line_number + 1, line_number + 100):
                if ("starbase=" in gamestate[sub_line_number]) and ("dpe_recent_talent" not in gamestate[sub_line_number]):
                    starbase_ID = int(gamestate[sub_line_number][17:])
                    break
            system_list.append(ob.system(line_number,ID,name,x_coord,y_coord,owner_ID,starbase_ID))
            current_line = line_number
        elif "starbase_mgr={" in gamestate[line_number]:
            break
    return system_list


def starbase_organizer(current_line,gamestate):
    starbase_list = []
    for line_number in range(current_line,len(gamestate)):
        if 'level="starbase_level' in gamestate[line_number]:
            ID = int(gamestate[line_number - 1][8:-2])
            level = gamestate[line_number][34:-1]
            owner_ID = -1
            for sub_line_number in range(line_number + 5, line_number + 9):
                if "owner=" in gamestate[sub_line_number]:
                    owner_ID = int(gamestate[sub_line_number][18:])
                    break
            modules = "None"
            buildings = "None"
            starbase_list.append(ob.starbase(line_number,ID,level,owner_ID,modules,buildings))
            current_line = line_number
        elif "planets={" in gamestate[line_number]:
            break
    return starbase_list

def system_owner_finder(system_list,starbase_list):
    for system in system_list:
        for starbase in starbase_list:
            if system.starbase_ID == starbase.ID:
                system.owner_ID = starbase.owner_ID
                break
