import galaxy_objects as ob

#File with galaxy from Savegame
gamestate = open("gamestate").read().replace("\t","    ").splitlines()

#READER
current_line = 0

#NEBULA ORGANIZER
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

#SYSTEM ORGANIZER
system_list = []
for line_number in range(current_line,len(gamestate)):
    if ("type=star" in gamestate[line_number]) and ("type=starbase" not in gamestate[line_number]):
        ID = len(system_list)
        name = gamestate[line_number+1][13:-1]
        x_coord = float(gamestate[line_number - 5][14:])
        y_coord = float(gamestate[line_number - 4][14:])
        owner_ID = -1
        starbase_ID = -1
        for sub_line_number in range(line_number + 1, line_number + 50):
            if "starbase=" in gamestate[sub_line_number]:
                starbase_ID = gamestate[sub_line_number][17:]
                break
        system_list.append(ob.system(line_number,ID,name,x_coord,y_coord,owner_ID,starbase_ID))
        current_line = line_number
    elif "starbase_mgr={" in gamestate[line_number]:
        break

#STARBASE ORGANIZER
starbase_list = []
for line_number in range(current_line,len(gamestate)):
    if 'level="starbase_level' in gamestate[line_number]:
        ID = len(starbase_list)
        level = gamestate[line_number][34:-1]
        owner = -1
        for sub_line_number in range(line_number + 5, line_number + 9):
            if "owner=" in gamestate[sub_line_number]:
                owner = gamestate[sub_line_number][18:]
                break
        modules = "None"
        buildings = "None"
        starbase_list.append(ob.starbase(line_number,ID,level,owner,modules,buildings))
        current_line = line_number
    elif "planets={" in gamestate[line_number]:
        break