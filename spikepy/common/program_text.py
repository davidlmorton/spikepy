# To differentiate between the strings that only differ by case, consider 
# ending variable with sc, uc, lc for start case, upper case, and lower case.

MAIN_FRAME_TITLE = "Spikepy - A python-based spike sorting framework."
STRATEGY_PANE_TITLE = 'Strategy'
FILE_LISTCTRL_TITLE = 'Opened Files List'

# ---- Preferences Frame Text ----
PREFERENCES_FRAME_TITLE = "Preferences"
WORKSPACES_MANAGER = "Workspaces Manager"

ABOUT_SPIKEPY = ("Spikepy is a python-based spike sorting "
            "framework. It has been designed to be general enough to implement "
            "many different spike sorting algorithms. Spikepy can be used by "
            "electrophysiologists without any additional programming required. "
            "Additionally, spikepy can be easily extended to include many more "
            "algorithms, or to mix and match aspects of any existing "
            "algorithms.")

# ---- Menu Bar Text ----            
FILE = "File"
OPEN = "Open File(s)..."
LOAD_SESSION = "Load Session..."
SAVE_SESSION = "Save Session..."
EXPORT_MARKED_TRIALS = "Export marked trials..."
EXPORT_ALL_TRIALS = "Export all trials..."
PRINT = "Print..."
PRINT_PREVIEW = "Print Preview..."
PAGE_SETUP = "Page Setup..."
PRINT_SUBMENU = "Print Results"
EXIT = "Exit"
EDIT = "Edit"
PREFERENCES = "Preferences" 
VIEW = "View"
SHOW_TOOLBARS_MENU = "Show toolbars on plots"
HELP = "Help"
PYTHON_SHELL_MENU = "Python shell"
ABOUT = "About"

# ---- File Grid Text ----
TRIAL_NAME = "Trial Name"
FILE_OPENING_STATUS = "**"
OPEN_ANOTHER_FILE = "Open Another File..."
CLOSE_MARKED_TRIALS = "Close Marked Trials"
CLOSE_THIS_TRIAL = "Close This Trial"
RENAME_TRIAL = 'Rename This Trial'

# ---- Export Panel Text ----
MAKE_THESE_SETTINGS_DEFAULT = "Make these settings default"
RESTORE_DEFAULT_SETTINGS = "Restore default settings"
EXPORT_TO_DIRECTORY = "Export to directory:"
BROWSE = "Browse..."
CHOOSE_EXPORT_DIRECTORY = "Choose export directory"
SELECT_STAGES = 'Select Stages'
RAW_TRACES = 'Raw Traces'
STORE_ARRAYS_AS = 'Store arrays as:'
ROWS = 'Rows'
COLUMNS = 'Columns'
FILE_FORMAT = 'File format:'
PLAIN_TEXT_SPACES = '*.txt  (space delimited plain text)'
PLAIN_TEXT_TABS = '*.txt  (tab delimited plain text)'
CSV = '*.csv  (comma delimited plain text)'
NUMPY_BINARY = '*.npz  (Numpy binary)'
MATLAB = '*.mat  (MATLAB(tm) format)'
EXPORT_ALL = 'Export ALL trials'
EXPORT_MARKED = 'Export MARKED trials'



ALL_FILES = "All Files (*)"
SESSION_FILES = "Session Files (*.ses)"
ENTER_NEW_WORKSPACE = "Enter a name for the new workspace:"
NEW_WORKSPACE_DLG_CAPTION = "Save current workspace"
OPEN_FILE_DLG_MESSAGE = "Choose file(s) to open."
TRACE = "Trace"
SAMPLE_NUMBER = "Sample Number"
PLOT_TIME = "Time (ms)"
TIME_AXIS = "Time (ms fixme)"
SPIKE_RATE_AXIS = "Estimated\nspike rate (Hz)"
DETECTION_TRACE_GRAPH_LABEL = "Detection Filtered"
STD_GRAPH_LABEL = 'Standard Deviation'
SPIKES_GRAPH_LABEL = "Spikes"
RAW = "Raw"
PSD_Y_AXIS_LABEL = "PSD (dB/Hz)"
TRIAL_NAME = 'Trial Name: '
FILTERED_TRACE_GRAPH_LABEL = "Filtered"
MISSING_PLOT_ERROR = "Plot associated with '%s' does not exist."
ENLARGE_CANVAS = "Enlarge Canvas"
ENLARGE_FIGURE_CANVAS = "Enlarge Figure Canvas"
SHRINK_CANVAS = "Shrink Canvas"
SHRINK_FIGURE_CANVAS = "Shrink Figure Canvas"
# ---- stages ----
DETECTION_FILTER = "Detection Filter"
DETECTION = "Spike Detection"
EXTRACTION_FILTER = "Extraction Filter"
EXTRACTION = "Feature Extraction"
CLUSTERING = "Clustering"
SUMMARY = "Summary"

FEATURE_AMPLITUDE = "Feature Amplitude"
FEATURE_INDEX = "Feature Index"
FEATURE_SETS = "Feature Sets"
PCA_LABEL = 'Principal Component %d (%3.1f%s)' #%(component_num, 
                                               #  percent_variance,'%')
FOUND = 'Found: '
EXCLUDED = "Excluded: "
SHOW_CURSOR_POSITION = "Show Cursor Position"
USE_SCIENTIFIC_NOTATION = "Use Scientific Notation"
SETTINGS = "Settings"
RUN_ALL = u'Run On All (\u2200)'
RUN_MARKED = "Run On Marked" 
METHOD = "Method"
METHOD_DETAILS = "Method Details"
METHOD_DETAILS_FRAME_TITLE = "Details for %s" # % method_name
RUN_BUTTON_RUNNING_STATUS = "Running"
SAVE_STRATEGY = "Save Strategy..."
STRATEGY = "Strategy"
STRATEGY_NAME = "Strategy Name:"
FILE_LISTCTRL_TITLE = "Opened Files"

METHODS_USED_NAME = 'Methods-used Name:'
SETTINGS_NAME = 'Settings Name:'
SAVE_STRATEGY_DIALOG_TITLE = 'Save Current Strategy'
ALREADY_EXISTS_LINE = ' already exists, would you like to overwrite?'
CONFIRM_OVERWRITE = 'Confirm Overwrite'

CUSTOM_LC = "custom"
CUSTOM_SC = "Custom"
AT_LEAST_ONE_CHARACTER = '* Name must be at least one character long.'
METHODS_USED_NAME_ALREADY_USED = 'Methods-used name: %s already exists.'
SETTINGS_NAME_ALREADY_USED = 'Settings name: %s already exists.'
MAY_NOT_CONTAIN_CUSTOM = '* Name may not contain custom.'
STRATEGY_SAVE_AS = "Save as: "
OK_TO_SAVE = 'Press OK to save.'
INVALID = '*Invalid*'

# --- Trial Rename Dialog ---
FULLPATH = 'Fullpath:'
NAME_ALREADY_EXISTS = 'The name "%s" already exists.' # % new_name
NAME_CANNOT_BEGIN_WITH = 'The name cannot begin with "."'



# --- Clustering Results ---
CLUSTER_NUMBER = "Cluster Number"
TRACE_NUMBER = "Trace Number"
AVERAGE_SPIKE_SHAPES = "Average Spike Shapes"
AVERAGE_OF = "Average of %d" # % number_of_spikes_in_cluster
SPIKE_STDS = "Spike STDs"
SPECIFIC_CLUSTER_NUMBER = "Cluster %d" # % cluster_num

# --- Printing ---
PRINT = "Print..."
PRINT_PREVIEW = "Print Preview"
PAGE_SETUP = "Page Setup..."

# --- STATUS ---
STATUS_IDLE = "Current Status: IDLE"
STATUS_RUNNING = "Current Status: RUNNING [%d]" # % num_processes
STATUS_OPENING = "Current Status: OPENING FILE(S) [%d]" # % num_files