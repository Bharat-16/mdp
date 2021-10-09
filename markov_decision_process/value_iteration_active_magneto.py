import random
import time
import tkinter as Mazegame
from tkinter import ttk, Canvas, Label

actions = [(-1,0),(1,0),(0,-1),(0,1)]

final_reward = 0

delta = 0.05
gamma = 0.85

#initial position
position_vector = [4,5,4,5,1,5]

#make the window to display
def make_screen(n):
    size = 300

    cell_width = int(size/n)
    cell_height = int(size/n)

    screen = Mazegame.Tk()
    screen.title("Value Iteration with Active Magneto")
    grid = Canvas(screen, width = cell_width*n, height = cell_height*n, highlightthickness=0)
    grid.pack(side="top", fill="both", expand="true")

    rect = {}
    for col in range(n):
        for row in range(n):
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height
            rect[row, col] = grid.create_rectangle(x1,y1,x2,y2, fill="red", tags="rect")
    return grid, rect, screen, cell_width

# update window with repect to given positions
def redraw_maze(grid, rect, screen, n, maze, delay, wid):
    grid.itemconfig("rect", fill="green")
    
    for i in range(n):
        for j in range(n):
            item_id = rect[i,j]
            if maze[i][j] == 0:                      
                grid.itemconfig(item_id, fill="salmon")
            elif maze[i][j] == 1:                      
                grid.itemconfig(item_id, fill="brown")	#magneto
            elif maze[i][j] == 2:                        
                grid.itemconfig(item_id, fill="brown")	#blue
            elif maze[i][j] == 3:
                grid.itemconfig(item_id, fill="red")	#jean
    grid.itemconfig(rect[2,3], fill="black")
    screen.update_idletasks()
    screen.update()
    time.sleep(delay)
    return
	
#to calculate euclidean distance
def distance(A, B):
	return (abs(A[0] - B[0])*abs(A[0] - B[0]) + abs(A[1] - B[1])*abs(A[1] - B[1]))**0.5

	
#generates possible actions for magneto
def update_Magneto(x,y, x_w, y_w):
	best_pos = [(x,y)]
	valid = [(x-1 , y),(x , y-1),(x+1,y),(x,y+1)]
    
	min = distance((x_w,y_w),(x,y))
	for pos in valid:
		x_m , y_m = pos
		if x_m <=5 and y_m <=5 and x_m > 0 and y_m > 0 and (x_m,y_m) != (5,5) and (x_m,y_m) != (4,3):
			if min > distance((x_w,y_w),(x_m,y_m)):
				best_pos = []
				min = distance((x_w,y_w),(x_m,y_m))
				best_pos.append((x_m,y_m))
			elif min == distance((x_w,y_w),(x_m,y_m)):
				best_pos.append((x_m,y_m))
		
	return random.choice(best_pos)

#initialize screen and delay time
delay = 0.2
grid, rect, screen, wid = make_screen(5)

count = 0
#outer loop, each iteration means one step of all players
while(True):
	count += 1
	input()
	
	#set updated positions of all players on the board
	board = [[0 for i in range(5)] for j in range(5)]
	board[5-position_vector[1]][position_vector[0]-1] = 1	#magneto
	board[5-position_vector[3]][position_vector[2]-1] = 2	#wolverine
	board[5-position_vector[5]][position_vector[4]-1] = 3	#jean
	
	#redraw window
	redraw_maze(grid, rect, screen, 5, board, delay, wid)
	
	#old utility matrix
	V = [[0 for i in range(5)] for j in range(5)]
	
	#utility_matrix for next iteration
	utility_matrix = [[0 for i in range(5)] for j in range(5)]
					  
	if (position_vector[0],position_vector[1]) == (position_vector[4],position_vector[5]):
		V[position_vector[0]-1][position_vector[1]-1] = -15
		utility_matrix[position_vector[0]-1][position_vector[1]-1] = -15
	else:
		V[position_vector[0]-1][position_vector[1]-1] = -20
		V[position_vector[4]-1][position_vector[5]-1] = 20
		utility_matrix[position_vector[0]-1][position_vector[1]-1] = -20
		utility_matrix[position_vector[4]-1][position_vector[5]-1] = 20

	# iteration for convergence (value iteration algorithm begins)
	for _ in range(30):
		
		#for all states
		for i in range(5):
			for j in range(5):
				
				utilities = []	#contains utility for all actions at a perticular state
				
				if (i+1,j+1) == (position_vector[4],position_vector[5]) and (i+1,j+1) == (position_vector[0],position_vector[1]):
					reward = -15
				elif (i+1,j+1) == (position_vector[4],position_vector[5]):
					reward = 20
				elif (i+1,j+1) == (position_vector[0],position_vector[1]):
					reward = -20
				else:
					reward = 0
				
				if (i+1,j+1) != (4,3):	#to avoid blocked cell
					#for all actions calculate utilities
					for a in actions:
						new_state = (i+a[0]+1,j+a[1]+1)
							
						if  new_state != (4,3) and new_state[0] <= 5 and new_state[1] <= 5 and new_state[0] > 0 and new_state[1] > 0:
							utility = reward + gamma*(utility_matrix[new_state[0]-1][new_state[1]-1]*0.95 + utility_matrix[i][j]*0.05)
						else:
							utility = reward + gamma*utility_matrix[i][j]
						utilities.append(utility)
					
					#update utility matrix with max utility
					utility_matrix[i][j] = max(utilities)

		#check max diff in old and new utility matrix
		max_diff = 0
		for i in range(5):
			for j in range(5):
				max_diff = max(max_diff, abs(V[i][j] - utility_matrix[i][j]))
		
		#update old utility matrix with new one
		for i in range(5):
			for j in range(5):
				V[i][j] = utility_matrix[i][j]

		if max_diff < delta:
			break
	
	#print(utility_matrix)
	
	#check all possible positions for wolverine, and select position with max utility
	max_utility = 0					#V[position_vector[2]-1][position_vector[3]-1]
	move = (0,0)
	for a in actions:
		new_state = (position_vector[2]+a[0],position_vector[3]+a[1])
		if new_state[0] <= 5 and new_state[1] <= 5 and new_state[0] > 0 and new_state[1] > 0 and new_state != (4,3):
			if V[new_state[0]-1][new_state[1]-1] > max_utility:
				max_utility = V[new_state[0]-1][new_state[1]-1]
				move = a

	# change position of wolverine
	if random.randint(1,100) <= 95:	
		if move[0] == -1:
			print('Wolverine move: Left')
		if move[0] == 1:
			print('Wolverine move: Right')
		if move[1] == 1:
			print('Wolverine move: UP')
		if move[1] == -1:
			print('Wolverine move: Down')
			
		position_vector[2] += move[0]
		position_vector[3] += move[1]

	# change position of magneto
	if random.randint(1,100) <= 95:	
		x_m , y_m = update_Magneto(position_vector[0],position_vector[1],position_vector[2],position_vector[3])
		position_vector[0] = x_m
		position_vector[1] = y_m
		
	# change position of jean
	if random.randint(1,100) > 80:
		if position_vector[4] == 1:
			position_vector[4] = 5
			position_vector[5] = 2
		else:
			position_vector[4] = 1
			position_vector[5] = 5
		
	if (position_vector[2],position_vector[3]) == (position_vector[4],position_vector[5]) and (position_vector[2],position_vector[3]) == (position_vector[0],position_vector[1]):
		final_reward -= 15
	elif (position_vector[2],position_vector[3]) == (position_vector[4],position_vector[5]):
		final_reward += 20
		print('Wolverine won!!!')
		break
	elif (position_vector[2],position_vector[3]) == (position_vector[0],position_vector[1]):
		final_reward -= 20
		print('Magneto won!!!')
		break
	
print('Final Reward: ',final_reward)
		
print('total steps = ',count)
input()