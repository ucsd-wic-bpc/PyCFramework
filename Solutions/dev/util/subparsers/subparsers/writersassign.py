################################################################################
# Filename: util/subparsers/subparsers/writersassign.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     10 March 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers assign
################################################################################
"""
The proposed plan:

    When assigning, maintain a priority queue where writers assigned the least
    solutions are at the top. Thus, the next writer should automatically present
    themselves. 

    Rotate problem numbers, then languages.




    Writer names are provided via the argument list unless --full is provided.
    Module then searches each writer, makes list of which problems have been
    assigned and how many people have been assigned. This also inserts the
    writers into the priority queue (if full has been provided, all writers are
    inserted. Otherwise, only writers from arglist)

    Module will then look through problems (limited by --language, --problem flags),
    in numerical order, and assign them to the priority queue pop if they have
    not been completed enough times. If the --overallocate flag is given, problems
    will be evenly overallocated.

"""
