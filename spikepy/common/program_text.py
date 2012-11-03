

# To differentiate between the strings that only differ by case, consider 
# ending variable with sc, uc, lc for start case, upper case, and lower case.

MAIN_FRAME_TITLE = "Spikepy - A python-based spike sorting framework."

UNMARKABLE_TRIAL = '''
Trial named "%s" is unable to be marked.

This trial has %d channel(s), while the marked trials all have %d channel(s).

Trials with different numbers of channels cannot be marked at the same time.
''' 

MATPLOTLIB_VERSION = '''
Matplotlib versions less than %s will not render all plots optimally.

You're running version %s now.  
Consider upgrading to get better looking plots.''' # % (min_ver, current_ver)

ABOUT_SPIKEPY = '''
Spikepy is a python-based spike sorting application. 

It has been designed to be general enough to implement many different spike sorting algorithms.  Spikepy can be used by electrophysiologists without any additional programming skill required.  Additionally, spikepy can be easily extended to include many more spike sorting methods.  

For more information visit http://code.google.com/p/spikepy
'''

# ---- Menu Bar Text ----            
FILE = "File"
OPEN = "Open File(s)..."
LOAD_SESSION = "Load Session..."
SAVE_SESSION = "Save Session..."
EXPORT_MARKED_TRIALS = "Export marked trials..."
EXIT = "Exit"
EDIT = "Edit"
VIEW = "View"
SHOW_TOOLBARS_MENU = "Show toolbars on plots"
HELP = "Help"
PYTHON_SHELL_MENU = "Python shell"
ABOUT = "About"

# ---- Trial Grid Text ----
MARK_ALL_TRIALS = 'Mark all trials'
UNMARK_ALL_TRIALS = 'Unmark all trials'
OPEN_ANOTHER_FILE = "Open Another File..."
CLOSE_MARKED_TRIALS = "Close Marked Trials"
CLOSE_THIS_TRIAL = "Close This Trial"
RENAME_TRIAL = 'Rename This Trial'

# ---- Export Panel Text ----
EXPORT_DATA = "Export Data"
EXPORT_TO_DIRECTORY = "Export to directory:"
BROWSE = "Browse..."
CHOOSE_EXPORT_DIRECTORY = "Choose export directory"
EXPORT_MARKED = 'Export MARKED trials'
SAVE_STRATEGY = "Save..."

ALL_FILES = "All Files (*)"
SESSION_FILES = "Spikepy Session Files (*.ses)"
SAVE_SESSION = "Save Session File"
OPEN_FILE_DLG_MESSAGE = "Choose file(s) to open."
TRACE = "Trace"

# ---- stages ----
DETECTION_FILTER = "Detection Filter"
DETECTION = "Spike Detection"
EXTRACTION_FILTER = "Extraction Filter"
EXTRACTION = "Feature Extraction"
CLUSTERING = "Clustering"
AUXILIARY = 'Auxiliary'

# ---- progress dialog ----
STARTUP = "Starting up"
PROCESS_PROGRESS = "Progress"
COMPLETION_PROGRESS = "Completion Progress %s"

# ---- results notebook ----
SHOW_HIDE_OPTIONS = 'shows[+] or hides[-] options.'

# ---- strategy pane ----
STRATEGY_PANE_TITLE = 'Strategy'
RUN_STAGE = "Run '%s'" #% stage_name
RUN_AUXILIARY_PLUGINS = 'Run Auxiliary Plugins'
RUN_STRATEGY = "Run Strategy" 
STRATEGY_NAME = "Strategy"
CUSTOM_LC = "custom"
CUSTOM_SC = "Custom"

# ---- save_strategy ----
METHODS_USED_NAME = 'Methods-used Name:'
SETTINGS_NAME = 'Settings Name:'
SAVE_STRATEGY_DIALOG_TITLE = 'Save Current Strategy'
ALREADY_EXISTS_LINE = ' already exists, would you like to overwrite?'
CONFIRM_OVERWRITE = 'Confirm Overwrite'
AT_LEAST_ONE_CHARACTER = '* Name must be at least one character long.'
METHODS_USED_NAME_ALREADY_USED = 'Methods-used name: %s already exists.'
SETTINGS_NAME_ALREADY_USED = 'Settings name: %s already exists.'
MAY_NOT_CONTAIN_CUSTOM = '* Name may not contain custom.'
STRATEGY_SAVE_AS = "Save as: "
OK_TO_SAVE = 'Press OK to save.'
INVALID = '*Invalid*'

# ---- visualization ----
CANNOT_CREATE_VISUALIZATION = 'This visualization could not be completed.  The following trial resources were required but not computed:\n\n%s'
CANNOT_COMPLETE_VISUALIZATION = 'An error occured while trying to complete this visualization.\nPlease see the error message displayed on the console.'
NO_TRIAL_SELECTED = 'No trial was selected.\nSelect a trial or add trials to this session from %s --> %s' % (FILE, OPEN)

# --- Trial Rename Dialog ---
FULLPATH = 'Fullpath:'
NAME_ALREADY_EXISTS = 'The name "%s" already exists.' # % new_name
NAME_CANNOT_BEGIN_WITH = 'The name cannot begin with "."'

# --- STATUS ---
STATUS_IDLE = "Current Status: IDLE"
STATUS_RUNNING = "Current Status: RUNNING"
STATUS_OPENING = "Current Status: OPENING %d FILE(S)"
STATUS_CLOSING = "Current Status: CLOSING TRIAL(S)"
STATUS_PREPARING_EXPORT = "Current Status: PREPARING TO EXPORT DATA"
STATUS_EXPORTING = "Current Status: EXPORTING DATA"
STATUS_PLOTTING = "Current Status: GENERATING VISUALS"
STATUS_SAVING = "Surrent Status: SAVING SESSION"

# --- ERRORS ---
RESOURCE_LOCKED = 'Resource (%s) is locked.' # % self.name
RESOURCE_NOT_LOCKED = 'Resource (%s) is not locked and cannot be checked in.' # % self.name
RESOURCE_KEY_INVALID = 'Invalid key (%s) for Resource (%s), checkin failed.' # % (str(key), self.name)
RESOURCE_EXISTS = 'Resource (%s) already exists' # % resource.name

