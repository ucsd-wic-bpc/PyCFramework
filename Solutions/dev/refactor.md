PyCFramework Refactor
=====================
PyCFramework was originally created when I had very little knowledge about 
Python. The original design of PyCFramework had some good concepts; however,
the overall implementation was chaotic. The goal is to refactor PyCFramework
into something more manageable (using OOP standards).


Tasks
-----


### To-Do ###
* Create a 'Case' class
	* Problem number
	* Individual Case
* Create an 'IndividualCase' class
	* Input 
	* Correct output
* Create an Executor class, which handles execution of solutions

### DONE ###
* Create a 'Solution' class
	* Problem Number
	* Solution Path
	* Language
	* Writer
* Create a 'Writer' class
	* Name
	* Solutions
	* WriterPath
* Create a 'Language' class
	* Name
	* Compile Extension
	* Compile Command
	* Compile Arguments
	* Run Extension
	* Run Command
	* Run Arguments
* Create a 'Definitions' Class
* Create a 'Variables' Class
* Create useful utility classes
	
