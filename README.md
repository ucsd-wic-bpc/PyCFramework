PyCFramework
============
PyCFramework is a framework for managing programming competitions writter in
Python. Originally, this project was simply a rigirous refactoring of its BASH
counterpart [PCFramework](https://github.com/brandonio21/PCFramework). However,
it has evolved into a full-fledged application and is currently being used to
manage the quarterly Beginner's Programming Competition hosted by Women in 
Computing at University of California, San Diego.

Purpose
-------
A lot of information about why this project is being developed can be seen in
the documentation for PCFramework. 

When creating a programming competition, several things need to be done on the
technical level. PyCFramework attempts to automate these things to make things
easier for the creaters of the competition.

1. Creating challeneges/questions.
    
	When questions are developed, it needs to be made sure that the 
	questions are solvable, that they aren't too easy, and that they are 
	interesting. The best way to do this is to have the people designing
	the competition solve the problems. In this way, not only is the 
	difficulty of the questions verified, but template files for the 
	contestants are also created and verified. 

	Further, when the committee behind the competition writes their 
	solutions, they need to verify that their solutions are correct. These
	solutions prove that the question is solvable.

2. Managing Cases

	PyCFramework handles test cases to test solutions against with its
	"cases" functionality. Test cases are created in JSON format and are
	then used as input to the user-written solutions. This input is compared
	to the output (also written in JSON format) to determine whether a 
	solution is correct. These cases are the same cases that the contestants
	will use during the competition. 

3. Testing Solutions

	PyCFramework's primary feature is the testing of solutions. This means
	running user-written solutions against provided cases in order to 
	determine whether a solution is correct. This feature is not meant to
	be used during the competition (A platform such as HackerRank should
	probably be used), but is perfect for managing solutions written by the
	committee members.

4. Managing Solution Writers

	Of course, with a large committee full of many people writing solutions,
	there needs to be a way to manage the people writing the solutions. 
	PyCFramework takes care of this by allowing the adding and removal of
	solution writers, as well as assigning certain problems to certain users.

5. Managing Allowed Languages

	The contestants are surely only allowed to use certain languages to
	develop their solutions. Thus, the committee members should only
	use these languages. PyCFramework supports the management of allowed
	programming languages through a JSON configuration file and enforces
	these languages when testing solutions.


Installation
------------
PyCFramework can easily be installed by cloning this git repository. Nothing
else to it!



Running
-------
The executable for this project is found in Solutions/dev/runner.py. This file
should be the only file that is executed and should contain all the necessary
functionality. The script is separated into three modes of functionality:

#### ./runner.py writers ####
Manages all the writers in the competition. This module allows you to
view,add,edit, or delete writers. 

#### ./runner.py test ####
Manages the testing of solutions written for the competition. 

#### ./runner.py package ####
Manages the packaging of cases for importation into a programming
competition platform.

More information about these can be viewed inside their respective sources
(found in Solutions/dev/util/subparsers) or in the wiki.


Configuration
-------------
Many of PyCFramework's features make use of the user-provided configuration. 
This configuration is separated into three configuration files, all found
within the conf/ folder. More information of configuration can be found in the
[wiki](https://github.com/brandonio21/PyCFramework/wiki/Configuration).
	
#### definitions.json ####
Contains information regarding how the competition in general is 
configured. This includes things like how to name the solution files,
how many problems there are, how many solution writers must get a 
solution correct before it is accepted, etc.

#### languages.json ####
Contains information about the allowed languages during the competition.

#### packages.json ####
Contains information about how to package case files for uploading to
a programming competition framework such as HackerRank.

#### variables.json ####
Contains a list of variables that can be used in other configuration 
files. This file is not to be edited.
