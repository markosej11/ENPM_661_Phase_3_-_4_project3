# header files
import cv2
import numpy as np 
import math




# class for Astar
class Astar(object):
	# init function
	def __init__(self, start, goal, startOrientation, clearance, rpm1, rpm2, radius, wheelRadius, length, dt):
		self.start = start
		self.goal = goal
		self.k = startOrientation
		self.numRows = 1020
		self.numCols = 1020
		self.clearance = clearance
		self.rpm1 = rpm1
		self.rpm2 = rpm2
		self.radius = radius
		self.wheelRadius = wheelRadius
		self.length = length
		self.dt = dt
		self.finalGoal=[]
		self.cost=np.full((int(self.numRows),int(self.numCols)), np.inf)
		self.euclidean=np.full((int(self.numRows),int(self.numCols)), np.inf)
		self.totalCost=np.full((int(self.numRows),int(self.numCols)), np.inf)
		self.visited=np.array(np.zeros((self.numRows,self.numCols)))
		self.parentList=[]
		self.path=[]
	   
		
	# move is valid 
	def IsValid(self, currRow, currCol):
		if (currRow <= 1010 - (self.radius + self.clearance)) and (currRow >= 10 + (self.radius + self.clearance)) and (currCol <= 1010 - (self.radius + self.clearance)) and (currCol >= 10 + (self.radius + self.clearance)):             
			return 1
		else:
			return 0
	# checks for an obstacle
	def IsObstacle(self, row, col):
		safe_dist = self.clearance + self.radius
		# print(safe_dist,"safe_dist")
		circle1 = (row - 510)**2 + (col - 510)**2 - (100+safe_dist)**2 <= 0
		circle2 = (row - 710)**2 + (col - 210)**2 - (100+safe_dist)**2 <= 0
		circle3 = (row - 710)**2 + (col - 810)**2 - (100+safe_dist)**2 <= 0
		circle4 = (row - 310)**2 + (col - 810)**2 - (100+safe_dist)**2 <= 0
		square1 = row <= 385 + safe_dist and row >= 235 - safe_dist and col <= 285 + safe_dist and col >= 135 - safe_dist
		square2 = row <= 185 + safe_dist and row >= 35 -safe_dist and col <= 585 + safe_dist and col >= 435 -safe_dist
		square3 = row <= 985 + safe_dist and row >= 835 -safe_dist and col <= 585 + safe_dist and col >= 435 -safe_dist

		if (circle1 or circle2 or circle3 or circle4 or square1 or square2 or square3 ):
			output = 0
		else:
			output = 1
		
		return output

	# Calculates the movement for each action
	def Differential_motion(self,r1,r2,theta):
		thata = theta * ( 22 / ( 7 * 180 ) )
		dtheta=(self.wheelRadius*(r2-r1)*self.dt)/self.length + theta
		dtheta= dtheta * ( (7 * 180) / 22) 
		dtheta=dtheta%360
		if(dtheta == 360):
			dtheta = 0
		dx=(self.wheelRadius*(r1+r2)*math.cos(dtheta * (22 / (7 * 180)))*self.dt)/2
		dy=(self.wheelRadius*(r1+r2)*math.sin(dtheta * (22 / (7 * 180)))*self.dt)/2
		return dtheta,dx,dy


	# action move Straight
	def ActionStraight(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r1,r1,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	# action move FastStraight
	def ActionFastStraight(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r2,r2,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	# action move Left1
	def ActionLeft1(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(0,r1,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node
	
	
	# action move Left2
	def ActionLeft2(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(0,r2,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node
	

	# action move Left3
	def ActionLeft3(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r1,r2,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	# action move Right1
	def ActionRight1(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r1,0,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	# action move right2
	def ActionRight2(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r2,0,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	# action move Right3
	def ActionRight3(self, currRow, currCol, currangle):
		newtheta, dx, dy = self.Differential_motion(r2,r1,currangle)
		new_node=(int(round(currRow+dx)),int(round(currCol+dy)),int(round(newtheta)))
		return new_node


	#Checking if self.goal node reached or not
	def CheckIfGoal(self, currRow, currCol, angle):
		check = (((currRow - self.goal[0]) * (currRow - self.goal[0])) + ((currCol - self.goal[1]) * (currCol - self.goal[1])) - ( 2 * 2))
		if(check <= 0):

		
			print("goal reached")
			return True
		else:
			return False
			
	#Popoing from queue based on priority
	def popQueue(self,queue):
		index_min=0
 
		X_min = queue[0][0] 
		Y_min = queue[0][1]
		for i in range(len(queue)):
			x = queue[i][0]
			y = queue[i][1]
			if self.totalCost[x,y] < self.totalCost[X_min,Y_min]:
				index_min = i
				X_min = x 
				Y_min= y
		currNode = queue[index_min]
		queue.remove(queue[index_min])
		return currNode

	#Finding the solution
	def path_find(self,start):
			GN=self.finalGoal
			# print('GN',GN)
			self.path.append(self.finalGoal)
			while (GN!=start):
				z1 = GN[0]
				z2 = GN[1]
				a=self.parentList[GN[0]][GN[1]]
				self.path.append(a)
				GN=a


	   
	# astar algorithm
	def Astar(self):
		# Converting RPM to radian per second
		global r1
		global r2
		r1 = self.rpm1*(math.pi/30)
		r2 = self.rpm2*(math.pi/30)
		print("Creating numpy arrays")
		for h in range (self.numRows):
			column=[]
			for g in range (self.numCols):
				column.append(0)
			self.parentList.append(column)
		visitedNode = []
		queue = []
		aa = self.start[0]
		bb = self.start[1]
		cc = self.k
		start1 = (aa,bb,self.k)
		queue.append([aa,bb,cc])
		self.cost[aa][bb]=0
		self.totalCost[aa][bb]=0
		currNode=[aa,bb,cc]
		#Searching
		while(len(queue) > 0):
			NoPath = 0
			#Checking if goal node
			if(self.CheckIfGoal(currNode[0],currNode[1],currNode[2]) == True):
				NoPath = 1
				self.finalGoal=currNode
				break
			currNode=self.popQueue(queue)


			straight = self.ActionStraight(currNode[0],currNode[1],currNode[2])		
			status=self.IsObstacle(straight[0],straight[1])
			flag=self.IsValid(straight[0],straight[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[straight[0],straight[1]]==0:
					self.visited[straight[0],straight[1]]=1
					visitedNode.append(straight)
					queue.append(straight)
					self.parentList[straight[0]][straight[1]]=currNode
					self.cost[straight[0],straight[1]]=(self.cost[currNode[0],currNode[1]]+1)
					self.euclidean[straight[0],straight[1]]=math.sqrt(math.pow((straight[0]-self.goal[0]),2) + math.pow((straight[1]-self.goal[1]),2))
					self.totalCost[straight[0],straight[1]]= self.cost[straight[0],straight[1]]+self.euclidean[straight[0],straight[1]]
				else:
					if self.cost[straight[0],straight[1]]>(self.cost[currNode[0],currNode[1]]+1):
						self.cost[straight[0],straight[1]]=(self.cost[currNode[0],currNode[1]]+1)
						self.euclidean[straight[0],straight[1]]=math.sqrt(math.pow((straight[0]-self.goal[0]),2) + math.pow((straight[1]-self.goal[1]),2))
						self.parentList[straight[0]][straight[1]]=currNode
						self.totalCost[straight[0],straight[1]]= self.cost[straight[0],straight[1]]+self.euclidean[straight[0],straight[1]]
	
	
			straightFast=self.ActionFastStraight(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(straightFast[0],straightFast[1])
			flag=self.IsValid(straightFast[0],straightFast[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[straightFast[0],straightFast[1]]==0:
					self.visited[straightFast[0],straightFast[1]]=1
					visitedNode.append(straightFast)
					queue.append(straightFast)
					self.parentList[straightFast[0]][straightFast[1]]=currNode
					self.cost[straightFast[0],straightFast[1]]=(self.cost[currNode[0],currNode[1]]+1)
					self.euclidean[straightFast[0],straightFast[1]]=math.sqrt(math.pow((straightFast[0]-self.goal[0]),2) + math.pow((straightFast[1]-self.goal[1]),2))
					self.totalCost[straightFast[0],straightFast[1]]= self.cost[straightFast[0],straightFast[1]]+self.euclidean[straightFast[0],straightFast[1]]
				else:
					if self.cost[straightFast[0],straightFast[1]]>(self.cost[currNode[0],currNode[1]]+1):
						self.cost[straightFast[0],straightFast[1]]=(self.cost[currNode[0],currNode[1]]+1)
						self.euclidean[straightFast[0],straightFast[1]]=math.sqrt(math.pow((straightFast[0]-self.goal[0]),2) + math.pow((straightFast[1]-self.goal[1]),2))
						self.parentList[straightFast[0]][straightFast[1]]=currNode
						self.totalCost[straightFast[0],straightFast[1]]= self.cost[straightFast[0],straightFast[1]]+self.euclidean[straightFast[0],straightFast[1]]
	
			
			right1=self.ActionRight1(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(right1[0],right1[1])
			flag=self.IsValid(straight[0],straight[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[right1[0],right1[1]]==0:
					self.visited[right1[0],right1[1]]=1
					visitedNode.append(right1)
					queue.append(right1)         
					self.parentList[right1[0]][right1[1]]=currNode
					self.cost[right1[0],right1[1]]=(self.cost[currNode[0],currNode[1]]+1)
					self.euclidean[right1[0],right1[1]]=math.sqrt(math.pow((right1[0]-self.goal[0]),2) + math.pow((right1[1]-self.goal[1]),2))
					self.totalCost[right1[0],right1[1]]= self.cost[right1[0],right1[1]]+self.euclidean[right1[0],right1[1]]

				else:
					if self.cost[right1[0],right1[1]]>(self.cost[currNode[0],currNode[1]]+1):
						self.cost[right1[0],right1[1]]=(self.cost[currNode[0],currNode[1]]+1)
						self.parentList[right1[0]][right1[1]]=currNode
						self.euclidean[right1[0],right1[1]]=math.sqrt(math.pow((right1[0]-self.goal[0]),2) + math.pow((right1[1]-self.goal[1]),2))
						self.totalCost[right1[0],right1[1]]= self.cost[right1[0],right1[1]]+self.euclidean[right1[0],right1[1]]
	
	
			left1=self.ActionLeft1(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(left1[0],left1[1])
			flag=self.IsValid(left1[0],left1[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[left1[0],left1[1]]==0:
					self.visited[left1[0],left1[1]]=1
					visitedNode.append(left1)
					queue.append(left1)
					self.parentList[left1[0]][left1[1]]=currNode
					self.euclidean[left1[0],left1[1]]=math.sqrt(math.pow((left1[0]-self.goal[0]),2) + math.pow((left1[1]-self.goal[1]),2))
					self.cost[left1[0],left1[1]]=(self.cost[currNode[0],currNode[1]]+1)
					self.totalCost[left1[0],left1[1]]= self.cost[left1[0],left1[1]]+self.euclidean[left1[0],left1[1]]
				else:
					if self.cost[left1[0],left1[1]]>(self.cost[currNode[0],currNode[1]]+1):
						self.cost[left1[0],left1[1]]=(self.cost[currNode[0],currNode[1]]+1)
						self.parentList[left1[0]][left1[1]]=currNode
						self.euclidean[left1[0],left1[1]]=math.sqrt(math.pow((left1[0]-self.goal[0]),2) + math.pow((left1[1]-self.goal[1]),2))
						self.totalCost[left1[0],left1[1]]= self.cost[left1[0],left1[1]]+self.euclidean[left1[0],left1[1]]
	
	
			right2=self.ActionRight2(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(right2[0],right2[1])
			flag=self.IsValid(right2[0],right2[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[right2[0],right2[1]]==0:
					self.visited[right2[0],right2[1]]=1
					visitedNode.append(right2)
					queue.append(right2)
					self.parentList[right2[0]][right2[1]]=currNode
					self.euclidean[right2[0],right2[1]]=math.sqrt(math.pow((right2[0]-self.goal[0]),2) + math.pow((right2[1]-self.goal[1]),2))
					self.cost[right2[0],right2[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
					self.totalCost[right2[0],right2[1]]= self.cost[right2[0],right2[1]]+self.euclidean[right2[0],right2[1]]
				else:
					if self.cost[right2[0],right2[1]]>(self.cost[currNode[0],currNode[1]]+math.sqrt(2)):
						self.cost[right2[0],right2[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
						self.parentList[right2[0]][right2[1]]=currNode
						self.euclidean[right2[0],right2[1]]=math.sqrt(math.pow((right2[0]-self.goal[0]),2) + math.pow((right2[1]-self.goal[1]),2))
						self.totalCost[right2[0],right2[1]]= self.cost[right2[0],right2[1]]+self.euclidean[right2[0],right2[1]]
	
	
			right3=self.ActionRight3(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(right3[0],right3[1])
			flag=self.IsValid(right3[0],right3[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[right3[0],right3[1]]==0:
					self.visited[right3[0],right3[1]]=1
					visitedNode.append(right3)
					queue.append(right3)
					self.parentList[right3[0]][right3[1]]=currNode
					self.euclidean[right3[0],right3[1]]=math.sqrt(math.pow((right3[0]-self.goal[0]),2) + math.pow((right3[1]-self.goal[1]),2))
					self.cost[right3[0],right3[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
					self.totalCost[right3[0],right3[1]]= self.cost[right3[0],right3[1]]+self.euclidean[right3[0],right3[1]]
				else:
					if self.cost[right3[0],right3[1]]>(self.cost[currNode[0],currNode[1]]+math.sqrt(2)):
						self.cost[right3[0],right3[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
						self.parentList[right3[0]][right3[1]]=currNode
						self.euclidean[right3[0],right3[1]]=math.sqrt(math.pow((right3[0]-self.goal[0]),2) + math.pow((right3[1]-self.goal[1]),2))
						self.totalCost[right3[0],right3[1]]= self.cost[right3[0],right3[1]]+self.euclidean[right3[0],right3[1]]
			
			
			left2=self.ActionLeft2(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(left2[0],left2[1])
			flag=self.IsValid(left2[0],left2[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[left2[0],left2[1]]==0:
					self.visited[left2[0],left2[1]]=1
					visitedNode.append(left2)
					queue.append(left2)
					self.parentList[left2[0]][left2[1]]=currNode
					self.euclidean[left2[0],left2[1]]=math.sqrt(math.pow((left2[0]-self.goal[0]),2) + math.pow((left2[1]-self.goal[1]),2))
					self.cost[left2[0],left2[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
					self.totalCost[left2[0],left2[1]]= self.cost[left2[0],left2[1]]+self.euclidean[left2[0],left2[1]]
				else:
					if self.cost[left2[0],left2[1]]>(self.cost[currNode[0],currNode[1]]+math.sqrt(2)):
						self.cost[left2[0],left2[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
						self.euclidean[left2[0],left2[1]]=math.sqrt(math.pow((left2[0]-self.goal[0]),2) + math.pow((left2[1]-self.goal[1]),2))
						self.parentList[left2[0]][left2[1]]=currNode
						self.totalCost[left2[0],left2[1]]= self.cost[left2[0],left2[1]]+self.euclidean[left2[0],left2[1]]
	
			
			left3=self.ActionLeft3(currNode[0],currNode[1],currNode[2])
			status=self.IsObstacle(left3[0],left3[1])
			flag=self.IsValid(left3[0],left3[1])
			if ( ((status) and (flag)) == 1):
				if self.visited[left3[0],left3[1]]==0:
					self.visited[left3[0],left3[1]]=1
					visitedNode.append(left3)
					queue.append(left3)
					self.parentList[left3[0]][left3[1]]=currNode
					self.euclidean[left3[0],left3[1]]=math.sqrt(math.pow((left3[0]-self.goal[0]),2) + math.pow((left3[1]-self.goal[1]),2))
					self.cost[left3[0],left3[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
					self.totalCost[left3[0],left3[1]]= self.cost[left3[0],left3[1]]+self.euclidean[left3[0],left3[1]]
				else:
					if self.cost[left3[0],left3[1]]>(self.cost[currNode[0],currNode[1]]+math.sqrt(2)):
						self.cost[left3[0],left3[1]]=(self.cost[currNode[0],currNode[1]]+math.sqrt(2))
						self.parentList[left3[0]][left3[1]]=currNode
						self.euclidean[left3[0],left3[1]]=math.sqrt(math.pow((left3[0]-self.goal[0]),2) + math.pow((left3[1]-self.goal[1]),2))
						self.totalCost[left3[0],left3[1]]= self.cost[left3[0],left3[1]]+self.euclidean[left3[0],left3[1]]

		if(NoPath == 1):
			print("There exists a path")
			print("Back tracking . . .")
		#If no path can be found	
		if(NoPath == 0):
			print("NO VALID PATH")
			return (visitedNode, [])

		#Back Tracking	
		start=[aa,bb,cc]		
		self.path_find(start)
		print("path found")
		return (visitedNode, self.path)

	# animate path
	def animate(self, explored_states, backtrack_states, path):
		print("Animation starting")
		fourcc = cv2.VideoWriter_fourcc(*'XVID')
		out = cv2.VideoWriter(str(path), fourcc, 20.0, ((self.numCols),(self.numRows)))
		image = np.zeros((int(self.numRows*1), int(self.numCols*1), 3), dtype=np.uint8)
		for row in range(0, self.numRows):
			for col in range(0, self.numCols):
				if(self.IsValid((row), (col)) and self.IsObstacle((row), (col)) == True):
					image[(col),(row)] = (0, 128, 255)
	
		count = 0
		image = cv2.circle(image, (int(self.start[0]),int(self.start[1])), 5, (255,255,255), 5)
		image = cv2.circle(image, (int(self.goal[0]),int(self.goal[1])), 5, (255,0,165), 5)

		for i in explored_states:
			cv2.circle(image,(int(i[0]),int(i[1])),(1),(255,255,0));
			cv2.imshow('result', image)
			cv2.waitKey(1)
			if(count%5==0):
				out.write(image)
			count = count + 1
		
		if(len(backtrack_states) > 0):
			for state in backtrack_states:
				image = cv2.circle(image, (int(state[0]),int(state[1])), 1, (0,0,255), 3)
				out.write(image)
		height = int(image.shape[0] * 0.8)
		width = int(image.shape[1] * 0.8)
		dim = (width,height)
		resized = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
		cv2.imshow('result', resized)
				
		cv2.waitKey(0)
		cv2.destroyAllWindows()
		out.release()