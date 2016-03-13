################################################################################
# Filename: util/subparsers/subparsers/writersassign.py
# Author:   Brandon Milton, http://brandonio21.com
# Date:     10 March 2016
#
# Contains logic for the subparser that is invoked when calling
# $ ./runner.py writers assign
################################################################################
from util.language import Languages
from util.writer import Writer, Writers
from util.definitions import Definitions
from util.perror import PyCException
from util.parse import NumberParse
import queue 
SUBPARSER_KEYWORD = 'assign'
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

class SpecificProblem(object):
    """ An object to keep track of a specific problem in a specific lang """
    def __init__(self, problemNumber: int, language):
        self.problemNumber = problemNumber
        self.language = language

    def __hash__(self):
        return hash(self.language.name) + self.problemNumber

    def __eq__(self, other):
        return hash(self) == hash(other)

class AssignedSpecificProblem(SpecificProblem):

    def __init__(self, problemNumber, language, assignments):
        SpecificProblem.__init__(self, problemNumber, language)
        self.assignmentCount = assignments
        self.considered = True

    @classmethod
    def from_specific_problem(cls, problem, assignments):
        return AssignedSpecificProblem(problem.problemNumber, 
                problem.language, assignments)

    def __lt__(self, other):
        return self.assignmentCount < other.assignmentCount

class AssignedWriterWrapper(object):
    def __init__(self, writer, assignedCount):
        self.writer = writer
        self.assignedCount = assignedCount

    def __lt__(self, other):
        return self.assignedCount < other.assignedCount
        
class AssignmentAllocator(object):
    """
    An object used to assign problems and languages to various solution writers
    """
    def __init__(self, allowedProblems: list, allowedLanguages: list, 
            writerList: list, fromScratch=False):
        """
        Create a new assignment allocator by providing a list of allowed problem
        numbers (where each element is an int) and a list of allowed languages
        (where each element is a Language object)
        """
        self.writers = writerList
        self.allowedProblemNumbers = allowedProblems
        self.allowedLanguages = allowedLanguages
        self.allocation_queue = queue.PriorityQueue()
        self.writer_queue = queue.PriorityQueue()
        self.populate_allocation_queue(allZeroes=fromScratch)

    def do_assignment(self, completionThreshold, overflow=False, overflowDiff=2):
        """ Assigns the problems evenly to all writers """
        # Get the next problem off of the queue. If the queue is empty, we 
        # simply return since there is nothing left to do 
        try:
            nextProblem = self.allocation_queue.get_nowait()
        except queue.Empty:
            return

        # If this particular problem has already been assigned enough times,
        # skip it and move onto the next problem
        if ((nextProblem.assignmentCount >= completionThreshold and not overflow)
            or (nextProblem.assignmentCount >= completionThreshold and 
                nextProblem.assignmentCount - completionThreshold >= overflowDiff)):
            return self.do_assignment(completionThreshold, overflow=overflow, overflowDiff=overflowDiff)

        # Keep track of the number of writers we need to scan and keep track
        # of which ones we have not assigned
        writerCount = self.writer_queue.qsize()
        writersSearched = 1
        unassignedWriters = []

        while writersSearched <= writerCount:
            # Consider this writer and see if they are able to complete this
            # problem.
            nextWriter = self.writer_queue.get_nowait()
            if (nextWriter.writer.knows_language(nextProblem.language.name) and 
               (nextProblem.problemNumber, nextProblem.language.name) not in 
                nextWriter.writer.assignedProblems):
                    # They are able to complete it. Assign it, incremement
                    # counters, requeue, and break.
                    nextWriter.writer.add_assigned_problem(nextProblem.problemNumber, 
                            nextProblem.language.name)
                    nextWriter.assignedCount += 1
                    nextProblem.assignmentCount += 1
                    self.writer_queue.put(nextWriter)
                    self.allocation_queue.put(nextProblem)
                    break

            # This writer could not complete the problem.
            # Mark that we've searched another writer. If we reach this point,
            # then we need to mark this writer as unassigned
            writersSearched += 1
            unassignedWriters.append(nextWriter)

        # Requeue all the unassigned writers
        for unassignedWriter in unassignedWriters:
            self.writer_queue.put(unassignedWriter)

        if writersSearched <= writerCount:
            self.allocation_queue.put(nextProblem)
               
        # Recurse to get all the other problems as well
        self.do_assignment(completionThreshold, overflow=overflow, overflowDiff=overflowDiff)

    def populate_allocation_queue(self, allZeroes=False):
        """ Looks through all writers' completed solutions and assigns numbers
        to the allocation queue """
        problemsAssignedDict = {}
        writersAssignedDict = {}
        if not allZeroes:
            (problemsAssignedDict, writersAssignedDict) = self.count_assignments()


        # Now fill in zeroes for all not listed problems
        for problemNumber in self.allowedProblemNumbers:
            for problemLanguage in self.allowedLanguages:
                specificInstance = SpecificProblem(problemNumber, problemLanguage)
                if not specificInstance in problemsAssignedDict:
                    problemsAssignedDict[specificInstance] = 0

        # Now fill in zeroes for all not listed writers
        for writer in self.writers:
            # If we are reassigning, unassign from all writers as well
            if allZeroes: 
                writer.unassign_all_problems()
            if not writer in writersAssignedDict:
                writersAssignedDict[writer] = 0

        for specificProblem in problemsAssignedDict:
            self.allocation_queue.put(
                AssignedSpecificProblem.from_specific_problem(specificProblem,
                    problemsAssignedDict[specificProblem]))

        for specificWriter in writersAssignedDict:
            self.writer_queue.put( AssignedWriterWrapper(specificWriter,
                    writersAssignedDict[specificWriter]))

    def count_assignments(self):
        """ Looks through all writers' assigned solutions and counts which have
        been assigned and how many times they have """
        problemsAssignedDict = {} # Maps specificProblems to completed counts
        writersAssignedDict = {}
        for writer in Writers.get_all_writers():
            for (problemNumber, problemLanguage) in writer.assignedProblems:
                languageObject = Languages.get_language_by_name(problemLanguage)

                # Only consider the languages and problems sent into the object
                if (not problemNumber in self.allowedProblemNumbers or
                    not languageObject in self.allowedLanguages):
                    continue

                specificInstance = SpecificProblem(problemNumber, languageObject)
                if not specificInstance in problemsAssignedDict:
                    problemsAssignedDict[specificInstance] = 1
                else:
                    problemsAssignedDict[specificInstance] += 1
            
            if writer in self.writers:
                writersAssignedDict[writer] = len(writer.assignedProblems)


        return (problemsAssignedDict, writersAssignedDict)

def operate(args):
    """
    Takes the passed in args and delegates to proper functionality. This is set
    as the executable function when the `writers assign` subparser is used.

    Arguments:
    args: Namespace - The arguments passed via CLI
    """
    # If the user specified a problem list, use that as the list of problems. 
    problemParser = NumberParse()
    if not args.problems is None:
        specifiedProblems = problemParser.str_list_to_uniq_range(args.problems)
    else:
        specifiedProblems = problemParser.str_list_to_uniq_range(['1+'])

    specifiedLanguages = []
    if not args.language is None:
        for languageName in args.language:
            loadedLanguage = Languages.get_language_by_name(languageName)
            if loadedLanguage is None:
                raise PyCException('Error: {} is an invalid language'.format(languageName))
            specifiedLanguages.append(loadedLanguage)
    else:
        specifiedLanguages = [Languages.get_language_by_name(name) for name in 
                Languages.get_all_language_names()]

    specifiedWriters = []
    if not args.full and not args.writer_names is None and len(args.writer_names) > 0:
        for writerName in args.writer_names:
            loadedWriter = Writer.load_from_folder(writerName)
            if loadedWriter is None:
                raise PyCException('Error: {} is an invalid writer'.format(writerName))
            specifiedWriters.append(loadedWriter)
    else:
        specifiedWriters = Writers.get_all_writers()

    allocator = AssignmentAllocator(specifiedProblems, specifiedLanguages, 
            specifiedWriters, fromScratch=args.full)
    allocator.do_assignment(Definitions.get_value('complete_threshold'), overflow=args.overallocate)

def add_to_subparser_object(subparserObject, parentParser):
    """
    Adds the "assign" subparser to a given subparsers object and delegates
    assign functionality to the operate() function.

    Arguments:
    subparserObject - The ArgumentParser given by parser.add_subparsers() to
                      add the "delete" subparser to.
    parentParser    - The parser to be included as a parent to the subparser,
                      useful for global flags.
    """
    assignParser = subparserObject.add_parser(SUBPARSER_KEYWORD, 
                                                parents=[parentParser])

    assignParser.add_argument('writer_names', nargs='*')
    assignParser.add_argument('--overallocate', action='store_true')
    assignParser.add_argument('--full', action='store_true')
    assignParser.set_defaults(func=operate)
